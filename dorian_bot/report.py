"""Static local HTML report generation."""

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Dict, Optional

from .config import OUTPUTS_DIR


AXIS_PAIRS = [
    ("directedness", "drift"),
    ("public", "private"),
    ("self", "others"),
    ("vitality", "gloom"),
    ("ai_mediation", "direct_engagement"),
]


def _score(value: float) -> str:
    return f"{value:.3f}"


def _rows_for_categories(category_counts: Dict[str, int]) -> str:
    total = sum(category_counts.values())
    rows = []
    for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0])):
        share = (count / total * 100) if total else 0
        rows.append(
            "<tr>"
            f"<td>{escape(category)}</td>"
            f"<td class=\"num\">{count}</td>"
            f"<td class=\"num\">{share:.1f}%</td>"
            "</tr>"
        )
    return "\n".join(rows) or "<tr><td colspan=\"3\">No activity recorded.</td></tr>"


def _rows_for_axes(cumulative_axes: Dict[str, float], daily_axes: Dict[str, float]) -> str:
    rows = []
    for left, right in AXIS_PAIRS:
        rows.append(
            "<tr>"
            f"<td>{escape(left.replace('_', ' ').title())}</td>"
            f"<td class=\"num\">{_score(daily_axes.get(left, 0.0))}</td>"
            f"<td class=\"num\">{_score(cumulative_axes.get(left, 0.0))}</td>"
            f"<td>{escape(right.replace('_', ' ').title())}</td>"
            f"<td class=\"num\">{_score(daily_axes.get(right, 0.0))}</td>"
            f"<td class=\"num\">{_score(cumulative_axes.get(right, 0.0))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _rows_for_temporal(features: Dict) -> str:
    values = [
        ("Sessions", features.get("total_sessions", 0)),
        ("Late-night entries", features.get("late_night_entries", 0)),
        ("Checking loops", features.get("checking_loops", {}).get("intensity", 0.0)),
        ("Feed surrender", features.get("feed_surrender", {}).get("intensity", 0.0)),
        ("Doomscroll vigilance", features.get("doomscroll_vigilance", {}).get("intensity", 0.0)),
        ("Creative absorption", features.get("creative_absorption", {}).get("intensity", 0.0)),
        ("Research chain", features.get("research_chain", {}).get("intensity", 0.0)),
        ("Task completion", features.get("task_completion", {}).get("intensity", 0.0)),
        ("Social connection", features.get("social_connection", {}).get("intensity", 0.0)),
        ("Health anxiety", features.get("health_anxiety", {}).get("intensity", 0.0)),
        ("Financial stress", features.get("financial_stress", {}).get("intensity", 0.0)),
        ("Escapism", features.get("escapism", {}).get("intensity", 0.0)),
    ]
    rows = []
    for label, value in values:
        text = f"{value:.3f}" if isinstance(value, float) else str(value)
        rows.append(f"<tr><td>{escape(label)}</td><td class=\"num\">{escape(text)}</td></tr>")
    return "\n".join(rows)


def write_today_html(
    date_str: str,
    caption: str,
    prompt: str,
    state: Dict,
    daily_axes: Dict[str, float],
    category_counts: Dict[str, int],
    features: Dict,
    image_path: Optional[Path],
) -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    image_html = "<div class=\"empty\">No image generated for this run.</div>"
    if image_path and image_path.exists():
        image_html = f"<img src=\"{escape(image_path.resolve().as_uri())}\" alt=\"Generated Dorian Gray portrait\">"

    axes = state.get("axes", {})
    visual = state.get("visual_intensity", {})
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dorian Gray Bot - {escape(date_str)}</title>
  <style>
    :root {{
      --ink: #171512;
      --muted: #676056;
      --line: #d8d0c2;
      --paper: #f7f3ea;
      --panel: #fffdf8;
      --accent: #6d1d2d;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 28px 32px 20px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }}
    h1, h2 {{ margin: 0; line-height: 1.15; }}
    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 18px; margin-bottom: 10px; }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 26px 22px 46px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(280px, 420px) 1fr;
      gap: 22px;
      align-items: start;
    }}
    .portrait {{
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: var(--panel);
    }}
    .portrait img, .empty {{
      display: block;
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
    }}
    .empty {{
      display: grid;
      place-items: center;
      color: var(--muted);
      padding: 24px;
      text-align: center;
    }}
    section {{
      margin-top: 24px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); background: #f0eadf; }}
    tr:last-child td {{ border-bottom: 0; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .caption {{ font-size: 22px; margin: 0 0 14px; color: var(--accent); }}
    .meta {{ color: var(--muted); margin-top: 6px; }}
    pre {{
      white-space: pre-wrap;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      max-height: 420px;
      overflow: auto;
    }}
    @media (max-width: 820px) {{
      header {{ padding: 22px 18px 16px; }}
      main {{ padding: 20px 14px 36px; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Dorian Gray Bot</h1>
    <div class="meta">{escape(date_str)} generated {escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</div>
  </header>
  <main>
    <div class="grid">
      <div class="portrait">{image_html}</div>
      <div>
        <p class="caption">{escape(caption)}</p>
        <table>
          <tbody>
            <tr><th>Deterioration</th><td class="num">{_score(visual.get("deterioration", 0.0))}</td></tr>
            <tr><th>Restoration</th><td class="num">{_score(visual.get("restoration", 0.0))}</td></tr>
            <tr><th>Synthetic mediation</th><td class="num">{_score(visual.get("synthetic_mediation", 0.0))}</td></tr>
            <tr><th>World presence</th><td class="num">{_score(visual.get("world_presence", 0.0))}</td></tr>
            <tr><th>Days processed</th><td class="num">{len(state.get("days_processed", []))}</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <section>
      <h2>Axes</h2>
      <table>
        <thead><tr><th>Axis</th><th class="num">Daily</th><th class="num">Cumulative</th><th>Axis</th><th class="num">Daily</th><th class="num">Cumulative</th></tr></thead>
        <tbody>{_rows_for_axes(axes, daily_axes)}</tbody>
      </table>
    </section>

    <section>
      <h2>Activity Categories</h2>
      <table>
        <thead><tr><th>Category</th><th class="num">Visits</th><th class="num">Share</th></tr></thead>
        <tbody>{_rows_for_categories(category_counts)}</tbody>
      </table>
    </section>

    <section>
      <h2>Temporal Patterns</h2>
      <table>
        <thead><tr><th>Pattern</th><th class="num">Value</th></tr></thead>
        <tbody>{_rows_for_temporal(features)}</tbody>
      </table>
    </section>

    <section>
      <h2>Visual Prompt</h2>
      <pre>{escape(prompt)}</pre>
    </section>
  </main>
</body>
</html>
"""
    path = OUTPUTS_DIR / "today.html"
    path.write_text(html)
    return path
