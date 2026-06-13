#!/bin/bash
# Auto-update Hermes Agent — runs via cron
# Exits silently if no update; reports if one was applied.

set -e
export PATH="/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME=/root

# Check whether an update is actually available first
VERSION_OUT=$(hermes --version 2>&1 || true)
if ! echo "$VERSION_OUT" | grep -q "Update available"; then
    # Already up to date — cron stays silent on no-op
    exit 0
fi

echo "Hermes update available — starting auto-install..."
echo "$VERSION_OUT"
echo "---"

# Run update non-interactively, skip backup to avoid daily snapshot bloat
hermes update --yes --no-backup

echo "---"
echo "Hermes auto-update finished."
