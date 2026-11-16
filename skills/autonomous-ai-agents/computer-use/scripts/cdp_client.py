#!/usr/bin/env python3
"""Minimal CDP CLI for driving an already-logged-in Chromium.

Requires: pip install websocket-client
Targets the browser started with --remote-debugging-port (default 9222; override
with CDP_PORT). See references/cdp-logged-in-browser.md for the launch recipe.

Commands:
  text [limit]        location.href + visible body text
  goto URL            navigate the page target, wait for readyState=complete
  eval "<js>"         evaluate an expression, print JSON
  tapbtn "Label"      trusted click on button / a[role=button] by exact text
  taptext "Label"     trusted click on any leaf element by text (menu options, rows)
  tapxy X Y           trusted click at viewport coordinates
  fill ID "value"     set an input by element id (native setter + input event)
  inputs              list visible inputs with id / aria / placeholder / value
  buttons             list visible buttons with text, disabled flag, centre
  links               list visible buttons / links / role=button texts

All taps go through the DevTools input domain (Input.dispatchMouseEvent): plain
JS .click() is isTrusted=false and is ignored by Angular Material and friends.
"""
import json
import os
import sys
import time
import urllib.request

import websocket

PORT = os.environ.get("CDP_PORT", "9222")
BASE = "http://127.0.0.1:" + PORT
NORM = "const norm=s=>(s||'').replace(/\\s+/g,' ').trim();"


class CDP:
    def __init__(self, match=None):
        pages = [t for t in json.load(urllib.request.urlopen(BASE + "/json/list", timeout=10))
                 if t["type"] == "page"]
        if match:
            pages = [p for p in pages if match in p["url"] or match in p.get("title", "")] or pages
        if not pages:
            raise SystemExit("no page target - is Chromium running with --remote-debugging-port?")
        self.ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=60,
                                             suppress_origin=True)
        self.i = 0

    def send(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.i:
                return msg

    def ev(self, expr, await_promise=True):
        r = self.send("Runtime.evaluate", expression=expr, returnByValue=True,
                      awaitPromise=await_promise)
        res = r.get("result", {})
        if "exceptionDetails" in res:
            exc = res["exceptionDetails"].get("exception", {})
            return {"error": str(exc.get("description", ""))[:500]}
        return res.get("result", {}).get("value")

    def click_xy(self, x, y):
        self.send("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y,
                  button="none", clickCount=0)
        time.sleep(0.08)
        self.send("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y,
                  button="left", buttons=1, clickCount=1)
        time.sleep(0.08)
        self.send("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y,
                  button="left", buttons=0, clickCount=1)
        time.sleep(0.6)

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def find_js(label, selector):
    return ("(()=>{" + NORM + " const want=" + json.dumps(label) +
            "; const els=[...document.querySelectorAll(" + json.dumps(selector) + ")]"
            ".filter(e=>e.offsetParent!==null && norm(e.innerText)===want);"
            " if(!els.length) return null;"
            " els.sort((a,b)=>(a.innerText||'').length-(b.innerText||'').length);"
            " const el=els[0]; el.scrollIntoView({block:'center'});"
            " const r=el.getBoundingClientRect();"
            " return {x:r.x+r.width/2,y:r.y+r.height/2,txt:norm(el.innerText).slice(0,50),"
            "tag:el.tagName,dis:!!el.disabled};})()")


def tap(c, label, selector):
    js = find_js(label, selector)
    box = c.ev(js)
    if not box:
        return "NOTFOUND: " + label
    time.sleep(0.3)
    box = c.ev(js) or box          # re-measure: the layout drifts between steps
    c.click_xy(box["x"], box["y"])
    return "TAPPED %s '%s' @%d,%d disabled=%s" % (
        box["tag"], box["txt"], round(box["x"]), round(box["y"]), box["dis"])


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "text"
    c = CDP()
    if cmd == "text":
        print("URL:", c.ev("location.href"))
        body = c.ev("document.body ? document.body.innerText : ''") or ""
        lim = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
        print(body[:lim])
    elif cmd == "goto":
        c.send("Page.enable")
        c.send("Page.navigate", url=sys.argv[2])
        c.close()
        for _ in range(20):
            time.sleep(1.5)
            c = CDP()
            if c.ev("document.readyState") == "complete":
                break
        print(c.ev("location.href"))
    elif cmd == "eval":
        print(json.dumps(c.ev(sys.argv[2]), ensure_ascii=False)[:5000])
    elif cmd == "tapbtn":
        print(tap(c, sys.argv[2], "button,a[role=button],[role=button]"))
    elif cmd == "taptext":
        print(tap(c, sys.argv[2], "mat-option,[role=option],li,td,a,div,span"))
    elif cmd == "tapxy":
        c.click_xy(float(sys.argv[2]), float(sys.argv[3]))
        print("tap", sys.argv[2], sys.argv[3])
    elif cmd == "fill":
        print(c.ev("(()=>{const el=document.getElementById(%s); if(!el) return 'NOINPUT';"
                   " const s=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el),'value').set;"
                   " el.focus(); s.call(el,%s);"
                   " el.dispatchEvent(new Event('input',{bubbles:true}));"
                   " el.dispatchEvent(new Event('change',{bubbles:true})); return el.value;})()"
                   % (json.dumps(sys.argv[2]), json.dumps(sys.argv[3]))))
    elif cmd == "inputs":
        print(json.dumps(c.ev("[...document.querySelectorAll('input,textarea,select')]"
                              ".filter(e=>e.offsetParent!==null).map(e=>({id:e.id,name:e.name,"
                              "aria:e.getAttribute('aria-label'),ph:e.getAttribute('placeholder'),"
                              "type:e.type,val:(e.value||'').slice(0,40)}))"), ensure_ascii=False))
    elif cmd == "buttons":
        print(json.dumps(c.ev("[...document.querySelectorAll('button,[role=button]')]"
                              ".filter(e=>e.offsetParent!==null && (e.innerText||'').trim())"
                              ".map(e=>{const r=e.getBoundingClientRect();"
                              "return {t:e.innerText.replace(/\\s+/g,' ').trim().slice(0,30),"
                              "dis:!!e.disabled,x:Math.round(r.x+r.width/2),"
                              "y:Math.round(r.y+r.height/2)}})"), ensure_ascii=False))
    elif cmd == "links":
        print(json.dumps(c.ev("[...document.querySelectorAll('button,a,[role=button]')]"
                              ".filter(e=>e.offsetParent!==null)"
                              ".map(e=>(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,50))"
                              ".filter(Boolean).slice(0,80)"), ensure_ascii=False))
    else:
        print(__doc__)
    c.close()


if __name__ == "__main__":
    main()
