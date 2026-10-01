"""Dry simulation: replay real history days through the selection logic.

No images, no API calls, nothing written. Shows which edits and captions the
bot would choose day after day, to check for variety and plateaus.

    python scripts/simulate.py 2026-05-01 2026-06-15
"""

import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dorian_bot.analysis import analyse_day  # noqa: E402
from dorian_bot.caption import choose_caption  # noqa: E402
from dorian_bot.history import read_entries_for_day  # noqa: E402
from dorian_bot.selection import choose_moves, update_weather  # noqa: E402
from dorian_bot.state import new_state  # noqa: E402


def main(start: str, end: str) -> None:
    state = new_state()
    d, last = date.fromisoformat(start), date.fromisoformat(end)
    n = 1
    channels, moves_used, words = Counter(), Counter(), []
    while d <= last:
        entries = read_entries_for_day(d)
        if entries:
            n += 1
            _, mods, scores = analyse_day(entries)
            moves = choose_moves(scores, mods, state["weather"], state["channel_last"], state["move_last"], n, f"{n}-{d}")
            word, caption = choose_caption(moves[0]["source"] if moves else None, state["caption_words"], f"{n}-{d}")
            state["weather"] = update_weather(state["weather"], scores)
            for m in moves:
                state["channel_last"][m["channel"]] = n
                state["move_last"][m["id"]] = n
                channels[m["channel"]] += 1
                moves_used[m["id"]] += 1
            state["caption_words"].append(word)
            words.append(word)
            top = ", ".join(f"{k} {v:.2f}" for k, v in sorted(scores.items(), key=lambda kv: -kv[1])[:3])
            print(f"Day {n:3d} {d}  [{top}]  {caption}")
            for m in moves:
                print(f"           {m['channel']:<20} {m['source']:<26} {m['strength']:.2f}  {m['id']}")
        d += timedelta(days=1)
    print("\nChannels used:", dict(channels.most_common()))
    print("Distinct moves:", len(moves_used), "  most used:", moves_used.most_common(6))
    print("Distinct caption words:", len(set(words)), "of", len(words))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
