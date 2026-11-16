#!/usr/bin/env python3
"""Google OAuth for a Desktop client: loopback listener + PKCE, no code paste.

Requires: google-auth-oauthlib (pip install google-auth-oauthlib)

Usage:
  python oauth_loopback.py --port 8765
  python oauth_loopback.py --services email,calendar
  python oauth_loopback.py --client-secret /path/to/client_secret.json --port 8765

Prints AUTH_URL and waits. Open the URL in a browser already signed in as the
target account, approve, and the redirect is captured by the listener; the token
is written to $HERMES_HOME/google_token.json (default ~/.hermes) in the
`authorized_user` shape google_api.py / google-auth expect.

If the redirect page errors (browser resolved `localhost` to ::1 while the
listener is on 127.0.0.1), do NOT restart: read the `?code=` out of the erroring
page's URL and feed it in —  curl "http://127.0.0.1:8765/?code=<code>"
"""
import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import socketserver
import threading
import time
import urllib.parse
from pathlib import Path

from google_auth_oauthlib.flow import Flow

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
PROFILES = {
    "all": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/contacts.readonly",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/documents",
    ],
    "email": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ],
    "email,calendar": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/calendar",
    ],
    "calendar,drive,sheets,docs": [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/documents",
    ],
}

captured = {}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        captured["code"] = (qs.get("code") or [""])[0]
        captured["error"] = (qs.get("error") or [""])[0]
        body = ("<html><body style='font-family:sans-serif;padding:40px'>"
                "<h2>Listo / Done</h2><p>Autorizacion recibida. "
                "Podes cerrar esta pestana.</p></body></html>").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-secret", default=str(HERMES_HOME / "google_client_secret.json"))
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--services", default="all", help=", ".join(PROFILES))
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()

    scopes = PROFILES.get(args.services)
    if not scopes:
        scopes = [s.strip() for s in args.services.split(",") if s.strip()]

    cs = Path(args.client_secret).expanduser()
    if not cs.exists():
        raise SystemExit(f"missing client secret: {cs}")

    redirect = f"http://localhost:{args.port}/"
    flow = Flow.from_client_secrets_file(str(cs), scopes=scopes, redirect_uri=redirect)
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode().rstrip("=")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    url, _state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent",
        code_challenge=challenge, code_challenge_method="S256")

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", args.port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print("LISTENING on", redirect, flush=True)
    print("AUTH_URL", url, flush=True)

    t0 = time.time()
    while time.time() - t0 < args.timeout:
        if captured.get("code") or captured.get("error"):
            break
        time.sleep(1)
    httpd.shutdown()

    if captured.get("error"):
        raise SystemExit("ERROR_AUTH " + captured["error"])
    if not captured.get("code"):
        raise SystemExit("ERROR_TIMEOUT: no code captured")

    flow.fetch_token(code=captured["code"], code_verifier=verifier)
    creds = flow.credentials
    payload = {
        "type": "authorized_user",
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token": creds.token,
        "token_uri": creds.token_uri or "https://oauth2.googleapis.com/token",
        "scopes": list(creds.scopes or scopes),
        "universe_domain": "googleapis.com",
        "expiry": creds.expiry.isoformat() + "Z" if creds.expiry else None,
    }
    out = HERMES_HOME / "google_token.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.chmod(out, 0o600)
    print("TOKEN_SAVED", out, f"({len(payload['scopes'])} scopes)")


if __name__ == "__main__":
    main()
