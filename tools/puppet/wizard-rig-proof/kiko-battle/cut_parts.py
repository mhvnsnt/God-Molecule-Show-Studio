#!/usr/bin/env python3
"""Worker C Wave 8 — Kiko BATTLE variant part extraction, step 2.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe, 02_head (hood + void), 03_accessory (chains + KIKO pendant),
  04_arm_l (single raised LEFT arm — zoom-verified; the top-right white is hood),
  05_eyes (white glints, split L/R at assembly)

Method: ROI rectangles x HSV color masks. Occluded areas (robe under the
head/arms/chains) are Telea-inpainted so each layer is self-contained.
Honest constraints: figure cut by the frame's bottom edge (no legs in frame);
arm/shoulder boundaries are spatial cuts in flat white fur (documented, not
faked); KIKO pendant text preserved byte-for-byte (owner keep-or-cut flag);
no mouth art — pipeline no-mouth path.
Canon: white fur + KIKO pendant; black-void face + white glints; no design
alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/kiko-battle"
PARTS = os.path.join(OUT, "parts")
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115]))
gold = cv2.inRange(hsv, np.array([14, 90, 120]), np.array([45, 255, 255]))

def with_linework(mask_in_roi, dilate_px=7):
    near = cv2.dilate(mask_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return mask_in_roi | cv2.bitwise_and(dark, near)

# ---- part masks
# head: hood + void face (measured from gridded crop).
# NOTE: Kiko's RIGHT arm is not raised — the white at top-right is the hood.
# Only the LEFT arm is raised. Corrected after zoom verification.
head_roi = roi_mask(95, 180, W, 525)
head_m = cv2.bitwise_and(FIG, head_roi)
# accessory: gold chains + KIKO pendant
acc_roi = roi_mask(145, 395, 380, 740)
acc_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, acc_roi)), acc_roi)
acc_m = cv2.bitwise_and(acc_m, FIG)
# arm: the single RAISED left arm (character's left). The right side is hood.
arm_l_roi = roi_mask(0, 0, 105, 430)
arm_l_m = cv2.bitwise_and(FIG, arm_l_roi)
# keep head/chains out of the arm
arm_l_m = cv2.bitwise_and(arm_l_m, cv2.bitwise_not(head_m))
arm_l_m = cv2.bitwise_and(arm_l_m, cv2.bitwise_not(acc_m))
# eyes: white angular glint shards ON the void. The fur is also white, so
# select by component: white components in a TIGHT glint ROI (250,270)-
# (380,325) that touch the dilated void and have glint-sized areas
# (300-600 px). Verified visually: L ~(266-298, 278-298), R ~(332-367,
# 294-317). A plain white+ROI mask catches the hood fur (verified failure);
# a wider ROI catches fur-edge noise (verified failure).
_white = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 70, 255]))
_glint_roi = roi_mask(250, 270, 380, 325)
_white_face = cv2.bitwise_and(_white, _glint_roi)
_nw, _wlab, _wstats, _wcent = cv2.connectedComponentsWithStats(_white_face, 8)
_void_dil = cv2.dilate(cv2.bitwise_and(
    cv2.inRange(hsv, np.array([100, 100, 5]), np.array([135, 255, 90])),
    roi_mask(140, 250, 410, 500)), np.ones((7, 7), np.uint8))
_glints = []
for _i in range(1, _nw):
    _a = _wstats[_i, cv2.CC_STAT_AREA]
    if 300 <= _a <= 600:
        _comp = (_wlab == _i).astype(np.uint8) * 255
        if (cv2.bitwise_and(_comp, _void_dil) > 0).sum() == 0:
            continue
        # exclude fur intruding from the ROI edge: real glints are interior
        _ys, _xs = np.nonzero(_comp)
        if _xs.min() <= 251 or _xs.max() >= 378 or _ys.min() <= 271 or _ys.max() >= 323:
            continue
        _glints.append((_wcent[_i][0], _comp))
_glints.sort(key=lambda t: t[0])
assert len(_glints) == 2, f"expected 2 glints, found {len(_glints)}"
eyeL_m = _glints[0][1]
eyeR_m = _glints[1][1]
eyes_m = cv2.bitwise_and(eyeL_m | eyeR_m, FIG)
# robe = figure minus actual part masks; inpaint holes
part_union = head_m | acc_m | arm_l_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m = clean_small(eyes_m)
acc_m = clean_small(acc_m)
arm_l_m = clean_small(arm_l_m, 5)
# arm_r removed: single raised left arm only
head_m = clean_small(head_m, 5)
part_union = head_m | acc_m | arm_l_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

def finalize(rgb, m):
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    z = m == 0
    rgba[z, 0] = 0; rgba[z, 1] = 0; rgba[z, 2] = 0
    return rgba

layers = [
    ("01_robe", robe_rgb, robe_m),
    ("02_head", clean, head_m),
    ("03_accessory", clean, acc_m),
    ("04_arm_l", clean, arm_l_m),
    
    ("06_eyes", clean, eyes_m),
]

manifest = []
for name, rgb, m in layers:
    rgba = finalize(rgb, m)
    px = int((m > 0).sum())
    Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, f"{name}.png"))
    ys, xs = np.nonzero(m)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if px else None
    manifest.append({"layer": name, "pixels": px, "bbox_xyxy": bbox})
    print(f"{name}: {px} px  bbox={bbox}")

import json
with open(os.path.join(PARTS, "parts_manifest.json"), "w") as f:
    json.dump({"source": "kiko_battle_crop_source.png (500x912)",
               "method": "ROI x HSV color segmentation + Telea inpainting",
               "note": "battle variant: fists-raised pose; frame-cut bottom (no legs); spatial arm/shoulder cuts; KIKO pendant preserved (owner keep-or-cut flag); no mouth art",
               "stack_bottom_to_top": [m["layer"] for m in manifest],
               "layers": manifest}, f, indent=2)
print("manifest written")

comp = np.zeros((H, W, 4), np.uint8)
for name, rgb, m in layers:
    rgba = finalize(rgb, m)
    a = (m > 0)
    comp[a] = rgba[a]
Image.fromarray(cv2.cvtColor(comp, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "_composite_check.png"))
print("composite check saved")
