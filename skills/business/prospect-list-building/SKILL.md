---
name: prospect-list-building
description: "Build targeted B2B prospect lists from a prospecting tool."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [prospecting, leads, apollo, outbound, commercial, latam]
    related_skills: [cdp-logged-in-browser, investor-outreach, personal-agent-operating-rules]
    category: business
---

# Building a prospect list

## When to Use

- "Conectate a Apollo / HubSpot / Sales Navigator y armame una lista de…"
- Scoping a new market or vertical and needing to know how many reachable decision-makers exist.
- Before any outbound: the list is the input, the message is the next skill.

## The deliverable is a scored CSV plus a coverage read, not a wall of names

Every list ships as three things:

1. **Full deduped CSV** — name, title, company, employees, industry, city, country, email status,
   LinkedIn. This is the queryable record.
2. **A top-N CSV** (N ≈ 100-150) of the highest-scored contacts. This is what actually gets read and
   worked by hand.
3. **A three-line read in chat**: total, split by country, and how many have a verified email. Plus the
   one thing the numbers revealed about the market.

Do not paste 2,000 names into chat. Attach the files, summarise in five lines.

## Procedure

1. **Translate the ICP into the tool's own fields.** Titles, geography, and company keywords — in the
   language(s) the market uses. Spanish and English titles coexist at the same company more often than
   not, so include the pair (`Gerente Comercial` / `Commercial Director`).
2. **Probe before harvesting**: 3 records, check the field names and the per-page cap, then size the
   loop. The mechanics — page limits, `awaitPromise`, JSONL appends, dedupe — live in the
   `cdp-logged-in-browser` skill, under its internal-API reference for Apollo.
3. **Count first, harvest second.** If the query returns 40,000 people, the filter is wrong — narrow by
   company type or seniority until the universe is small enough to read.
4. **Dedupe by record id**, never by name: the same person appears under several keyword terms and
   across countries with slightly different spellings.
5. **Score for decision power**, not for seniority theatre: general manager, commercial, leasing,
   expansion and marketing outrank operations and "jefe". Add the email-status bonus on top.
6. **Filter placeholders out before delivering.** Tools return `email_not_unlocked@domain.com` until
   credits are spent. Strip them, say they are locked, and quote the credit cost of unlocking the
   subset you recommend — do not spend the account's budget on your own judgement.
7. **Close with the next action**, one option: unlock the top N, or filter by operator/country first.

## Title taxonomy for LatAm retail, malls and consumer brands

Useful starting set when the buyer is a shopping-centre operator or a retail chain:

- Operador: `Gerente General`, `Gerente Comercial`, `Gerente de Centros Comerciales`, `Leasing Manager`,
  `Gerente de Leasing`, `Gerente de Expansión`, `Real Estate Manager`, `Shopping Manager`,
  `Gerente de Marketing`, `Gerente de Operaciones`.
- Marca que abre locales: `Gerente de Expansión`, `Real Estate`, `Country Manager`,
  `Gerente de Retail`, `Gerente Comercial`.

Keyword tags that actually return malls: `shopping center`, `shopping mall`, `centro comercial`,
`centros comerciales`, `mall`. Plain `retail` returns an order of magnitude more and mostly noise.

## Pitfalls

- **Coverage is not uniform, and the gap is the finding.** Data vendors are thin in some markets and
  deep in others (an order of magnitude between neighbouring countries is normal). Report the count by
  country on the first line; a market the tool barely covers needs a different source, not a wider
  filter, and saying so is more useful than a padded list.
- **Big-brand counts mislead.** A retailer with hundreds of branches will dominate the contact counts
  and drown the operators. Decide which side of the table the user sells to and group accordingly.
- **Aggregator and marketplace records.** Keyword searches pull in malls' own tenants, mall-adjacent
  service providers and directories. Skim the top 50 company names before scoring the whole set.
- **A revealed email is a spent credit.** Never reveal in bulk to "see what comes back"; reveal the
  shortlist and keep the balance for the follow-up round.
- **The list is not the outreach.** Do not start writing messages inside this task; hand the list over
  and let the outreach skill (and the user's own words) drive the copy.
- **Terms of service.** Scraping a personal LinkedIn session or automating messages at volume puts the
  user's own account at risk — the list is fine, the spam is not.
