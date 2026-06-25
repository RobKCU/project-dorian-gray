#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

hour="$(date +%H)"
minute="$(date +%M)"
minutes_since_midnight=$((10#$hour * 60 + 10#$minute))
first_run_minutes=$((8 * 60 + 30))

if [ "$minutes_since_midnight" -lt "$first_run_minutes" ]; then
  echo "Before 08:30 local time; skipping catch-up check."
  exit 0
fi

lock_dir="data/outputs/.daily_run.lock"
if ! mkdir "$lock_dir" 2>/dev/null; then
  echo "Daily run already in progress; exiting."
  exit 0
fi
trap 'rmdir "$lock_dir"' EXIT

.venv/bin/python -m dorian_bot.bot --copy-history --post
