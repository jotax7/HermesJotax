# Auditing a Drive folder / document set

Use when the user says "scan my Drive folder X and give me a roadmap / analysis /
diagnosis". The job is a grounded read of the whole corpus, not a listing: read
the documents, then report what they say, where they contradict each other, and
what is missing.

## 1. Enumerate before reading

Folder names come with variants (all-caps, trailing space, `BoulderTech` vs
`Boulder Tech`, per-user transfer folders). Match loosely (strip non-alphanumerics,
lowercase) and **print every hit with its id, then say which ones you audited** —
silently picking one drops half the material.

Always pass `supportsAllDrives=True, includeItemsFromAllDrives=True`: shared
drives and files shared *to* the user are invisible otherwise. Recurse by
`'<id>' in parents and trashed=false`, keeping a visited set so a shortcut loop
doesn't hang the walk.

`scripts/drive_corpus_export.py` does the walk plus the export and writes
`tree.json` + a manifest.

## 2. Export everything to text first

| Type | Export as |
|---|---|
| Google Doc | `files().export(mimeType='text/plain')` |
| Google Sheet | `files().export(mimeType='text/csv')` |
| Slides | `files().export(mimeType='text/plain')` |
| PDF | download bytes → `pypdf.PdfReader` per page |
| DOCX | download bytes → `python-docx` paragraphs |

Then read from disk. Exporting on demand while you analyse means every
follow-up question costs another API round trip.

Pitfalls:

- A Drive `export` can return **HttpError 500** for a perfectly valid Doc. Retry
  once immediately; it usually succeeds. Never report it as "file is broken".
- **Decks and scanned PDFs are mostly images**: an 11-page deck exporting 681
  characters is normal, not an export failure. Don't infer content from a short
  text dump — say the deck is visual, or render pages if you truly need it.
- **Duplicates are the norm**: the same deck reappears as `X`, `Copia de X`,
  `X (1).pdf`, `X.pptx.pdf`. Hash the exported bytes (or dedupe on
  name+size) before reading, or you will read the same whitepaper five times and
  count it as five sources.
- **A 3-byte export is an empty document.** Record it as a gap in the report
  rather than as "no relevant content".
- Per-user transfer folders (`user@domain 2026-…`) are usually a bulk migration
  dump. Note the count and the duplication, recommend consolidating, and don't
  audit them file by file.

## 3. Read in the right order

The value is in the strategy layer, so read in this order and stop widening once
the picture is coherent:

1. Strategy / commercial base documents (whitepaper, "the wheel", playbooks) —
   they define vocabulary and the intended funnel.
2. Spreadsheets and CRM exports (pipeline state, lead lists) — they define reality.
3. Meeting notes — they carry decisions, objections and next steps that never
   made it into any deck.
4. Decks — skim headings only; they are marketing renderings of the above.
5. Operational/technical handover docs — only if the question touches delivery.

## 4. What the report must contain

- **Inventory**: how many items per block, per type, and which folders you
  audited (with the caveat if you capped the scan).
- **Findings, sourced**: each one names the file it came from, so the user can
  check it. "The pricing annex has no amounts" — cite the proposal and the
  whitepaper tier table.
- **Contradictions between documents are findings.** The single most useful
  output of a corpus audit is two documents disagreeing: 6 vs 12 production
  clients, a pitch for enterprise vs a pitch for SMB, a step with no named owner.
  Diff the numbers and the positioning explicitly.
- **Stale state**: sort dates and compute "days since". A CRM whose last contact
  date is two months old is the headline, not a detail — compute it against today
  rather than describing the file as "recent".
- **Gaps**: empty docs, missing pricing, missing win/loss records, failed
  exports, folders nobody maintains.
- **Recommendations tied to the gaps**, phased (immediate unblock → reactivate →
  scale), each with the owner the documents already name.

Do not paste raw document text back at the user, and do not turn the audit into a
summary of every file. Ten findings they can verify beat forty they can't.

## 5. Delivery

Write the full audit to a file and send it (`MEDIA:/abs/path.md`), with the sharp
findings inline in chat. The chat version is the argument; the file is the
reference.

Deliver the artefact that was asked for. Close with **one** concrete next step you
can execute yourself, not a menu of four options — and if the user declines, drop
it and stop selling; re-pitching work they already refused after each deliverable
is the fastest way to lose their attention.

