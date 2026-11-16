# Messaging Channels — connect, restart, authorize

Wiring a chat platform (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, …) into the
gateway and proving it works. Per-platform credential/feature detail lives in the docs
(`/user-guide/messaging/<platform>`); this file is the part the docs do not say.

## Order of operations

1. **Credentials → the active profile's `.env`**, never `config.yaml`. Write them with a script that
   parses and rewrites the file, then `chmod 600`. Never echo the token back into chat, a command
   line, or a summary.
2. **Authorization and home channel in the same write**: `<PLATFORM>_ALLOWED_USERS=<numeric id>` and
   `<PLATFORM>_HOME_CHANNEL=<chat id>`. The default posture is deny (`gateway.allow_all_users:
   false`), which is what makes a bot with terminal access safe out of the box.
3. **Restart the gateway** (below). Adapters are constructed at startup; nothing hot-reloads a
   platform added after the process booted.
4. **Verify from state file + log**, not from a command's exit code.

## Restarting the gateway from inside an agent turn

`hermes gateway restart|stop`, `systemctl --user restart hermes-gateway`, and
`systemd-run … systemctl restart` are all refused by the terminal guard while the command runs
inside the gateway process. That refusal is fail-closed by design and also scans referenced
scripts — do not try to reword or obfuscate a restart.

The supported path is the one `hermes update` itself uses: `kill -USR1 <gateway pid>`. It maps to
`request_restart(via_service=True)` — refuse new turns, drain in-flight turns (defer `stop()`, cap
1800 s), exit, and the `process_supervisor.sh` child relaunches the process. The current turn is
**not** amputated: the reply is delivered, then the restart happens. `kill -USR1` is not a
lifecycle verb, so it passes the guard; never escalate to SIGTERM, which kills the in-flight
command and the turn with it.

```
pid=$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.hermes/gateway_state.json')))['pid'])")
kill -USR1 "$pid"
```

Confirm acceptance instead of assuming it: `gateway_state.json` shows `restart_requested: true` and
`gateway_state: draining`, and the log prints `SIGUSR1 received … graceful gateway restart` plus
`Restart deferred: waiting on N active work unit(s)`. After the relaunch: new `pid`,
`gateway_state: running`, `platforms.<name>.state: connected`.

## Discovering a Telegram user ID (allowlist without a second account)

Only numeric IDs are honored; `@username` is not an ID for this purpose.

- Poll `getUpdates` yourself **before** the gateway connects with the token. Once the gateway is
  long-polling, your own `getUpdates` returns 409 and updates are consumed by the gateway.
- Long-poll (`timeout=30`) until the user sends `/start`, then read `message.from.id` (for a private
  chat the chat id equals the user id). Write the allowlist, then restart.
- A `/start` sent before any gateway restart is expected — it is what proves the token works and
  yields the id.

## Verifying authorization (test it, do not assert it)

Run the gateway's own decision function against the live `.env` with
`scripts/verify-channel-authz.py`. It calls `GatewayAuthorizationMixin._principal_authorized` with a
real `SessionSource`, so it exercises the same allowlist / pairing / allow-all order the gateway
applies at intake. Assert owner `True` and a stranger `False` for both `dm` and `group`.

Two mechanics make that probe work: the tools python runs with `-I`, so third-party deps live in
the uv cache archives — prepend `$HERMES_HOME/cache/uv/archive-v0/*` to `sys.path` before importing
gateway modules; and the mixin is safe to instantiate with `object.__new__` plus `adapters = {}`
because its methods use `getattr` for bare runners.

What the verdict actually means when answering "only I can talk to the bot":

- `<PLATFORM>_ALLOWED_USERS` is platform-wide: it gates DMs **and** group traffic.
  `TELEGRAM_GROUP_ALLOWED_USERS` is the group-scoped knob (`TELEGRAM_GROUP_ALLOWED_CHATS` gates by
  chat id).
- A configured allowlist **suppresses DM pairing**: unauthorized senders get behavior `ignore` — no
  reply, no pairing code, nothing that reveals the bot exists — and no pairing state is minted for
  them (see `gateway/run_inbound_unauthorized.py`).
- The owner gets one notice per (platform, user) per process in the home channel, plus a WARNING log
  line — that is how a typo'd allowlist gets noticed.
- Cheap corroboration: `hermes pairing list` reports no pairing data, and `state.db` `sessions`
  holds exactly one row per allowed `user_id` for that platform.

## End-to-end proof

The gateway log is the evidence: `inbound message: platform=… user=… msg='…'` followed by
`response ready: … time=… api_calls=…` and `[Telegram] Sending response` means the bot answered for
real. `Sent home-channel startup notification to <platform>:<id>` confirms the home channel wiring.

## Reporting the result

Lead with the outcome and the single next action ("ya funciona: escribime al bot"), then the
evidence, then at most one line of framework mechanics. This user pushed back when a setup reply
led with drain/restart internals instead of "está listo, hacé X". If a token was pasted in plain
chat, say once that `@BotFather /revoke` is the remedy and move on.
