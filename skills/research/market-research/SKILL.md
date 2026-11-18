---
name: market-research
description: Conduct market research, competitive analysis, investor due diligence, and industry intelligence with source attribution and decision-oriented summaries. Use when the user wants market sizing, competitor comparisons, fund research, technology scans, or research that informs business decisions.
license: MIT
---

# Market Research

Produce research that supports decisions, not research theater.

## When to Activate

- researching a market, category, company, investor, or technology trend
- building TAM/SAM/SOM estimates
- comparing competitors or adjacent products
- preparing investor dossiers before outreach
- pressure-testing a thesis before building, funding, or entering a market

## Research Standards

1. Every important claim needs a source.
2. Prefer recent data and call out stale data.
3. Include contrarian evidence and downside cases.
4. Translate findings into a decision, not just a summary.
5. Separate fact, inference, and recommendation clearly.

## Common Research Modes

### Investor / Fund Diligence
Collect:
- fund size, stage, and typical check size
- relevant portfolio companies
- public thesis and recent activity
- reasons the fund is or is not a fit
- any obvious red flags or mismatches

#### Mapping where a fund is investing *right now*

A portfolio page answers "who did they back in 2015". The current direction is elsewhere, and the two big
funds publish it in different places:

- **Y Combinator** — `/rfs` (Requests for Startups). Each batch gets its own set, each item signed by a
  partner, and it is the closest thing to a public investment thesis: read the titles first, then the body
  of the two or three that touch the user's market, and quote the partner's own words rather than
  paraphrasing. `/companies?batch=<Batch>` gives per-batch counts and the industry split in the filter
  sidebar (B2B, Industrials, Fintech, Consumer, Healthcare…), and `/companies/industry/<sector>` lists a
  sector across all batches. The directory only renders ~40 cards at a time; the sidebar total is the real
  batch size.
- **Sequoia** — has **no complete portfolio page**: `our-companies` shows only a couple of dozen trophy
  names. Their direction lives in `/article/*` (the annual "this is AGI"-style thesis), `/series/*`
  (thematic series such as sovereign AI) and the news posts announcing a partner's investment with a named
  author. Read the thesis essay before the portfolio or you will describe 2020.
- **Both** — read the *difference in stage* before comparing: one fund spreads hundreds of small bets, the
  other writes three-figure cheques into a dozen. The same "hot area" means opposite things to each.

### Competitive Analysis
Collect:
- product reality, not marketing copy
- funding and investor history if public
- traction metrics if public
- distribution and pricing clues
- strengths, weaknesses, and positioning gaps

### Company Dossier (a single company)
Collect, in this order:
- what the company actually sells and where — verified from its own catalogue, never inferred from the
  name or from the category the user called it
- legal shape, headcount, HQ, founding year
- business model and who really pays: distributor, franchisee or end customer are not the same payer
- scale signals: location count, openings, network size, hiring activity
- pricing and catalogue shape (SKU count by category beats "a wide range")
- digital footprint with quality metrics — follower count *and* engagement, never followers alone
- undated sources, flagged as possibly stale
Output separates `## Facts`, `## Inference`, `## Information gaps`.

For retail and franchise businesses, work out who the customer of the business actually is before
analysing risk: a franchisor earns from supplying its network, not from the till of any single store.
That inverts the risk read and is usually where the operational data pain lives.

#### Portfolio operators (mall groups, chains, REITs)

When the subject owns many assets, the interesting unit is the **asset**, not the group, and the
per-asset numbers are already public:

- **A listed operator's annual report is the only source with asset-level KPIs.** The 20-F (foreign
  private issuers) or the earnings release carries, per property: gross leasable area, store count,
  occupancy rate, tenant sales, and **sales per square metre** with the year-on-year change in real
  terms. A marketing site gives you one flattering headline; the filing gives you the ranking that
  makes a comparison possible.
- **Sales per m² is the comparison metric.** Absolute revenue tracks size and hides performance: a
  mall twice the area can earn the same and be half as productive. Whenever the question is "which
  one should I be in", answer in sales per m², occupancy and real growth, in that order.
- **Real vs nominal is the trap.** In a high-inflation market the nominal table looks like growth. Take
  the deflator from the filing itself, or state the assumption, and label every rate as nominal or
  real — a reader who assumes real from an unlabelled column will double the growth.
- **Occupancy is where the negotiating leverage is.** The properties well below portfolio occupancy
  are the ones with space to fill; the ones at 100% have nothing to offer and will price accordingly.
- **The mix matters more than the average.** A portfolio average blends an anchor and a kiosk, so ask
  for the category breakdown before drawing conclusions from a single number.

Once the per-asset picture exists, turn it into decision questions rather than a report: why one
property is twice as productive as a peer of the same owner, which assets sit below the occupancy
line, how much demand the operator is capturing in each catchment, and whether the portfolio's
growth came from the base or from one new tenant. The last one is usually the finding.

### Market Sizing
Use:
- top-down estimates from reports or public datasets
- bottom-up sanity checks from realistic customer acquisition assumptions
- explicit assumptions for every leap in logic

### Technology / Vendor Research
Collect:
- how it works
- trade-offs and adoption signals
- integration complexity
- lock-in, security, compliance, and operational risk

## Output Format

Default structure:
1. executive summary
2. key findings
3. implications
4. risks and caveats
5. recommendation
6. sources

### Chat answer vs. artefact — this split is the user's preference, not a style choice

- **The chat reply is a summary**: one paragraph plus bullets, roughly 15 lines, carrying the decision
  and the two or three numbers that drive it. No tables, no restating the method.
- **The full dossier goes to a file** (`research/<company-or-topic>.md` inside the versioned work repo,
  linked or attached), with sources, gaps and the long analysis. Never paste a 60-line dossier into chat
  and never make the user scroll for the conclusion.
- **Live-meeting mode:** when the user is in a call while asking, drop the structure entirely and reply
  with three things — the question to ask, the number to cite, and the hook — in under ten lines. Save the
  depth for after the call.
- Say which of the two you are delivering in the first line ("resumen, ficha completa en el archivo").

### Startup-list requests ("dame N startups que…")

When the user wants a shopping list rather than a dossier, the format *is* the deliverable and they will
say "nada más" if you add commentary:

- one line per company: **name** — what it does, in the language the founder would use, no adjectives
- group by area when they ask for areas (educación, salud, nichos raros, bien público)
- close with a short **top 3** and the reason in a clause, not a paragraph
- no preamble, no method note, no closing question
- filter for what they actually asked: easy to implement, an obvious buyer, a product describable in one
  line. Skip the deep-tech bets unless the list is explicitly about them — and say so when a whole batch
  turned out to be wrappers on a real pain, because that *is* the finding.

Keep the honest read: "simple to describe" is not "simple to run". The moat in that class of company is
go-to-market and integration work, and the user profits from hearing that once rather than three times.

## Pitfalls

- **Verify the vertical before analysing it.** A brand name plus the user's context is not evidence of
  what the company sells — a brand present in shopping malls can be beauty retail rather than apparel.
  Confirm from its own catalogue or store listing first; analysing the wrong industry invalidates the
  whole dossier and the recommendation built on it.
- **Consumer brand names collide.** Same-country namesakes and unrelated shops with an identical sign are
  the standard trap. Search the name with a differentiator (city, category, founder) and check every source
  is about the same company.
- **Franchise and "current status" case studies are usually undated.** Figures like "2 open, 3 opening, 9
  reserved" age badly; present them as "at the time of that source" and list the live count as an
  information gap instead of asserting it as current.
- **Re-verify the user's own premise before building on it.** When the brief states a portfolio size,
  a headcount or a price, check it against the latest filing first. These numbers move every fiscal
  year, and a count that is one year stale misnumbers every comparison built on top — better to correct
  it in the first line than to hand over an analysis of a portfolio that no longer exists.
- **A company's own website is not the record.** It describes the brand it wants today: no divestments,
  no closed assets, no weak quarter. Use it for identity and catalogue, the filing for numbers.

- **A curated portfolio page is marketing, not a dataset.** If a fund's site lists a handful of famous
  names, that is the brand it wants associated with today — the absence of a company there says nothing
  about whether it was funded. Say "their site shows N names" instead of "they only invested in N".
- **Batch counts move after demo day.** The directory states how many companies have *launched* so far and
  keeps adding; a count quoted today is a snapshot, not the final batch size.
- **Requests for Startups are forward-looking asks, not investments.** They say what a fund wants to see
  next; never present an RFS theme as evidence that the fund has backed someone in it.

## Quality Gate

Before delivering:
- all numbers are sourced or labeled as estimates
- old data is flagged
- the recommendation follows from the evidence
- risks and counterarguments are included
- the output makes a decision easier
