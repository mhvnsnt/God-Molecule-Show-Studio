#!/usr/bin/env python3
"""Worker C Wave 7 — Ashes BATTLE variant (mid-dunk) part extraction, step 2.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe, 02_head, 03_braid_L, 04_braid_R, 05_chain,
  06_arm (raised arm: sleeve + glove), 07_ball (prop),
  08_eyes, 09_grill

Method: ROI rectangles x HSV color masks, tuned from blob inspection.
Occluded areas (robe under arm/head) are Telea-inpainted so each layer is
self-contained. Honest constraints: only ONE arm is visible in the source
dunk pose (the other is inside the robe) — no second arm layer is cut;
the basketball is a scene prop on its own layer, not puppeted.
Canon: diamond-grill smile kept intact on its own layer; no redesign.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/ashes-battle"
PARTS = os.path.join(OUT, "parts")
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([12, 80, 90]), np.array([48, 255, 255]))
tan = cv2.inRange(hsv, np.array([7, 60, 110]), np.array([22, 210, 245]))  # braid wheat-tan
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115]))   # linework/shadow strokes
orange = cv2.inRange(hsv, np.array([4, 140, 140]), np.array([17, 255, 255]))  # basketball

def with_linework(gold_in_roi, dilate_px=7):
    """Gold fill plus the dark linework strokes that outline it."""
    near = cv2.dilate(gold_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return gold_in_roi | cv2.bitwise_and(dark, near)

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255

# ---- part masks (ROI x color, all intersected with figure)
head_roi = roi_mask(585, 140, 748, 318)
eyeL_m = cv2.bitwise_and(gold, roi_mask(632, 190, 670, 212))
eyeR_m = cv2.bitwise_and(gold, roi_mask(675, 190, 704, 212))
eyes_m = cv2.bitwise_and(eyeL_m | eyeR_m, FIG)
grill_m = cv2.bitwise_and(gold, roi_mask(636, 200, 710, 264))
grill_m = cv2.bitwise_and(with_linework(grill_m), FIG)
braidL_roi = roi_mask(588, 215, 650, 435)
braidR_roi = roi_mask(698, 215, 762, 435)
chain_roi = roi_mask(642, 268, 714, 382)   # left edge at 642: braid hangs visibly left of the chain links
# grill ROI grazes the braids: exclude braid zones
grill_m = cv2.bitwise_and(grill_m, cv2.bitwise_not(braidL_roi))
grill_m = cv2.bitwise_and(grill_m, cv2.bitwise_not(braidR_roi))
# eyes and grill are separate rig layers: eyes win the overlap
grill_m = cv2.bitwise_and(grill_m, cv2.bitwise_not(eyeL_m))
grill_m = cv2.bitwise_and(grill_m, cv2.bitwise_not(eyeR_m))
braidL_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(tan | gold, braidL_roi)), braidL_roi)
braidL_m = cv2.bitwise_and(braidL_m, FIG)
braidR_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(tan | gold, braidR_roi)), braidR_roi)
braidR_m = cv2.bitwise_and(braidR_m, FIG)
chain_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, chain_roi)), chain_roi)
chain_m = cv2.bitwise_and(chain_m, FIG)
# keep chain pixels out of the braid layers (chain hangs in front) — subtract
# actual chain pixels, not the ROI rect (the rect grazes the left braid)
braidL_m = cv2.bitwise_and(braidL_m, cv2.bitwise_not(chain_m))
braidR_m = cv2.bitwise_and(braidR_m, cv2.bitwise_not(chain_m))
# raised arm: sleeve (red) + white glove, everything in the arm zone except ball
arm_roi = roi_mask(405, 95, 588, 432)
arm_m = cv2.bitwise_and(FIG, arm_roi)
# basketball prop: orange fill + its dark seam linework
ball_roi = roi_mask(398, 22, 532, 158)
ball_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(orange, ball_roi), 5), ball_roi)
ball_m = cv2.bitwise_and(ball_m, FIG)
arm_m = cv2.bitwise_and(arm_m, cv2.bitwise_not(ball_roi))  # glove stays in arm, ball separate
head_m = cv2.bitwise_and(FIG, head_roi)
# robe = figure minus the ACTUAL part pixel masks; then inpaint holes.
part_union = head_m | braidL_m | braidR_m | chain_m | arm_m | ball_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m, grill_m = clean_small(eyes_m), clean_small(grill_m)
braidL_m, braidR_m, chain_m = clean_small(braidL_m), clean_small(braidR_m), clean_small(chain_m)
arm_m = clean_small(arm_m, 5)
ball_m = clean_small(ball_m, 3)
head_m = clean_small(head_m, 5)
part_union = head_m | braidL_m | braidR_m | chain_m | arm_m | ball_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

# ---- robe: fill holes left by removed parts via inpaint on the RGB
holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

layers = [
    ("01_robe", robe_rgb, robe_m),
    ("02_head", clean, head_m),
    ("03_braid_L", clean, braidL_m),
    ("04_braid_R", clean, braidR_m),
    ("05_chain", clean, chain_m),
    ("06_arm", clean, arm_m),
    ("07_ball", clean, ball_m),
    ("08_eyes", clean, eyes_m),
    ("09_grill", clean, grill_m),
]

manifest = []
for name, rgb, m in layers:
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    px = int((m > 0).sum())
    Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, f"{name}.png"))
    ys, xs = np.nonzero(m)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if px else None
    manifest.append({"layer": name, "pixels": px, "bbox_xyxy": bbox})
    print(f"{name}: {px} px  bbox={bbox}")

import json
with open(os.path.join(PARTS, "parts_manifest.json"), "w") as f:
    json.dump({"source": "ashes_battle_crop_source.png (780x885)",
               "method": "ROI x HSV color segmentation + Telea inpainting",
               "note": "battle variant: mid-dunk pose; only one arm visible (honest constraint); ball is a scene prop layer",
               "stack_bottom_to_top": [m["layer"] for m in manifest],
               "layers": manifest}, f, indent=2)
print("manifest written")

# ---- composite check
comp = np.zeros((H, W, 4), np.uint8)
for name, rgb, m in layers:
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    a = (m > 0)
    comp[a] = rgba[a]
Image.fromarray(cv2.cvtColor(comp, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "_composite_check.png"))
print("composite check saved")
