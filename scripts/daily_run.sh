#!/usr/bin/env bash
# Run by launchd. Makes the next frame and posts it to Bluesky.
set -euo pipefail

cd "$(dirname "$0")/.."

# Wait until 08:30 local time so "yesterday" is finished browsing.
now=$((10#$(date +%H) * 60 + 10#$(date +%M)))
if [ "$now" -lt $((8 * 60 + 30)) ]; then
  exit 0
fi

mkdir -p data/logs
lock_dir="data/.daily_run.lock"
if ! mkdir "$lock_dir" 2>/dev/null; then
  echo "Run already in progress; exiting."
  exit 0
fi
trap 'rmdir "$lock_dir"' EXIT

.venv/bin/python -m dorian_bot.bot --copy-history --post
