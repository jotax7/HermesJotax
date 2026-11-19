# Harvesting from a logged-in SaaS over CDP

Recipes for the "read the app's own JSON API instead of clicking" path. The generic pattern, the
pagination and locked-field rules are in SKILL.md; this file holds endpoint-level detail and the
post-processing that turns a raw dump into something deliverable.

## Apollo.io

Logged in at `https://app.apollo.io`. Every call below is a `fetch` from the page context, so the
session cookie applies and no API key is needed.

**People search** — `POST /api/v1/mixed_people/search`

```json
{
  "page": 1,
  "per_page": 25,
  "person_titles": ["Gerente Comercial", "Gerente General", "Leasing Manager"],
  "person_locations": ["Chile", "Colombia"],
  "q_organization_keyword_tags": ["shopping center", "centro comercial", "mall"]
}
```

- `per_page` ceiling is **25**; 100 returns `422 {"error":"Per Page Limit Crossed."}`.
- **A query stops yielding around 2,500 records (100 pages × 25).** When `total_entries` is larger,
  pages past that ceiling come back empty, so a loop keyed on `page * per_page >= total` spends a
  hundred calls and gains nothing. Split the query — by country, by vertical, by title cluster —
  instead of paginating deeper, and say in the deliverable when the universe is bigger than the cap
  and the harvest is partial.
- Response: `pagination.total_entries`, `pagination.total_pages`, and `people[]` where each record
  carries `id`, `name`, `title`, `city`, `state`, `country`, `linkedin_url`, `email_status`,
  `email`, and a nested `organization` (`name`, `estimated_num_employees`, `industry`).
- `email` comes back as `email_not_unlocked@domain.com` for every record until revealed; the real
  unlock costs credits per contact. `email_status` (`verified` / `extrapolated` / `unavailable`) is
  free and is a good quality proxy before spending anything.
- `q_organization_keyword_tags` behaves as OR, so a keyword list returns the union — dedupe by `id`.
- Title filters are substring-ish and match the site's own titles, so include both Spanish and
  English variants (`Gerente Comercial` / `Commercial Director`) rather than assuming one.

Check the remaining credit balance on `/#/home` ("2.9K credits") before proposing any reveal.

**Company search** — `POST /api/v1/mixed_companies/search`

```json
{
  "page": 1,
  "per_page": 25,
  "q_organization_keyword_tags": ["logistics", "freight"],
  "organization_locations": ["Argentina"],
  "organization_num_employees_ranges": ["51,100", "101,200"]
}
```

- Same 25/page ceiling. Response: `pagination.total_entries` plus `organizations[]` (fall back to
  `accounts[]`) carrying `id`, `name`, `linkedin_url`, `website_url`, `estimated_num_employees`,
  `organization_headcount_six_month_growth` / `_twelve_month_growth` / `_twenty_four_month_growth`,
  `num_retail_locations`, `organization_revenue`, `has_intent_signal_account`, `intent_strength`,
  `founded_year`, `naics_codes`.
- `/api/v1/organizations/search` also answers 200 but returns the leaner shape; the mixed endpoint is
  the one that carries the growth fields.
- `estimated_num_employees` and `organization_revenue` are frequently null or `0` outside the
  vendor's core markets, so revenue-per-employee tables built on them are fiction. Check one page
  before designing around a field.

**Filters worth knowing**

- `person_seniorities`: `owner | founder | c_suite | vp | head | director | manager | senior | entry |
  intern`. One call per level gives a distribution — the fastest way to tell whether a function has an
  internal owner or is a pure cost line.
- `person_titles` **plus** `q_organization_keyword_tags` in the same people body is a vertical × role
  cross-tab, which is where the interesting numbers live.
- Counting is free: send `per_page: 1` and read `total_entries`. A few hundred of these cost no credits.

**Parse on the Python side.** A `.then(j => j.some?.chain)` that throws comes back as `null` through
`Runtime.evaluate` and reads as "no results". Return `r.text()` from the promise and `json.loads`
client-side: the query that "returned nothing" is usually fine.

## From raw rows to a list he can act on

1. Load the JSONL, dedupe by `id` with `dict.setdefault`, keep insertion order.
2. Score each record: map the title to a decision-role weight (general manager and commercial /
   leasing / expansion outrank operations, marketing, "jefe", "manager"), then add the email-status
   bonus (`verified` > `extrapolated` > `unavailable`). Sort by that score, then by country.
3. Write two CSVs: the full deduped list, and a top-N of the highest-scored contacts — the second is
   what gets read, the first is what gets queried later.
4. Report the count **by country** next to the total. Coverage is wildly uneven in emerging markets
   (Apollo held ~100 records for Argentina against ~900 for Mexico), and that gap is itself a finding:
   it tells the user which market needs another source instead of a bigger filter.
5. Never ship a list whose emails are placeholders. Strip them, say they are locked, and state the
   credit cost of unlocking the subset you recommend.

## Other apps

- **LinkedIn / Sales Navigator**: do not scrape it in a loop; the account is the user's livelihood.
  Use the search UI, or a first-party export when the tenant has one.
- **Google Workspace admin / Cloud Console**: the internal endpoints are auth-scoped and change
  often; prefer the documented API with the OAuth token the user already granted (see the
  `google-workspace` skill) over replaying UI calls.
- Any app: when a POST needs a nonce, CSRF header or `x-` header, read it off the page first
  (`document.cookie`, a hidden meta tag, or the same request the UI just made) instead of guessing.
