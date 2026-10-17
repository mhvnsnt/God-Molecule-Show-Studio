#!/usr/bin/env python3
"""Worker C Wave 9 — Onyx BATTLE variant part extraction, step 2.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe, 02_head, 03_accessory (gold chains + pendant + jester bells),
  04_arm (green sleeve + white glove, gripping pose), 05_eyes (green glints,
  split L/R at assembly)

Method: polygon silhouette x HSV color masks. Occluded areas (robe under the
head/arm/accessory) are Telea-inpainted so each layer is self-contained.
The glints share the robe's green hue — they are cut by tight measured ROIs
only (no color mask), the void interior guarantees purity.
Honest constraints: staff is a prop — inpainted out (claw-machine precedent,
Wave 8); the gripping hand stays (a sliver of staff between the fingers is
the grip, kept). Figure cut by the skate-park ledge (no legs in frame) —
none invented. No mouth art (pipeline no-mouth path).
Canon: green jester robe + bells, green glints, gold chains — matches the
skate-park source; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/onyx-battle"
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
# head: jester hood + void (measured: hood crown y110-300, void y250-440)
head_roi = poly([(95, 110), (340, 110), (345, 300), (90, 300)])
void_zone = roi_mask(110, 240, 290, 450)
head_m = cv2.bitwise_and(FIG, head_roi | void_zone)
# accessory: gold chains + pendant + jester bells (peach)
chest_roi = roi_mask(110, 370, 330, 560)
gold = cv2.inRange(hsv, np.array([12, 70, 60]), np.array([48, 255, 255]))
bells = cv2.inRange(hsv, np.array([0, 60, 150]), np.array([22, 200, 255]))
acc_m = with_linework(cv2.bitwise_and(gold | bells, chest_roi), 6)
acc_m = cv2.bitwise_and(acc_m, FIG)
# arm: green sleeve + white glove gripping (character's right arm, screen left)
arm_roi = poly([(25, 370), (165, 370), (165, 640), (25, 640)])
hand_roi = roi_mask(30, 375, 115, 485)
arm_m = cv2.bitwise_and(FIG, arm_roi)
arm_m = arm_m | cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 100, 255])), hand_roi)
arm_m = cv2.bitwise_and(arm_m, FIG)
# eyes: green glints — same hue as the robe/hood, so a plain green+ROI mask
# catches hood edges (verified failure). Selection by component: green
# components in the tight glint ROIs that do NOT touch the ROI border
# (Kiko-battle Wave-8 recipe). Measured: L (133,256)-(156,268);
# R (170,241)-(195,259), small and high, partially behind the hood edge.
_green = cv2.inRange(hsv, np.array([52, 100, 100]), np.array([75, 255, 255]))
def interior_green(x0, y0, x1, y1):
    sub = _green[y0:y1, x0:x1].copy()
    n, lab, stats, _ = cv2.connectedComponentsWithStats(sub, 8)
    keep = np.zeros_like(sub)
    bh, bw = sub.shape
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        touches = (x == 0 or y == 0 or x + w >= bw or y + h >= bh)
        if not touches and area >= 60:
            keep[lab == i] = 255
    full = np.zeros((H, W), np.uint8)
    full[y0:y1, x0:x1] = keep
    return full
eyeL_m = cv2.bitwise_and(interior_green(125, 250, 165, 275), FIG)
eyeR_m = cv2.bitwise_and(interior_green(165, 235, 200, 265), FIG)
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

# punch the eyes out of the head texture (Wave-8 Static precedent): the eye
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
    json.dump({"source": "onyx_battle_crop_source.png (470x852)",
               "method": "polygon silhouette x HSV color segmentation + Telea inpainting",
               "note": "battle variant: staff-raised jester stance, bust length (ledge cut). staff prop inpainted out (hand stays); glints cut by tight ROIs (same hue as robe); no mouth art (pipeline no-mouth path)",
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
