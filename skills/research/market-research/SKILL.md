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

## Quality Gate

Before delivering:
- all numbers are sourced or labeled as estimates
- old data is flagged
- the recommendation follows from the evidence
- risks and counterarguments are included
- the output makes a decision easier
