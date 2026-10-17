#!/usr/bin/env python3
"""Worker C Wave 4 — Ashes part extraction, step 2: cut rig layers.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + ashes_parts.psd
        (layer stack for nijigenerate PSD import).

Layer stack, bottom -> top:
  01_robe, 02_head, 03_braid_L, 04_braid_R, 05_chain,
  06_arm_L, 07_arm_R, 08_eyes, 09_grill

Method: ROI rectangles x HSV color masks (gold / red / white / black),
tuned from blob inspection of the head region. Occluded areas (e.g. robe
under the arms, robe under the head) are Telea-inpainted so each layer is
self-contained. Overlapping cutouts are normal for 2D cutout rigs; the
topmost layer wins at composite time.
Canon: diamond-grill smile kept intact on its own layer; no redesign.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/ashes"
PARTS = os.path.join(OUT, "parts")
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([12, 80, 90]), np.array([50, 255, 255]))
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115]))   # linework/shadow strokes
white = cv2.inRange(hsv, np.array([0, 0, 195]), np.array([180, 70, 255]))

def with_linework(gold_in_roi, dilate_px=7):
    """Gold fill plus the dark linework strokes that outline it."""
    near = cv2.dilate(gold_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return gold_in_roi | cv2.bitwise_and(dark, near)
red1 = cv2.inRange(hsv, np.array([0, 70, 60]), np.array([12, 255, 255]))
red2 = cv2.inRange(hsv, np.array([168, 70, 60]), np.array([180, 255, 255]))
red = red1 | red2
maroon = cv2.inRange(hsv, np.array([0, 45, 25]), np.array([12, 255, 90]))
white = cv2.inRange(hsv, np.array([0, 0, 195]), np.array([180, 70, 255]))

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255

# ---- part masks (ROI x color, all intersected with figure)
head_roi   = roi_mask(50, 10, 345, 270)
eyes_m  = cv2.bitwise_and(gold | white, roi_mask(115, 95, 270, 142)); eyes_m = cv2.bitwise_and(eyes_m, FIG)
grill_m = cv2.bitwise_and(gold | white, roi_mask(115, 142, 265, 185)); grill_m = cv2.bitwise_and(grill_m, FIG)
braidL_roi = roi_mask(85, 170, 178, 400)
braidR_roi = roi_mask(222, 170, 318, 400)
chain_roi  = roi_mask(158, 225, 242, 345)
braidL_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, braidL_roi)), braidL_roi)
braidL_m = cv2.bitwise_and(braidL_m, FIG)
braidR_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, braidR_roi)), braidR_roi)
braidR_m = cv2.bitwise_and(braidR_m, FIG)
chain_m  = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, chain_roi)), chain_roi)
chain_m  = cv2.bitwise_and(chain_m, FIG)
# keep chain pixels out of the braid layers (chain hangs in front)
braidL_m = cv2.bitwise_and(braidL_m, cv2.bitwise_not(chain_roi))
braidR_m = cv2.bitwise_and(braidR_m, cv2.bitwise_not(chain_roi))
armL_m = cv2.bitwise_and(FIG, roi_mask(0, 295, 208, 460))
armR_m = cv2.bitwise_and(FIG, roi_mask(208, 295, 400, 460))
head_m = cv2.bitwise_and(FIG, head_roi)
# robe = figure minus the ACTUAL part pixel masks (not the ROI rects, which
# would punch transparent gaps); then inpaint the holes so the robe layer
# is self-contained behind the overlapping parts.
part_union = head_m | braidL_m | braidR_m | chain_m | armL_m | armR_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m, grill_m = clean_small(eyes_m), clean_small(grill_m)
braidL_m, braidR_m, chain_m = clean_small(braidL_m), clean_small(braidR_m), clean_small(chain_m)
armL_m, armR_m = clean_small(armL_m, 5), clean_small(armR_m, 5)
head_m = clean_small(head_m, 5)
part_union = head_m | braidL_m | braidR_m | chain_m | armL_m | armR_m
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
    ("06_arm_L", clean, armL_m),
    ("07_arm_R", clean, armR_m),
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
    json.dump({"source": "ashes_crop_source.png (400x864)",
               "method": "ROI x HSV color segmentation + Telea inpainting",
               "stack_bottom_to_top": [m["layer"] for m in manifest],
               "layers": manifest}, f, indent=2)
print("manifest written")

# ---- composite check: stack all layers, compare to base
comp = np.zeros((H, W, 4), np.uint8)
for name, rgb, m in layers:
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    a = (m > 0)
    comp[a] = rgba[a]
Image.fromarray(cv2.cvtColor(comp, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "_composite_check.png"))
print("composite check saved")
