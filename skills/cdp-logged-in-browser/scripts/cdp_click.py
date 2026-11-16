#!/usr/bin/env python3
"""Drive a logged-in Chromium over CDP with trusted input.

Subcommands:
  text                     URL + body innerText
  eval "<js>"              evaluate JS, print JSON
  goto <url>               navigate and wait for readyState complete
  buttons                  list visible buttons with rects + disabled
  tap-button "<label>"     trusted click on a real <button>/[role=button]
  tap-text "<label>"       trusted click on the smallest leaf element with that text
  tap-xy <x> <y>           trusted click at viewport coordinates
  fill-id <id> "<value>"   set an input value with Angular-safe events
  chip "<value>"           type into a chip input and commit with Enter

Requires: pip install websocket-client.  Global flag: --port N (default 9222).
"""
import json
import sys
import time
import urllib.request

import websocket

PORT = 9222


def target(port):
    pages = [t for t in json.load(urllib.request.urlopen(
        f"http://127.0.0.1:{port}/json/list", timeout=10)) if t["type"] == "page"]
    if not pages:
        raise SystemExit("no page target — is the browser running with --remote-debugging-port?")
    return pages[0]


class CDP:
    def __init__(self, port=PORT):
        self.ws = websocket.create_connection(
            target(port)["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
        self.i = 0

    def send(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.i:
                return msg

    def ev(self, expr):
        r = self.send("Runtime.evaluate", expression=expr,
                      returnByValue=True, awaitPromise=True).get("result", {})
        if "exceptionDetails" in r:
            return {"error": str(r["exceptionDetails"])[:400]}
        return r.get("result", {}).get("value")

    def tap(self, x, y):
        self.send("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y,
                  button="none", clickCount=0)
        time.sleep(0.1)
        self.send("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y,
                  button="left", buttons=1, clickCount=1)
        time.sleep(0.08)
        self.send("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y,
                  button="left", buttons=0, clickCount=1)
        time.sleep(0.7)

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


FIND = """(()=>{const want=%s; const norm=s=>(s||'').replace(/\\s+/g,' ').trim();
 let els=[...document.querySelectorAll(%s)].filter(e=>e.offsetParent!==null && norm(e.innerText)%s);
 if(!els.length) return null;
 els.sort((a,b)=>(a.innerText||'').length-(b.innerText||'').length);
 const el=els[0]; el.scrollIntoView({block:'center'});
 const r=el.getBoundingClientRect();
 return {x:r.x+r.width/2, y:r.y+r.height/2, txt:norm(el.innerText).slice(0,60),
         tag:el.tagName, dis:!!el.disabled};})()"""


def _find(c, label, selector, exact=True):
    js = FIND % (json.dumps(label), selector,
                 "===want" if exact else ".toLowerCase().includes(want.toLowerCase())")
    box = c.ev(js)
    if not box:
        return None
    time.sleep(0.3)
    return c.ev(js) or box      # re-read: scrolling moved it


def main(argv):
    global PORT
    if argv[:1] == ["--port"]:
        PORT = int(argv[1])
        argv = argv[2:]
    cmd, rest = argv[0], argv[1:]
    c = CDP(PORT)
    try:
        if cmd == "text":
            print(c.ev("location.href"))
            print(c.ev("document.body ? document.body.innerText : ''"))
        elif cmd == "eval":
            print(json.dumps(c.ev(rest[0]), ensure_ascii=False)[:4000])
        elif cmd == "goto":
            c.send("Page.enable")
            c.send("Page.navigate", url=rest[0])
            for _ in range(40):
                time.sleep(1.0)
                if c.ev("document.readyState") == "complete":
                    break
            print(c.ev("location.href"))
        elif cmd == "buttons":
            print(json.dumps(c.ev("""(()=>[...document.querySelectorAll('button,[role=button]')]
              .filter(e=>e.offsetParent!==null && (e.innerText||'').trim())
              .map(e=>{const r=e.getBoundingClientRect();
                return {t:(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,30),
                        x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2),
                        dis:!!e.disabled}})())()"""), ensure_ascii=False))
        elif cmd in ("tap-button", "tap-text"):
            sel = ("button,a[role=button],[role=button]" if cmd == "tap-button"
                   else "button,a,[role=button],[role=option],mat-option,li,div,span")
            box = _find(c, rest[0], sel) or _find(c, rest[0], sel, exact=False)
            if not box:
                print("NOTFOUND", rest[0])
                return 1
            c.tap(box["x"], box["y"])
            print(f"TAPPED {box['tag']} {box['txt']!r} @{round(box['x'])},{round(box['y'])} "
                  f"disabled={box['dis']}")
        elif cmd == "tap-xy":
            c.tap(float(rest[0]), float(rest[1]))
            print("TAPPED xy", rest[0], rest[1])
        elif cmd == "fill-id":
            print(c.ev("""(()=>{const el=document.getElementById(%s); if(!el) return 'NOINPUT';
 const s=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el),'value').set;
 el.focus(); s.call(el,%s);
 el.dispatchEvent(new Event('input',{bubbles:true}));
 el.dispatchEvent(new Event('change',{bubbles:true})); return el.value;})()"""
                          % (json.dumps(rest[0]), json.dumps(rest[1]))))
        elif cmd == "chip":
            box = c.ev("""(()=>{const i=[...document.querySelectorAll('input,textarea')]
              .filter(e=>e.offsetParent!==null && !e.disabled);
              if(!i.length) return null; const el=i[0]; el.scrollIntoView({block:'center'});
              const r=el.getBoundingClientRect();
              return {x:r.x+r.width/2, y:r.y+r.height/2};})()""")
            if not box:
                print("NOINPUT")
                return 1
            c.tap(box["x"], box["y"])
            c.send("Input.insertText", text=rest[0])
            time.sleep(0.4)
            for t in ("keyDown", "keyUp"):
                c.send("Input.dispatchKeyEvent", type=t, key="Enter", code="Enter",
                       windowsVirtualKeyCode=13, nativeVirtualKeyCode=13,
                       text="\r" if t == "keyDown" else "")
            time.sleep(0.8)
            print(c.ev("(()=>[...document.querySelectorAll('mat-chip,[role=listitem]')]"
                       ".filter(e=>e.offsetParent!==null).map(e=>e.innerText.trim()).join(' | '))()"))
        else:
            print(__doc__)
            return 2
    finally:
        c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
