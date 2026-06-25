"""CLI runner for the Dorian Gray Bluesky bot."""

from datetime import datetime, timedelta
import argparse
import json
import shutil

from .analysis import (
    AXES,
    caption_for_day,
    classify_entries,
    create_initial_state,
    daily_axis_scores,
    load_state,
    mark_first_posted,
    save_state,
    temporal_features,
    update_state,
)
from .bluesky import BlueskyClient
from .config import BASE_DIR, BASE_PORTRAIT_PATH, DAILY_OUTPUTS_DIR, OUTPUTS_DIR
from .env import load_env
from .history import copy_chrome_history, read_entries_for_day
from .image_generation import generate_portrait, prepare_jpeg_for_bluesky
from .prompt import generate_visual_prompt
from .report import write_today_html


FIRST_POST_CAPTION = "The jpeg absorbs its first day."
FIRST_POST_PROMPT = "The unaltered base portrait before any cumulative browsing-derived transformation."


def _parse_day(day: str | None) -> datetime:
    if day:
        return datetime.strptime(day, "%Y-%m-%d")
    return datetime.now() - timedelta(days=1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and optionally post the daily Dorian Gray portrait.")
    parser.add_argument("--day", help="Day to process as YYYY-MM-DD. Defaults to yesterday.")
    parser.add_argument("--copy-history", action="store_true", help="Refresh the local Chrome history copy first.")
    parser.add_argument("--post", action="store_true", help="Publish the generated portrait to Bluesky.")
    parser.add_argument("--skip-image", action="store_true", help="Analyze and caption only; do not call OpenAI.")
    parser.add_argument("--force", action="store_true", help="Regenerate outputs even if this day already appears in state.")
    parser.add_argument("--repost-first", action="store_true", help="Repost the base image without changing cumulative state.")
    return parser.parse_args()


def write_run_artifacts(
    day_dir,
    date_str: str,
    caption: str,
    prompt: str,
    total_entries: int,
    category_counts: dict,
    domain_counts: dict,
    features: dict,
    daily_axes: dict,
) -> None:
    day_dir.mkdir(parents=True, exist_ok=True)
    (day_dir / "caption.txt").write_text(caption)
    (day_dir / "prompt.txt").write_text(prompt)
    (day_dir / "features.json").write_text(
        json.dumps(
            {
                "date": date_str,
                "total_entries": total_entries,
                "category_counts": category_counts,
                "domain_counts_by_category": domain_counts,
                "temporal_features": features,
                "daily_axes": daily_axes,
                "caption": caption,
            },
            indent=2,
        )
    )


def handle_first_post(args: argparse.Namespace, date_str: str, state: dict | None = None, record_state: bool = True) -> int:
    """Write and optionally post the baseline image before cumulative processing begins."""
    state = state or create_initial_state()
    day_dir = DAILY_OUTPUTS_DIR / "first-post"
    current_image_path = OUTPUTS_DIR / "today.jpg"
    daily_axes = {axis: 0.0 for axis in AXES}
    features = {}
    category_counts = {}
    domain_counts = {}

    write_run_artifacts(
        day_dir=day_dir,
        date_str=date_str,
        caption=FIRST_POST_CAPTION,
        prompt=FIRST_POST_PROMPT,
        total_entries=0,
        category_counts=category_counts,
        domain_counts=domain_counts,
        features=features,
        daily_axes=daily_axes,
    )
    prepared_path, width, height, mime_type = prepare_jpeg_for_bluesky(BASE_PORTRAIT_PATH, current_image_path)
    report_path = write_today_html(
        date_str=date_str,
        caption=FIRST_POST_CAPTION,
        prompt=FIRST_POST_PROMPT,
        state=state,
        daily_axes=daily_axes,
        category_counts=category_counts,
        features=features,
        image_path=prepared_path,
    )

    print(FIRST_POST_CAPTION)
    print(f"Updated latest JPEG: {current_image_path}")
    print(f"Updated local report: {report_path}")

    if args.post:
        client = BlueskyClient()
        client.login()
        result = client.create_image_post(
            text=FIRST_POST_CAPTION,
            image_path=current_image_path,
            alt_text="The unaltered base portrait before the cumulative Dorian Gray bot transformation begins.",
            width=width,
            height=height,
            mime_type=mime_type,
        )
        (day_dir / "bluesky_post.json").write_text(json.dumps(result, indent=2))
        if record_state:
            state = mark_first_posted(state)
            save_state(state)
        print(f"Posted first jpeg to Bluesky: {result.get('uri')}")
    else:
        print("First portrait prepared locally. Pass --post to publish and begin cumulative daily processing.")

    return 0


def main() -> int:
    load_env(BASE_DIR / ".env")
    args = parse_args()
    target_date = _parse_day(args.day)
    date_str = target_date.strftime("%Y-%m-%d")

    state = load_state()
    if args.repost_first:
        return handle_first_post(args, date_str, state=state, record_state=False)

    if not state.get("first_posted_at"):
        if state.get("days_processed"):
            print("No baseline post is recorded; resetting local cumulative state before the first post.")
        return handle_first_post(args, date_str)

    if args.copy_history and not copy_chrome_history():
        return 1

    entries = read_entries_for_day(target_date)
    print(f"{date_str}: found {len(entries)} sanitized browsing entries")
    if not entries:
        print("No entries found; no portrait generated.")
        return 0

    category_counts, domain_counts = classify_entries(entries)
    features = temporal_features(entries)
    daily_axes = daily_axis_scores(category_counts, features)

    already_processed = date_str in state["days_processed"]
    state_changed = False
    if already_processed and not args.force:
        print("This day is already in state; reusing cumulative state. Pass --force to update it again.")
    else:
        state = update_state(state, date_str, daily_axes, features, category_counts)
        state_changed = True

    caption = caption_for_day(daily_axes, features)
    prompt = generate_visual_prompt(state, date_str)

    day_dir = DAILY_OUTPUTS_DIR / date_str
    post_record = day_dir / "bluesky_post.json"
    if already_processed and args.post and post_record.exists() and not args.force:
        print(f"{date_str} already has a Bluesky post record; skipping duplicate post.")
        return 0

    write_run_artifacts(
        day_dir=day_dir,
        date_str=date_str,
        caption=caption,
        prompt=prompt,
        total_entries=len(entries),
        category_counts=category_counts,
        domain_counts=domain_counts,
        features=features,
        daily_axes=daily_axes,
    )

    print(caption)

    current_image_path = OUTPUTS_DIR / "today.jpg"

    if args.skip_image:
        if state_changed:
            save_state(state)
        report_path = write_today_html(
            date_str=date_str,
            caption=caption,
            prompt=prompt,
            state=state,
            daily_axes=daily_axes,
            category_counts=category_counts,
            features=features,
            image_path=current_image_path if current_image_path.exists() else None,
        )
        print(f"Wrote analysis artifacts to {day_dir}")
        print(f"Updated local report: {report_path}")
        return 0

    generated_path = day_dir / "portrait_openai.png"
    post_image_path = day_dir / "portrait_bluesky.jpg"
    generate_portrait(prompt, generated_path)
    prepared_path, width, height, mime_type = prepare_jpeg_for_bluesky(generated_path, post_image_path)
    shutil.copy2(prepared_path, current_image_path)
    report_path = write_today_html(
        date_str=date_str,
        caption=caption,
        prompt=prompt,
        state=state,
        daily_axes=daily_axes,
        category_counts=category_counts,
        features=features,
        image_path=current_image_path,
    )
    print(f"Generated portrait: {generated_path}")
    print(f"Updated latest JPEG: {current_image_path}")
    print(f"Updated local report: {report_path}")

    if args.post:
        client = BlueskyClient()
        client.login()
        result = client.create_image_post(
            text=caption,
            image_path=current_image_path,
            alt_text="A generated painterly portrait transformed by the day's browsing-derived behavioral state.",
            width=width,
            height=height,
            mime_type=mime_type,
        )
        post_record.write_text(json.dumps(result, indent=2))
        if state_changed:
            save_state(state)
        print(f"Posted to Bluesky: {result.get('uri')}")
    else:
        if state_changed:
            save_state(state)
        print("Not posted. Pass --post to publish to Bluesky.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
