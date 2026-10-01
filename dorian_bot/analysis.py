"""Turn one day of sanitized browsing into pole scores and modifier intensities.

Five axes, ten independently scored poles. Unlike the first version, daily
scores are not clamped flat at 1.0: they are squashed smoothly, so a heavy day
still reads differently from an extreme one.
"""

from collections import defaultdict
from datetime import datetime
from math import exp
from typing import Dict, List, Tuple

from .config import ACTIVITY_CATEGORIES, EARLY_MORNING_THRESHOLD, LATE_NIGHT_THRESHOLD

AXIS_PAIRS = [
    ("directedness", "drift"),
    ("public", "private"),
    ("self", "others"),
    ("vitality", "gloom"),
    ("ai_mediation", "direct_engagement"),
]
POLES = [pole for pair in AXIS_PAIRS for pole in pair]

MODIFIERS = [
    "checking_loop", "feed_surrender", "doomscroll_vigilance", "late_night_spiral",
    "comparative_evaluation", "administrative_burden", "creative_absorption", "research_chain",
    "social_exposure", "social_connection", "health_anxiety", "sensual_escape",
    "ai_delegation", "direct_source_immersion", "task_pressure",
]

CATEGORY_POLE_MAP = {
    "generative_ai": {"ai_mediation": 1.0, "directedness": 0.4},
    "email_admin": {"others": 0.3, "private": 0.3, "directedness": 0.2},
    "search": {"directedness": 0.3, "drift": 0.2},
    "social_media": {"drift": 0.5, "self": 0.4, "public": 0.2},
    "video_streaming": {"drift": 0.5, "private": 0.3},
    "news": {"public": 0.6, "gloom": 0.25},
    "research_reference": {"directedness": 0.7, "public": 0.3, "direct_engagement": 0.7},
    "archives_primary_sources": {"directedness": 0.8, "public": 0.5, "direct_engagement": 1.0, "vitality": 0.2},
    "work_tools": {"directedness": 0.6, "others": 0.3},
    "shopping": {"self": 0.5, "drift": 0.3, "private": 0.2},
    "health": {"self": 0.7, "private": 0.5, "gloom": 0.3},
    "finance": {"self": 0.6, "private": 0.5, "directedness": 0.2},
    "education_university": {"directedness": 0.6, "public": 0.4, "direct_engagement": 0.5},
    "entertainment_culture": {"vitality": 0.4, "drift": 0.2, "private": 0.2},
    "maps_travel_local": {"public": 0.7, "vitality": 0.4, "direct_engagement": 0.4},
    "adult": {"private": 0.9, "self": 0.6, "drift": 0.4},
    "other": {"drift": 0.15},
}

MODIFIER_POLE_MAP = {
    "checking_loop": {"drift": 0.4, "self": 0.3, "gloom": 0.3},
    "feed_surrender": {"drift": 0.7, "private": 0.3, "gloom": 0.2},
    "doomscroll_vigilance": {"public": 0.4, "gloom": 0.7},
    "late_night_spiral": {"gloom": 0.7, "private": 0.5, "drift": 0.4, "vitality": -0.5},
    "comparative_evaluation": {"self": 0.5, "directedness": 0.2},
    "administrative_burden": {"directedness": 0.4, "gloom": 0.3, "vitality": -0.2},
    "creative_absorption": {"directedness": 0.8, "vitality": 0.6, "direct_engagement": 0.6},
    "research_chain": {"directedness": 0.7, "public": 0.4, "direct_engagement": 0.7},
    "social_exposure": {"self": 0.7, "public": 0.5},
    "social_connection": {"others": 0.9, "vitality": 0.5},
    "health_anxiety": {"self": 0.6, "gloom": 0.6, "private": 0.4},
    "sensual_escape": {"private": 0.6, "drift": 0.4, "self": 0.3},
    "ai_delegation": {"ai_mediation": 0.8},
    "direct_source_immersion": {"direct_engagement": 0.9, "public": 0.3, "vitality": 0.3},
    "task_pressure": {"directedness": 0.6, "gloom": 0.2},
}


def classify_domain(domain: str) -> str:
    domain = domain.lower()
    best = None
    for category, patterns in ACTIVITY_CATEGORIES.items():
        for pattern in patterns:
            pattern = pattern.lower()
            if pattern.startswith("."):
                hit = domain.endswith(pattern)
            elif "." in pattern:
                hit = domain == pattern or domain.endswith("." + pattern)
            else:
                hit = pattern in domain
            if hit and (best is None or len(pattern) > best[0]):
                best = (len(pattern), category)
    return best[1] if best else "other"


def classify_entries(entries: List[Dict]) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for entry in entries:
        entry["category"] = classify_domain(entry["domain"])
        counts[entry["category"]] += 1
    return dict(counts)


def _sessions(entries: List[Dict], gap_minutes: int = 10) -> List[Dict]:
    sessions, current = [], None
    for entry in entries:
        ts = datetime.fromisoformat(entry["timestamp"])
        if current and (ts - current["end"]).total_seconds() / 60 < gap_minutes:
            current["end"] = ts
            current["entries"].append(entry)
            current["categories"].add(entry["category"])
            current["domains"].add(entry["domain"])
        else:
            current = {"start": ts, "end": ts, "entries": [entry],
                       "categories": {entry["category"]}, "domains": {entry["domain"]}}
            sessions.append(current)
    for s in sessions:
        s["minutes"] = (s["end"] - s["start"]).total_seconds() / 60
    return sessions


def _cap(value: float, full: float) -> float:
    return max(0.0, min(1.0, value / full)) if full else 0.0


def modifier_intensities(entries: List[Dict], counts: Dict[str, int]) -> Dict[str, float]:
    """Pattern detectors. Each returns 0..1. Requires classify_entries first."""
    total = max(1, len(entries))
    sessions = _sessions(entries)
    share = {c: n / total for c, n in counts.items()}

    late = sum(
        1 for e in entries
        if e["hour"] + e["minute"] / 60 >= LATE_NIGHT_THRESHOLD or e["hour"] < EARLY_MORNING_THRESHOLD
    )

    # returns to the same domain within 30 minutes, excluding continuous use
    visits = defaultdict(list)
    for e in entries:
        visits[e["domain"]].append(datetime.fromisoformat(e["timestamp"]))
    returns = 0
    for times in visits.values():
        for a, b in zip(times, times[1:]):
            gap = (b - a).total_seconds() / 60
            if 3 <= gap <= 30:
                returns += 1

    def minutes_in(cats, min_len):
        return sum(s["minutes"] for s in sessions if s["minutes"] >= min_len and s["categories"] & cats)

    feed_minutes = minutes_in({"social_media", "video_streaming"}, 15)
    creative_minutes = sum(
        s["minutes"] for s in sessions
        if s["minutes"] >= 10 and len(s["domains"]) <= 3 and s["categories"] & {"work_tools", "research_reference"}
    )
    research_sessions = sum(
        1 for s in sessions
        if s["minutes"] >= 8 and len(s["categories"] & {"research_reference", "archives_primary_sources", "education_university"}) >= 1
        and len(s["domains"]) >= 3
    )
    focused_sessions = sum(1 for s in sessions if s["minutes"] >= 15 and len(s["domains"]) <= 3)

    return {
        "checking_loop": _cap(returns, 110),
        "feed_surrender": _cap(feed_minutes, 300),
        "doomscroll_vigilance": _cap(counts.get("news", 0), 15) * (0.5 + 0.5 * _cap(late, 40)),
        "late_night_spiral": _cap(late, 80),
        "comparative_evaluation": _cap(counts.get("shopping", 0), 60),
        "administrative_burden": _cap(counts.get("email_admin", 0) + counts.get("finance", 0), 260),
        "creative_absorption": _cap(creative_minutes, 45),
        "research_chain": _cap(research_sessions, 10),
        "social_exposure": _cap(share.get("social_media", 0), 0.6),
        "social_connection": _cap(counts.get("email_admin", 0) * 0.3 + sum(
            1 for e in entries if any(p in e["domain"] for p in ("slack.com", "discord.com", "messages.google.com", "whatsapp"))
        ), 100),
        "health_anxiety": _cap(counts.get("health", 0), 15),
        "sensual_escape": _cap(counts.get("adult", 0), 15),
        "ai_delegation": _cap(counts.get("generative_ai", 0), 30),
        "direct_source_immersion": _cap(counts.get("archives_primary_sources", 0), 10),
        "task_pressure": _cap(focused_sessions, 3),
    }


def _squash(x: float) -> float:
    """Smoothly map 0..inf onto 0..1 without a hard ceiling."""
    return 1 - exp(-1.6 * max(0.0, x))


def pole_scores(counts: Dict[str, int], modifiers: Dict[str, float]) -> Dict[str, float]:
    raw = {pole: 0.0 for pole in POLES}
    total = sum(counts.values())
    if total:
        for category, n in counts.items():
            for pole, w in CATEGORY_POLE_MAP.get(category, CATEGORY_POLE_MAP["other"]).items():
                raw[pole] += (n / total) * w
    for modifier, intensity in modifiers.items():
        for pole, w in MODIFIER_POLE_MAP.get(modifier, {}).items():
            raw[pole] += intensity * w * 0.6
    # Time away from the browser counts toward vitality and direct engagement:
    # a light, daytime day is the main route to "redemption".
    offline = 1 - min(1.0, total / 450)
    daytime = 1 - modifiers.get("late_night_spiral", 0.0)
    raw["vitality"] += offline * 0.9 * daytime + 0.15 * daytime
    raw["direct_engagement"] += offline * 0.4
    return {pole: round(_squash(v), 4) for pole, v in raw.items()}


def analyse_day(entries: List[Dict]) -> Tuple[Dict[str, int], Dict[str, float], Dict[str, float]]:
    counts = classify_entries(entries)
    mods = modifier_intensities(entries, counts)
    scores = pole_scores(counts, mods)
    return counts, {k: round(v, 4) for k, v in mods.items()}, scores


def average(dicts: List[Dict[str, float]]) -> Dict[str, float]:
    if not dicts:
        return {}
    keys = set().union(*dicts)
    return {k: round(sum(d.get(k, 0.0) for d in dicts) / len(dicts), 4) for k in keys}
