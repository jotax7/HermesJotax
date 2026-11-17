# Reading the client's own inputs before pricing

The strongest review is one that quotes the client's own discovery answers back. This is the mechanical
recipe: pull the file out of the mail thread, extract it, and mine the numbers that decide the price.

## 1. Find the message and download the attachment

Gmail attachments are not in the message body; fetch them by id. Run with the interpreter that has the
Google libs (see the `google-workspace` skill for the venv path on this host).

```python
q = 'from:<client-domain> has:attachment newer_than:7d'
res = g.users().messages().list(userId="me", q=q, maxResults=5).execute().get("messages", [])
full = g.users().messages().get(userId="me", id=m["id"], format="full").execute()

def walk(part, out):
    if part.get("filename") and part.get("body", {}).get("attachmentId"):
        out.append(part)
    for child in part.get("parts", []) or []:
        walk(child, out)

parts = []
walk(full["payload"], parts)
blob = g.users().messages().attachments().get(
    userId="me", messageId=m["id"], id=parts[0]["body"]["attachmentId"]).execute()
open(name, "wb").write(base64.urlsafe_b64decode(blob["data"]))
```

Inline signature images arrive as attachments too — filter by extension, not by count.

## 2. Extract, including tables

- `.docx` → `python-docx`: `Document(path).paragraphs` for the answers **and** `.tables` for the source
  inventory. Reading only the paragraphs loses the table where the client listed every system, its
  owner, its history and its access method — the one artefact that sets integration effort.
- `.pdf` → `pypdf` page by page, or `pdftotext` (poppler) which is faster and usually already installed.

## 3. What to mine, in this order

1. **Sources table**: count them, note access method per row (API / database / export). API vs export is a
   multiple in effort and belongs in the scope, not in a footnote.
2. **The business questions they wrote** — quote them verbatim in the review; it proves the document was
   read and they are the definition of "working".
3. **Users and areas named** — compare against the seats the plan grants.
4. **Their own declared data problems** (dirty emails, a field that only stores a name, plates with no
   owner). Each is a future paid module; surface them by name instead of folding them into the base scope.
5. **Systems already in place** (CRM, BI, loyalty app) — these decide the value anchor: the buyer compares
   against the tool they already pay for.
6. **Approver** and who signs — it sets the length and tone of the proposal.

## 4. Keep the extract

Save the plain-text extract next to the proposal draft in the working repo. Reviews get re-opened when the
client answers a follow-up, and re-downloading the same attachment wastes a round trip.
