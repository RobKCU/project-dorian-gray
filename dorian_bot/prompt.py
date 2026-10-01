"""Build the daily edit instruction sent to the image model.

The prompt describes only today's change. The image itself carries everything
that has happened before, including artefacts, which are deliberately kept.
"""

from typing import Dict, List

CHANNEL_LABELS = {
    "composition": "Composition", "background": "Background", "lighting": "Light and colour",
    "posture": "Posture and body", "gaze": "Eyes and gaze", "mouth": "Mouth",
    "skin": "Skin and face", "handling": "Surface", "depth": "Space and focus",
    "world_traces": "Traces of the world", "interpersonal_traces": "Traces of others",
}


def build_prompt(day: int, moves: List[Dict]) -> str:
    lines = [
        f"Edit this image. It is day {day} of a portrait that is re-processed once a day, "
        "each day starting from the previous day's JPEG.",
        "",
        "Make only these changes:",
    ]
    for move in moves:
        lines.append(f"- {CHANNEL_LABELS.get(move['channel'], move['channel'])}: {move['text']}.")
    lines += [
        "",
        "Leave everything else as it is. Keep the same person, framing and pose except where a change above says otherwise.",
        "Preserve every existing distortion, artefact, colour shift and oddity from earlier days: "
        "do not repair, restore, clean up, beautify or re-style the image, and do not convert it into a different medium.",
        "Do not add text, screens, phones, logos, interface elements or other literal technology.",
    ]
    return "\n".join(lines)


def quiet_note(day: int) -> str:
    return f"Day {day}: no browsing recorded; the image is only re-saved as a JPEG."
