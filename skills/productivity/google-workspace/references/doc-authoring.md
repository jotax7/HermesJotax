# Authoring a formatted Google Doc from a script

`google_api.py docs create --body` inserts **plain text only**. When the deliverable is a document a
human will read (state doc, proposal, report), build it with the Docs API in two passes: insert the
text, then style the paragraphs.

## Recipe

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(str(Path.home()/".hermes"/"google_token.json"))
drive = build("drive", "v3", credentials=creds, cache_discovery=False)
docs  = build("docs",  "v1", credentials=creds, cache_discovery=False)

TEXT = """Work OS — Joaco

1. Cómo se trabaja
..."""

# pass 1 — create and insert
doc = drive.files().create(
    body={"name": "Work OS — Joaco", "mimeType": "application/vnd.google-apps.document"},
    fields="id,name,webViewLink").execute()
did = doc["id"]
docs.documents().batchUpdate(documentId=did, body={"requests": [
    {"insertText": {"location": {"index": 1}, "text": TEXT}}]}).execute()

# pass 2 — style by walking the same string and accumulating offsets
lines, reqs, idx = TEXT.split("\n"), [], 1
for ln in lines:
    length = len(ln) + 1                      # +1 for the newline insertText added
    if ln.strip() and idx == 1:
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": idx, "endIndex": idx + length},
            "paragraphStyle": {"namedStyleType": "TITLE"}, "fields": "namedStyleType"}})
    elif ln.strip()[0].isdigit() and "." in ln[:3]:
        reqs.append({"updateParagraphStyle": {
            "range": {"startIndex": idx, "endIndex": idx + length},
            "paragraphStyle": {"namedStyleType": "HEADING_1"}, "fields": "namedStyleType"}})
    idx += length
if reqs:
    docs.documents().batchUpdate(documentId=did, body={"requests": reqs}).execute()
```

## Appending a section to an existing doc

For a living document (state board, running log) the update path is append-only, and it has two traps:
duplicating a section that already exists, and styling the wrong paragraph.

```python
doc = docs.documents().get(documentId=did).execute()
insert_at = doc["body"]["content"][-1]["endIndex"] - 1   # last valid index; -1 because it is exclusive

existing = "".join(r.get("textRun", {}).get("content", "")
                   for c in doc["body"]["content"]
                   for r in c.get("paragraph", {}).get("elements", []))
if "7. Pendientes" in existing:
    return "already there — do not append twice"

TEXT = "\n\n7. Pendientes\n\nHablarle a Migoya.\n"
reqs = [
    {"insertText": {"location": {"index": insert_at}, "text": TEXT}},
    {"updateParagraphStyle": {
        "range": {"startIndex": insert_at + 2,                     # +2 skips the leading blank lines
                  "endIndex": insert_at + 2 + len("7. Pendientes")},
        "paragraphStyle": {"namedStyleType": "HEADING_1"}, "fields": "namedStyleType"}},
]
docs.documents().batchUpdate(documentId=did, body={"requests": reqs}).execute()
```

- **Dedupe before writing.** Docs has no upsert: read the document, flatten its text, look for the section
  heading, and skip if it is there. Cheaper than reconciling a document with two copies of the same list.
- **`endIndex` is exclusive**, so the append point is `endIndex - 1`, and the style range of the appended
  block starts after however many leading newlines you inserted, not at the insert index.
- Appending is the right move for a log or a pending list. Rewriting the whole body is the right move for a
  structural change — pick per document and note which one it is at the top of the file.

## Rules

- **Offsets are cumulative and include the trailing newline** of every line (`len(line) + 1`).
  Forgetting the newline shifts every later range by one and silently styles the wrong paragraph.
- Style in a **second** batchUpdate: ranges cannot be computed until the text exists.
- `namedStyleType` accepts `TITLE`, `HEADING_1..6`, `NORMAL_TEXT`. Setting it via
  `updateParagraphStyle` with `fields: "namedStyleType"` is enough for a readable doc — no fonts or
  colours needed.
- Verify by exporting it back as text and checking the length and both ends:
  `drive.files().export(fileId=did, mimeType="text/plain")`. A doc that exists but is empty is a
  silent failure.
- One document that gets updated beats one per conversation. Before creating, search Drive for the
  existing doc by name and update it instead.
