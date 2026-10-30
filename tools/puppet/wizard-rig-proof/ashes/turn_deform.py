"""Ashes head-turn / nod deformation field v2 — TURNFIX 2026-10-29.

Shared by build_turnfix.py (bakes keyforms into the .inp) and the
report. render_turnfix.py renders the baked .inp, so the proof IS the
rig data.

Construction (standard Live2D / pro-rig head-turn, cf. the Smiling
Friends house-style kits and image2live2d's own _head_turn_warp —
but applied per-vertex to the part meshes, which the nijilive
backend never did):

  ONE master yaw displacement D(x) for the whole head, from a
  parabolic dome profile (finite edge slope, no flipped triangles):
      Z(u) = 0.92 * R * (1 - (u/R)^2),  u = x - CX
      D(x) = u*(cos t - 1) + Z(u) * sin t        (t = yaw angle)
  Surface features (eyes, grill) follow D at their own vertices,
  blended 20% toward D at their centroid (the library's rigidity
  rule: features stay readable, never fold). The turn reads because
  features sit where Z is large (they translate up to ~R*sin t)
  while the outline edges (Z ~ 0) only foreshorten — features shift
  INSIDE the hood opening, turn-side cheek compresses, far cheek
  opens. Hood rim rides D at 0.92 weight, hood outer at 0.78 (the
  shell lags slightly), so shared borders never separate by more
  than a few px. Braids move per-row (constant across their width,
  so no tearing): roots take D at the root, tips swing — near braid
  swings out, far braid tucks (narrowed toward its root line) and
  shortens, per the owner's acceptance wording. Chain and neck
  follow through at partial weight.

  Pitch (nod) rotates about the horizontal axis through the NECK
  pivot (author.py's NECK_DROP rule) with near-uniform depth (the
  author's pitch rule: uniform depth keeps eye->mouth spacing):
      dy = (y - py)*(cos p - 1) + Zp * sin p
  with Zp = R for face+features, 0.9R rim, 0.85R hood; braids swing
  down/forward at their tips; hood hem pinned to the shoulders.

All coordinates are layer pixels (400x864 canvas, y down).
"""
import math

CX = 192.0          # face centre x (face alpha bbox 111..273)
R = 81.0            # face dome radius (face half-width)
FACE_TOP = 87.0
FACE_BOT = 233.0
PIVOT_Y = FACE_BOT + 0.35 * (FACE_BOT - FACE_TOP)   # neck pivot ~284

YAW_MAX = 0.60      # radians at ParamAngleX = +/-30
PITCH_MAX = 0.55    # radians at ParamAngleY = -/+30

BRAIDS = {          # node-name -> (centre_x, root_y, tip_y)
    "06_hair_side": (128.0, 162.0, 449.0),
    "07_hair_side": (252.0, 157.0, 404.0),
}
FEATURES = ("10_eye_l", "11_eye_r", "12_mouth",
            "13_eye_closed_l", "14_eye_closed_r")
FEATURE_CX = {"10_eye_l": 144.0, "11_eye_r": 234.5, "12_mouth": 189.0,
              "13_eye_closed_l": 150.0, "14_eye_closed_r": 223.5}


def _Z(x):
    u = x - CX
    if abs(u) >= R:
        return 0.0
    return 0.92 * R * (1.0 - (u / R) ** 2)


def _D(x, th):
    """Master yaw displacement at canvas x for yaw angle th."""
    c, s = math.cos(th), math.sin(th)
    return (x - CX) * (c - 1.0) + _Z(x) * s


def _fade(y, y0, y1, lo=0.0):
    if y <= y0:
        return 1.0
    if y >= y1:
        return lo
    t = (y - y0) / (y1 - y0)
    return lo + (1.0 - lo) * (1.0 - t * t * (3.0 - 2.0 * t))


def _shell_w(x):
    """Shared hood/rim weight: 0.97 at the face opening -> 0.80 at the
    hood's outer edge. hair_back and hair_front use the SAME weight at
    the SAME x, so the two shell layers can never separate."""
    a = abs(x - CX)
    if a <= R - 10.0:
        return 0.97
    if a >= R + 25.0:
        return 0.80
    t = (a - (R - 10.0)) / 35.0
    return 0.97 + (0.80 - 0.97) * (t * t * (3.0 - 2.0 * t))


def _island(name, x):
    """Detached flame-lick islands inside the braid parts (measured
    from the part textures' alpha components: braid L island
    x 80-100, braid R island x 277-299 — hood accents that were cut
    into the braid parts; they must ride with the SHELL, not the
    braid, or they detach at any turn)."""
    return (name == "06_hair_side" and x <= 105.0) or \
           (name == "07_hair_side" and x >= 272.0)


def field(name, x, y, s_yaw, s_pitch):
    """Displacement (dx, dy) in layer px for a vertex of part `name`
    at (x, y). s_yaw = ParamAngleX/30 (+ = turn toward screen-right),
    s_pitch = -ParamAngleY/30 (+ = nod down)."""
    if name.startswith("03_face"):
        name = "03_face_base"   # underplate deforms with the face plate
    dx = dy = 0.0

    # ---------- YAW ----------
    if s_yaw != 0.0:
        th = s_yaw * YAW_MAX
        if name in FEATURES:
            cx_f = FEATURE_CX[name]
            dx += 0.8 * _D(x, th) + 0.2 * _D(cx_f, th)
        elif name == "03_face_base":
            dx += _D(x, th) * _fade(y, FACE_BOT, PIVOT_Y, lo=0.55)
        elif name == "02_hair_back":      # hood outer (shared shell weight)
            dx += _shell_w(x) * _D(x, th) * _fade(y, 240.0, 283.0, lo=0.0)
        elif name == "08_hair_front":     # hood rim (same shell weight)
            dx += _shell_w(x) * _D(x, th) * _fade(y, 235.0, 249.0, lo=0.7)
        elif name in BRAIDS and _island(name, x):
            dx += _shell_w(x) * _D(x, th) * _fade(y, 235.0, 249.0, lo=0.7)
        elif name in BRAIDS:
            bcx, root, tip = BRAIDS[name]
            side = 1.0 if bcx > CX else -1.0
            t = max(0.0, min(1.0, (y - root) / (tip - root)))
            turn_side = (s_yaw > 0 and side > 0) or (s_yaw < 0 and side < 0)
            if turn_side:   # near braid: root tracks the jaw anchor, tips swing out
                root_dx = _D(CX + side * 33.0, th)
                tip_dx = root_dx + s_yaw * 24.0
                dx += root_dx * (1.0 - t) + tip_dx * t
            else:           # far braid: root tracks its side's face EDGE, tuck + shorten
                root_dx = _D(CX + side * 74.5, th)
                tip_dx = root_dx * 0.85
                dx += (root_dx * (1.0 - t) + tip_dx * t
                       - (x - bcx) * 0.5 * abs(s_yaw))
                dy += -9.0 * abs(s_yaw) * t
        elif name.startswith("09_accessory"):
            dx += 0.45 * _D(x, th)
        elif name == "01_neck":
            dx += 0.3 * _D(x, th) * _fade(y, 230.0, 253.0, lo=0.0)
        # torso / arms: no yaw

    # ---------- PITCH (nod) ----------
    if s_pitch != 0.0:
        ph = s_pitch * PITCH_MAX
        c, s = math.cos(ph), math.sin(ph)
        dyv = y - PIVOT_Y
        if name in FEATURES or name == "03_face_base":
            d = dyv * (c - 1.0) + R * s
            if name == "03_face_base":
                d *= _fade(y, FACE_BOT, PIVOT_Y, lo=0.6) if y > FACE_BOT else 1.0
            dy += d
        elif name in ("02_hair_back", "08_hair_front"):
            zp = R * (0.88 + 0.12 * ((_shell_w(x) - 0.80) / 0.17))
            pin = _fade(y, 240.0, 283.0, lo=0.0) if name == "02_hair_back" \
                else _fade(y, 235.0, 249.0, lo=0.7)
            dy += (dyv * (c - 1.0) + zp * s) * pin
        elif name in BRAIDS and _island(name, x):
            zp = R * (0.88 + 0.12 * ((_shell_w(x) - 0.80) / 0.17))
            dy += (dyv * (c - 1.0) + zp * s) * _fade(y, 235.0, 249.0, lo=0.7)
        elif name in BRAIDS:
            bcx, root, tip = BRAIDS[name]
            t = max(0.0, min(1.0, (y - root) / (tip - root)))
            base = dyv * (c - 1.0) + 0.9 * R * s
            dy += base * (1.0 - t) + (base + s * 52.0) * t
            if x != CX:
                dx += -math.copysign(1.0, x - CX) * 6.0 * abs(s_pitch) * t
        elif name.startswith("09_accessory"):
            hang = max(0.0, min(1.0, (y - 222.0) / 122.0))
            dy += dyv * (c - 1.0) + 0.5 * R * s + s * 20.0 * hang
        elif name == "01_neck":
            dy += (dyv * (c - 1.0) + 0.3 * R * s) * _fade(y, 230.0, 253.0, lo=0.0)
    return dx, dy
