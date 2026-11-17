---
name: commercial-proposal-pricing
description: "Review, price and protect B2B service proposals."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pricing, proposals, sales, scoping, b2b]
    related_skills: [personal-agent-operating-rules, market-research]
    category: business
---

# Commercial proposals: scope, price architecture, protections

## When to Use

- The user shares a proposal, budget or quote (PDF, doc, or a draft in chat) and asks for an opinion.
- He needs one built for a named client from a discovery questionnaire, meeting notes or a call.
- A deal is stalling on scope, price or terms and the question is "¿está bien esto?".

## Division of labour: he owns the numbers, you own the architecture

The user prices the deal — he has the cost base, the client relationship and the margin target that you
do not. Never propose a currency figure as "the right price", and never re-open a price he already
settled. Your job is the structure around the number: what is included, what is capped, what is left
out, and what protects the margin when reality diverges.

Frame every critique against **margin risk** and **expansion upside**, not against taste. "El fee está
bajo" is an opinion; "un proveedor que cambia su API se come el margen de tres meses" is an argument.

## Procedure

1. **Read the client's own inputs before judging the proposal.** The discovery questionnaire or meeting
   notes contain the scope the client already agreed to. Quote their words back — it is the strongest
   part of the reply and it proves the proposal was read.
2. **Extract the real scope**: number of data sources (and their access method), areas, users, what the
   agent must answer, and what the client believes it will get. The gap between the last two is where
   proposals bleed.
3. **Check the price architecture** against the rules below.
4. **Check the commercial protections** against the checklist below.
5. **Check the out-of-scope section.** A proposal without one is a scope-creep contract.
6. **List the open questions that change the number** — user count, whether a source is API / database /
   export-only, who the technical contact is, pilot length. These go to the client *before* the number is
   final, not after they sign.
7. **Deliver the verdict first**, then the three or four changes that matter, then what is missing but
   non-pricing. Numbers stay his.

## Price architecture rules

- **The monthly fee must stand on its own against the annual setup.** A recurring fee whose annual total
  is well under the one-time setup tells the client the implementation is the product and the operation is
  an afterthought — and it will not cover the integration maintenance that follows.
- **Never ship "consultoría incluida" without an hour cap.** Open-ended advisory is the most expensive line
  in the document and the one the client values most; cap it (hours per month) and price the overflow.
- **Never ship "hasta N usuarios" under a flat fee.** Define the seats included and charge in tiers. Otherwise
  the day the rest of the company logs in, revenue stays flat and the relationship has nowhere to grow.
- **Do not gift extra sources or modules.** Price them, then discount the bundle. A gift destroys the
  reference price for the next source the client asks for; a discounted line item keeps it.
- **Every recurring line has a variable cost behind it.** Map it before signing: per-conversation messaging,
  inference, telephony, storage, support hours, third-party subscriptions. If the client can drive usage up
  without the fee moving, the contract is short a lever.
- **Price the entry product, not the whole platform.** The piece that does not depend on a third-party
  integration ships first and pays for the rest of the discovery.

## Commercial protections checklist

Every proposal that leaves the building carries:

- **Term**: minimum duration plus notice period.
- **Payment schedule**: e.g. part at kickoff, part at go-live.
- **Validity date**: a proposal with no expiry sits in a drawer for three months and forces a reprice.
- **What breaks the fixed fee**: a vendor changing or deprecating an integration, a client-side system
  migration, new sources, new areas, extra users.
- **Data and exit**: what happens to the configuration, the business definitions ("qué es un cliente
  activo") and the accesses when the engagement ends.
- **Proof**: the reference case with numbers. It is the cheapest credibility in the document.

## Output shape

- **Chat**: verdict in one line, then the changes ranked by money at risk. Short; he is usually mid-deal.
- **File**: the full scope, the source inventory table, the out-of-scope list and the open questions, saved
  in the proposals folder of his working repo and mirrored to Drive if he asks.
- Do not send anything to the client from this skill: drafts only, his OK in the same turn.

## Pitfalls

- **Judging the price without the scope.** A number is only cheap or expensive against what it includes;
  count sources, users and areas first, then speak.
- **Anchoring on consultancies instead of the client's real alternative.** The buyer compares against doing
  nothing or against the BI tool they already pay for, not against a Big Four quote. The value argument must
  beat *that* alternative.
- **"Bonificación" of the expansion lever.** Discounting extra integrations "as a courtesy for this pilot"
  reads as generous and costs the pricing anchor for every future request.
- **Setup priced without confirming the integration path.** API vs database vs spreadsheet export is a
  multiple in effort; confirm before the number leaves, or the project starts underwater.
- **Naming it a pilot while charging for production.** A pilot needs its own price, duration and success
  criteria; a full implementation with an indefinite monthly fee is a different contract.
- **Ignoring the client's own declared data problems.** They usually name them in discovery (dirty emails,
  a field that only stores the location name, plates with no owner). Each one is a scoped module and a reason
  to expand later — do not fold them silently into the base price.

## References

- `references/cost-drivers.md` — variable cost components per product line (voice/WhatsApp agents,
  self-hosted knowledge agents, integrations) and the questions that decide integration effort.
