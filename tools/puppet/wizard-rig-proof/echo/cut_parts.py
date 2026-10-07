#!/usr/bin/env python3
"""Worker C Wave 5 — Echo part extraction, step 2: cut rig layers.

Input: parts/_clean_bgr.npy + parts/_figmask.npy
Output: parts/*.png + rig_layers/{order}_{role}.png

Layer stack, bottom -> top:
  00_torso     (01_robe): pink splatter robe (holes inpainted)
  01_face_base (02_head): hood + black void face. Glint pixels removed and
                          inpainted with void color (Wave-5 lesson from Onyx:
                          the blink is an opacity crossfade, so the head must
                          not ghost the open glints).
  02_accessory (03_chain): gold chain + ECHO name pendant -> sway physics
                          (Ashes-chain analog, ParamAcc0)
  03_arm_l     (04_arm_L): left crossed arm + white glove
  04_arm_r     (05_arm_R): right crossed arm + white glove
  05_eye_l     (06_eye_L): left pink glint
  06_eye_r     (06_eye_R): right pink glint
  NO hair_side (no sway flourishes besides the chain) and NO mouth layer:
  void-face character (same policy as Onyx).
Canon: ECHO pendant text kept as painted; no spray can (street-persona prop,
        not in the cartoonier group base — honest delta documented).
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/echo"
PARTS = os.path.join(OUT, "parts")
RIG = os.path.join(OUT, "rig_layers")
os.makedirs(RIG, exist_ok=True)
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115]))

def with_linework(gold_in_roi, dilate_px=5):
    near = cv2.dilate(gold_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return gold_in_roi | cv2.bitwise_and(dark, near)

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255

# ---- eyes first (head must exclude them)
# The bright-pink mask catches the two glints PLUS two pink hood highlights
# above them. Split L/R by the face centre x=197 (not by sorted extremes —
# the highlights are the extreme-left/right blobs and would steal the eyes).
glint_roi = roi_mask(140, 125, 255, 195)
glints = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([138, 70, 200]), np.array([162, 220, 255])), glint_roi)
n, lab, stats, cent = cv2.connectedComponentsWithStats((glints > 0).astype(np.uint8), 8)
eyeL_m = np.zeros((H, W), np.uint8); eyeR_m = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] < 40:
        continue
    if cent[i][0] < 197:
        eyeL_m[lab == i] = 255
    else:
        eyeR_m[lab == i] = 255
assert (eyeL_m > 0).sum() > 0 and (eyeR_m > 0).sum() > 0, "missing glint side"
eyeL_m = cv2.bitwise_and(eyeL_m, FIG); eyeR_m = cv2.bitwise_and(eyeR_m, FIG)

# ---- part masks
chain_roi = roi_mask(130, 320, 270, 410)
chain_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, chain_roi)), FIG)
head_roi = roi_mask(50, 40, 290, 330)
head_m = cv2.bitwise_and(FIG, head_roi)
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(chain_m, np.ones((3, 3), np.uint8))))
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(eyeL_m | eyeR_m, np.ones((3, 3), np.uint8))))
armL_m = cv2.bitwise_and(FIG, roi_mask(40, 360, 175, 500))
armR_m = cv2.bitwise_and(FIG, roi_mask(175, 360, 300, 500))
# keep chain pixels out of the arm layers (chain hangs in front)
armL_m = cv2.bitwise_and(armL_m, cv2.bitwise_not(chain_roi))
armR_m = cv2.bitwise_and(armR_m, cv2.bitwise_not(chain_roi))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

chain_m = clean_small(chain_m)
armL_m, armR_m = clean_small(armL_m, 5), clean_small(armR_m, 5)
eyeL_m, eyeR_m = clean_small(eyeL_m), clean_small(eyeR_m)
head_m = clean_small(head_m, 5)
head_holes = cv2.bitwise_and(cv2.bitwise_and(FIG, head_roi), cv2.bitwise_not(head_m))
head_rgb = cv2.inpaint(clean, cv2.dilate(head_holes, np.ones((5, 5), np.uint8)),
                       8, cv2.INPAINT_TELEA)

part_union = head_m | chain_m | armL_m | armR_m | eyeL_m | eyeR_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))
holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

layers = [  # (part name, rgb source, mask, rig filename)
    ("01_robe",  robe_rgb, robe_m,  "00_torso.png"),
    ("02_head",  head_rgb, head_m,  "01_face_base.png"),
    ("03_chain", clean,    chain_m, "02_accessory.png"),
    ("04_arm_L", clean,    armL_m,  "03_arm_l.png"),
    ("05_arm_R", clean,    armR_m,  "04_arm_r.png"),
    ("06_eye_L", clean,    eyeL_m,  "05_eye_l.png"),
    ("06_eye_R", clean,    eyeR_m,  "06_eye_r.png"),
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

import json
with open(os.path.join(PARTS, "parts_manifest.json"), "w") as f:
    json.dump({"source": "echo_crop_source.png (320x960)",
               "method": "ROI x HSV color segmentation + Telea inpainting (Wave-4 Ashes recipe, Wave-5 fixes)",
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
