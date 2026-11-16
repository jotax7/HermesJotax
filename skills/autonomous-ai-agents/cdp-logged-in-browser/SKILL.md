---
name: cdp-logged-in-browser
description: "Use when automating a logged-in Chrome via CDP."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [browser, cdp, automation, chrome, oauth, console]
    category: automation
---

# Driving a logged-in browser over CDP

## When to Use

Any task that needs the user's *existing* browser session — Google Cloud Console, LinkedIn, Instagram, a SaaS admin — or where `computer_use` captures come back empty on Linux (no AT-SPI bus). Also for OAuth flows where you drive the browser that must land on a loopback redirect.

Do NOT start a fresh headless browser — the session is gone. Attach to a real Chromium instead. This beats pixel-clicking via `computer_use` on Linux, where the AT-SPI bus is usually missing and AX trees come back empty.

## 1. Launch with a debugging port

Chrome/Chromium **136+ refuses `--remote-debugging-port` on the default profile** (silently ignores the flag). Copy the profile instead — cookies come along, so the login survives:

```bash
PD=~/scratch/chrome-cdp-profile
mkdir -p "$PD"
tar -C ~/.config/chromium --exclude=Cache --exclude='Code Cache' --exclude=GPUCache \
    --exclude=GrShaderCache --exclude=ShaderCache -cf - . | tar -C "$PD" -xf -

DISPLAY=:10 chromium --user-data-dir="$PD" --remote-debugging-port=9222 \
  --password-store=basic --no-first-run --no-default-browser-check \
  --new-window "https://target.example" &   # background=true in the terminal tool
curl -s http://127.0.0.1:9222/json/version
```

- `--password-store=basic` keeps cookie decryption working without a keyring prompt. Use the flag the original browser used.
- Do not `pkill -f "chromium.*<url>"` — the pattern matches your own shell and kills the command. Kill by PID or a narrower pattern.
- The profile copy is the user's cookie jar: tell them it exists and offer to delete it when done.

## 2. Talk to it with websocket-client

```bash
python3 -m venv ~/.hermes/venvs/cdp && ~/.hermes/venvs/cdp/bin/pip install websocket-client
```

List targets at `http://127.0.0.1:9222/json/list` (filter `type == "page"`), then `Runtime.evaluate` with `returnByValue: true` for reads and `Page.navigate` to move. Keep a small local helper module instead of re-writing the client each time.

`scripts/cdp_click.py` is that helper — copy it to scratch and drive the page from the shell:

```bash
C="~/.hermes/venvs/cdp/bin/python cdp_click.py"
$C text                              # URL + innerText
$C goto "https://console.example.com"
$C tap-button "Siguiente"            # <button> only, scrolls, re-reads rect, taps
$C tap-text "App de escritorio"       # any leaf element (menu options, tiles)
$C tap-xy 582 312                    # when you already resolved the rect
$C fill-id p6ntest-name-input "hermes-wiggy"
$C chip "someone@example.com"        # chip inputs: type + Enter
$C eval "location.href"
```

Pass `--port N` when not on 9222. The client sets `suppress_origin=True` on the
websocket — Chromium rejects handshakes carrying an `Origin` header.

## 3. Clicking real web apps (Angular / Material / Cloud Console)

Synthetic JS events are **not enough**. Dispatching `pointerdown`/`mousedown`/`click` from `element.click()` or a `MouseEvent` chain gets ignored by Angular Material buttons — the page just sits there and looks like the click never happened.

Use the CDP Input domain, which produces trusted input:

```python
c.send("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y, button="none", clickCount=0)
c.send("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", buttons=1, clickCount=1)
c.send("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", buttons=0, clickCount=1)
```

Coordinates come from `element.getBoundingClientRect()` — viewport CSS pixels. `scrollIntoView({block:'center'})` first, then **re-read the rect** after a short sleep, because scrolling moves it.

For text: focus the input, `Input.insertText`, then real `keyDown`/`keyUp` for Enter (chip inputs commit on Enter).

Resolve and tap **in the same process**: find → `scrollIntoView` → sleep ~0.3s →
re-read the rect → dispatch the three events. Splitting that into separate shell
calls reintroduces the drift, because each new connection re-reads layout after
the page has scrolled or re-rendered.

## 4. Find the element you mean

Matching `innerText` across all tags is a trap: a step label, a hidden span and the actual `<button>` all share the same text, and picking the smallest one lands on the wrong pixel. When clicking, restrict the selector to `button, a[role=button], [role=button]` and also match on `disabled`. Log the tag, text, and coordinates before tapping so a miss is obvious.

Two failure modes look identical in a log — "tapped Siguiente @582,359" when the
real button was at `387,363` is a silent wrong-element tap, not a dead button. If
a tap changes nothing, do not tap again: re-list the visible `<button>`/`[role=button]`
elements with their rects and compare against what you tapped.

## 5. Verify after every step

Read `location.href` and `document.body.innerText` after each action instead of trusting the click. Angular wizards scroll and re-render; "nothing happened" and "it advanced but I read a stale page" look identical otherwise.

Verify silently, though. A console flow is **one deliverable, not a progress log**: chain
create → enable → consent → client → download inside as few calls as possible, and
report once at the end with the verified end state (project id, what got enabled, what
the token can actually read). Narrating each click back to the user reads as stalling,
and "why is it taking so long" is the usual response to it. When the user has said
"just do it", finish the flow — including the final `Allow` / `Permitir` — and state
the scopes it granted afterwards.

## OAuth with a loopback listener (bonus)

For desktop-app OAuth you control the browser: run an `http.server` on `127.0.0.1:PORT`, use `http://localhost:PORT/` as the redirect, and let the redirect land in the browser you are driving. If the browser resolves `localhost` to `::1` and the server only bound IPv4, the page errors but the URL bar still holds `?code=...` — read it over CDP and feed it to the listener with `curl "http://127.0.0.1:PORT/?code=<code>"`. Keeps the PKCE verifier in the server process.
