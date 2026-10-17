#!/usr/bin/env python3
"""Worker C Wave 10 — HOLLOW BATTLE variant (bust) part extraction, step 2.

Input: parts/_clean_bgr.npy (bg-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe (orange robe + layered gold chains + HOLLOW name-pendant MERGED —
  Wave-6 Hollow precedent: the outline-proximity chain cut catches too much
  robe, so no separate accessory layer and no ParamAcc0),
  02_head (orange hood + dark-navy void, glint zones punched = Wave-9
  eye-punch fix), 03_eyes (angular orange glints, split L/R at assembly into
  full-canvas masked halves)

Method: polygon silhouette x HSV color masks. Occluded areas are
Telea-inpainted so each layer is self-contained.
Honest constraints: BUST-ONLY (no full-body battle source exists); no arms
in any source — no arm parts/params; no ParamAcc0 (see above); figure cut
at mid-torso — none invented; no mouth art (pipeline no-mouth path).
Canon: orange robe, orange glints, gold chains + HOLLOW plate — matches the
pilot still; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/hollow-battle"
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

# ---- part masks (measured from gridded zoom)
# head: orange hood + void (hood y20-400, void y120-380)
head_roi = poly([(270, 20), (670, 20), (700, 400), (240, 400)])
void_zone = roi_mask(300, 120, 640, 380)
head_m = cv2.bitwise_and(FIG, head_roi | void_zone)
# eyes: angular orange glints — tight measured ROIs only
# (L (365,200)-(440,250), R (485,200)-(565,250)); split at x=462
_orange = cv2.inRange(hsv, np.array([8, 140, 120]), np.array([28, 255, 255]))
eyeL_m = cv2.bitwise_and(_orange, roi_mask(365, 200, 462, 250))
eyeR_m = cv2.bitwise_and(_orange, roi_mask(462, 200, 565, 250))
eyeL_m = cv2.bitwise_and(eyeL_m, FIG)
eyeR_m = cv2.bitwise_and(eyeR_m, FIG)
eyes_m = eyeL_m | eyeR_m
# robe = figure minus head (chains + HOLLOW pendant stay merged on torso)
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(head_m))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m = clean_small(eyes_m)
head_m = clean_small(head_m, 5)
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(head_m))

holes = cv2.dilate(cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m)), np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

# punch the eyes out of the head texture (Wave-9 eye-punch fix)
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
    ("03_eyes", clean, eyes_m),
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
    json.dump({"source": "hollow_battle_crop_source.png (940x872)",
               "method": "polygon silhouette x HSV color segmentation + Telea inpainting",
               "note": "battle variant: bust (pilot still). chains + HOLLOW pendant merged on torso (no separate accessory, no ParamAcc0 — Wave-6 precedent). no arms in source (no arm params). glints cut by tight ROIs. no mouth art (pipeline no-mouth path)",
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

with open(os.path.join(PARTS, "_eye_split.json"), "w") as f:
    json.dump({"split_x": 462}, f)
