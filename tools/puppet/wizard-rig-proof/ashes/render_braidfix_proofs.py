#!/usr/bin/env python3
"""Braidfix proof driver — Ashes standard rig v2, repo copy.

Identical to the driver that produced the 2026-10-29 repair proofs, with
paths pointed at the repo layout (rig_layers/ in this folder). Renders the
48-pose turn+nod sequence to frames_braidfix/ and dumps the parameter
table to rig_parameters_braidfix.json.

Same render path the first-use lane proved (image2live2d preview.render_pose
over rig_from_layer_dir + prepare_meshes, with the repo's own two preview
monkeypatches), pointed at the v2 layer stack. Choreography is the owner's
required demonstration, on 2s at 24 fps:
  settle -> head turn + nod (hood rim counter-moves on HairFront, braids lag
  and overshoot on HairSide, jaw plate carries the face, BodyAngle held at 0
  so the bust/shoulders provably do not move) -> return with braid swing-
  through -> blink + grill speech burst -> settle.
"""
import json
import math
import os
import sys

import image2live2d.pipeline as P
import image2live2d.preview as PV


def _safe_synth_no_cavity(stack) -> None:
    from image2live2d.core.synth import synthesize_closed_eyes
    try:
        synthesize_closed_eyes(stack)   # keep closed-eye synth (real blink)
    except (ImportError, OSError):
        pass


P._safe_synth = _safe_synth_no_cavity

# same mesh density as the shipped build (build_rig.py): 28x28 — the 14x14
# default leaves a 130 px coverage hole in the grill
_orig_build_meshes = P.mesh.build_meshes
P.mesh.build_meshes = lambda stack: _orig_build_meshes(stack, grid=28)


def _offsets_fixed(params, settings):
    # verbatim from the repo's render_poses.py: skip params AT THEIR DEFAULT
    # (the stock preview skips at 0.0, which silently drops a blink whose
    # rest is 1.0; applying _interp at the default value is NOT identity
    # for the mouth in this pipeline and notches the grill)
    from image2live2d.preview import _interp
    acc = {}
    for p in params:
        v = settings.get(p.id, p.default)
        if v == p.default:
            continue
        for pid, arr in _interp(p, v).items():
            acc[pid] = acc.get(pid, 0) + arr
    return acc


def _grouped_fixed(params, settings, head_ids, body_ids):
    from image2live2d.preview import _interp, _HEAD_TURN, _BODY_TURN
    acc = {}
    for p in params:
        v = settings.get(p.id, p.default)
        if v == p.default:
            continue
        skip = head_ids if p.id in _HEAD_TURN else (body_ids if p.id in _BODY_TURN else set())
        for pid, arr in _interp(p, v).items():
            if pid in skip:
                continue
            acc[pid] = acc.get(pid, 0) + arr
    return acc


PV._offsets = _offsets_fixed
PV._grouped_offsets = _grouped_fixed

from image2live2d import rig_from_layer_dir
from image2live2d.core.decompose import from_layer_dir
from image2live2d.pipeline import prepare_meshes
from image2live2d.preview import render_pose
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LAYERS = os.path.join(HERE, "rig_layers")
FRAMES = os.path.join(HERE, "frames_braidfix")
os.makedirs(FRAMES, exist_ok=True)

print("building rig from v2 layers ...", flush=True)
stack = from_layer_dir(LAYERS)
meshes = prepare_meshes(stack)
rig = rig_from_layer_dir(LAYERS, name="Ashes")
params = rig.parameters
RANGES = {p.id: (p.min, p.max, p.default) for p in params}
print(f"rig built: {len(rig.parts)} parts, {len(params)} parameters", flush=True)
for p in rig.parts:
    print("  part:", getattr(p, "id", "?"), "| role:", p.semantic_role, flush=True)
with open(os.path.join(HERE, "rig_parameters_braidfix.json"), "w") as f:
    json.dump([{"id": p.id, "min": p.min, "max": p.max, "default": p.default,
                "keyforms": len(p.keyforms)} for p in params], f, indent=2)


def clamp(pid, v):
    if pid not in RANGES:
        return v
    lo, hi, _ = RANGES[pid]
    return max(lo, min(hi, v))


def track(keys):
    keys = sorted(keys)

    def at(s):
        if s <= keys[0][0]:
            return keys[0][1]
        if s >= keys[-1][0]:
            return keys[-1][1]
        for (s0, v0), (s1, v1) in zip(keys, keys[1:]):
            if s0 <= s <= s1:
                t = (s - s0) / (s1 - s0)
                e = 0.5 - 0.5 * math.cos(math.pi * t)
                return v0 + (v1 - v0) * e
        return keys[-1][1]

    return at


STEPS = 48  # 48 unique poses on 2s = 4.0 s at 24 fps

angle_x = track([(0, 0), (5, 0), (15, 27), (21, 27), (31, 2), (47, 2)])
angle_y = track([(0, 0), (9, 0), (14, -13), (19, -13), (24, -2), (47, -2)])  # nod inside the turn
angle_z = track([(0, 0), (15, 3.0), (31, 1.0), (47, 1.0)])
# braid pendulum: follows the head turn delayed ~3 steps, overshoots on return
hair_side = track([(0, 0), (8, 0), (18, -0.85), (24, -0.55), (30, 0.35), (36, -0.12), (47, 0.0)])
hair_front = track([(0, 0), (5, 0), (15, 0.4), (21, 0.4), (31, 0.05), (47, 0.05)])  # rim counter-move
hair_back = track([(0, 0), (5, 0), (15, -0.3), (21, -0.3), (31, -0.04), (47, -0.04)])
mouth = track([(0, 0), (35, 0), (37, 0.9), (38, 0.3), (39, 0.95), (40, 0.2), (42, 0)])
mouth_form = track([(0, 0), (37, 0.4), (42, 0.4), (47, 0.15)])
eye_open = track([(0, 1), (32, 1), (33, 0), (34, 1), (47, 1)])
eye_smile = track([(0, 0), (40, 0), (45, 0.55), (47, 0.55)])
acc = track([(0, 0), (15, 0.3), (21, 0.25), (31, -0.05), (47, -0.05)])

BG = (30, 30, 36, 255)
frames = []
for s in range(STEPS):
    settings = {
        "ParamAngleX": clamp("ParamAngleX", angle_x(s)),
        "ParamAngleY": clamp("ParamAngleY", angle_y(s)),
        "ParamAngleZ": clamp("ParamAngleZ", angle_z(s)),
        "ParamBodyAngleX": 0.0,   # held: the bust must not move (verified below)
        "ParamBodyAngleY": 0.0,
        "ParamBodyAngleZ": 0.0,
        "ParamMouthOpenY": clamp("ParamMouthOpenY", mouth(s)),
        "ParamMouthForm": clamp("ParamMouthForm", mouth_form(s)),
        "ParamEyeLOpen": clamp("ParamEyeLOpen", eye_open(s)),
        "ParamEyeROpen": clamp("ParamEyeROpen", eye_open(s)),
        "ParamEyeLSmile": clamp("ParamEyeLSmile", eye_smile(s)),
        "ParamEyeRSmile": clamp("ParamEyeRSmile", eye_smile(s)),
        "ParamAcc0": clamp("ParamAcc0", acc(s)),
        "ParamBreath": 0.5 - 0.5 * math.cos(2 * math.pi * 2 * s / STEPS),
        "ParamHairFront": clamp("ParamHairFront", hair_front(s)),
        "ParamHairBack": clamp("ParamHairBack", hair_back(s)),
        "ParamHairSideV": clamp("ParamHairSideV", 0.25 * math.sin(2 * math.pi * s / STEPS)),
        "ParamHairFrontV": clamp("ParamHairFrontV", 0.15 * math.sin(2 * math.pi * s / STEPS)),
        "ParamHairBackV": clamp("ParamHairBackV", 0.15 * math.sin(2 * math.pi * s / STEPS + 1.0)),
    }
    # drive EVERY strand/accessory parameter the rig actually has (the
    # strand split differs between builds — enumerate, don't hardcode)
    hv = hair_side(s)
    for prefix, base, lagstep in (("ParamHairSide", hv, 0.07),
                                  ("ParamHairFront", hair_front(s), 0.10),
                                  ("ParamHairBack", hair_back(s), 0.08)):
        pids = sorted(p for p in RANGES if p.startswith(prefix) and not p.endswith("V"))
        for i, pid in enumerate(pids):
            settings[pid] = clamp(pid, base * (1.0 - lagstep * i))
    for pid in sorted(p for p in RANGES if p.startswith("ParamAcc")):
        settings[pid] = clamp(pid, acc(s))

    img = render_pose(stack, meshes, params, settings, res=864)
    if img.mode == "RGBA":
        canvas = Image.new("RGBA", img.size, BG)
        img = Image.alpha_composite(canvas, img).convert("RGB")
    img.save(os.path.join(FRAMES, f"pose_{s:03d}.png"))
    frames.append(np.asarray(img).astype(int))
    print(f"pose {s:02d}/{STEPS-1} ax={settings['ParamAngleX']:.1f} ay={settings['ParamAngleY']:.1f} "
          f"hair={hv:.2f} mouth={settings['ParamMouthOpenY']:.2f} eye={settings['ParamEyeLOpen']:.1f}", flush=True)

# shoulder-stability evidence: pixel diff in the bust band (below the hood
# hem, outside the braid/chain swing zone) between neutral and max turn
f0, f1 = frames[0], frames[18]
band = np.zeros(f0.shape[:2], bool)
band[560:840, 60:300] = True
band[560:840, 560:800] = True
d = np.abs(f0 - f1).max(axis=2)
print(f"BUST-BAND diff neutral vs max-turn: mean={d[band].mean():.2f} px>12: {int((d[band] > 12).sum())} of {int(band.sum())}")
# braid-zone motion evidence: diff in the braid columns between turn frames
bz = np.zeros(f0.shape[:2], bool)
bz[250:700, 150:420] = True
bz[250:700, 480:720] = True
d2 = np.abs(frames[18] - frames[33]).max(axis=2)
print(f"BRAID-ZONE diff turn vs swing-through: px>12: {int((d2[bz] > 12).sum())} of {int(bz.sum())}")
print("all poses rendered")
