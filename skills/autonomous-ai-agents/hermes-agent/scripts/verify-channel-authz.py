#!/usr/bin/env python3
"""Check a messaging platform's allowlist against the gateway's OWN authorization function.

Answers "can only I talk to the bot?" with a real verdict instead of reading config by eye.

Usage:
    python3 verify-channel-authz.py --platform telegram --owner 6002442854
    python3 verify-channel-authz.py --platform telegram --owner 6002442854 --stranger 555000111

Exit code 0 when every probe matches the expected verdict, 1 on mismatch.
Runs against the live .env of $HERMES_HOME (default ~/.hermes).
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

HOME = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
REPO = os.path.join(HOME, "hermes-agent")

# The tools python runs isolated (-I): third-party deps live in the uv cache archives, so put them
# on the path before importing gateway modules.
sys.path[:0] = sorted(glob.glob(os.path.join(HOME, "cache/uv/archive-v0/*"))) + [REPO]

from hermes_cli.env_loader import load_hermes_dotenv  # noqa: E402

try:
    load_hermes_dotenv(hermes_home=HOME)
except TypeError:  # older signature without hermes_home
    load_hermes_dotenv()

from gateway.authz_mixin import GatewayAuthorizationMixin  # noqa: E402
from gateway.config import Platform  # noqa: E402
from gateway.session import SessionSource  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", default="telegram", help="platform value, e.g. telegram, discord")
    ap.add_argument("--owner", required=True, help="allowed user id that must pass")
    ap.add_argument("--stranger", default="555000111", help="unlisted user id that must be denied")
    ap.add_argument("--group-id", default="-1001234567890", help="group chat id used for group probes")
    args = ap.parse_args()

    platform = Platform(args.platform.lower())
    runner = object.__new__(GatewayAuthorizationMixin)  # bare runner: methods use getattr
    runner.adapters = {}
    runner._profile_adapters = {}

    def verdict(user_id: str, chat_type: str, chat_id: str) -> bool:
        src = SessionSource(
            platform=platform, chat_id=chat_id, chat_type=chat_type,
            user_id=user_id, user_name="probe",
        )
        return bool(runner._principal_authorized(src, allow_adapter_delegation=True))

    probes = [
        ("owner dm", args.owner, "dm", args.owner, True),
        ("stranger dm", args.stranger, "dm", args.stranger, False),
        ("owner group", args.owner, "group", args.group_id, True),
        ("stranger group", args.stranger, "group", args.group_id, False),
    ]

    ok = True
    for label, user_id, chat_type, chat_id, expected in probes:
        got = verdict(user_id, chat_type, chat_id)
        ok = ok and got == expected
        print(f"{label:15s} uid={user_id:12s} chat={chat_type:5s} authorized={got!s:5s} expected={expected}")

    print("unauthorized dm behavior:", runner._get_unauthorized_dm_behavior(platform))
    print("VERDICT:", "OK" if ok else "MISMATCH — check the allowlist in .env")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
