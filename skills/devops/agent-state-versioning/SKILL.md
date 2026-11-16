---
name: agent-state-versioning
description: "Version agent memory, skills and notes into a git repo."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [git, backup, state, cron, skills, memory]
    related_skills: [linux-cron-jobs]
    category: devops
---

# Versioning the agent's own state

## When to Use

- The user asks for their agent's memory/skills/notes to be backed up, versioned, or pushed to a repo.
- They say "commiteá", "pusheá", "guardá todo" as a recurring request.
- Setting up a periodic snapshot so a dead machine does not take the agent's knowledge with it.

## What gets versioned

Markdown and scripts only — memory files, the skills tree, work notes, config. **Never** OAuth
tokens, client secrets, API keys or anything under a credentials store. Exclude caches: the skills
hub index alone can exceed 50 MB and a single oversized blob rejects the whole push on GitHub.

```
repo/
├── memory/       copy of the memory + user profile files
├── skills/       every SKILL.md with its scripts/references
├── <domain>/     work material, one folder per area
├── ideas/  experiments/  logs/
└── AGENTS.md     rules the agent (and its subagents) must follow
```

## Auth: deploy key, never a token in chat

A personal access token pasted into chat lives in the transcript forever and usually carries account-wide
scope. Instead:

1. Generate a **dedicated ed25519 keypair** for this repo; the private half never leaves the machine.
2. Give the user **only the public key** to paste into the repo's *Settings → Deploy keys*, with
   **Allow write access** ticked. Public keys are safe to show in chat.
3. Point the remote at the SSH form of the URL and put the key in the SSH client config with
   `IdentitiesOnly yes`, so plain `git push` works unattended (which the cron needs).
4. Tell the user where to revoke it, and that it only grants access to that one repo.

If the user insists on a token, have *them* feed it to the GitHub CLI themselves; never accept it in chat.

Do not try to complete the interactive web/device auth yourself when the CLI is unauthenticated: the
device flow needs a browser session that is already logged in and then a 2FA code, and 2FA is the
user's to enter. Driving the browser to the code page only parks you in front of a prompt you cannot
answer (and "Continue with Google" gets you exactly as far as the TOTP screen). Go straight to the
deploy-key path above — one paste of a public key and the push is unblocked.

## Getting the first push through

- The empty-looking repo may already contain an `Initial commit` with a README. Do not force-push over
  it: fetch, rename the local branch to the remote's default (`main`), `rebase origin/main`, and resolve
  the README conflict by keeping both (their title + your content).
- `git rebase --continue` fails with "Terminal is dumb, but EDITOR unset" under a non-interactive
  shell — prefix with `GIT_EDITOR=true`.
- Commit identity: pass `-c user.email=… -c user.name=…` per call instead of writing to the user's git
  config.
- **Verify against the remote**, not the push output: `git ls-remote origin` plus `git log --oneline
  origin/main` should show your commits. A push that printed warnings may still have landed.

## Scheduled sync with an interval gate

User crontabs run daily at best; "every 3 days" is not expressible cleanly (`*/3` on day-of-month
skews at month end, and a missed run while the machine sleeps never catches up). Run the script
daily and let it gate itself:

- store the last successful push as an epoch marker file;
- if `(now - last) / 86400 < INTERVAL`, log `skip` and exit 0;
- otherwise refresh the file tree, commit only if `git status --porcelain` is non-empty, push, and
  write the marker.
- Provide `--force` (ignore the interval, for "commiteá ahora") and `--dry-run`.
- Log every run to a file outside the repo, or the log itself becomes a commit every day.
- Keep the crontab line to a single absolute script path and register it idempotently; validate with a
  real `* * * * *` tick, then remove the temporary line.

## Pitfalls

- `rsync --delete` leaves excluded files behind and fails with "cannot delete non-empty directory";
  add `--delete-excluded` when the exclusion is a cache you do want gone from the mirror.
- `cp -r src dest && echo OK;` prints OK even when `cp` failed because the parent directory did not
  exist. `mkdir -p` the category directory first and check the copy result, not the echo.
- Sync scripts that copy the whole skills tree will pull in hub caches and `__pycache__`; exclude them
  in both the script and `.gitignore`.
