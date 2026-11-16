# Driving a logged-in web app over CDP

Use this when the page you must operate **requires the user's own session** — an
already-signed-in Google/Microsoft/CRM admin console, a portal behind SSO, a
vendor dashboard — and neither normal route can carry that session:

- `browser_exec` drives its **own headless Chromium** with its own profile. No
  cookies from the user's browser, so every page redirects to a login wall.
- `computer_use` can operate the user's browser window, but page *content* is out
  of scope and on Linux it often has no accessibility tree at all
  (`hermes computer-use doctor` → `ax_capability: X11 reachable but AT-SPI is
  not`), which leaves blind pixel clicking on a dense console UI.

Attaching to the user's real browser over the DevTools protocol gives you the
session **and** the DOM. Prefer it over pixel clicking whenever the browser is
Chrome/Chromium and you can restart it with a debug flag.

## 1. Launch a debuggable browser with the user's cookies

Chromium ≥136 **ignores `--remote-debugging-port` when the profile is the default
one** (it simply starts without opening the port), so copy the profile somewhere
non-default and use the copy:

```bash
PD="$HOME/.hermes/cache/scratch/chrome-cdp-profile"
mkdir -p "$PD"
tar -C "$HOME/.config/chromium" \
  --exclude=Cache --exclude='Code Cache' --exclude=GPUCache \
  --exclude=GrShaderCache --exclude=ShaderCache -cf - . | tar -C "$PD" -xf -
```

Launch it **on the display the user is actually looking at** (an xrdp session is
usually `:10`, not `:0`), as a tracked background process, with the same password
store the profile was created with — `--password-store=basic` means the cookie
key is fixed, so the copied cookies still decrypt:

```bash
DISPLAY=:10 XAUTHORITY=$HOME/.Xauthority \
  chromium --user-data-dir="$PD" --remote-debugging-port=9222 \
  --password-store=basic --no-first-run --no-default-browser-check \
  --new-window "https://target.app/"
```

Verify before anything else:

```bash
curl -s http://127.0.0.1:9222/json/version | head -5
curl -s http://127.0.0.1:9222/json/list | grep -o '"url": "[^"]*"' | head
```

The window is visible to the user, so say what you are doing — a browser that
reopens on an unexpected page looks like a hijack otherwise.

## 2. Drive it with the bundled client

`scripts/cdp_client.py` is a small CLI over `websocket-client`. One venv with the
dep installed is enough.

```bash
CDP="python $HOME/.hermes/skills/autonomous-ai-agents/computer-use/scripts/cdp_client.py"
$CDP goto "https://console.example.com/things/create"
$CDP text 4000            # location.href + visible text: the ground truth
$CDP inputs               # visible inputs with id / aria-label / value
$CDP buttons              # text, disabled flag and centre of every button
$CDP tapbtn "Create"      # trusted click, exact button text
$CDP taptext "Desktop app"  # trusted click on a menu option / row / cell
$CDP tapxy 552 274        # trusted click at viewport coordinates
$CDP fill input-id "value"
$CDP eval "(()=>{...})()"
```

## 3. The rules that actually make it work

**Synthetic clicks don't exist for framework UI.** `el.click()` and hand-built
`MouseEvent` / `pointerdown` sequences are `isTrusted: false`; Angular Material
(the Google Cloud console) and many React widgets accept the event but the
handler never fires. Symptom: your helper prints `CLICKED …` and the page does
not change. Use the DevTools **input** domain so the browser generates trusted
input:

```python
c.send("Input.dispatchMouseEvent", type="mouseMoved",    x=x, y=y, button="none")
c.send("Input.dispatchMouseEvent", type="mousePressed",  x=x, y=y, button="left", buttons=1, clickCount=1)
c.send("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", buttons=0, clickCount=1)
```

Type through the same domain (`Input.insertText`), and commit widget chips with
`Input.dispatchKeyEvent` (`key="Enter"`, `windowsVirtualKeyCode=13`). Setting
`el.value` with the native prototype setter plus `input`/`change` events is fine
for plain inputs and selects it, but it is the second choice.

**Re-measure after anything that scrolls or reflows.** A wizard that advances to
the next step keeps the previous step's labels in the DOM and shifts every
control vertically; coordinates captured a step earlier land on the wrong
thing. Read the rect, `scrollIntoView({block:'center'})`, sleep ~0.3 s, read the
rect again, then click.

**Match buttons narrowly.** Filtering `querySelectorAll('*')` by text picks the
innermost `<span>`, and step labels ("Next", "Siguiente", "Finalizar") also exist
as plain text in the step accordion — you click the label, nothing happens, and
it reads as a broken page. Query `button, a[role=button], [role=button]` and
compare `innerText` with whitespace collapsed and exact equality.

**Verify by reading state, not by trusting the return value.** After each step do
a cheap read-back: a `document.body.innerText` slice, `input.checked`,
`location.href`, or a `buttons` dump. A silent no-op and a successful click both
return normally.

**Progress, not silence.** These flows are slow (page loads, wizard steps,
consent screens). Post a short interim status to the user every few steps; a
multi-minute gap reads as a hang.

## 4. Safety and cleanup

- Never type a password, 2FA code or card number. Let the user complete sign-in.
- Selecting an already-signed-in account tile is navigation. Pressing
  **Allow / Authorize / Permitir** grants data access — leave that to the user
  unless they have explicitly told you to finish the flow.
- The copied profile contains the user's live cookies (hundreds of MB). Delete it
  and stop the launcher when you are done, and tell them you did.
- Don't run a debug-enabled browser against the default profile "for a minute":
  the flag is ignored, so all you create is a leftover copy.
