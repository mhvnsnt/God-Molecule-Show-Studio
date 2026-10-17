#!/usr/bin/env python3
"""Worker C Wave 9 — Sombra Negra BATTLE variant part extraction, step 2.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe, 02_head, 03_accessory (gold chains + skull pendant + belt chain
  with cross pendant), 05_eyes (white glints, split L/R at assembly)

Method: polygon silhouette x HSV color masks. Occluded areas (robe under the
head/accessory) are Telea-inpainted so each layer is self-contained.
Honest constraints: the hands are dark-gloved and visually merged with the
robe sleeves in this painterly source (no separable hand pixels; the cuff
trim stays on the robe) — so no arm parts/params, same class as the Wave-6
Sombra "arms inside the robe" constraint. Painterly dark-on-dark means part
edges follow the measured polygon silhouette; nothing invented.
Canon: black robe + purple trim/embroidery, white glints, gold chains +
skull pendant + belt chain with cross — matches the ritual source.
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/sombra-battle"
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
# head: hood + hair + void (measured: hood crown ~y95-180, void y150-335)
head_roi = poly([(92, 95), (298, 95), (300, 335), (88, 335)])
head_m = cv2.bitwise_and(FIG, head_roi)
# accessory: gold chains + skull pendant + belt chain + cross pendant
chest_roi = roi_mask(120, 320, 260, 480)          # chains + skull
belt_roi = roi_mask(120, 620, 260, 720)           # belt chain + cross
gold = cv2.inRange(hsv, np.array([12, 70, 50]), np.array([48, 255, 255]))
acc_m = with_linework(cv2.bitwise_and(gold, chest_roi | belt_roi), 6)
acc_m = cv2.bitwise_and(acc_m, FIG)
# eyes: white glints, full-canvas masked splits (Wave-8 lesson: never crops).
# measured tight ROIs: L x133-172 y213-233, R x208-242 y225-242
eye_white = cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 100, 255]))
eyeL_m = cv2.bitwise_and(eye_white, roi_mask(125, 205, 180, 240))
eyeR_m = cv2.bitwise_and(eye_white, roi_mask(200, 215, 250, 250))
eyes_m = cv2.bitwise_and(eyeL_m | eyeR_m, FIG)
# robe = figure minus actual part masks; inpaint holes
part_union = head_m | acc_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m = clean_small(eyes_m)
# chains are thin strands: close to connect, light open only (Wave-8 lesson)
acc_m = cv2.morphologyEx(acc_m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
acc_m = cv2.morphologyEx(acc_m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
head_m = clean_small(head_m, 5)
part_union = head_m | acc_m
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
    json.dump({"source": "sombra_battle_crop_source.png (400x1250)",
               "method": "polygon silhouette x HSV color segmentation + Telea inpainting",
               "note": "battle variant: ritual-circle summoning pose, full body. hands merged with robe sleeves (painterly dark-on-dark, no separable pixels); no mouth art (pipeline no-mouth path)",
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
