---
name: scheduled-agent-routines
description: "Recurring agent jobs: morning brief, radars, weekly reviews."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cron, briefing, assistant, automation, proactive]
    category: productivity
    related_skills: [linux-cron-jobs, agent-state-versioning]
---

# Scheduled agent routines

## When to Use

- The user asks for something to happen on its own: a morning brief, a mail/site radar, a weekly
  review, a monitoring digest, "avisame cuando…".
- Turning a one-off analysis the user liked into a recurring one.
- Any recurring task that needs judgment, not just a shell command — for pure shell work use
  `linux-cron-jobs` (OS crontab) or `agent-state-versioning` (interval-gated sync script).

The distinction matters: Hermes jobs run in a **fresh agent session** with tools and a model; an OS cron
line runs a script with a minimal environment. Pick the one that matches the work.

## Procedure

1. **Write the prompt as if the future session knows nothing.** It does not see this conversation, the
   user's last message, or any file you read. Every path, command and rule must be inside the prompt:
   absolute paths to context files, the exact command lines, the output format, and what to do when data
   is missing.
2. **Point the prompt at durable context files first.** A job that opens with "read <repo>/memory/*.md"
   stays correct as the situation changes; one that hard-codes today's facts rots in a week.
3. **Constrain the toolset.** `enabled_toolsets` (e.g. `["terminal", "web"]`) cuts the token overhead of
   every fire and keeps the job from wandering into unrelated tools.
4. **Choose delivery deliberately.** `deliver: "origin"` returns to the chat that created it; `"local"`
   saves silently; a platform:chat_id target posts elsewhere.
5. **Set `attach_to_session: true` for conversational routines** (briefings, digests the user replies to)
   so a follow-up has the brief in context. Leave it off for fire-and-forget alerts.
6. **Create with a natural-language schedule and an explicit timezone** (`"every day at 8:30am"` plus
   `America/Argentina/Buenos_Aires`), not a hand-written cron expression in the wrong zone.
7. **Test-fire it in the same turn** with `action="run"` and read the delivered message. A routine that
   was never fired is an untested routine, and its first real run is at 8:30am when nobody is watching.

## Prompt shape that works

```
Sos <agent>, el agente de <user>. Task: <one line>.
1. Read <absolute paths to context files>.
2. Run: <absolute command 1>   /   <absolute command 2>
3. Cross-check <named open threads / sources>.
Return a message in <language, register>, format:
- <block 1>
- <block 2>
- <top 3 actions, prioritising anything with a deadline or blocked on the user>
If a block has nothing, write 'nada'. Do not invent data: if it is missing, say so. Max N lines.
```

## Pitfalls

- **Jobs cannot ask questions.** If the prompt leaves a decision open, the run guesses or stalls. Write
  the fallback explicitly ("if the mailbox is empty, reply 'nada' and stop").
- **Do not poll after `action="run"`.** It fires in the background and its output re-enters the
  conversation on its own; waiting burns turns.
- **List before update.** Job IDs are opaque; get them from `action="list"`, never from memory of a
  previous turn.
- **Prefer updating an existing job over creating a near-duplicate.** Two briefings at 8:30 is the usual
  outcome of forgetting the first one exists.
- **The model follows the profile's current model** unless pinned. Pinning is the user's call — it locks
  the job to a model across later model changes, which is exactly wrong when they are still tuning.
- **A routine whose value is "more output" gets muted within a week.** Keep the format short and put the
  depth behind a link or file; the user's attention is the scarce resource, not tokens.
- **Timezone drift is silent.** A schedule written without an explicit zone follows the profile's zone and
  fires at the wrong hour after any environment change.
- Cron jobs that touch the filesystem should also land their work in the versioned repo, so the next
  session (and a fresh machine) can see what the routine produced.
