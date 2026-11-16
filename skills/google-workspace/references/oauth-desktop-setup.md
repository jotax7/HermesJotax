# Creating the Desktop OAuth client in the Cloud console

`scripts/setup.py` drives the OAuth exchange, but the **client** has to exist
first, and there is no CLI for a Desktop OAuth client — `gcloud` can create
projects and enable APIs, never an OAuth client of type "Desktop app". So this
step is either the user clicking or you driving their browser.

Prerequisite: the user is signed in to the target account in a browser you can
reach (see `computer-use` → `references/cdp-logged-in-browser.md` if you are
driving it yourself). Confirm the account before creating anything — the console
silently uses whatever project/account it last had open.

## The click path (direct URLs, fewer clicks)

| Step | URL | What to do |
|---|---|---|
| Project | `console.cloud.google.com/projectcreate` | Set the name, keep the auto-derived ID, create. Prefer a dedicated project over an existing one. |
| APIs | `console.cloud.google.com/flows/enableapi?apiid=<a>,<b>,<c>&project=<ID>` | Comma-separate every API: this single flow enables them all after one **Next → Enable**. Faster and less error-prone than six visits to the library page. |
| Consent screen | `console.cloud.google.com/auth/overview?project=<ID>` | `Comenzar` / `Get started` → wizard: app name, user-support email (a combobox), audience, contact emails (a **chip** input — type, then Enter to commit), policy checkbox, `Continuar`, `Crear`. |
| Client | `console.cloud.google.com/auth/clients/create?project=<ID>` | Type `Desktop app`, name it, `Crear`, then `Descargar JSON`. The secret is shown **once** — download before closing the dialog. |

The API IDs for the usual set:

```
gmail.googleapis.com,calendar-json.googleapis.com,drive.googleapis.com,
sheets.googleapis.com,docs.googleapis.com,people.googleapis.com
```

(`calendar-json.googleapis.com` — not `calendar.googleapis.com` — is the Calendar API.)

After `Crear` on the client dialog, the browser downloads
`client_secret_<id>.apps.googleusercontent.com.json`. With RDP/remote desktops the
download may land on the user's local machine instead of the host you are on —
check the host's `~/Downloads` first, and if it is empty ask for the file or for
the client ID + secret so you can write the JSON yourself:

```json
{"installed":{"client_id":"…","project_id":"…","auth_uri":"https://accounts.google.com/o/oauth2/auth",
 "token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
 "client_secret":"…","redirect_uris":["http://localhost"]}}
```

## Audience: Internal vs External is not cosmetic

- **Internal** (Workspace org accounts) — available when the console offers it.
  Only org users can authorize, no verification review, and the refresh token does
  not expire on a timer. This is the right choice for a personal/team automation
  on a Workspace domain.
- **External + Testing** — any Google account can authorize, but in Testing mode
  Google **expires refresh tokens after ~7 days**, so the integration silently
  dies every week and the user has to re-consent. Only pick it when the account
  must be a consumer `@gmail.com`, and say the 7-day caveat out loud.

Pick Internal whenever it is offered; it removes a recurring support ticket.

## Authorization flow without copy-paste

`scripts/oauth_loopback.py` runs a loopback listener plus PKCE and writes the
token in the `authorized_user` shape `google_api.py` reads:

```bash
python scripts/oauth_loopback.py --port 8765     # prints AUTH_URL, then waits
```

Open that URL in the browser that is already signed in, have the user approve,
and the listener captures `?code=` and writes `~/.hermes/google_token.json`
(mode 600). No code paste, no `localhost:1` error page.

Pitfalls:

- **`localhost` vs `127.0.0.1`.** A listener bound to `127.0.0.1` does not answer
  when the browser resolves `localhost` to `::1` first: the redirect page shows
  "connection refused" while the URL bar still holds the `?code=`. Don't restart
  the flow — read the URL out of the page (`cdp_client.py eval "location.href"`)
  and hand the code to the listener: `curl "http://127.0.0.1:8765/?code=<code>"`.
- **Desktop clients accept any loopback port** on `http://localhost:<port>` /
  `http://127.0.0.1:<port>` for a Desktop-type client, so a local listener needs
  no pre-registered redirect URI.
- **Approval is the user's decision.** Selecting the account tile is navigation;
  the `Allow` / `Permitir` button grants data access. Click it only when the user
  has explicitly told you to finish the flow.
- **The consent screen lists scary scopes.** Drive and Docs write scopes read as
  "delete all your files". Say plainly which powers are being granted before the
  click, and never widen the scope set "while we're here".

## Verify with a real API call, not with the token file

A token file existing proves nothing. Run one read per family you promised
(`gmail search`, `calendar list`, `drive search`) and quote a real result. This
is also the cheapest way to catch a missing API enablement
(`403 Access Not Configured`) right after setup instead of in the middle of the
user's first real request.
