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
- **Telephony**: only when the agent answers real calls rather than a chat channel. Check the direction:
  outbound minutes commonly cost several times inbound in the same country.
- **Inference**: per token on a hosted model, or fixed on own hardware / on-premise.
- **Human fallback**: whoever picks up when the agent escalates.
- **Media streaming surcharge**: bridging carrier audio into the pipeline is billed per minute on top of
  the call.
- **Audio retention**: small in GB, but it is recorded client conversations — decide retention in the
  contract, not in the code.

Price in a bundle of conversations or minutes included, plus an overflow rate. An agent that promises 24/7
without a per-conversation cost line is a bet against your own margin.

### Own the stack or rent it: the number that decides

Do this arithmetic before promising on-premise voice, because the intuition is usually wrong.

- Take the expected volume in conversations × 3 min and compute the **duty cycle**. A client doing a few
  hundred conversations a month leaves a dedicated GPU idle >95% of the time.
- Rent-equivalent of a modest inference GPU lands around **USD 0.30/min ≈ USD 0.90 per 3-min
  conversation**; a parts-based cloud cascade (STT + LLM + TTS per use) lands at **USD 0.05-0.06/min ≈
  USD 0.15-0.19** per conversation.
- Break-even is in the low thousands of conversations per month. Against a first-party realtime API it
  never closes at SMB volume.
- **The case that does work: the server already exists for the text product.** Adding voice to a box that
  is already running the agent is an incremental tens-of-dollars per month, not a new capital line. Quote
  that number, not a new GPU.

If the client insists on on-premise for data-residency reasons (a normal requirement), say plainly that
voice rides on the server they already have — and that a dedicated GPU *for voice* only pays past a few
thousand conversations a month.

## Self-hosted knowledge agents

- **Fixed** on the vendor side: the deployment, monitoring and the identity/permissions model.
- **Variable in human hours**: keeping business criteria current (what counts as an active customer, how a
  channel is attributed), onboarding new sources, and re-validating answers after a schema change.
- **Hardware**: a dedicated server or an on-premise box is a line in the setup, never an implicit cost.

Charge for the criteria maintenance as capped hours or a named service; it is the part clients ask for most
and value the least when it is invisible.

## Licensing traps that become delivery risk

Price and promise only against licences you actually checked. Open weights are not the same as commercial
rights, and the trap is on the **outputs**:

- Some strong TTS models are **non-commercial including the audio they generate** — fine for a prototype,
  unusable for a client deliverable.
- Others are published as *research only*, or carry a **revenue cap** and forbid reselling the model as an
  API. A "permissive" repo label does not survive the licence file.
- Some models **watermark** generated audio; if the client wants clean audio for their own ads, they cannot
  use them.
- **Voice cloning needs written consent** from the person whose voice is used, and disclosure duties vary by
  jurisdiction. Validate locally before offering a branded voice.

A licence you did not read is a re-implementation you will pay for after the client has already signed.

## Packaging rules that survive negotiations

- **Entry product first**: modules that do not depend on a third party ship first — they generate revenue and
  fund the integration work that follows.
- **Name the modules**: a problem the client stated in discovery (average real rate, plate-to-customer match,
  duplicate emails) becomes a scoped, separately priced module with their own words in the title.
- **One price per chain, decreasing per site**: for a multi-location client, a single proposal priced per
  location gets a single signature instead of N budgets.
- **Explicit out-of-scope list**: sending campaigns, writing to production systems, and data that does not
  exist yet. Each one written down is an argument you do not have later.
