"""The visual vocabulary: eleven channels, and the small moves each pole can make.

Each day the image is edited from yesterday's JPEG, so every move is phrased as an
INCREMENT ("a little more ..."), not as a description of a final state. Repeated
moves compound. Positive poles push back the other way, so redemption is possible
but has to be earned, edit by edit.

Most of the language here comes from the Project Dorian Gray planning chats
(Mondrian geometry, the fishbowl lens, the Kubrick gaze, Renaissance perspective,
reflections rather than ghosts, electric colour vs. grayscale, burned-out,
cyborg AI mediation, ageing / youthening).
"""

CHANNELS = [
    "composition", "background", "lighting", "posture", "gaze", "mouth",
    "skin", "handling", "depth", "world_traces", "interpersonal_traces",
]

# (move_id, channel, phrase). "{adv}" is replaced by an intensity adverb.
POLE_MOVES = {
    "directedness": [
        ("dir_grid", "composition", "{adv} strengthen the hidden geometry of the picture, pulling verticals and horizontals into a firmer, Mondrian-like grid of flat planes behind the figure"),
        ("dir_posture", "posture", "{adv} straighten the spine and square the shoulders toward the viewer"),
        ("dir_gaze", "gaze", "{adv} sharpen and steady the gaze, the eyes wider and fixed"),
        ("dir_mouth", "mouth", "{adv} firm the mouth into a straighter, closed, slightly tensed line"),
        ("dir_edges", "handling", "{adv} harden the contours, making edges crisper and transitions more abrupt"),
        ("dir_fishbowl", "depth", "{adv} bow the space outward as if seen through a wide-angle lens, the room curving tightly around the figure"),
    ],
    "drift": [
        ("dri_edges", "handling", "{adv} loosen the edges, letting forms break into soft, impressionistic dabs"),
        ("dri_posture", "posture", "{adv} let the posture sag, shoulders rounding into a stoop, clothes hanging baggier"),
        ("dri_gaze", "gaze", "{adv} unfix the gaze: heavier lids, attention sliding off to one side"),
        ("dri_mouth", "mouth", "{adv} let the lips part and slacken"),
        ("dri_background", "background", "{adv} dissolve the background into a vague, hazy wash"),
        ("dri_smear", "depth", "{adv} smear a band of the image sideways, like a frame caught mid-scroll"),
        ("dri_body", "skin", "{adv} soften and thicken the face and neck, as with slack weight gain"),
    ],
    "public": [
        ("pub_open", "background", "{adv} open the space behind the figure toward open air, with more of the world visible"),
        ("pub_light", "lighting", "{adv} raise the light toward even, outdoor daylight"),
        ("pub_gaze", "gaze", "{adv} turn the face to address the viewer directly, as if about to speak"),
        ("pub_world", "world_traces", "{adv} let traces of the outside world enter the margins: weather, a horizon, the edge of a street"),
        ("pub_posture", "posture", "{adv} turn the body more frontally, as if on show"),
    ],
    "private": [
        ("pri_room", "background", "{adv} close the room in around the figure: nearer walls, less space, no view out"),
        ("pri_light", "lighting", "{adv} lower the light into a dim, low-key interior with deeper shadow"),
        ("pri_gaze", "gaze", "{adv} lower the gaze and turn it inward, away from the viewer"),
        ("pri_posture", "posture", "{adv} draw the arms and shoulders in, the body more closed and guarded"),
        ("pri_world", "world_traces", "{adv} erase traces of the outside world; the room's surfaces grow blank and sealed"),
    ],
    "self": [
        ("self_perspective", "composition", "{adv} centre the figure and tilt the lines of the room so they converge on the head, like Renaissance perspective"),
        ("self_pout", "mouth", "{adv} push the expression toward a self-regarding, selfie-like pout, chin lifted"),
        ("self_gaze", "gaze", "{adv} make the gaze self-appraising, as if checking its own reflection"),
        ("self_retouch", "skin", "{adv} smooth and flatter the face, as if retouched for display"),
        ("self_spot", "lighting", "{adv} put a flattering spotlight on the face while the rest of the image dims"),
    ],
    "others": [
        ("oth_reflection", "interpersonal_traces", "{adv} let a faint reflection of another person appear in a pane of glass behind the figure (a reflection, never a ghost or shadow)"),
        ("oth_gaze", "gaze", "{adv} angle the gaze toward someone just beside the viewer, warm and reciprocal"),
        ("oth_posture", "posture", "{adv} turn the body slightly toward another person, open and receptive"),
        ("oth_light", "lighting", "{adv} warm the light, as if the room were shared"),
        ("oth_mouth", "mouth", "{adv} soften the mouth toward listening, on the verge of reply"),
    ],
    "vitality": [
        ("vit_colour", "lighting", "{adv} charge the colours toward electric, saturated hues moving between figure and ground"),
        ("vit_skin", "skin", "{adv} bring blood back into the face: warmer, fuller skin, colour in the lips, hair darker and thicker, as if younger"),
        ("vit_eyes", "gaze", "{adv} brighten the eyes with stronger catchlights"),
        ("vit_marks", "handling", "{adv} make the mark-making livelier and more energetic"),
        ("vit_lift", "posture", "{adv} lift the body: more alert, more buoyant"),
    ],
    "gloom": [
        ("glo_grey", "lighting", "{adv} drain colour toward grey and darken the whole image"),
        ("glo_age", "skin", "{adv} age the face: greyer, thinner hair, mottled skin, heavier bags under the eyes"),
        ("glo_eyes", "gaze", "{adv} let the gaze drop and dull"),
        ("glo_bow", "posture", "{adv} let the head and shoulders bow, as under weight"),
        ("glo_murk", "background", "{adv} let the background sink into murk"),
    ],
    "ai_mediation": [
        ("ai_plastic", "skin", "{adv} make the skin smoother, more plastic and too regular, like a synthetic render"),
        ("ai_eyes", "gaze", "{adv} make the eyes more symmetrical and glassy, with a faint mechanical glint"),
        ("ai_halogen", "lighting", "{adv} shift the light toward cold, flat halogen"),
        ("ai_artefacts", "handling", "{adv} introduce digital artefacts: blocky compression, banding, posterised tones"),
        ("ai_symmetry", "composition", "{adv} make the whole composition more mirrored and symmetrical"),
        ("ai_cyborg", "skin", "{adv} let parts of the face or hands turn faintly mechanical: seams, hard surfaces just under the skin"),
    ],
    "direct_engagement": [
        ("dir_eng_skin", "skin", "{adv} roughen the skin toward human irregularity: pores, flushes, uneven texture"),
        ("dir_eng_sun", "lighting", "{adv} let real sunlight fall across part of the figure"),
        ("dir_eng_hand", "handling", "{adv} add handmade irregularity to the surface: visible, uneven marks"),
        ("dir_eng_world", "world_traces", "{adv} let tactile textures of the world (paper, cloth, wood grain) surface near the edges"),
    ],
}

# Moves that need the long-run "weather" of a pole to be high before they unlock.
WEATHER_GATES = {"ai_cyborg": ("ai_mediation", 0.35), "dri_body": ("drift", 0.45), "glo_age": ("gloom", 0.25)}

# Fired when BOTH poles are high on the same day. (pole_a, pole_b, move_id, channel, phrase)
COMBO_MOVES = [
    ("public", "private", "combo_kubrick", "gaze",
     "{adv} turn the gaze into a sidelong, upward glower at the viewer, confrontational but closed, with one hard light catching half the face and the rest in shadow"),
    ("directedness", "drift", "combo_focus", "depth",
     "{adv} narrow the focus so one part of the face is sharp while the rest slips out of focus"),
    ("vitality", "gloom", "combo_burnout", "lighting",
     "{adv} push toward a burned-out, feverish look: hot, overexposed colour around dull, tired eyes"),
    ("self", "public", "combo_display", "composition",
     "{adv} pose the figure more frontally for display, as if for a camera held at arm's length"),
    ("ai_mediation", "gloom", "combo_failed_render", "skin",
     "{adv} turn the skin grey and waxy, like a failed render"),
    ("others", "public", "combo_passers", "interpersonal_traces",
     "{adv} let reflections of passers-by appear faintly in glass behind the figure"),
]

# Small, local traces left by behavioural patterns. (channel, phrase)
MODIFIER_TRACES = {
    "checking_loop": ("handling", "{adv} double a few contours, as if the face had been redrawn twice in quick succession"),
    "feed_surrender": ("depth", "{adv} repeat a thin horizontal strip of the image, like a stuttering feed"),
    "doomscroll_vigilance": ("gaze", "{adv} widen the eyes into a strained, vigilant stare"),
    "late_night_spiral": ("lighting", "{adv} cast a cold blue glow up onto the face from below, as at night"),
    "comparative_evaluation": ("composition", "{adv} split the background into two nearly identical panels"),
    "administrative_burden": ("posture", "{adv} weigh the shoulders down, as under a pile of small obligations"),
    "creative_absorption": ("handling", "{adv} concentrate the surface's intensity around the hands"),
    "research_chain": ("gaze", "{adv} give the eyes a sharp, searching focus"),
    "social_exposure": ("lighting", "{adv} add a flat frontal flash, as if just photographed"),
    "social_connection": ("mouth", "{adv} lift the corners of the mouth toward warmth"),
    "health_anxiety": ("skin", "{adv} let the skin show a faint anxious flush and tightness"),
    "sensual_escape": ("skin", "{adv} flush the cheeks and soften the eyelids"),
    "ai_delegation": ("handling", "{adv} let small areas resolve into overly smooth, generated detail"),
    "direct_source_immersion": ("skin", "{adv} sharpen real-world texture: fabric weave, skin grain"),
    "task_pressure": ("mouth", "{adv} tighten the jaw"),
}

ADVERBS = [(0.30, "very slightly"), (0.50, "slightly"), (0.70, "noticeably"), (9.99, "markedly")]


def adverb(strength: float) -> str:
    for limit, word in ADVERBS:
        if strength < limit:
            return word
    return ADVERBS[-1][1]
