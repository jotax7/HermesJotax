# Cost drivers and effort multipliers

Use this to price the *shape* of a deal before the user puts numbers on it, and to find the question that
must be answered before a fixed price is safe to quote.

## The one question that moves every integration price

For each data source, establish **how it is reached**:

| Access | Effort | Consequence for the fee |
|---|---|---|
| Documented API with a token | Low | Fits a standard plan |
| Database replica (read-only) | Medium | Needs a schema map + a stable connection; price monitoring |
| Vendor export (CSV/Excel, weekly or monthly) | Medium-high | Breaks silently when someone renames a column; the maintenance is *recurring*, not one-time |
| No clear path ("lo pregunta el de sistemas") | Unknown | Do not quote a fixed setup until this is answered |

Two or three export-only sources turn a fixed monthly fee into an open-ended support obligation. That is
the reason to cap support hours rather than to raise the fee alone.

## Voice and messaging agents

Variable cost per unit of usage — the client controls the volume, so decide who pays:

- **WhatsApp Business API**: charged per 24-hour conversation, with a different rate per category
  (service / utility / marketing). Marketing conversations are the expensive ones; a "sales lead" agent
  easily crosses into them.
- **Speech-to-text and text-to-speech**: per minute of audio, both directions.
- **Telephony**: only when the agent answers real calls rather than a chat channel.
- **Inference**: per token on a hosted model, or fixed on own hardware / on-premise.
- **Human fallback**: whoever picks up when the agent escalates.

Price in a bundle of conversations or minutes included, plus an overflow rate. An agent that promises 24/7
without a per-conversation cost line is a bet against your own margin.

## Self-hosted knowledge agents

- **Fixed** on the vendor side: the deployment, monitoring and the identity/permissions model.
- **Variable in human hours**: keeping business criteria current (what counts as an active customer, how a
  channel is attributed), onboarding new sources, and re-validating answers after a schema change.
- **Hardware**: a dedicated server or an on-premise box is a line in the setup, never an implicit cost.

Charge for the criteria maintenance as capped hours or a named service; it is the part clients ask for most
and value the least when it is invisible.

## Packaging rules that survive negotiations

- **Entry product first**: modules that do not depend on a third party ship first — they generate revenue and
  fund the integration work that follows.
- **Name the modules**: a problem the client stated in discovery (average real rate, plate-to-customer match,
  duplicate emails) becomes a scoped, separately priced module with their own words in the title.
- **One price per chain, decreasing per site**: for a multi-location client, a single proposal priced per
  location gets a single signature instead of N budgets.
- **Explicit out-of-scope list**: sending campaigns, writing to production systems, and data that does not
  exist yet. Each one written down is an argument you do not have later.
