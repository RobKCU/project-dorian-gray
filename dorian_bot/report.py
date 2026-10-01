"""The review folder: each day's image plus a local index.html to look through.

Nothing here is posted. Open review/index.html in a browser to see the run.
"""

from html import escape
from pathlib import Path
from typing import Dict
import shutil

from .config import REVIEW_DIR

CSS = """
:root { --bg:#f4f1ea; --ink:#1d1b18; --muted:#6d675e; --rule:#d8d2c6; --card:#fffdf8; }
@media (prefers-color-scheme: dark) { :root { --bg:#141311; --ink:#ebe6dc; --muted:#9a9388; --rule:#2c2a26; --card:#1c1b18; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 Georgia, 'Times New Roman', serif; }
header { padding:32px 20px 8px; max-width:1200px; margin:auto; }
h1 { font-weight:normal; font-size:28px; margin:0 0 4px; letter-spacing:.01em; }
header p { color:var(--muted); margin:0; font-family: ui-monospace, Menlo, monospace; font-size:12px; }
main { display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:20px; padding:20px; max-width:1200px; margin:auto; }
article { background:var(--card); border:1px solid var(--rule); }
article img { width:100%; display:block; aspect-ratio:2/3; object-fit:cover; background:#000; }
.meta { padding:10px 12px 14px; }
.day { font-family: ui-monospace, Menlo, monospace; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; }
.cap { font-style:italic; margin:4px 0 8px; }
ul { margin:0; padding-left:16px; font-size:12.5px; color:var(--muted); }
.posted { font-family: ui-monospace, Menlo, monospace; font-size:11px; color:var(--muted); margin-top:8px; }
"""


def publish_frame(frame: Dict, image_path: Path) -> Path:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    dest = REVIEW_DIR / f"day_{frame['day']:04d}.jpg"
    shutil.copy2(image_path, dest)
    shutil.copy2(image_path, REVIEW_DIR / "latest.jpg")
    return dest


def write_index(state: Dict) -> Path:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    cards = []
    for frame in reversed(state.get("frames", [])):
        moves = "".join(
            f"<li>{escape(m['source'].replace('_', ' '))}: {escape(m['text'])}</li>" for m in frame.get("moves", [])
        ) or f"<li>{escape(frame.get('note', 'no edit'))}</li>"
        dates = frame["dates"][0] if len(frame["dates"]) == 1 else f"{frame['dates'][0]} – {frame['dates'][-1]}"
        posted = "posted" if frame.get("posted") else "not posted"
        cards.append(
            f"<article><img src=\"day_{frame['day']:04d}.jpg\" alt=\"Day {frame['day']}\" loading=\"lazy\">"
            f"<div class=\"meta\"><div class=\"day\">Day {frame['day']} · {escape(dates)}</div>"
            f"<div class=\"cap\">{escape(frame['caption'])}</div><ul>{moves}</ul>"
            f"<div class=\"posted\">{posted}</div></div></article>"
        )
    html = (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>Dorian Gray Review</title><style>{CSS}</style></head><body>"
        "<header><h1>The JPEG of Dorian Gray</h1>"
        f"<p>local review · {len(state.get('frames', []))} frames · newest first · nothing here is public</p></header>"
        f"<main>{''.join(cards)}</main></body></html>"
    )
    path = REVIEW_DIR / "index.html"
    path.write_text(html)
    return path
