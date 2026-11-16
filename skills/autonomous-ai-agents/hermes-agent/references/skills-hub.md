# Skills Hub — browsing and installing third-party skills

When the user asks for a "marketplace of skills", "what skills can I add", or
"install something cool", the answer is the built-in hub — not a website.

## Commands

```bash
hermes skills browse                 # paginated index across every source
hermes skills search "<topic>"       # 25 hits per query, all sources
hermes skills inspect <identifier>   # full SKILL.md before it touches disk
hermes skills install <identifier>
hermes skills list / check / update / audit / uninstall
hermes skills tap                    # manage skill sources
hermes skills publish                # publish a local skill
```

The hub indexes `skills.sh`, ClawHub, GitHub repos, Nous's own optional skills,
and any well-known agent-skill endpoint — six figures of skills, so search by
topic and quote identifiers rather than dumping the browse index into chat.
Widen the terminal table before reading it (`export COLUMNS=200`); the default
width wraps every row into unreadable confetti.

## Trust tiers mean something

| Tier | Meaning |
|---|---|
| ★ `official` | Nous Research's own optional skills (a few hundred). Safe default. |
| `trusted` | Vendor-published repos (e.g. Airtable's sales-ops / marketing-ops). Read the description, then fine. |
| `community` | Everything else — third-party authors. |

**A skill is executable instruction, not a bookmark.** Installing one means its
steps and bundled scripts run with whatever tools the session has, including
mail, Drive and shell access. So:

- Recommend official and trusted sources by default.
- For community skills, run `hermes skills inspect` first and read what it
touches; mention `hermes skills audit` as the post-install scan.
- Say this plainly to the user once — "una skill es ejecución, no un bookmark" —
instead of silently installing whatever scored best in search.
- Prefer writing a local skill for anything one-of-a-kind; the hub is for
  capabilities someone else already maintains.

## Recommending a set

Search the user's actual domains before proposing anything (sales, crm,
prospecting, hubspot, linkedin, instagram, whatsapp, seo), then read back a
short shortlist with identifier + trust tier + one line of what it does. Pair it
with what the user already has connected — a HubSpot skill is useless to someone
living in Gmail and Sheets, while `sales-ops` on Airtable or a Google-Workspace
persona skill works immediately.

The format is compatible with the open Agent Skills standard
(`agentskills.io`), so `anthropics/skills` and other public SKILL.md repos can be
added as a source with `hermes skills tap`.
