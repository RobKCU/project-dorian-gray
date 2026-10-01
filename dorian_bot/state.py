"""Persistent state (data/state.json)."""

from datetime import datetime
from typing import Dict
import json

from .analysis import POLES
from .config import STATE_FILE


def new_state() -> Dict:
    return {
        "version": 2,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "day": 0,                     # number of the latest frame (1 = base photo)
        "last_date": None,            # last calendar date absorbed (YYYY-MM-DD)
        "weather": {p: 0.0 for p in POLES},
        "channel_last": {},           # channel -> day number last edited
        "move_last": {},              # move id -> day number last used
        "caption_words": [],
        "frames": [],                 # one record per day (see bot.py)
    }


def load_state() -> Dict:
    if not STATE_FILE.exists():
        return new_state()
    state = json.loads(STATE_FILE.read_text())
    fresh = new_state()
    for key, value in fresh.items():
        state.setdefault(key, value)
    return state


def save_state(state: Dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(STATE_FILE)
