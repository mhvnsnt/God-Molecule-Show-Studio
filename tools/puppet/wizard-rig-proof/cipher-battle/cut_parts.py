#!/usr/bin/env python3
"""Worker C Wave 10 — CIPHER BATTLE variant part extraction, step 2.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe, 02_head (glint zones punched = Wave-9 eye-punch fix),
  03_accessory (gold chains; NO pendant plate in this source — none grafted,
  Wave-6 Cipher precedent), 04_arm (raised left arm: yellow sleeve + partial
  white-glove fist cut by the crop top, auto-split _lo/_up two-link FK by
  convert_layers), 05_eyes (manic yellow glints, split L/R at assembly into
  full-canvas masked halves)

Method: polygon silhouette x HSV color masks. The glints share the robe's
YELLOW hue — cut by tight measured ROIs + interior-component selection
(Kiko-battle Wave-8 recipe): components in the glint ROIs that do NOT touch
the ROI border. Occluded areas are Telea-inpainted so each layer is
self-contained.
Honest constraints: raised fist cut by the crop's top edge (arm = sleeve +
partial fist) — none invented; no pendant (none in source); figure cut by
the stone ledge (3/4-body, no legs) — none invented; no mouth art (pipeline
no-mouth path). Canon: yellow robe + runes, manic yellow glints, gold
chains — matches the fireworks source; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/cipher-battle"
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
# head: yellow hood + void (hood y90-280, void y135-265)
head_roi = poly([(220, 90), (405, 90), (405, 280), (220, 280)])
void_zone = roi_mask(240, 135, 380, 265)
head_m = cv2.bitwise_and(FIG, head_roi | void_zone)
# accessory: gold chains (chest y265-410); NO pendant plate in this source
chest_roi = roi_mask(240, 265, 410, 410)
gold = cv2.inRange(hsv, np.array([12, 70, 60]), np.array([48, 255, 255]))
acc_m = with_linework(cv2.bitwise_and(gold, chest_roi), 6)
acc_m = cv2.bitwise_and(acc_m, FIG)
# arm: raised left arm — yellow sleeve + partial white-glove fist (cut at top)
# (sleeve x385-469 y40-210, fist x395-465 y0-55, screen-right = her left)
arm_roi = poly([(385, 0), (W, 0), (W, 210), (385, 210)])
fist_roi = roi_mask(390, 0, W, 60)
arm_m = cv2.bitwise_and(FIG, arm_roi)
arm_m = arm_m | cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 95, 255])), fist_roi)
arm_m = cv2.bitwise_and(arm_m, FIG)
# the fireworks sky has yellow sparkles that match the sleeve hue inside the
# arm polygon — keep only the largest connected component (the actual arm)
n, lab, stats, _ = cv2.connectedComponentsWithStats(arm_m, 8)
if n > 1:
    arm_m = ((lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)) * 255
# eyes: manic yellow glints — same hue as the robe AND the hood rim. The rim
# sits at the very top of the face (y<148); the glints are at y150-172.
# Selection: yellow components in tight ROIs with y0=148 (rim excluded),
# area>=40. Measured: L (235,148)-(280,178), R (297,148)-(343,178).
_yellow = cv2.inRange(hsv, np.array([18, 120, 150]), np.array([38, 255, 255]))
def glint_roi(x0, y0, x1, y1):
    sub = _yellow[y0:y1, x0:x1].copy()
    n, lab, stats, _ = cv2.connectedComponentsWithStats(sub, 8)
    keep = np.zeros_like(sub)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 40:
            keep[lab == i] = 255
    full = np.zeros((H, W), np.uint8)
    full[y0:y1, x0:x1] = keep
    return full
eyeL_m = cv2.bitwise_and(glint_roi(247, 148, 280, 178), FIG)
eyeR_m = cv2.bitwise_and(glint_roi(297, 148, 343, 178), FIG)
eyes_m = eyeL_m | eyeR_m
# robe = figure minus actual part masks; inpaint holes
part_union = head_m | acc_m | arm_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m = cv2.morphologyEx(eyes_m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
eyes_m = cv2.morphologyEx(eyes_m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
acc_m = cv2.morphologyEx(acc_m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
acc_m = cv2.morphologyEx(acc_m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
arm_m = clean_small(arm_m, 5)
head_m = clean_small(head_m, 5)
part_union = head_m | acc_m | arm_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

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
    json.dump({"source": "cipher_battle_crop_source.png (469x882)",
               "method": "polygon silhouette x HSV color segmentation + Telea inpainting",
               "note": "battle variant: left fist raised (fist cut by crop top; sleeve + partial fist). arm auto-split _lo/_up FK. glints cut by tight ROIs + interior-component selection (same hue as robe). no pendant in source (none grafted). figure cut by stone ledge (3/4-body); no mouth art (pipeline no-mouth path)",
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
    json.dump({"split_x": 290}, f)
