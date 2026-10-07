#!/usr/bin/env python3
"""Worker C Wave 10 — THEORY BATTLE variant part extraction, step 2.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe, 02_head (glint zones punched = Wave-9 eye-punch fix),
  03_accessory (gold chains + THEORY name-pendant),
  04_arm (raised right arm: purple sleeve + white-glove fist, auto-split
  _lo/_up two-link FK by convert_layers), 05_eyes (white glints, split L/R
  at assembly into full-canvas masked halves)

Method: polygon silhouette x HSV color masks. Occluded areas are
Telea-inpainted so each layer is self-contained.
Honest constraints: figure cut by the stone ledge (3/4-body, no legs) —
none invented; Ashes' red robe sliver between arm and hood subtracted
globally (Theory has no red in canon). No mouth art (pipeline no-mouth
path). Canon: purple robe + rune trim, white glints, gold chains +
THEORY plate — matches the fireworks source; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/theory-battle"
PARTS = os.path.join(OUT, "parts")
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

def poly(pts):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
    return m

FIG = (fig > 0).astype(np.uint8) * 255
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115]))

def with_linework(mask_in_roi, dilate_px=7):
    near = cv2.dilate(mask_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return mask_in_roi | cv2.bitwise_and(dark, near)

# ---- part masks (measured from gridded zooms)
# head: purple hood + void (hood crown y165-345, void y205-335)
head_roi = poly([(140, 165), (345, 165), (345, 345), (140, 345)])
void_zone = roi_mask(170, 200, 315, 335)
head_m = cv2.bitwise_and(FIG, head_roi | void_zone)
# accessory: gold chains + THEORY pendant plate (chest y305-505)
chest_roi = roi_mask(165, 305, 345, 505)
gold = cv2.inRange(hsv, np.array([12, 70, 60]), np.array([48, 255, 255]))
acc_m = with_linework(cv2.bitwise_and(gold, chest_roi), 6)
acc_m = cv2.bitwise_and(acc_m, FIG)
# arm: raised right arm — purple sleeve + white-glove fist
# (sleeve x105-225 y150-300, fist x130-220 y25-170, screen-left = her right)
arm_roi = poly([(150, 20), (222, 20), (222, 300), (132, 300), (132, 120), (150, 120)])
fist_roi = roi_mask(130, 25, 220, 170)
arm_m = cv2.bitwise_and(FIG, arm_roi)
arm_m = arm_m | cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 95, 255])), fist_roi)
arm_m = cv2.bitwise_and(arm_m, FIG)
# the fireworks sky has purple sparkles that match the sleeve hue inside the
# arm polygon — keep only the largest connected component (the actual
# fist+sleeve; sparkles are small and disconnected)
n, lab, stats, _ = cv2.connectedComponentsWithStats(arm_m, 8)
if n > 1:
    arm_m = ((lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)) * 255
# eyes: white glints on the void — tight measured ROIs only
# (L (245,225)-(309,258), R (309,225)-(358,258)); split at x=309
# (V>150 & S<150 = the working glint selector from the face-overlay check)
_white = cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 150, 255]))
eyeL_m = cv2.bitwise_and(_white, roi_mask(245, 225, 309, 258))
eyeR_m = cv2.bitwise_and(_white, roi_mask(309, 225, 358, 258))
eyeL_m = cv2.bitwise_and(eyeL_m, FIG)
eyeR_m = cv2.bitwise_and(eyeR_m, FIG)
eyes_m = eyeL_m | eyeR_m
# robe = figure minus actual part masks; inpaint holes
part_union = head_m | acc_m | arm_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m = clean_small(eyes_m)
acc_m = cv2.morphologyEx(acc_m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
acc_m = cv2.morphologyEx(acc_m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
arm_m = clean_small(arm_m, 5)
head_m = clean_small(head_m, 5)
part_union = head_m | acc_m | arm_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

holes = cv2.dilate(cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m)), np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

# punch the eyes out of the head texture (Wave-9 eye-punch fix): the eye
# layers draw over the head at rest, but the blink crossfade would reveal the
# glints baked into the head texture. Inpaint the glint zones with the void.
head_rgb = cv2.inpaint(clean, cv2.dilate(eyes_m, np.ones((9, 9), np.uint8)), 12, cv2.INPAINT_TELEA)

# clear RGB where alpha=0 (premultiply hygiene — Wave-7 lesson)
def finalize(rgb, m):
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    z = m == 0
    rgba[z, 0] = 0; rgba[z, 1] = 0; rgba[z, 2] = 0
    return rgba

layers = [
    ("01_robe", robe_rgb, robe_m),
    ("02_head", head_rgb, head_m),
    ("03_accessory", clean, acc_m),
    ("04_arm", clean, arm_m),
    ("05_eyes", clean, eyes_m),
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

with open(os.path.join(PARTS, "parts_manifest.json"), "w") as f:
    json.dump({"source": "theory_battle_crop_source.png (430x882)",
               "method": "polygon silhouette x HSV color segmentation + Telea inpainting",
               "note": "battle variant: right fist raised (white glove). arm auto-split _lo/_up FK. figure cut by stone ledge (3/4-body); Ashes red sliver subtracted; glints cut by tight ROIs; no mouth art (pipeline no-mouth path)",
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

# stash L/R eye split coords for assembly (full-canvas masked halves)
with open(os.path.join(PARTS, "_eye_split.json"), "w") as f:
    json.dump({"split_x": 309}, f)
