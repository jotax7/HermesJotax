#!/bin/bash
# Unattended daily apt maintenance, safe under cron (no TTY).
# Usage: apt-daily-upgrade.sh [--dry-run]
# Install: sudo install -m 755 -o root -g root apt-daily-upgrade.sh /usr/local/bin/
# Register: 0 23 * * * sudo /usr/local/bin/apt-daily-upgrade.sh

set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

LOG="/var/log/apt-daily-upgrade.log"
DRY=""
[ "${1:-}" = "--dry-run" ] && DRY="-s"

exec >>"$LOG" 2>&1

echo "===== $(date -Is) start (dry-run='${DRY}') ====="

# && semantics: upgrade only if the index refresh succeeded.
if ! /usr/bin/apt-get update; then
    echo "===== $(date -Is) END: apt-get update FAILED ====="
    exit 1
fi

/usr/bin/apt-get -y $DRY \
    -o Dpkg::Options::=--force-confdef \
    -o Dpkg::Options::=--force-confold \
    upgrade
rc=$?

echo "===== $(date -Is) END: apt-get upgrade rc=$rc ====="
exit "$rc"
