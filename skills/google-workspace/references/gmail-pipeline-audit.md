# Auditing a sales pipeline from Gmail alone

Use when the user asks "who should I follow up with", "where is my pipeline", or
"why am I not closing" and their deals live in email rather than a CRM. Gmail is
usually the only complete record of what was actually said and who went silent.

`scripts/gmail_pipeline_audit.py` does the scan; this file is the judgement.

## The classification that matters

Per **thread**, not per message. Take the last message and ask who it is from:

- last sender is **external** → the ball is in the user's court. This is the
  "waiting on us" list, and it is the only list that produces immediate revenue.
- last sender is the **user** → they are waiting on the prospect. Older than
  ~14 days is effectively dead unless there is a live meeting.
- the user **never replied at all** → an inbound lead that was dropped. Rank by
  age and by whether the first message looks like a real inquiry.

Threads with many messages are the most engaged prospects: always surface
message count next to staleness, because a 27-message thread idle for 23 days is
a much bigger deal than a 2-message one.

## Noise that will otherwise dominate the list

Filter before ranking, or the top of the report is calendar spam:

- **Calendar responses**: subjects starting `Accepted:`, `Declined:`,
  `Invitation:`, `Updated invitation:`, `Canceled:`, `Cancelada`, `Aceptado`,
  `Rechazado`. These look like prospect messages and are pure noise.
- **Billing**: `factura`, `invoice`, `recibo`, `pago`, `payment`, `cobro`.
- **Bulk categories**: `CATEGORY_PROMOTIONS`, `CATEGORY_SOCIAL`,
  `CATEGORY_FORUMS`, `CATEGORY_UPDATES` — unless the thread also carries
  `IMPORTANT` or `STARRED`.
- **Role addresses and vendors**: `no-reply`, `noreply`, `mailer`, `newsletter`,
  plus the SaaS senders the user obviously doesn't sell to (their own tools).

State the filter in the report, so the numbers are auditable.

## Scan cheaply, and say when it was partial

- `format="metadata"` with `metadataHeaders=["From","To","Subject","Date"]` is
  several times faster than fetching bodies. Snippets still come back on the
  message resource and are enough to judge a thread.
- Paginate with `pageToken` and cap the total. Then **report the cap**: "scanned
  350 messages of the last 90 days" is honest; presenting a capped scan as the
  whole mailbox is not.
- Query `-in:chats` unless the user wants chats, and prefer `newer_than:<N>d`
  over date arithmetic.
- Parse `Date` headers with `parsedate_to_datetime` and **attach UTC when naive**
  before sorting — mixed offsets raise
  `can't compare offset-naive and offset-aware datetimes`.

## Reporting

Lead with counts, then a short ranked list with: days idle, counterparty address,
subject, message count, and the last snippet truncated to one line. Group by
domain to show how many separate accounts are stuck, and by country/segment when
the addresses reveal it.

Close with the action, not the diagnosis: which 3-5 threads to answer today, and
whether the user wants drafts. **Never send or reply without explicit approval** —
show the drafts first.

## Pair it with the CRM file

If the user also keeps a pipeline spreadsheet (Drive), audit both and diff them:
contacts in the sheet with no email in the scanned window, and email threads with
no row in the sheet. That gap is usually the most actionable finding — it shows
where the sheet has stopped tracking reality.
