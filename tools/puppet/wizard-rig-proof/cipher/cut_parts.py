#!/usr/bin/env python3
"""Worker C Wave 6 — Cipher part extraction, step 2: cut rig layers.

Input: parts/_clean_bgr.npy + parts/_figmask.npy
Output: parts/*.png + rig_layers/{order}_{role}.png for convert_layers.

Cipher's chains are NOT color-separable from the robe (H~20 vs H~21), so the
accessory mask = gold pixels near thick black outlines, in the chest ROI.
The robe between chains is flat yellow (no outlines) and is excluded; the
inpainted chain-shaped holes on the torso are invisible (yellow on yellow).
If the chains fragment, the fallback is chains-on-torso (Onyx precedent) —
verified visually below.

Layer stack, bottom -> top:
  00_torso     (01_robe): yellow robe + darker-gold runes. Holes inpainted.
  01_face_base (02_head): hood + dark-blue void face.
  02_arm_l     (03_arm_L): left crossed arm: yellow sleeve + white glove.
  03_arm_r     (04_arm_R): right crossed arm: yellow sleeve.
  04_accessory (05_chain): heavy gold chains (ParamAcc0 sway) — IF clean.
  05_eye_l     (06_eye_L): left yellow glint.
  06_eye_r     (07_eye_R): right yellow glint.
  NO mouth layer: void-face character. Closed-eye synthesis kept.

Canon: yellow robe = Cipher. No grill invented (Ashes only). No pendant on
the group-2 source (chains only) — none grafted.
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/cipher"
PARTS = os.path.join(OUT, "parts")
RIG = os.path.join(OUT, "rig_layers")
os.makedirs(RIG, exist_ok=True)
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
assert (W, H) == (305, 910), (W, H)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([15, 120, 150]), np.array([40, 255, 255]))
dark = cv2.inRange(hsv, np.array([0, 0, 5]), np.array([180, 200, 90]))  # outlines

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255

# ---- eyes: tight measured ROIs (same as extract)
glintL_roi = roi_mask(108, 88, 142, 120)
glintR_roi = roi_mask(148, 86, 184, 118)
glint_col = cv2.inRange(hsv, np.array([20, 100, 180]), np.array([38, 255, 255]))
eyeL_m = cv2.bitwise_and(glint_col, glintL_roi)
eyeR_m = cv2.bitwise_and(glint_col, glintR_roi)
eyeL_m = cv2.bitwise_and(eyeL_m, FIG); eyeR_m = cv2.bitwise_and(eyeR_m, FIG)

# ---- accessory: gold near thick black outlines, chest ROI
acc_roi = roi_mask(85, 150, 255, 330)
near_dark = cv2.dilate(dark, np.ones((13, 13), np.uint8))
acc_m = cv2.bitwise_and(cv2.bitwise_and(gold, near_dark), acc_roi)
acc_m = cv2.bitwise_and(acc_m, FIG)

# ---- head: hood + void
head_roi = roi_mask(60, 0, 250, 235)
head_m = cv2.bitwise_and(FIG, head_roi)
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(acc_m, np.ones((5, 5), np.uint8))))
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(eyeL_m | eyeR_m, np.ones((3, 3), np.uint8))))

# ---- arms: crossed-arm band split at figure centre
armL_m = cv2.bitwise_and(FIG, roi_mask(0, 250, 152, 400))
armR_m = cv2.bitwise_and(FIG, roi_mask(152, 250, 305, 400))
armL_m = cv2.bitwise_and(armL_m, cv2.bitwise_not(cv2.dilate(acc_m, np.ones((5, 5), np.uint8))))
armR_m = cv2.bitwise_and(armR_m, cv2.bitwise_not(cv2.dilate(acc_m, np.ones((5, 5), np.uint8))))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyeL_m, eyeR_m = clean_small(eyeL_m), clean_small(eyeR_m)
acc_m = clean_small(acc_m, 3)
armL_m, armR_m = clean_small(armL_m, 5), clean_small(armR_m, 5)
head_m = clean_small(head_m, 5)

head_holes = cv2.bitwise_and(cv2.bitwise_and(FIG, head_roi),
                             cv2.bitwise_not(head_m))
head_rgb = cv2.inpaint(clean, cv2.dilate(head_holes, np.ones((5, 5), np.uint8)),
                       8, cv2.INPAINT_TELEA)

part_union = head_m | armL_m | armR_m | acc_m | eyeL_m | eyeR_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))
holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

layers = [
    ("01_robe",   robe_rgb, robe_m,   "00_torso.png"),
    ("02_head",   head_rgb, head_m,   "01_face_base.png"),
    ("03_arm_L",  clean,    armL_m,   "02_arm_l.png"),
    ("04_arm_R",  clean,    armR_m,   "03_arm_r.png"),
    ("05_chain",  clean,    acc_m,    "04_accessory.png"),
    ("06_eye_L",  clean,    eyeL_m,   "05_eye_l.png"),
    ("07_eye_R",  clean,    eyeR_m,   "06_eye_r.png"),
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
    json.dump({"source": "cipher_crop_source.png (305x910)",
               "method": "ROI x HSV color segmentation + Telea inpainting (Wave-4/5/6 recipe)",
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
