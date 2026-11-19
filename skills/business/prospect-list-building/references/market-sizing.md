# Sizing a market from a prospecting database

Use when the question is *where is the money / where should a product exist*, not *give me names*.
Same endpoints as list-building, read as structure. Searches are free; only reveals cost credits, so a
whole sizing study can cost zero.

## The six queries

Run each as a count (`per_page: 1`, read `pagination.total_entries`). Record every single number to a
JSONL as it lands — a study is 100-400 calls and a truncated run must still be analysable.

Mechanics, verified against the live app: `POST /api/v1/mixed_people/search` and
`POST /api/v1/mixed_companies/search`, issued as a `fetch` **from the logged-in page** so session cookies
ride along. `per_page` caps at **25** (above that the API answers `422 Per Page Limit Crossed`), so a
2,000-row universe is ~80 sequential calls — sleep ~0.4 s between them and append after each page.
Dedupe on the record `id`, never on name.

1. **Role density per country.** One call per (country × title cluster). Use 8-12 clusters of 5-8
   synonymous titles each, mixing the local language and English (`Cobranzas` / `Collections`,
   `Facturación` / `Billing`).
2. **Company universe per vertical.** One call per (country × vertical × employee band), bands
   `51,100`+`101,200` and `201,500`+`501,1000`. Keyword tags OR together, so pass the synonyms.
3. **Vertical × role cross-tab.** People search with both `person_titles` and
   `q_organization_keyword_tags`. This is the table that finds the pockets; everything else is context.
4. **Seniority distribution.** Same people query plus `person_seniorities: ["entry"]`, `["manager"]`,
   `["head"]`, … one call per level. This is the champion test (below).
5. **Reachability sample.** Pull 25 people per candidate pocket and compute `email_status == verified`
   and `linkedin_url` presence. Cheap, and it kills ideas before you write them up.
6. **Growth.** Sample 20-25 companies per vertical and take the median of
   `organization_headcount_six_month_growth` / `_twelve_month_growth`.

## Reading rules

- **Headcount in a role = budget already spent.** This is the market, not the TAM slide. A pool of
  20k people doing one repetitive task is a line item someone wants to cut.
- **Seats per buyer** = pool ÷ companies in the 51-1000 band. High seats means one sale lands many
  seats; low seats means a long tail of small deals.
- **Entry-level share is the champion test.** Above ~80% entry-level the function has no internal owner
  and the sale goes to the CFO or the founder — budget it as a longer cycle. A role with 20-30%
  managers has someone whose job is the process, and they can sign.
- **Growth outranks size.** A vertical hiring at 2-3%/year has an approved budget and scale pain; one at
  0.5% is cutting. Growth is the "where are they investing" proxy the job-postings endpoint would give.
- **Reachability gates everything.** Under ~15% verified email the buyer effectively does not answer:
  change the entry point (partner, association, incumbent software vendor) or drop the pocket, however
  big the pool is.
- **Compare against a benchmark market.** The same role queried in a large, well-covered market yields
  a ratio that is a strategy, not trivia: a role 2-3× denser locally is a structural local advantage
  nobody from outside will attack; a role 10-25× denser there means build locally at local cost and
  sell into the big market.

## Limits to state in the deliverable

Prospecting databases are contact stores, not demand stores. Say so explicitly instead of padding:

- Job-postings endpoints may not exist on the plan (`/api/v1/job_postings/search` answering 404 means
  unavailable) — then headcount and growth are the proxy, and name them as such.
- `organization_revenue` frequently comes back `0`/null for emerging markets: do not build a
  revenue-per-employee table on it, and do not substitute an invented figure.
- Intent signals (`has_intent_signal_account`, `intent_strength`) can be uniformly false outside the
  vendor's core markets; sample one page to confirm before promising intent data.
- Anything inferred (cost per seat, salary, capture rate) ships labelled as `supuesto, no dato`, with
  the arithmetic visible.

## Deliverable shape

One document, in this order: method and its limits → the size numbers by country → the cross-tab of
pockets → 2-4 named opportunities with the data behind each → where NOT to go and why → the economics
with assumptions flagged → next step. Attach the raw JSONL files as the annex so any number can be
traced. Five lines in chat with the headline number and the top pick; the analysis lives in the file.
