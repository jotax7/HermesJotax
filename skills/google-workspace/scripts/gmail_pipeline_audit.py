#!/usr/bin/env python3
"""Audit a sales pipeline from Gmail: who is waiting on us, who went silent.

Usage:
  python gmail_pipeline_audit.py [--days 90] [--max 400] [--own-domain example.com]
                                 [--top 15] [--json out.json]

Without --own-domain it is derived from the authenticated profile address.
Output: JSON with the three lists (waiting_on_us, waiting_on_them, never_answered)
plus stats. See references/gmail-pipeline-audit.md for how to read it.

Requires: google-auth-oauthlib + google-api-python-client
Token: $HERMES_HOME/google_token.json
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
TOKEN = HERMES_HOME / "google_token.json"

CAL_NOISE = re.compile(
    r"^(accepted|declined|invitation|updated invitation|canceled|cancelled|"
    r"invitaci[oó]n|actualizaci[oó]n de la invitaci[oó]n|aceptad|rechaz|cancelad)", re.I)
BILL_NOISE = re.compile(r"factura|invoice|recibo|pago|payment|cobro", re.I)
ROLE_NOISE = re.compile(r"no-?reply|donotreply|mailer|newsletter|bounce|notifications?@", re.I)
BULK = {"CATEGORY_PROMOTIONS", "CATEGORY_SOCIAL", "CATEGORY_FORUMS", "CATEGORY_UPDATES"}


def svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN))
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def addr(hval):
    m = re.search(r"<([^>]+)>", hval or "")
    return (m.group(1) if m else (hval or "")).strip().lower()


def parse_date(hval):
    try:
        dt = parsedate_to_datetime(hval or "")
        if dt.tzinfo is None:                     # naive vs aware breaks sorting
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def own_domain(g):
    prof = g.users().getProfile(userId="me").execute()
    email = prof.get("emailAddress", "")
    print("account:", email, file=sys.stderr)
    return email.split("@")[-1].lower() if "@" in email else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--max", type=int, default=400)
    ap.add_argument("--own-domain", default=None)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    g = svc()
    own = (args.own_domain or own_domain(g)).lower()
    q = f"newer_than:{args.days}d -in:chats"

    ids, token = [], None
    while len(ids) < args.max:
        r = g.users().messages().list(userId="me", q=q,
                                      maxResults=min(500, args.max - len(ids)),
                                      pageToken=token).execute()
        ids += r.get("messages", [])
        token = r.get("nextPageToken")
        if not token:
            break

    threads = defaultdict(list)
    for i, m in enumerate(ids):
        try:
            full = g.users().messages().get(
                userId="me", id=m["id"], format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"]).execute()
        except Exception:
            continue
        h = {x["name"].lower(): x["value"] for x in full["payload"].get("headers", [])}
        sender = addr(h.get("from", ""))
        threads[full["threadId"]].append({
            "ts": parse_date(h.get("date")),
            "from": sender,
            "dom": sender.split("@")[-1] if "@" in sender else "",
            "subj": h.get("subject", "(no subject)"),
            "labels": full.get("labelIds", []),
            "snippet": (full.get("snippet") or "")[:160],
        })
        if i % 50 == 0:
            print(f"  {i}/{len(ids)}", file=sys.stderr, flush=True)

    now = datetime.now(timezone.utc)
    waiting_us, waiting_them, never = [], [], []

    for tid, ms in threads.items():
        ms = [m for m in ms if m["ts"]]
        if not ms:
            continue
        ms.sort(key=lambda m: m["ts"])
        last = ms[-1]
        if last["dom"] == own or ROLE_NOISE.search(last["from"]):
            continue
        if BULK & set(last["labels"]) and not any(
                lab in ("IMPORTANT", "STARRED") for m in ms for lab in m["labels"]):
            continue
        subj = re.sub(r"^(re|rv|fw|fwd)\s*:\s*", "", last["subj"], flags=re.I)[:90]
        if CAL_NOISE.match(subj) or BILL_NOISE.search(subj):
            continue
        rec = {
            "thread": tid,
            "subject": subj,
            "who": last["from"],
            "domain": last["dom"],
            "days": (now - last["ts"]).days,
            "msgs": len(ms),
            "first_seen_days": (now - ms[0]["ts"]).days,
            "they_replied": any(m["dom"] != own for m in ms),
            "we_replied": any(m["dom"] == own for m in ms),
            "snippet": last["snippet"],
        }
        if not rec["we_replied"]:
            never.append(rec)
        elif last["dom"] != own:
            waiting_us.append(rec)
        else:
            waiting_them.append(rec)

    for lst in (waiting_us, waiting_them, never):
        lst.sort(key=lambda r: -r["days"])

    out = {
        "account": own,
        "scanned_messages": len(ids),
        "threads": len(threads),
        "window_days": args.days,
        "stats": {
            "waiting_on_us": len(waiting_us),
            "waiting_on_us_7d_plus": len([r for r in waiting_us if r["days"] >= 7]),
            "waiting_on_them": len(waiting_them),
            "never_answered": len(never),
            "never_answered_7d_plus": len([r for r in never if r["days"] >= 7]),
        },
        "waiting_on_us": waiting_us[:args.top],
        "waiting_on_them": waiting_them[:args.top],
        "never_answered": never[:args.top],
    }
    text = json.dumps(out, ensure_ascii=False, indent=1, default=str)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
