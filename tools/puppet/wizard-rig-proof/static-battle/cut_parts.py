#!/usr/bin/env python3
"""Worker C Wave 8 — Static BATTLE variant part extraction, step 2.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe, 02_head, 03_accessory (pale-gold chains, no pendant in source),
  04_arm (blue sleeve + white glove, extended to the button),
  05_eyes (muted-blue glints, split L/R at assembly)

Method: ROI rectangles x HSV color masks. Occluded areas (robe under the
arm/head/chains) are Telea-inpainted so each layer is self-contained.
Honest constraints: full-body visible; claw machine is background (inpainted
out) — hand/arm stay; no pendant in this source so none grafted; Static has
no mouth art — the pipeline's "mouth simply stays shut" path applies.
Canon: blue rune embroidery rides on the robe; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/static-battle"
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

def with_linework(mask_in_roi, dilate_px=7):
    near = cv2.dilate(mask_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return mask_in_roi | cv2.bitwise_and(dark, near)

# ---- part masks
# head: hood + void (measured from gridded zoom)
head_roi = roi_mask(150, 0, 395, 265)
head_m = cv2.bitwise_and(FIG, head_roi)
# accessory: pale-gold chains in the chest ROI (no pendant in this source).
# Measured chain pixels: H 23-29, S 64-136, V 178-254 (washed pale gold).
chest_roi = roi_mask(185, 140, 375, 340)
pale_gold = cv2.inRange(hsv, np.array([20, 40, 170]), np.array([42, 160, 255]))
acc_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(pale_gold, chest_roi)), chest_roi)
acc_m = cv2.bitwise_and(acc_m, FIG)
# arm: blue sleeve + white glove, extended to the button (character's right)
arm_roi = roi_mask(55, 285, 215, 495)
glove_roi = roi_mask(60, 340, 175, 435)
glove = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 190]), np.array([180, 90, 255])), glove_roi)
arm_m = cv2.bitwise_and(FIG, arm_roi)
arm_m = arm_m | cv2.bitwise_and(glove, FIG)
arm_m = cv2.bitwise_and(arm_m, cv2.bitwise_not(cv2.bitwise_and(pale_gold, chest_roi)))  # chains stay on accessory
# The machine's glowing frame has a BLUE component (H~120, in the robe
# family) at x 100-125, y 280-360 — outside the sleeve's left outline, so it
# is machine, not sleeve. Kill it spatially: the hand starts at y~375 and
# the sleeve at x>130 here, so ROI (95,275)-(130,368) is safe.
frame_blue_roi = roi_mask(95, 275, 130, 368)
arm_m = cv2.bitwise_and(arm_m, cv2.bitwise_not(frame_blue_roi))
# The frame strip continues below y=368 alongside the glove fingers
# (x 95-130, y 368-495). Kill by color there: frame is blue (H 100-125)
# or magenta (H 135-168), saturated; the white glove (S<90) survives.
low_roi = roi_mask(95, 368, 130, 495)
frame_colored = cv2.inRange(hsv, np.array([100, 80, 50]), np.array([125, 255, 255])) | \
                cv2.inRange(hsv, np.array([135, 80, 50]), np.array([168, 255, 255]))
arm_m = cv2.bitwise_and(arm_m, cv2.bitwise_not(cv2.bitwise_and(frame_colored, low_roi)))
# eyes: muted-blue glints. Measured: H 108-111, S 150-187, V 231-254.
# Tight ROIs from the gridded zoom: L x 215-240, R x 250-275.
eyeL_m = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([100, 120, 220]), np.array([118, 220, 255])), roi_mask(215, 135, 240, 155))
eyeR_m = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([100, 120, 220]), np.array([118, 220, 255])), roi_mask(250, 128, 275, 148))
eyes_m = cv2.bitwise_and(eyeL_m | eyeR_m, FIG)
# robe = figure minus actual part masks; inpaint holes
part_union = head_m | acc_m | arm_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m = clean_small(eyes_m)
# chains are thin strands: close to connect dashes, light open only (k=2) —
# a k=3 open fragments them (verified visually).
acc_m = cv2.morphologyEx(acc_m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
acc_m = cv2.morphologyEx(acc_m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
arm_m = clean_small(arm_m, 5)
head_m = clean_small(head_m, 5)
part_union = head_m | acc_m | arm_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

# clear RGB where alpha=0 (premultiply hygiene — Wave 7 lesson)
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

import json
with open(os.path.join(PARTS, "parts_manifest.json"), "w") as f:
    json.dump({"source": "static_battle_crop_source.png (540x740)",
               "method": "ROI x HSV color segmentation + Telea inpainting",
               "note": "battle variant: arm-extended claw-machine pose; full body; no pendant in source (none grafted); no mouth art (pipeline no-mouth path)",
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
