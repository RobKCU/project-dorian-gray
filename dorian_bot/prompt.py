"""Generate image-edit prompts from cumulative portrait state."""

from typing import Dict, List, Tuple


ELEVATED = 0.35
MODERATE = 0.50
STRONG = 0.65


def _level(value: float) -> str:
    if value < ELEVATED:
        return "faint"
    if value < MODERATE:
        return "elevated"
    if value < STRONG:
        return "moderate"
    return "strong"


def _join(parts: List[str], fallback: str) -> str:
    return ", ".join(parts) if parts else fallback


def _negative_convergence(axes: Dict[str, float], days_processed: int) -> Tuple[int, List[str], List[str]]:
    """Return cumulative darker effects when several non-AI negative drivers converge."""
    drift = axes["drift"]
    private = axes["private"]
    self_score = axes["self"]
    gloom = axes["gloom"]
    vitality = axes["vitality"]

    drivers = []
    if drift >= ELEVATED:
        drivers.append(("drift", drift))
    if private >= ELEVATED:
        drivers.append(("private", private))
    if self_score >= ELEVATED:
        drivers.append(("self", self_score))
    if gloom >= ELEVATED:
        drivers.append(("gloom", gloom))

    # Vitality starts at zero in the state model, so treat low vitality as a
    # convergence driver only after the portrait has had time to accumulate.
    if days_processed >= 3 and vitality < 0.30 and drivers:
        drivers.append(("low vitality", 0.50 - vitality))

    if len(drivers) < 2:
        return len(drivers), [name for name, _ in drivers], []

    driver_names = [name for name, _ in drivers]
    effects = []

    if len(drivers) == 2:
        effects.append("allow subtle cumulative deterioration, but do not make it generic")
    else:
        effects.append("allow stronger cumulative Dorian Gray effects while preserving identity")

    effects.append("aging, misery, emaciation, frazzledness, or bodily thinning may appear only through this convergence")

    if "self" in driver_names:
        effects.append("self-interest may harden into coldness, cruelty, or stinginess")
    if "drift" in driver_names:
        effects.append("drift may become scattered or frazzled rather than merely soft")
    if "gloom" in driver_names:
        effects.append("gloom may become visibly depressive and miserable")
    if "private" in driver_names:
        effects.append("private inwardness may become sealed-off withdrawal")
    if "low vitality" in driver_names:
        effects.append("low vitality may reduce fullness, warmth, and bodily substance")

    return len(drivers), driver_names, effects


def _gaze_descriptors(axes: Dict[str, float]) -> List[str]:
    directedness = axes["directedness"]
    drift = axes["drift"]
    public = axes["public"]
    private = axes["private"]
    gloom = axes["gloom"]
    vitality = axes["vitality"]

    parts = []

    if directedness >= ELEVATED and drift >= ELEVATED:
        parts.append("gaze divided between purposive focus and wandering, unfixed attention")
    elif directedness >= ELEVATED:
        parts.append("steady, focused gaze with a sense of intention")
    elif drift >= ELEVATED:
        parts.append("wandering, unfixed gaze; not downcast or defeated")

    if public >= ELEVATED and gloom >= ELEVATED:
        parts.append("attention partly meets the viewer but is pulled downward by depressive heaviness")
    elif public >= ELEVATED:
        parts.append("gaze meets the viewer attentively and curiously")
    elif gloom >= ELEVATED:
        parts.append("downcast depressive gaze")

    if private >= ELEVATED and public < ELEVATED:
        parts.append("eyes turned inward rather than outward")

    if vitality >= ELEVATED:
        parts.append("eyes brighter with bodily aliveness")

    return parts


def _expression_descriptors(axes: Dict[str, float]) -> List[str]:
    self_score = axes["self"]
    others = axes["others"]
    gloom = axes["gloom"]

    parts = []

    if self_score >= ELEVATED and others >= ELEVATED:
        parts.append("self-regard softened by compassion, expression conflicted rather than cruel")
    elif self_score >= ELEVATED:
        parts.append("self-interested, faintly smug expression, disinterested in others")

    if others >= ELEVATED:
        parts.append("open expression with compassion and generosity")

    if gloom >= ELEVATED:
        parts.append("quieted depressive affect")

    return parts


def _skin_and_body_descriptors(axes: Dict[str, float]) -> List[str]:
    vitality = axes["vitality"]
    gloom = axes["gloom"]
    ai_mediation = axes["ai_mediation"]
    direct_engagement = axes["direct_engagement"]

    parts = []

    if vitality >= ELEVATED:
        parts.append("warmer skin, fuller flesh, more color in lips and face")
    if gloom >= ELEVATED:
        parts.append("muted color and cooler skin tones without defaulting to illness")
    if ai_mediation >= ELEVATED:
        parts.append("robotic smoothness, uncanny regularity, glossy compressed surface")
    if ai_mediation >= STRONG:
        parts.append("machine-like facial regularity may become visibly stronger")
    if direct_engagement >= ELEVATED:
        parts.append("human, fleshy, irregular, tactile bodily surface")

    return parts


def _posture_descriptors(axes: Dict[str, float]) -> List[str]:
    directedness = axes["directedness"]
    drift = axes["drift"]
    public = axes["public"]
    private = axes["private"]
    others = axes["others"]

    parts = []

    if directedness >= ELEVATED and drift >= ELEVATED:
        parts.append("posture shows purpose fighting instability")
    elif directedness >= ELEVATED:
        parts.append("clearer, more purposive posture")
    elif drift >= ELEVATED:
        parts.append("slightly loosened bodily alignment")

    if public >= ELEVATED and private >= ELEVATED:
        parts.append("exposed but guarded: outward setting with inward bodily reserve")
    elif public >= ELEVATED:
        parts.append("more outward and on display")
    elif private >= ELEVATED:
        parts.append("inward, self-contained posture")

    if others >= ELEVATED:
        parts.append("shoulders and mouth more receptive and generous")

    return parts


def _light_and_space_descriptors(axes: Dict[str, float]) -> List[str]:
    public = axes["public"]
    private = axes["private"]
    vitality = axes["vitality"]
    gloom = axes["gloom"]
    ai_mediation = axes["ai_mediation"]
    direct_engagement = axes["direct_engagement"]

    parts = []

    if public >= ELEVATED and private >= ELEVATED:
        parts.append("outdoors-y world presence complicated by an indoors-y guardedness")
    elif public >= ELEVATED:
        parts.append("outdoors-y atmosphere with more world visible behind the figure")
    elif private >= ELEVATED:
        parts.append("indoors-y enclosure with less world visible")

    if vitality >= ELEVATED:
        parts.append("warmer healthier light")
    if gloom >= ELEVATED:
        parts.append("cooler dimmer light, heavier atmosphere, muted contrast")
    if ai_mediation >= ELEVATED:
        parts.append("halogen-like artificial lighting")
    if direct_engagement >= ELEVATED:
        parts.append("sunlight or natural light as a counterforce to mediation")

    return parts


def _surface_descriptors(axes: Dict[str, float]) -> List[str]:
    directedness = axes["directedness"]
    drift = axes["drift"]
    vitality = axes["vitality"]
    ai_mediation = axes["ai_mediation"]
    direct_engagement = axes["direct_engagement"]

    parts = []

    if directedness >= ELEVATED:
        parts.append("sharper contours and more resolved painterly structure")
    if drift >= ELEVATED:
        parts.append("softened edges and blurred contours")
    if vitality >= ELEVATED:
        parts.append("livelier brushwork")
    if ai_mediation >= ELEVATED:
        parts.append("reduced painterly irregularity, glossy compression, robotic finish")
    if direct_engagement >= ELEVATED:
        parts.append("handmade irregularity, tactile paint, human imperfection")

    return parts


def generate_visual_prompt(state: Dict, date_str: str) -> str:
    axes = state["axes"]
    days_processed = len(state.get("days_processed", []))
    convergence_count, convergence_drivers, convergence_effects = _negative_convergence(
        axes,
        days_processed,
    )

    lines = [
        f"Portrait transformation for {date_str}.",
        "Edit the original portrait while preserving the subject's identity and basic pose.",
        "Use the cumulative axis state below as a visual grammar, not as a generic command to make the subject worse or better.",
        "",
        "AXIS-SPECIFIC GRAPHIC DIRECTIONS:",
        f"Directedness ({_level(axes['directedness'])}): sharper contours, steady gaze, clearer posture, purposiveness.",
        f"Drift ({_level(axes['drift'])}): softened edges, blurred contours, wandering unfixed gaze; not downcast.",
        f"Public ({_level(axes['public'])}): outdoors-y world presence, more visible environment, on-display outwardness, curious viewer-facing gaze.",
        f"Private ({_level(axes['private'])}): indoors-y enclosure, less visible world, inward gaze and posture.",
        f"Self ({_level(axes['self'])}): self-interest, disinterest in others, faint smugness; may harden toward cruelty only in convergence.",
        f"Others ({_level(axes['others'])}): openness, compassion, generosity, receptive warmth.",
        f"Vitality ({_level(axes['vitality'])}): warmth, fuller flesh, livelier brushwork, brighter eyes, color in lips and skin.",
        f"Gloom ({_level(axes['gloom'])}): cooler palette, dimmer light, heavier atmosphere, muted color, downcast depressive gaze.",
        f"AI mediation ({_level(axes['ai_mediation'])}): robotic smoothness, uncanny symmetry, glossy compressed surface, halogen light.",
        f"Direct engagement ({_level(axes['direct_engagement'])}): sunlight, human fleshy irregularity, tactile embodiment, handmade imperfection.",
        "",
        "APPLY TO THE IMAGE:",
        f"Gaze: {_join(_gaze_descriptors(axes), 'neutral, unmarked gaze')}.",
        f"Expression: {_join(_expression_descriptors(axes), 'neutral expression without strong affect')}.",
        f"Skin and body: {_join(_skin_and_body_descriptors(axes), 'natural skin and bodily presence')}.",
        f"Posture: {_join(_posture_descriptors(axes), 'balanced natural posture')}.",
        f"Lighting and space: {_join(_light_and_space_descriptors(axes), 'balanced light and simple space')}.",
        f"Painterly surface: {_join(_surface_descriptors(axes), 'natural painterly handling')}.",
    ]

    if convergence_count >= 2:
        lines.extend(
            [
                "",
                "CUMULATIVE CONVERGENCE:",
                f"Elevated non-AI negative drivers: {', '.join(convergence_drivers)}.",
                "Because two or more of these drivers are elevated, cumulative darker effects may appear.",
                "Apply these effects gradually and specifically: " + "; ".join(convergence_effects) + ".",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "CUMULATIVE CONVERGENCE:",
                "Do not add generic aging, misery, emaciation, horror, illness, or frazzled exhaustion.",
                "Those qualities should appear only when multiple non-AI negative drivers converge over time.",
            ]
        )

    lines.extend(
        [
            "",
            "AVOID:",
            "Do not include browser windows, screens, logos, text, icons, or interface elements.",
            "Do not add props, costumes, wires, devices, or literal web imagery.",
            "Do not default to generic Dorian Gray decay; aging and misery must be earned by cumulative convergence.",
            "Express the condition through body, gaze, light, space, surface, and painterly treatment.",
        ]
    )

    return "\n".join(lines)
