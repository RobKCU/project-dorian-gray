"""Caption ritual: "The jpeg absorbs a day of [BLANK]."

The blank comes from the source of the day's lead edit, drawn from a controlled,
allusive vocabulary, and is not reused within the last few posts.
"""

import random
from typing import List, Optional

from .config import CAPTION_NO_REPEAT

FIRST_CAPTION = "The jpeg absorbs its first day."

VOCABULARY = {
    "directedness": ["focus", "method", "intent", "procedure", "resolve"],
    "drift": ["drift", "wandering", "diffusion", "scrolling", "latency", "dispersal"],
    "public": ["exposure", "display", "circulation", "visibility", "weather"],
    "private": ["withdrawal", "seclusion", "interiority", "enclosure", "shuttering"],
    "self": ["self-regard", "mirroring", "profile", "pose", "retouching"],
    "others": ["correspondence", "company", "relation", "sharing", "reply"],
    "vitality": ["renewal", "warmth", "charge", "pulse"],
    "gloom": ["fatigue", "shadow", "erosion", "sediment", "dimming"],
    "ai_mediation": ["synthesis", "interpolation", "prediction", "generation", "delegation", "rendering"],
    "direct_engagement": ["contact", "study", "inquiry", "presence", "grain"],
    # modifier traces
    "checking_loop": ["refresh", "repetition", "telemetry"],
    "feed_surrender": ["scrolling", "buffering", "the feed"],
    "doomscroll_vigilance": ["vigilance", "alarm", "monitoring"],
    "late_night_spiral": ["insomnia", "vigil", "unrest"],
    "comparative_evaluation": ["comparison", "appraisal"],
    "administrative_burden": ["paperwork", "obligation"],
    "creative_absorption": ["making", "absorption", "discipline"],
    "research_chain": ["inquiry", "citation", "study"],
    "social_exposure": ["display", "posting", "capture"],
    "social_connection": ["correspondence", "company"],
    "health_anxiety": ["symptoms", "worry"],
    "sensual_escape": ["appetite", "longing"],
    "ai_delegation": ["delegation", "prompting"],
    "direct_source_immersion": ["archives", "sources"],
    "task_pressure": ["deadlines", "pressure"],
    "quiet": ["absence", "stillness", "compression"],
}


def choose_caption(lead_source: Optional[str], recent_words: List[str], seed: str, days_span: int = 1) -> tuple:
    rng = random.Random(seed + "caption")
    key = lead_source or "quiet"
    if "+" in key:  # combo: pick either pole's vocabulary
        key = rng.choice(key.split("+"))
    pool = VOCABULARY.get(key, VOCABULARY["quiet"])
    blocked = set(recent_words[-CAPTION_NO_REPEAT:])
    fresh = [w for w in pool if w not in blocked]
    if not fresh:  # fall back to any unused word in the whole vocabulary
        fresh = sorted({w for words in VOCABULARY.values() for w in words} - blocked) or pool
    word = rng.choice(fresh)
    if days_span > 1:
        text = f"The jpeg absorbs {days_span} days of {word}."
    else:
        text = f"The jpeg absorbs a day of {word}."
    return word, text
