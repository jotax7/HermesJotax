# Running Hermes for someone else

Use when the goal is not *my* agent but *their* agent: handing an instance to a family member, a
non-technical colleague, or a small client who should never see a terminal.

## Decide first: managed or self-hosted

| | Managed plan (subscription with hosted agent) | Self-hosted VPS you administer |
|---|---|---|
| Who holds the model key | The vendor | You |
| Who runs updates | The vendor | A cron |
| Who they call when it breaks | Support | **You** |
| Cost shape | Flat per person | Cheap per box, plus model spend, plus your time |
| Best for | 1-5 people who must simply work | You are reselling, or data must stay in your infra |

For friends and family the managed path wins even at several times the VPS price: the two things that
actually break a non-technical user's assistant are **the model credential** and **the update**, and the
managed plan removes both. A VPS only wins when you are running it as a service for several people (one
box, one profile per person) or when the data cannot leave your infrastructure.

**Say the support cost out loud.** The moment you hand over a self-hosted instance you become its
administrator. If that time is not priced or bounded, it is the most expensive part of the gift.

## Self-hosting: the parts that are not obvious

1. **Size the box to the feature set, not to the install.** The agent itself idles in 1-2 GB; the browser
   toolset (Chromium/Playwright) is the memory hog, and a remote desktop is worse. Practical floor for a
   browser-enabled instance is **2 vCPU / 8 GB**. A 1 vCPU / 4 GB box works only with the browser disabled.
2. **The dashboard does not run on a server install by default.** A gateway that answers on Telegram is
   not a web UI. Start it explicitly: `hermes dashboard --port 9119 --host 127.0.0.1 --skip-build`
   (`--skip-build` when pnpm is unavailable on the box; `hermes dashboard --status` lists what is running,
   `--stop` kills it). Default bind is loopback on 9119.
3. **A public bind always needs an auth provider.** Since the June 2026 hardening `--insecure` is a no-op:
   binding a non-loopback address requires a password or OAuth, otherwise the server refuses. For a quick
   look from a phone, a tunnel in front of the loopback bind is less risky than opening a port — and say
   out loud that the host is exposed while the tunnel is up.
4. **Two ways to survive a reboot, pick one.** `hermes gateway install` (systemd/launchd user service) for
   a native install, or the official image with `--restart unless-stopped` for Docker. Without this the
   assistant dies at the first reboot and the recipient reports it as "se rompió".
5. **Back up `~/.hermes`.** Sessions, memory, skills and config all live there; a nightly archive plus the
   provider's own weekly snapshot is enough to rebuild in minutes.
6. **Schedule the update, with a snapshot before it.** `hermes update` on a cron, snapshot first, restart
   the gateway after. An instance left a year behind loses the models and the tool fixes it depends on.

## Handover checklist

- Non-root user owns the agent; root stays for the OS only.
- SSH by key only, password auth off, firewall on.
- **Terminal/shell toolset disabled.** A personal assistant has no use for a shell, and a shell in untrained
  hands is an accident. Web search, files, calendar, reminders and voice are the useful set.
- A hard **spend cap on the model provider** so their enthusiasm does not arrive as an invoice on your card.
- One page, in their language: which app to open (usually Telegram), what the bot is called, and three
  things to try. No URLs to admin panels, no tokens.
- Their own memory primed once: who the family is, fixed commitments, recurring errands. That is what makes
  it feel like an assistant rather than a chatbot.

## Pitfalls

- **Do not give the recipient an admin surface you have not secured.** A dashboard on a public IP with basic
  auth and a weak password is the whole box.
- **A remote desktop is not "more assistant".** For someone who only talks to it, a chat channel on a phone
  beats any desktop; RDP earns its RAM only when the assistant must drive a machine or show a browser.
  Vendor Linux desktop images are also a vCPU/RAM tier above the plain OS one — check the floor before
  selling someone a plan that cannot run the template.
- **Do not hand over a credential you share with your own account.** If their usage can drain your key, a
  cap or a separate key is part of the install, not a nice-to-have.
- **Test with their words, not yours.** Three real requests in their language (a reminder, a mail, a search)
  before you call it delivered; a demo that works on your prompts fails on a parent's.
- **Prices and template floors move.** Confirm the current plan limits and template requirements on the
  provider's own page at the moment of buying instead of quoting last quarter's numbers.
