#!/usr/bin/env python3
"""Enumerate a Drive folder tree and export every readable file to text.

Usage:
  python drive_corpus_export.py "folder name" --out ./corpus [--max-depth 6]

Writes:
  <out>/tree.json      every item: id, name, mimeType, size, modifiedTime, path, depth
  <out>/<path>.txt     Google Docs/Slides as text, Sheets as CSV, PDF/DOCX extracted
  <out>/manifest.json  what was exported, deduped by content hash

Requires: google-auth-oauthlib (token) + google-api-python-client + pypdf + python-docx
Token: $HERMES_HOME/google_token.json (default ~/.hermes)
"""
import argparse
import hashlib
import io
import json
import os
import re
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
TOKEN = HERMES_HOME / "google_token.json"
FOLDER = "application/vnd.google-apps.folder"
FIELDS = ("nextPageToken, files(id,name,mimeType,size,modifiedTime,parents,"
          "webViewLink,shortcutDetails)")
EXPORT = {
    "application/vnd.google-apps.document": ("text/plain", ".txt"),
    "application/vnd.google-apps.spreadsheet": ("text/csv", ".csv"),
    "application/vnd.google-apps.presentation": ("text/plain", ".txt"),
}
BINARY = ("application/pdf",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


def svc():
    creds = Credentials.from_authorized_user_file(str(TOKEN))
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def norm(s):
    return "".join(ch for ch in (s or "").lower() if ch.isalnum())


def find_folders(d, needle):
    hits, token = [], None
    while True:
        r = d.files().list(q=f"mimeType='{FOLDER}' and trashed=false", fields=FIELDS,
                           pageSize=200, pageToken=token, includeItemsFromAllDrives=True,
                           supportsAllDrives=True).execute()
        hits += [f for f in r.get("files", []) if needle in norm(f["name"])]
        token = r.get("nextPageToken")
        if not token:
            return hits


def walk(d, root_id, root_name, max_depth, out, seen):
    if root_id in seen:
        return out
    seen.add(root_id)
    token = None
    while True:
        r = d.files().list(q=f"'{root_id}' in parents and trashed=false", fields=FIELDS,
                           pageSize=200, pageToken=token, includeItemsFromAllDrives=True,
                           supportsAllDrives=True).execute()
        for f in r.get("files", []):
            f["_path"] = f"{root_name}/{f['name']}"
            f["_depth"] = f["_path"].count("/") - 1
            out.append(f)
            if f["mimeType"] == FOLDER and f["_depth"] < max_depth:
                walk(d, f["id"], f["_path"], max_depth, out, seen)
        token = r.get("nextPageToken")
        if not token:
            return out


def download(d, file_id):
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, d.files().get_media(fileId=file_id))
    done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue()


def to_text(mime, fid, d, out_path):
    if mime in EXPORT:
        want, ext = EXPORT[mime]
        data = d.files().export(fileId=fid, mimeType=want).execute()
        raw = data if isinstance(data, bytes) else str(data).encode()
        out_path = out_path.with_suffix(ext)
        out_path.write_bytes(raw)
        return out_path, raw
    raw = download(d, fid)
    if mime == "application/pdf":
        from pypdf import PdfReader
        txt = "\n\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(raw)).pages)
    else:
        from docx import Document
        txt = "\n".join(p.text for p in Document(io.BytesIO(raw)).paragraphs)
    out_path = out_path.with_suffix(".txt")
    out_path.write_text(txt, encoding="utf-8")
    return out_path, raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default="corpus")
    ap.add_argument("--max-depth", type=int, default=6)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    d = svc()

    roots = find_folders(d, norm(args.folder))
    if not roots:
        raise SystemExit("no folder matched: " + args.folder)
    print("FOLDERS:")
    for f in roots:
        print("  -", f["name"], "|", f["id"], "|", f.get("modifiedTime"))

    tree = []
    for f in roots:
        walk(d, f["id"], f["name"], args.max_depth, tree, set())
    (out_dir / "tree.json").write_text(json.dumps(tree, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    print("items:", len(tree))

    seen_hash, manifest = {}, []
    for f in tree:
        if f["mimeType"] not in EXPORT and f["mimeType"] not in BINARY:
            continue
        rel = f["_path"].split("/", 1)[-1]
        stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", rel.replace("/", "__"))[:80].strip()
        try:
            path, raw = to_text(f["mimeType"], f["id"], d, out_dir / stem)
        except Exception as exc:                      # Drive 500s are transient: retry once
            try:
                path, raw = to_text(f["mimeType"], f["id"], d, out_dir / stem)
            except Exception as exc2:
                print("  ERR", rel[:60], repr(exc2)[:90])
                continue
        digest = hashlib.sha256(raw).hexdigest()[:16]
        if digest in seen_hash:
            print("  dup", rel[:60], "==", seen_hash[digest])
            continue
        seen_hash[digest] = rel
        manifest.append({"path": rel, "file": path.name, "bytes": len(raw),
                         "hash": digest, "modified": f.get("modifiedTime")})
        print("  OK", f"{len(raw):>9}", rel[:70])

    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
    print("exported:", len(manifest), "unique of", sum(1 for f in tree
          if f["mimeType"] in EXPORT or f["mimeType"] in BINARY))


if __name__ == "__main__":
    main()
