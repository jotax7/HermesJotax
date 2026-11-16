---
name: linux-cron-jobs
description: Use when scheduling OS jobs. Cron install, logging, verify.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cron, apt, linux, maintenance, scheduling, raspberry-pi]
    related_skills: [hermes-agent]
---

# Cron jobs for OS maintenance

## When to Use

- The user asks for a recurring shell action on the host ("every day at 23:00 run …"),
  an update/backup/cleanup job, or any periodic command.
- A crontab, `/etc/cron.d` file, systemd timer or existing job needs review or repair.
- Not for Hermes agent tasks (LLM runs, digests, reminders): those use `cronjob_manage`.


Scope: recurring shell work on the host itself — apt upgrades, backups, cleanup, log rotation.

## Procedure

1. Probe preconditions in ONE call before writing anything:

       sudo -n true && echo NOPASSWD || echo needs-password
       crontab -l; ls -l /etc/cron.d
       systemctl is-active cron; systemctl is-enabled cron
       systemctl list-timers --all | grep -Ei 'apt|unattended'

   Passwordless sudo works → user crontab entry may call `sudo <script>`.
   It does not → put the job in `/etc/cron.d/<name>` (root runs it, six-field
   format with the user column) instead of fighting sudo.

2. Fix the command before installing it. The user's literal one-liner is usually
   interactive and will silently do nothing under cron (see Pitfalls). Rewrite it,
   then tell them which parts you changed and why — do not install a dead command
   verbatim because that is what was typed.

3. Install a script, not an inline one-liner. Quoting `&&`, redirects and
   `Dpkg::Options` inside a crontab line is where jobs rot. Put the body in
   `/usr/local/bin/<name>.sh` (root:root 755), keep the crontab line to a single
   absolute path, and give the script a `--dry-run` switch that adds `-s`/`--dry-run`
   to the destructive command.

4. Register idempotently — never `crontab file` wholesale:

       LINEA='0 23 * * * sudo /usr/local/bin/apt-daily-upgrade.sh'
       if ! crontab -l | grep -qF 'apt-daily-upgrade.sh'; then
         ( crontab -l; echo "$LINEA" ) | crontab -
       fi

   Preserve existing lines (the `PATH=` line at the top matters) and re-print
   `crontab -l` afterwards as proof.

5. Verify with a REAL cron tick, not just a manual run. Manual execution proves the
   script, not that cron fires it with its minimal environment:

       ( crontab -l; echo '* * * * * sudo /usr/local/bin/<name>.sh --dry-run' ) | crontab -
       sleep $(( 62 - $(date +%S) ))
       grep inicio /var/log/<name>.log | tail -2      # timestamp must be the tick minute
       crontab -l | grep -v -- '--dry-run' | crontab -

   Remove the temporary line in the same call. Always dry-run first: never validate
   a maintenance job by actually upgrading the machine mid-session.

6. Report what landed (paths, crontab line, log), what the test proved, and any
   open decision (kept-back packages, timers to disable). Reply in the user's
   language (this user: Spanish rioplatense), plain text, short — facts and the
   one question that matters, no narration of the steps.

## Pitfalls

- **Never pipe between apt commands.** `apt-get update | apt-get upgrade` sends
  update's stdout into upgrade's stdin; upgrade reads EOF at the confirmation
  prompt and aborts, so the job "succeeds" having upgraded nothing. Use `&&`.
- **No TTY under cron.** Any confirmation prompt waits forever. Always `-y`,
  `DEBIAN_FRONTEND=noninteractive`, and
  `-o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold` for apt;
  otherwise one modified conffile freezes the job permanently.
- **Cron PATH is minimal.** Set `PATH` inside the script and call binaries by
  absolute path; the user's interactive PATH is not inherited.
- **`apt-get upgrade` keeps back what needs new deps or removals.** On Raspberry Pi
  that includes kernels (`linux-image-rpi-*`, `linux-headers-rpi-*`), `rpi-eeprom`
  and the desktop stack. Run `apt-get -s upgrade` first and report the kept-back
  count; never silently switch to `full-upgrade` — it pulls kernel/desktop and
  usually forces a reboot, so that is the user's call.
- **Check for existing systemd timers first.** `apt-daily.timer` /
  `apt-daily-upgrade.timer` are enabled by default on Debian/Pi even when
  `unattended-upgrades` is not installed, in which case they fail silently. Two apt
  runs racing means lock contention; offer to disable them rather than adding a
  duplicating job blindly.
- **User crontabs have no anacron.** A job missed while the machine is off never
  runs later. Say so for laptops/Pis that sleep.
- **Log to a file** (`/var/log/<name>.log`) with a timestamped header and exit code.
  Cron mail is usually unconfigured, so an unlogged job is unobservable. If the job
  runs as root, `chown` the log to the user so they can read it.
- Do not restart/reload cron after editing a user crontab — edits are picked up
  automatically; `/etc/cron.d` files are too.

## Known-good job

`scripts/apt-daily-upgrade.sh` — tested unattended update+upgrade with dry-run mode,
logging and conffile-safe flags. Copy to `/usr/local/bin/`, `chmod 755`, register per
step 4, validate per step 5.
