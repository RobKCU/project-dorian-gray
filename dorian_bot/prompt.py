"""Generate image-edit prompts from cumulative portrait state."""

from typing import Dict


def _intensity(value: float) -> str:
    if value < 0.15:
        return "absent"
    if value < 0.35:
        return "faint"
    if value < 0.60:
        return "moderate"
    if value < 0.80:
        return "strong"
    return "extreme"


def generate_visual_prompt(state: Dict, date_str: str) -> str:
    axes = state["axes"]
    directedness = axes["directedness"]
    drift = axes["drift"]
    public = axes["public"]
    private = axes["private"]
    self_score = axes["self"]
    others = axes["others"]
    vitality = axes["vitality"]
    gloom = axes["gloom"]
    ai_mediation = axes["ai_mediation"]

    eye_parts = []
    if directedness > 0.4:
        eye_parts.append("eyes with steadier focus and intention")
    if drift > 0.4:
        eye_parts.append("a subtly wandering or glazed gaze")
    if gloom > 0.4:
        eye_parts.append("shadows beneath the eyes")
    if vitality > 0.4:
        eye_parts.append("a slight brightness returning to the eyes")

    skin_parts = []
    if gloom > 0.4:
        skin_parts.append("skin with pallor and fatigue")
    if vitality > 0.4:
        skin_parts.append("warmer, clearer complexion")
    if ai_mediation > 0.35:
        skin_parts.append("a faintly over-smoothed synthetic quality")
    if self_score > 0.4:
        skin_parts.append("tension around the jaw and temples")

    posture_parts = []
    if directedness > 0.35:
        posture_parts.append("posture more upright and purposeful")
    if private > 0.35:
        posture_parts.append("body language turning inward")
    if others > 0.35:
        posture_parts.append("expression more open to relation")
    if gloom > 0.5:
        posture_parts.append("shoulders slightly burdened")

    lighting_parts = []
    if public > 0.35:
        lighting_parts.append("more daylight and world-presence in the background")
    if private > 0.35:
        lighting_parts.append("a more enclosed interior atmosphere")
    if vitality > 0.35:
        lighting_parts.append("warmer natural light")
    if gloom > 0.35:
        lighting_parts.append("cooler dimmer shadows")

    texture_parts = []
    if directedness > 0.35:
        texture_parts.append("more coherent painterly handling")
    if drift > 0.35:
        texture_parts.append("slightly diffused brushwork")
    if ai_mediation > 0.35:
        texture_parts.append("subtle algorithmic smoothness in the surface")

    return "\n".join(
        [
            f"Portrait transformation for {date_str}.",
            "Edit the original portrait while preserving the subject's identity and basic pose.",
            f"Overall deterioration: {_intensity(state['visual_intensity'].get('deterioration', 0.0))}.",
            f"Overall restoration: {_intensity(state['visual_intensity'].get('restoration', 0.0))}.",
            f"Face and skin: {', '.join(skin_parts) or 'natural, even-toned skin'}.",
            f"Eyes and gaze: {', '.join(eye_parts) or 'neutral, unmarked gaze'}.",
            f"Posture: {', '.join(posture_parts) or 'balanced natural posture'}.",
            f"Lighting and environment: {', '.join(lighting_parts) or 'neutral balanced light'}.",
            f"Painterly surface: {', '.join(texture_parts) or 'natural painterly texture'}.",
            "Do not include browser windows, screens, logos, text, icons, devices, or literal web imagery.",
            "Express the condition only through body, gaze, light, space, and painterly treatment.",
        ]
    )

