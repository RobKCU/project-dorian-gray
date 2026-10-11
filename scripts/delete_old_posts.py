"""Remove the bot account's posts from before a cutoff date. Run it yourself.

    .venv/bin/python scripts/delete_old_posts.py --before 2026-10-11            # list only
    .venv/bin/python scripts/delete_old_posts.py --before 2026-10-11 --confirm  # actually delete

Deletion on Bluesky is permanent. Without --confirm nothing is changed.
Posts recorded in data/state.json (the current run) are never touched.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dorian_bot.bluesky import BlueskyClient  # noqa: E402
from dorian_bot.config import STATE_FILE  # noqa: E402
from dorian_bot.env import load_env  # noqa: E402


def parse_time(value: str) -> datetime:
    value = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", required=True, help="Delete posts created before this date (YYYY-MM-DD, UTC).")
    ap.add_argument("--confirm", action="store_true", help="Really delete. Without it, only list.")
    args = ap.parse_args()

    load_env(ROOT / ".env")
    cutoff = datetime.fromisoformat(args.before).replace(tzinfo=timezone.utc)
    keep = set()
    if STATE_FILE.exists():
        keep = {f.get("post_uri") for f in json.loads(STATE_FILE.read_text()).get("frames", []) if f.get("post_uri")}

    client = BlueskyClient()
    client.login()

    targets, cursor = [], None
    while True:
        params = {"repo": client.did, "collection": "app.bsky.feed.post", "limit": 100}
        if cursor:
            params["cursor"] = cursor
        r = client.session.get(f"{client.service}/xrpc/com.atproto.repo.listRecords", params=params, timeout=30)
        r.raise_for_status()
        page = r.json()
        for rec in page.get("records", []):
            created = parse_time(rec["value"].get("createdAt", "1970-01-01T00:00:00Z"))
            if created < cutoff and rec["uri"] not in keep:
                targets.append((created, rec["uri"], rec["value"].get("text", "")))
        cursor = page.get("cursor")
        if not cursor or not page.get("records"):
            break

    targets.sort()
    print(f"Account: {client.handle}")
    print(f"Posts created before {args.before}: {len(targets)}")
    if targets:
        print(f"  oldest: {targets[0][0]:%Y-%m-%d}  {targets[0][2]}")
        print(f"  newest: {targets[-1][0]:%Y-%m-%d}  {targets[-1][2]}")
    if not args.confirm:
        print("\nNothing deleted. Re-run with --confirm to delete these posts permanently.")
        return 0

    deleted = 0
    for _, uri, _ in targets:
        rkey = uri.rsplit("/", 1)[-1]
        r = client.session.post(
            f"{client.service}/xrpc/com.atproto.repo.deleteRecord",
            json={"repo": client.did, "collection": "app.bsky.feed.post", "rkey": rkey},
            timeout=30,
        )
        if r.ok:
            deleted += 1
        else:
            print(f"  could not delete {uri}: {r.status_code} {r.text[:120]}")
    print(f"Deleted {deleted} of {len(targets)} posts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
