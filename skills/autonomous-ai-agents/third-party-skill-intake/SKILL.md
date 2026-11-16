---
name: third-party-skill-intake
description: "Adopt skills from a marketplace or repo by cherry-picking."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [skills, marketplace, supply-chain, review]
    related_skills: [hermes-agent]
    category: autonomous-ai-agents
---

# Adopting third-party skills

## When to Use

- The user shares a skills repo or marketplace link and says "take what is useful".
- Installing from a registry, a git repo, or another agent's skill pack.

## Procedure

1. **Size it up before reading files.** Repo metadata plus the file tree tells you the shape:
   star count, license, how many skills, and which directories the repo advertises (a `.hermes/`,
   `.claude/`, `.codex/` folder each means an adapter exists for that harness).
2. **Read 3-4 SKILL.md heads, not all of them.** Judge quality by whether the skill states triggers,
   hard rules with a reason, and output shape. A frontmatter with `license: MIT` and explicit
   "Hard Bans" sections is a good signal; a one-paragraph marketing blurb is not.
3. **Filter by the user's actual work, not by repo fame.** In a 47-skill pack, expect 60-70% to be
   irrelevant (framework-specific coding rules, frontend patterns). Pick the ones that map to a real
   task the user has.
4. **Check dependencies before copying.** A skill that calls MCP tools you do not have (Firecrawl,
   Exa) or needs paid API credentials is a trap: it looks installed and fails mid-task. Skip it and
   say why, or copy it only after confirming the credential exists.
5. **Cherry-pick by copy, never run the pack's `install.sh`.** Installers seed rules, commands,
   hooks and config for the *whole* profile, and hooks execute code on every event. Copy
   `<pack>/.agents/skills/<name>/` (or the repo's equivalent) into
   `~/.hermes/skills/<category>/<name>/`, `mkdir -p` the category first.
6. **Verify they load**: `skills_list(category=…)` must show the new descriptions with no frontmatter
   error. Then commit them with the rest of the state.
7. **Report a shortlist with the reason for each pick**, what you deliberately skipped, and the open
   risks (needs credentials, written for another harness, hooks not installed).

## Pitfalls

- Cloning the whole pack to look at it is slow and floods the context: use a sparse/blobless checkout
  limited to the skill directories you are considering.
- Skills written for another harness reference its tool names (`allowed-tools: Read, Write, Bash`).
  The concepts port; the commands do not. Say so instead of promising a turnkey install.
- Copy-paste loops that echo success around a failed `cp` are how a "successfully installed" pack ends
  up half missing — check the destination directory, not the echo.
- Do not install hooks or rules from a third-party pack in the same pass as its skills. Review hook
  code line by line, separately, because it runs on every event.
