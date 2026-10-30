"""Ashes head-turn / nod deformation field v4 — TURNFIX v2, global field.

WHY v4 REPLACES THE PART-SPECIFIC FIELDS (v2 parabolic, v3 cosine):
the part separation smeared several visual objects across layers.
Measured from the .inp textures: the BRAID visual is a stack of
fragments from the braid parts (5,505 + 2,798 alpha px) PLUS braid
pixels painted into the torso (1,017/1,843 gold px in the braid
columns), both arm parts (981 px each) and both accessory parts
(468/1,336 px). The braid parts ALONE render as disconnected
fragments (leaf cluster / strand / tassel with gaps) even at rest —
the composite only looks whole because the fragments coincide.
ANY part-specific field moves the layers' copies of the same pixels
by different amounts and the stack separates into the red/gold
fragment mess seen in the v1 and v2 zoom sheets. No braid-local
field can fix that; it is a registration problem, not a braid
problem. (Same story for the chain: two accessory parts with
byte-identical textures + braid/chain pixels in the torso layer.)

v4: ONE GLOBAL FIELD OF POSITION. dx and dy are functions of the
vertex's canvas position (x, y) only — identical for every part —
so every layer's copy of a pixel moves by the same amount and the
whole stack stays registered at any angle. The only exceptions are
the facial features (eyes/grill ride slightly rigid over the face
plate — they overlap only the uniform void face, so a few px of
slide there reads as feature motion, not tearing) and a braid-tip
pitch extra in the nod (braid parts only; the torso's sparse braid
pixels there are the accepted minor cost — v1's nod, which used
part fields throughout, already read clean).

Yaw:  dx = W(y) * D(x)   — cosine-dome D (zero edge slope: no folds,
      measured 0 flipped triangles), W = 1.0 down to y=280 fading to
      0 at y=580 so the chest follows the head and the robe settles.
Pitch: dy = P(y) * [(y-PIVOT)*(cos-1) + Zp(x)*sin] — rotation about
      the neck pivot with dome depth Zp(x); P = 1.0 to y=300 fading
      to 0 at y=580.
"""
import math

CX = 192.0
R = 81.0
ZMAX = 0.82 * R
FACE_BOT = 233.0
PIVOT_Y = FACE_BOT + 0.35 * (233.0 - 87.0)   # ~284

YAW_MAX = 0.52
PITCH_MAX = 0.55

FEATURES = ("10_eye_l", "11_eye_r", "12_mouth",
            "13_eye_closed_l", "14_eye_closed_r")
FEATURE_CX = {"10_eye_l": 144.0, "11_eye_r": 234.5, "12_mouth": 189.0,
              "13_eye_closed_l": 150.0, "14_eye_closed_r": 223.5}
BRAIDS = ("06_hair_side", "07_hair_side")


def _Z(x):
    u = x - CX
    if abs(u) >= R:
        return 0.0
    return ZMAX * 0.5 * (1.0 + math.cos(math.pi * u / R))


def _D(x, th):
    return (x - CX) * (math.cos(th) - 1.0) + _Z(x) * math.sin(th)


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _W(y):
    """Yaw follow weight by height: head/braids/chain 1.0, robe -> 0."""
    return 1.0 - _smooth((y - 280.0) / 300.0)


def _P(y):
    """Pitch follow weight by height."""
    return 1.0 - _smooth((y - 300.0) / 280.0)


def field(name, x, y, s_yaw, s_pitch):
    dx = dy = 0.0
    if s_yaw != 0.0:
        th = s_yaw * YAW_MAX
        if name in FEATURES:
            dx += _W(y) * (0.75 * _D(x, th) + 0.25 * _D(FEATURE_CX[name], th))
        else:
            dx += _W(y) * _D(x, th)
    if s_pitch != 0.0:
        ph = s_pitch * PITCH_MAX
        c, s = math.cos(ph), math.sin(ph)
        zp = R * (0.85 + 0.15 * (_Z(x) / ZMAX))
        dy += _P(y) * ((y - PIVOT_Y) * (c - 1.0) + zp * s)
        if name in BRAIDS:
            # braid tips swing forward/down past the global rotation
            dy += s * 48.0 * _smooth((y - 280.0) / 170.0) * _P(y)
    return dx, dy
