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

## 3. Password walls: use the provider session

When the target site offers social login and the copied profile already holds that provider's
session, that is the fastest way past a password prompt: tap `Continue with Google`, then the
account tile. The site authenticates without any credential crossing the chat.

**When the account wanted is NOT the one in the profile**, do not fight Google's account chooser.
Its rows are `c-wiz` custom elements: they render text in `body.innerText` but come back with no
layout box, so `tap-text "Usar otra cuenta"` matches nothing and the helper dies with
`KeyError: 'x'`. Drive it through the URL instead:

```python
# from the accountchooser URL the site redirected you to
new = url.replace("/v3/signin/accountchooser?", "/v3/signin/identifier?")
q = parse_qs(urlsplit(new).query)
q["login_hint"] = ["the-account@example.com"]   # keep every other param intact
Page.navigate(urlunsplit((..., urlencode(q, doseq=True), ...)))
```

Google then prefills the address, and one `tap-button "Siguiente"` lands on `challenge/pwd` with
the email confirmed, the password box empty and focused — exactly the handover point. Typing the
email is yours; the password and the 2FA code are the user's, always.

**The copied profile carries the password store too.** On that password screen the field can arrive
already filled with the *other* account's saved password — the browser autofilled it, nobody typed
it. Never advance on a prefilled field: select-all and Delete over the Input domain
(`"modifiers": 2` is Ctrl) until `input[type=password].value.length === 0`, then say you cleared it
and hand over. Staying silent here reads as you having tried the password.

Two-factor is a hard stop — it is the user's step. Drive the browser up to the 2FA screen, tell
them exactly which window is waiting (screenshot it), and stop there. Never attempt the code, and
never ask for it in chat. If the site's social login belongs to a *different* account than the one
owning the target repo/project, the user will say so — ask which account owns it before starting.

## Before clicking: call the app's own JSON API

A logged-in SaaS is already talking to its backend from the page; `fetch()` executed through
`Runtime.evaluate` inherits the session cookies, so it returns data the UI would take twenty clicks
to show. Reach for this whenever the goal is *data* (lists, records, exports) rather than a state
change: it is faster, it survives re-renders, and it paginates in code.

```python
expr = ("fetch('/api/v1/things/search',{method:'POST',"
        "headers:{'Content-Type':'application/json'},body:JSON.stringify(%s)})"
        ".then(r=>r.json()).then(j=>JSON.stringify({total:j.pagination&&j.pagination.total_entries,"
        "rows:(j.items||[]).map(p=>({id:p.id,name:p.name}))}))") % json.dumps(body)
c.send(json.dumps({"id":i,"method":"Runtime.evaluate","params":{
    "expression":expr,"returnByValue":True,"awaitPromise":True}}))
```

- `returnByValue` **plus** `awaitPromise` is the whole trick; a bare `fetch()` returns a Promise you
  cannot serialise.
- **Project the fields you need inside `.then()`**, never return the raw payload — one page of 25
  records with embedded organizations is ~120 KB and bloats the transcript.
- **Discover the request shape from the UI**, not by guessing: open the app's search page, watch what
  it posts, reproduce the body. A 200 carrying `pagination.total_entries` confirms the field names.
- **Probe the page-size ceiling before looping.** Per-page is capped per endpoint and over-cap raises
  a specific error instead of clamping (Apollo answers `per_page: 100` with HTTP 422 `Per Page Limit
  Crossed`; 25 works). Ask for 3 records first, then size the loop from what came back.
- **Append each page to a JSONL file as it arrives.** A wide harvest outlives one tool call's timeout;
  incremental writes leave a usable dataset even when truncated, and dedupe happens in Python after.
- **Stop on `page * per_page >= total_entries` and dedupe by record id.** Keyword-OR queries return
  the same record under several terms, so raw row counts overstate the list.

Locked fields are the other half of the pattern: a prospect tool cheerfully returns 2,400 contacts
whose emails are all `email_not_unlocked@domain.com` until credits are spent one by one. Filter the
placeholders out before handing a list over, and ask how many to unlock rather than spending the
budget yourself. Endpoint bodies, pagination quirks and the scoring/dedupe recipe for prospect lists
are in `references/saas-internal-api.md`.

## 4. Clicking real web apps (Angular / Material / Cloud Console)

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

A `KeyError: 'x'` out of the helper is the same family: the matched node has **no layout box**. That
means a hidden duplicate, or — more often on Google and other `c-wiz`/custom-element UIs — the real
control lives outside the light DOM. Stop text-matching and switch strategy: set the state through a
URL parameter, or resolve the rect from a screenshot and `tap-xy`.

## 5. Verify after every step

Read `location.href` and `document.body.innerText` after each action instead of trusting the click. Angular wizards scroll and re-render; "nothing happened" and "it advanced but I read a stale page" look identical otherwise.

Verify silently, though. A console flow is **one deliverable, not a progress log**: chain
create → enable → consent → client → download inside as few calls as possible, and
report once at the end with the verified end state (project id, what got enabled, what
the token can actually read). Narrating each click back to the user reads as stalling,
and "why is it taking so long" is the usual response to it. When the user has said
"just do it", finish the flow — including the final `Allow` / `Permitir` — and state
the scopes it granted afterwards.

To *show* the state, capture over CDP — `Page.captureScreenshot` returns base64 PNG of the tab,
with no X screenshot binary and no dependence on the window manager, so it works on a headless
display or an RDP session alike. Send that file when the user needs to see where the handover is.

## OAuth with a loopback listener (bonus)

For desktop-app OAuth you control the browser: run an `http.server` on `127.0.0.1:PORT`, use `http://localhost:PORT/` as the redirect, and let the redirect land in the browser you are driving. If the browser resolves `localhost` to `::1` and the server only bound IPv4, the page errors but the URL bar still holds `?code=...` — read it over CDP and feed it to the listener with `curl "http://127.0.0.1:PORT/?code=<code>"`. Keeps the PKCE verifier in the server process.
