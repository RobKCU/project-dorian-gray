"""Choose today's small set of edits (the "change budget").

Inputs: today's pole scores and modifier intensities, plus memory of
- weather: a running average of recent pole scores (how things have been lately)
- when each channel and each move was last used

Today's salience for a pole = how strong it is today, plus a bonus for how far
it rises above recent weather. So a pole that is always high still acts, but a
change in behaviour gets noticed first. Recently used channels and moves rest
for a while, so the edits wander across the whole picture instead of hammering
the same feature.
"""

import random
from typing import Dict, List

from .channels import COMBO_MOVES, MODIFIER_TRACES, POLE_MOVES, WEATHER_GATES, adverb
from .config import AXIS_MOVES_PER_DAY, CHANNEL_REST_DAYS, MIN_POLE_SALIENCE, MOVE_REST_DAYS, WEATHER_RATE

COMBO_THRESHOLD = 0.45
TRACE_THRESHOLD = 0.35


def salience(scores: Dict[str, float], weather: Dict[str, float]) -> Dict[str, float]:
    return {
        pole: round(0.6 * s + 0.6 * max(0.0, s - weather.get(pole, 0.0)), 4)
        for pole, s in scores.items()
    }


def _rest(day: int, last_used: Dict[str, int], key: str, rest_days: int) -> float:
    since = day - last_used.get(key, -999)
    return max(0.0, min(1.0, since / rest_days))


def choose_moves(
    scores: Dict[str, float],
    modifiers: Dict[str, float],
    weather: Dict[str, float],
    channel_last: Dict[str, int],
    move_last: Dict[str, int],
    day: int,
    seed: str,
) -> List[Dict]:
    rng = random.Random(seed)
    sal = salience(scores, weather)

    def freshness(channel: str, move_id: str) -> float:
        ch = _rest(day, channel_last, channel, CHANNEL_REST_DAYS)
        mv = _rest(day, move_last, move_id, MOVE_REST_DAYS)
        return ch * (0.3 + 0.7 * mv)

    candidates = []
    for a, b, move_id, channel, phrase in COMBO_MOVES:
        if scores.get(a, 0) >= COMBO_THRESHOLD and scores.get(b, 0) >= COMBO_THRESHOLD:
            strength = min(sal[a], sal[b]) + 0.1
            candidates.append({
                "id": move_id, "channel": channel, "source": f"{a}+{b}", "poles": [a, b],
                "strength": strength, "phrase": phrase,
                "rank": strength * 1.15 * freshness(channel, move_id) * rng.uniform(0.85, 1.15),
            })
    for pole, moves in POLE_MOVES.items():
        if sal.get(pole, 0) < MIN_POLE_SALIENCE:
            continue
        for move_id, channel, phrase in moves:
            gate = WEATHER_GATES.get(move_id)
            if gate and weather.get(gate[0], 0.0) < gate[1]:
                continue
            candidates.append({
                "id": move_id, "channel": channel, "source": pole, "poles": [pole],
                "strength": sal[pole], "phrase": phrase,
                "rank": sal[pole] * freshness(channel, move_id) * rng.uniform(0.85, 1.15),
            })

    chosen, used_channels, used_poles = [], set(), set()
    for cand in sorted(candidates, key=lambda c: c["rank"], reverse=True):
        if len(chosen) >= AXIS_MOVES_PER_DAY or cand["rank"] <= 0:
            break
        if cand["channel"] in used_channels or used_poles & set(cand["poles"]):
            continue
        chosen.append(cand)
        used_channels.add(cand["channel"])
        used_poles.update(cand["poles"])

    # one local trace from the strongest behavioural pattern, if any
    traces = []
    for name, intensity in modifiers.items():
        if intensity < TRACE_THRESHOLD or name not in MODIFIER_TRACES:
            continue
        channel, phrase = MODIFIER_TRACES[name]
        move_id = f"trace_{name}"
        if channel in used_channels:
            continue
        rank = intensity * freshness(channel, move_id) * rng.uniform(0.9, 1.1)
        if rank > 0:
            traces.append({"id": move_id, "channel": channel, "source": name, "poles": [],
                           "strength": intensity * 0.6, "phrase": phrase, "rank": rank})
    if traces:
        chosen.append(max(traces, key=lambda t: t["rank"]))

    for move in chosen:
        move["strength"] = round(min(1.0, move["strength"]), 3)
        move["text"] = move["phrase"].format(adv=adverb(move["strength"]))
        move["rank"] = round(move["rank"], 3)
        del move["phrase"]
    return chosen


def update_weather(weather: Dict[str, float], scores: Dict[str, float]) -> Dict[str, float]:
    return {
        pole: round(weather.get(pole, 0.0) * (1 - WEATHER_RATE) + s * WEATHER_RATE, 4)
        for pole, s in scores.items()
    }
