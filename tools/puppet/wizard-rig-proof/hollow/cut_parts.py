#!/usr/bin/env python3
"""Worker C Wave 6 — Hollow part extraction, step 2: cut rig layers.

Input: parts/_clean_bgr.npy + parts/_figmask.npy
Output: parts/*.png + rig_layers/{order}_{role}.png for convert_layers.

Hollow is a HALF-BODY bust (pilot still cut at mid-torso) — no arm layers
exist (no arms visible). The rig therefore has no arm params (honest
constraint, documented).

Layer stack, bottom -> top:
  00_torso     (01_robe): orange robe + darker runes. Holes inpainted.
  01_face_base (02_head): hood + dark-navy void face.
  02_accessory (03_chain): layered gold chains + HOLLOW name-pendant
                          (ParamAcc0 sway). Chains cut via black-outline
                          proximity (Cipher method): chain gold and robe
                          orange overlap in hue.
  03_eye_l     (04_eye_L): left orange glint.
  04_eye_r     (05_eye_R): right orange glint.
  NO mouth layer: void-face character. Closed-eye synthesis kept.

Canon: orange robe = Hollow (Hollows leader). No grill invented (Ashes only).
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/hollow"
PARTS = os.path.join(OUT, "parts")
RIG = os.path.join(OUT, "rig_layers")
os.makedirs(RIG, exist_ok=True)
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
assert (W, H) == (960, 872), (W, H)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([5, 100, 120]), np.array([28, 255, 255]))
dark = cv2.inRange(hsv, np.array([0, 0, 5]), np.array([180, 200, 90]))  # outlines

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255

# ---- eyes: tight measured ROIs (same as extract; right glint position
# verified against the gridded zoom: left glint ~(135-225, 198-248),
# right glint ~(275-355, 200-242). Neither touches the hood.
glintL_roi = roi_mask(135, 198, 225, 248)
glintR_roi = roi_mask(275, 200, 355, 242)
glint_col = cv2.inRange(hsv, np.array([3, 140, 110]), np.array([18, 255, 255]))
eyeL_m = cv2.bitwise_and(glint_col, glintL_roi)
eyeR_m = cv2.bitwise_and(glint_col, glintR_roi)
eyeL_m = cv2.bitwise_and(eyeL_m, FIG); eyeR_m = cv2.bitwise_and(eyeR_m, FIG)
assert (eyeL_m > 0).sum() > 100 and (eyeR_m > 0).sum() > 100, "glint missing"

# ---- NO separate accessory layer: the outline-proximity chain cut caught
# too much robe (runes/folds share the dark outlines) — verified visually.
# Chains + HOLLOW pendant stay on the torso (Onyx staff precedent). The rig
# therefore has no ParamAcc0 (documented honest constraint).

# ---- head: hood + void (chains stay on the torso, so no chain hole)
head_roi = roi_mask(60, 0, 650, 430)
head_m = cv2.bitwise_and(FIG, head_roi)
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(eyeL_m | eyeR_m, np.ones((3, 3), np.uint8))))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyeL_m, eyeR_m = clean_small(eyeL_m), clean_small(eyeR_m)
head_m = clean_small(head_m, 5)

head_holes = cv2.bitwise_and(cv2.bitwise_and(FIG, head_roi),
                             cv2.bitwise_not(head_m))
head_rgb = cv2.inpaint(clean, cv2.dilate(head_holes, np.ones((5, 5), np.uint8)),
                       8, cv2.INPAINT_TELEA)

# ---- torso: everything else (robe + chains + HOLLOW pendant); inpaint holes
part_union = head_m | eyeL_m | eyeR_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))
holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

layers = [
    ("01_robe",   robe_rgb, robe_m,   "00_torso.png"),
    ("02_head",   head_rgb, head_m,   "01_face_base.png"),
    ("03_eye_L",  clean,    eyeL_m,   "02_eye_l.png"),
    ("04_eye_R",  clean,    eyeR_m,   "03_eye_r.png"),
]

manifest = []
for name, rgb, m, rig_name in layers:
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    px = int((m > 0).sum())
    Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, f"{name}.png"))
    Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(RIG, rig_name))
    ys, xs = np.nonzero(m)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if px else None
    manifest.append({"layer": name, "rig_file": rig_name, "pixels": px, "bbox_xyxy": bbox})
    print(f"{name:10s} -> {rig_name:18s} {px:6d} px  bbox={bbox}")

with open(os.path.join(PARTS, "parts_manifest.json"), "w") as f:
    json.dump({"source": "hollow_crop_source.png (960x872, half-body bust)",
               "method": "ROI x HSV color segmentation (Wave-4/5/6 recipe)",
               "stack_bottom_to_top": [m["rig_file"] for m in manifest],
               "layers": manifest}, f, indent=2)
print("manifest written")

comp = np.zeros((H, W, 4), np.uint8)
for name, rgb, m, rig_name in layers:
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    comp[m > 0] = rgba[m > 0]
Image.fromarray(cv2.cvtColor(comp, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "_composite_check.png"))
print("composite check saved")
