#!/usr/bin/env bash
# One-time (and re-runnable) install of the rebooted bot.
#
#   bash scripts/install.sh
#
# What it does:
#   1. Switches off the old posting job (com.robking.dorian-gray-bsky).
#   2. The first time: moves the old ~/.dorian_gray_bot aside to an archive folder.
#   3. Copies this code to ~/.dorian_gray_bot (keeps data/ and review/ on re-runs).
#   4. Creates a virtual environment and installs requirements.
#   5. Links the review folder onto your Desktop as "Dorian Gray review".
#   6. Schedules the daily review run (com.robking.dorian-gray-review). It never posts.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.dorian_gray_bot"
OLD_LABEL="com.robking.dorian-gray-bsky"
NEW_LABEL="com.robking.dorian-gray-review"
AGENTS="$HOME/Library/LaunchAgents"
UID_NUM="$(id -u)"

echo "== Switching off the old posting job"
launchctl bootout "gui/$UID_NUM/$OLD_LABEL" 2>/dev/null || true
launchctl bootout "gui/$UID_NUM/$NEW_LABEL" 2>/dev/null || true

if [ -d "$DEST" ] && [ ! -f "$DEST/.reboot" ]; then
  ARCHIVE="$HOME/.dorian_gray_bot_archive_$(date +%Y%m%d-%H%M%S)"
  echo "== Archiving the old bot folder to $ARCHIVE"
  mv "$DEST" "$ARCHIVE"
  if [ -f "$AGENTS/$OLD_LABEL.plist" ]; then
    mv "$AGENTS/$OLD_LABEL.plist" "$ARCHIVE/$OLD_LABEL.plist"
  fi
fi

echo "== Copying code to $DEST"
mkdir -p "$DEST"
rsync -a --delete \
  --exclude ".git" --exclude ".venv" --exclude "data" --exclude "review" \
  --exclude ".pytest_cache" --exclude "__pycache__" --exclude ".DS_Store" --exclude ".env" \
  "$REPO/" "$DEST/"
touch "$DEST/.reboot"

mkdir -p "$DEST/data/inputs" "$DEST/data/logs" "$DEST/review"
if [ ! -f "$DEST/data/inputs/base_portrait.jpg" ]; then
  cp "$REPO/data/inputs/base_portrait.jpg" "$DEST/data/inputs/base_portrait.jpg"
fi

if [ ! -f "$DEST/.env" ]; then
  LATEST_ARCHIVE="$(ls -d "$HOME"/.dorian_gray_bot_archive_* 2>/dev/null | tail -1 || true)"
  if [ -n "$LATEST_ARCHIVE" ] && [ -f "$LATEST_ARCHIVE/.env" ]; then
    cp "$LATEST_ARCHIVE/.env" "$DEST/.env"
  elif [ -f "$REPO/.env" ]; then
    cp "$REPO/.env" "$DEST/.env"
  else
    cp "$REPO/.env.example" "$DEST/.env"
    echo "!! Fill in OPENAI_API_KEY in $DEST/.env"
  fi
  chmod 600 "$DEST/.env"
fi

echo "== Python environment"
if [ ! -x "$DEST/.venv/bin/python" ]; then
  python3 -m venv "$DEST/.venv"
fi
"$DEST/.venv/bin/pip" install -q --upgrade pip
"$DEST/.venv/bin/pip" install -q -r "$DEST/requirements.txt"

echo "== Desktop link"
ln -sfn "$DEST/review" "$HOME/Desktop/Dorian Gray review"

echo "== Scheduling the daily review run"
mkdir -p "$AGENTS"
sed "s#__DEST__#$DEST#g" "$DEST/launchd/$NEW_LABEL.plist.template" > "$AGENTS/$NEW_LABEL.plist"
launchctl bootstrap "gui/$UID_NUM" "$AGENTS/$NEW_LABEL.plist"

echo
echo "Done. Each morning after 08:30 a new frame appears in 'Dorian Gray review' on your Desktop."
echo "Nothing is posted. To make Day 1 right now:"
echo "  cd $DEST && .venv/bin/python -m dorian_bot.bot"
