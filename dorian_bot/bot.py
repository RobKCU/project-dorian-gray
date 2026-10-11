"""The JPEG of Dorian Gray: daily runner.

    python -m dorian_bot.bot                 absorb any finished days, make the next frame
    python -m dorian_bot.bot --copy-history  ...after refreshing the copy of Chrome history
    python -m dorian_bot.bot --dry-run       show what would happen; no image, nothing saved
    python -m dorian_bot.bot --mock-image    use a free stand-in for the OpenAI edit (testing)
    python -m dorian_bot.bot --status        print where things stand
    python -m dorian_bot.bot --post          make the next frame, then post anything unposted
    python -m dorian_bot.bot --post-latest   only post unposted frames; make nothing new

The scheduled job runs with --post. Without it, nothing is published.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List
import argparse
import json

from .analysis import analyse_day, average
from .caption import FIRST_CAPTION, choose_caption
from .config import BASE_DIR, BASE_PORTRAIT_PATH, CHAIN_DIR, LOG_FILE, MAX_CATCHUP_DAYS, RECORDS_DIR, REVIEW_DIR
from .env import load_env
from .history import copy_chrome_history, read_entries_for_day
from .image_generation import first_frame, mock_edit, openai_edit, prepare_for_bluesky, resave, to_chain_jpeg
from .prompt import build_prompt, quiet_note
from .report import publish_frame, write_index
from .selection import choose_moves, salience, update_weather
from .state import load_state, save_state


def log(message: str) -> None:
    stamp = datetime.now().isoformat(timespec="seconds")
    print(message)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a") as fh:
        fh.write(f"{stamp}  {message}\n")


def frame_path(day: int) -> "Path":
    return CHAIN_DIR / f"day_{day:04d}.jpg"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="The JPEG of Dorian Gray")
    p.add_argument("--through", help="Absorb days up to and including YYYY-MM-DD (default: yesterday).")
    p.add_argument("--copy-history", action="store_true", help="Refresh the local copy of Chrome history first.")
    p.add_argument("--dry-run", action="store_true", help="Show the planned edit without generating or saving anything.")
    p.add_argument("--mock-image", action="store_true", help="Use a free local stand-in instead of OpenAI.")
    p.add_argument("--status", action="store_true", help="Print current state and exit.")
    p.add_argument("--post", action="store_true", help="After making the frame, post any unposted frames to Bluesky.")
    p.add_argument("--post-latest", action="store_true", help="Only post unposted frames; make nothing new.")
    return p.parse_args()


def make_first_frame(state: Dict, through: date, dry: bool) -> int:
    if not BASE_PORTRAIT_PATH.exists():
        log(f"Base portrait missing: {BASE_PORTRAIT_PATH}")
        return 1
    if dry:
        print(f"[dry run] Day 1 would be the base photo. Caption: {FIRST_CAPTION}")
        return 0
    path = first_frame(BASE_PORTRAIT_PATH, frame_path(1))
    frame = {"day": 1, "dates": [through.isoformat()], "caption": FIRST_CAPTION, "word": None,
             "moves": [], "note": "the base photograph, unaltered", "image": str(path),
             "posted": False, "post_uri": None, "created_at": datetime.now().isoformat(timespec="seconds")}
    state.update(day=1, last_date=through.isoformat())
    state["frames"].append(frame)
    publish_frame(frame, path)
    write_index(state)
    save_state(state)
    log(f"Day 1 created from the base photo. {FIRST_CAPTION}")
    return 0


def absorb(state: Dict, through: date, dry: bool, mock: bool) -> int:
    last = date.fromisoformat(state["last_date"])
    start = last + timedelta(days=1)
    if start > through:
        print(f"Up to date: last absorbed {state['last_date']}.")
        return 0
    if (through - start).days + 1 > MAX_CATCHUP_DAYS:
        start = through - timedelta(days=MAX_CATCHUP_DAYS - 1)
    dates = [start + timedelta(days=i) for i in range((through - start).days + 1)]

    per_day_scores, per_day_mods, counts_total, entries_total = [], [], {}, 0
    for d in dates:
        entries = read_entries_for_day(d)
        if not entries:
            continue
        counts, mods, scores = analyse_day(entries)
        per_day_scores.append(scores)
        per_day_mods.append(mods)
        entries_total += len(entries)
        for k, v in counts.items():
            counts_total[k] = counts_total.get(k, 0) + v

    n = state["day"] + 1
    seed = f"{n}-{through.isoformat()}"
    scores = average(per_day_scores)
    mods = average(per_day_mods)

    if scores and not any(state["weather"].values()):
        # first edit: there is no "recent weather" yet, so start it at today's level
        state["weather"] = dict(scores)
    if scores:
        moves = choose_moves(scores, mods, state["weather"], state["channel_last"], state["move_last"], n, seed)
    else:
        moves = []
    lead = moves[0]["source"] if moves else None
    word, caption = choose_caption(lead, state["caption_words"], seed, days_span=len(dates))
    prompt = build_prompt(n, moves) if moves else quiet_note(n)

    span = dates[0].isoformat() if len(dates) == 1 else f"{dates[0]} to {dates[-1]}"
    print(f"Day {n} ({span}): {entries_total} browsing entries")
    for m in moves:
        print(f"  [{m['channel']}] ({m['source']}, {m['strength']}) {m['text']}")
    print(f"  {caption}")

    if dry:
        print("\n[dry run] prompt:\n" + prompt)
        return 0

    prev = frame_path(state["day"])
    if not prev.exists():
        log(f"Previous frame missing: {prev}")
        return 1
    out = frame_path(n)
    if not moves:
        resave(prev, out)
    else:
        raw = CHAIN_DIR / f"day_{n:04d}_raw.png"
        if mock:
            mock_edit(prev, moves, raw)
        else:
            openai_edit(prev, prompt, raw)
        to_chain_jpeg(raw, out)

    record = {
        "day": n, "dates": [d.isoformat() for d in dates], "entries": entries_total,
        "category_counts": counts_total, "pole_scores": scores, "modifiers": mods,
        "weather_before": state["weather"], "salience": salience(scores, state["weather"]) if scores else {},
        "moves": moves, "prompt": prompt, "caption": caption, "mock": mock,
    }
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    (RECORDS_DIR / f"day_{n:04d}.json").write_text(json.dumps(record, indent=2))

    if scores:
        state["weather"] = update_weather(state["weather"], scores)
    for m in moves:
        state["channel_last"][m["channel"]] = n
        state["move_last"][m["id"]] = n
    state["caption_words"] = (state["caption_words"] + [word])[-50:]
    frame = {"day": n, "dates": record["dates"], "caption": caption, "word": word,
             "moves": [{k: m[k] for k in ("id", "channel", "source", "strength", "text")} for m in moves],
             "note": None if moves else "no browsing recorded; re-saved only",
             "image": str(out), "mock": mock, "posted": False, "post_uri": None,
             "created_at": datetime.now().isoformat(timespec="seconds")}
    state["frames"].append(frame)
    state["day"] = n
    state["last_date"] = through.isoformat()
    publish_frame(frame, out)
    write_index(state)
    save_state(state)
    log(f"Day {n} made ({span}{', mock image' if mock else ''}). {caption}")
    return 0


MAX_POSTS_PER_RUN = 3


def post_pending(state: Dict) -> int:
    """Post every unposted frame, oldest first. A failed post is retried on the next run."""
    from .bluesky import BlueskyClient

    pending = [f for f in state["frames"] if not f.get("posted") and not f.get("mock")]
    if not pending:
        print("Nothing waiting to be posted.")
        return 0
    pending = pending[:MAX_POSTS_PER_RUN]
    try:
        client = BlueskyClient()
        client.login()
        for frame in pending:
            prepared, width, height, mime = prepare_for_bluesky(
                frame_path(frame["day"]), REVIEW_DIR / "_bluesky_upload.jpg"
            )
            result = client.create_image_post(
                text=frame["caption"], image_path=prepared,
                alt_text=f"Day {frame['day']} of a portrait that re-processes itself once a day.",
                width=width, height=height, mime_type=mime,
            )
            frame.update(posted=True, post_uri=result.get("uri"),
                         posted_at=datetime.now().isoformat(timespec="seconds"))
            save_state(state)
            log(f"Posted day {frame['day']} to Bluesky: {result.get('uri')}")
    except Exception as exc:
        log(f"Posting failed (will retry next run): {exc}")
        write_index(state)
        return 1
    write_index(state)
    return 0


def print_status(state: Dict) -> None:
    print(f"Frames: {state['day']}   last absorbed date: {state['last_date']}")
    print(f"Review folder: {REVIEW_DIR}")
    if state["frames"]:
        f = state["frames"][-1]
        print(f"Latest: day {f['day']} — {f['caption']}  ({'posted' if f.get('posted') else 'not posted'})")
    top = sorted(state["weather"].items(), key=lambda kv: -kv[1])[:4]
    print("Weather (recent): " + ", ".join(f"{k} {v:.2f}" for k, v in top))


def main() -> int:
    load_env(BASE_DIR / ".env")
    args = parse_args()
    state = load_state()

    if args.status:
        print_status(state)
        return 0
    if args.post_latest:
        return post_pending(state)

    through = date.fromisoformat(args.through) if args.through else date.today() - timedelta(days=1)
    if args.copy_history and not args.dry_run:
        if not copy_chrome_history():
            log("Could not copy Chrome history.")
            return 1
    elif args.copy_history:
        copy_chrome_history()

    if state["day"] == 0:
        rc = make_first_frame(state, through, args.dry_run)
    else:
        try:
            rc = absorb(state, through, args.dry_run, args.mock_image)
        except Exception as exc:  # keep state untouched on failure; the next scheduled run retries
            log(f"Run failed, state unchanged: {exc}")
            rc = 1
    if args.post and not args.dry_run:
        # post even if today's frame failed, so an earlier unposted frame still goes out
        rc = max(rc, post_pending(state))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
