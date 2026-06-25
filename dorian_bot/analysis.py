"""Classification, temporal analysis, scoring, state, and caption selection."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple
import json

from .config import (
    ACTIVITY_CATEGORIES,
    AXIS_UPDATE_RATE,
    EARLY_MORNING_THRESHOLD,
    LATE_NIGHT_THRESHOLD,
    PORTRAIT_STATE_FILE,
)


AXES = [
    "directedness",
    "drift",
    "public",
    "private",
    "self",
    "others",
    "vitality",
    "gloom",
    "ai_mediation",
    "direct_engagement",
]

MODIFIERS = [
    "checking_loops",
    "feed_surrender",
    "doomscroll_vigilance",
    "late_night_spiral",
    "creative_absorption",
    "research_chain",
    "task_completion",
    "social_connection",
    "health_anxiety",
    "financial_stress",
    "escapism",
]

CATEGORY_AXIS_MAP = {
    "generative_ai": {"ai_mediation": 0.9, "directedness": 0.4, "drift": 0.2},
    "email_admin": {"others": 0.3, "private": 0.4, "self": 0.1},
    "search": {"directedness": 0.3, "drift": 0.2},
    "social_media": {"drift": 0.6, "self": 0.3, "public": 0.2},
    "video_streaming": {"drift": 0.5, "private": 0.3, "vitality": 0.1, "gloom": 0.1},
    "news": {"public": 0.6, "gloom": 0.2, "directedness": 0.1},
    "research_reference": {"directedness": 0.8, "public": 0.5, "direct_engagement": 0.7},
    "archives_primary_sources": {
        "directedness": 0.9,
        "public": 0.8,
        "direct_engagement": 0.9,
        "vitality": 0.3,
    },
    "work_tools": {"directedness": 0.6, "others": 0.3, "vitality": 0.2},
    "shopping": {"drift": 0.3, "private": 0.2, "self": 0.3},
    "health": {"self": 0.8, "private": 0.6, "gloom": 0.4},
    "finance": {"self": 0.7, "private": 0.6, "directedness": 0.2},
    "education_university": {"directedness": 0.7, "public": 0.4, "direct_engagement": 0.6, "vitality": 0.2},
    "entertainment_culture": {"drift": 0.3, "vitality": 0.4, "private": 0.2},
    "maps_travel_local": {"public": 0.6, "directedness": 0.4, "vitality": 0.3},
    "other": {"drift": 0.2},
}

MODIFIER_AXIS_MAP = {
    "checking_loops": {"drift": 0.7, "private": 0.5, "self": 0.4, "gloom": 0.3},
    "feed_surrender": {"drift": 0.8, "private": 0.4, "gloom": 0.2},
    "doomscroll_vigilance": {"public": 0.6, "gloom": 0.7, "drift": 0.4},
    "late_night_spiral": {"gloom": 0.8, "private": 0.5, "drift": 0.5, "vitality": -0.6},
    "creative_absorption": {"directedness": 0.9, "vitality": 0.6, "direct_engagement": 0.7},
    "research_chain": {"directedness": 0.9, "public": 0.6, "direct_engagement": 0.8, "vitality": 0.4},
    "task_completion": {"directedness": 0.8, "vitality": 0.2, "gloom": 0.2},
    "social_connection": {"others": 0.9, "vitality": 0.6, "directedness": 0.3},
    "health_anxiety": {"self": 0.9, "gloom": 0.7, "private": 0.6, "drift": 0.4},
    "financial_stress": {"self": 0.7, "private": 0.5, "gloom": 0.5, "drift": 0.2},
    "escapism": {"drift": 0.6, "private": 0.5, "gloom": 0.3, "vitality": 0.1},
}

CAPTION_TERMS = {
    "drift": ["drift", "wandering", "diffusion"],
    "ai_mediation": ["synthesis", "mediation", "delegation"],
    "creative_absorption": ["discipline", "absorption", "making"],
    "research_chain": ["inquiry", "attention", "study"],
    "gloom": ["defeat", "fatigue", "shadow"],
    "vitality": ["renewal", "warmth", "vitality"],
    "public": ["witness", "exposure", "weather"],
    "private": ["withdrawal", "seclusion", "interiority"],
    "others": ["relation", "company", "correspondence"],
    "late_night_spiral": ["insomnia", "vigil", "unrest"],
}


def classify_domain(domain: str) -> str:
    domain_lower = domain.lower()
    best_match = None
    for category, patterns in ACTIVITY_CATEGORIES.items():
        for pattern in patterns:
            pattern = pattern.lower()
            matched = False
            if pattern.startswith(".") and domain_lower.endswith(pattern):
                matched = True
            elif "." in pattern:
                matched = domain_lower == pattern or domain_lower.endswith(f".{pattern}")
            else:
                matched = pattern in domain_lower
            if matched and (best_match is None or len(pattern) > best_match[0]):
                best_match = (len(pattern), category)
    return best_match[1] if best_match else "other"


def classify_entries(entries: List[Dict]) -> Tuple[Dict[str, int], Dict[str, Dict[str, int]]]:
    category_counts = {}
    domain_counts = {}
    for entry in entries:
        domain = entry["domain"]
        category = classify_domain(domain)
        category_counts[category] = category_counts.get(category, 0) + 1
        domain_counts.setdefault(category, {})
        domain_counts[category][domain] = domain_counts[category].get(domain, 0) + 1
    return category_counts, domain_counts


def _sessions(entries: List[Dict], gap_minutes: int = 10) -> List[Dict]:
    sessions = []
    current = None
    for entry in entries:
        timestamp = datetime.fromisoformat(entry["timestamp"])
        if current is None:
            current = {"start": timestamp, "end": timestamp, "entries": [entry], "domains": {entry["domain"]}}
            continue
        previous = datetime.fromisoformat(current["entries"][-1]["timestamp"])
        if (timestamp - previous).total_seconds() / 60 >= gap_minutes:
            current["duration_minutes"] = (current["end"] - current["start"]).total_seconds() / 60
            sessions.append(current)
            current = {"start": timestamp, "end": timestamp, "entries": [entry], "domains": {entry["domain"]}}
        else:
            current["end"] = timestamp
            current["entries"].append(entry)
            current["domains"].add(entry["domain"])
    if current:
        current["duration_minutes"] = (current["end"] - current["start"]).total_seconds() / 60
        sessions.append(current)
    return sessions


def temporal_features(entries: List[Dict]) -> Dict:
    sessions = _sessions(entries)
    late_night = [
        e for e in entries
        if e["hour"] + e["minute"] / 60 >= LATE_NIGHT_THRESHOLD or e["hour"] < EARLY_MORNING_THRESHOLD
    ]

    domain_visits = defaultdict(list)
    for entry in entries:
        domain_visits[entry["domain"]].append(datetime.fromisoformat(entry["timestamp"]))

    loop_returns = 0
    for timestamps in domain_visits.values():
        timestamps.sort()
        for index, start in enumerate(timestamps):
            for later in timestamps[index + 1:]:
                if (later - start).total_seconds() / 60 <= 60:
                    loop_returns += 1

    switches = sum(1 for left, right in zip(entries, entries[1:]) if left["domain"] != right["domain"])
    feed_domains = {"bsky.app", "x.com", "twitter.com", "facebook.com", "instagram.com", "reddit.com", "youtube.com", "tiktok.com"}
    news_domains = set(ACTIVITY_CATEGORIES["news"])
    creative_domains = {"github.com", "gitlab.com", "notion.so", "figma.com", "stackoverflow.com"}
    health_domains = set(ACTIVITY_CATEGORIES["health"])
    finance_domains = set(ACTIVITY_CATEGORIES["finance"])

    def contains_any(domain: str, patterns: set) -> bool:
        return any(pattern in domain for pattern in patterns)

    feed_minutes = sum(s["duration_minutes"] for s in sessions if s["duration_minutes"] >= 15 and any(contains_any(d, feed_domains) for d in s["domains"]))
    creative_minutes = sum(s["duration_minutes"] for s in sessions if s["duration_minutes"] >= 5 and any(contains_any(d, creative_domains) for d in s["domains"]))
    research_sessions = sum(1 for s in sessions if s["duration_minutes"] >= 5 and any("github.com" in d or "stackoverflow.com" in d or "wikipedia.org" in d for d in s["domains"]))
    focused_sessions = sum(1 for s in sessions if s["duration_minutes"] >= 15 and len(s["domains"]) <= 3)
    news_entries = [e for e in entries if contains_any(e["domain"], news_domains)]
    health_entries = [e for e in entries if contains_any(e["domain"], health_domains)]
    finance_entries = [e for e in entries if contains_any(e["domain"], finance_domains)]

    return {
        "total_sessions": len(sessions),
        "late_night_entries": len(late_night),
        "checking_loops": {"intensity": min(1.0, loop_returns / 50.0), "total_loop_returns": loop_returns},
        "feed_surrender": {"intensity": min(1.0, feed_minutes / 180.0), "minutes": feed_minutes},
        "domain_switching": {"switch_count": switches, "switch_intensity": min(1.0, switches / 50.0)},
        "doomscroll_vigilance": {"intensity": min(1.0, len(news_entries) / 40.0)},
        "creative_absorption": {"intensity": min(1.0, creative_minutes / 120.0), "minutes": creative_minutes},
        "research_chain": {"intensity": min(1.0, research_sessions / 3.0)},
        "task_completion": {"intensity": min(1.0, focused_sessions / 2.0)},
        "social_connection": {"intensity": min(1.0, sum(1 for e in entries if contains_any(e["domain"], {"gmail.com", "slack.com", "discord.com", "bsky.app"})) / 30.0)},
        "health_anxiety": {"intensity": min(1.0, len(health_entries) / 20.0)},
        "financial_stress": {"intensity": min(1.0, len(finance_entries) / 25.0)},
        "escapism": {"intensity": min(1.0, feed_minutes / 120.0)},
    }


def daily_axis_scores(category_counts: Dict[str, int], features: Dict) -> Dict[str, float]:
    scores = {axis: 0.0 for axis in AXES}
    total = sum(category_counts.values())
    if total:
        for category, count in category_counts.items():
            for axis, weight in CATEGORY_AXIS_MAP.get(category, CATEGORY_AXIS_MAP["other"]).items():
                scores[axis] += (count / total) * weight

    modifier_intensities = {name: features.get(name, {}).get("intensity", 0.0) for name in MODIFIERS}
    modifier_intensities["late_night_spiral"] = min(1.0, features.get("late_night_entries", 0) / 30.0)
    for modifier, intensity in modifier_intensities.items():
        for axis, weight in MODIFIER_AXIS_MAP.get(modifier, {}).items():
            scores[axis] += intensity * weight

    return {axis: max(0.0, min(1.0, value)) for axis, value in scores.items()}


def create_initial_state() -> Dict:
    now = datetime.now().isoformat()
    return {
        "version": 1,
        "created_at": now,
        "last_updated": now,
        "first_posted_at": None,
        "days_processed": [],
        "axes": {axis: 0.0 for axis in AXES},
        "visual_intensity": visual_intensity({axis: 0.0 for axis in AXES}),
        "daily_logs": [],
    }


def load_state() -> Dict:
    if not PORTRAIT_STATE_FILE.exists():
        return create_initial_state()
    state = json.loads(PORTRAIT_STATE_FILE.read_text())
    state.setdefault("axes", {})
    for axis in AXES:
        state["axes"].setdefault(axis, 0.0)
    state.setdefault("first_posted_at", None)
    state.setdefault("days_processed", [])
    state.setdefault("daily_logs", [])
    state.setdefault("visual_intensity", visual_intensity(state["axes"]))
    return state


def mark_first_posted(state: Dict) -> Dict:
    state["first_posted_at"] = datetime.now().isoformat()
    state["last_updated"] = datetime.now().isoformat()
    return state


def visual_intensity(axes: Dict[str, float]) -> Dict[str, float]:
    deterioration = axes["drift"] * 0.3 + axes["private"] * 0.2 + axes["self"] * 0.2 + axes["gloom"] * 0.2 + axes["ai_mediation"] * 0.1
    restoration = axes["directedness"] * 0.25 + axes["public"] * 0.2 + axes["others"] * 0.2 + axes["vitality"] * 0.25 + axes["direct_engagement"] * 0.1
    return {
        "deterioration": round(max(0.0, min(1.0, deterioration)), 4),
        "restoration": round(max(0.0, min(1.0, restoration)), 4),
        "synthetic_mediation": round(axes["ai_mediation"], 4),
        "world_presence": round(axes["public"] * 0.6 + axes["direct_engagement"] * 0.4, 4),
        "interpersonal_presence": round(axes["others"], 4),
    }


def update_state(state: Dict, date_str: str, daily_axes: Dict[str, float], features: Dict, category_counts: Dict[str, int]) -> Dict:
    if date_str in state["days_processed"]:
        return state
    for axis in AXES:
        current = state["axes"].get(axis, 0.0)
        state["axes"][axis] = round(current * (1 - AXIS_UPDATE_RATE) + daily_axes.get(axis, 0.0) * AXIS_UPDATE_RATE, 4)
    state["visual_intensity"] = visual_intensity(state["axes"])
    state["days_processed"].append(date_str)
    state["last_updated"] = datetime.now().isoformat()
    state["daily_logs"].append(
        {
            "date": date_str,
            "daily_axes": daily_axes,
            "category_counts": category_counts,
            "features": features,
        }
    )
    state["daily_logs"] = state["daily_logs"][-60:]
    return state


def save_state(state: Dict) -> None:
    PORTRAIT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PORTRAIT_STATE_FILE.write_text(json.dumps(state, indent=2))


def choose_caption_term(daily_axes: Dict[str, float], features: Dict) -> str:
    candidates = {
        "creative_absorption": features.get("creative_absorption", {}).get("intensity", 0.0),
        "research_chain": features.get("research_chain", {}).get("intensity", 0.0),
        "late_night_spiral": min(1.0, features.get("late_night_entries", 0) / 30.0),
        "drift": daily_axes.get("drift", 0.0),
        "ai_mediation": daily_axes.get("ai_mediation", 0.0),
        "gloom": daily_axes.get("gloom", 0.0),
        "vitality": daily_axes.get("vitality", 0.0),
        "public": daily_axes.get("public", 0.0),
        "private": daily_axes.get("private", 0.0),
        "others": daily_axes.get("others", 0.0),
    }
    winner = max(candidates.items(), key=lambda item: item[1])[0]
    terms = CAPTION_TERMS[winner]
    index = int(sum(daily_axes.values()) * 1000) % len(terms)
    return terms[index]


def caption_for_day(daily_axes: Dict[str, float], features: Dict) -> str:
    return f"The jpeg absorbs a day of {choose_caption_term(daily_axes, features)}."
