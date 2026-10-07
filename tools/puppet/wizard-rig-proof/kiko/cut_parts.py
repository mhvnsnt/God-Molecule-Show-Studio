#!/usr/bin/env python3
"""Worker C Wave 5 — Kiko part extraction, step 2: cut rig layers.

Input: parts/_clean_bgr.npy + parts/_figmask.npy
Output: parts/*.png + rig_layers/{order}_{role}.png

Layer stack, bottom -> top:
  00_torso     (01_body): fur coat + bare chest + dragon tights + legs
                          (everything below head except drapes/chains/arms;
                          holes inpainted)
  01_face_base (02_head): white fur hood + black void face (no glints exist —
                          pure void; see extract_parts.py)
  02_hair_side (03_drape_L): left front fur drape  -> sway physics
  03_hair_side (04_drape_R): right front fur drape -> sway physics
  04_accessory (05_chains): gold chains + KIKO pendant + skulls + cross +
                             compass -> sway physics (ParamAcc0)
  05_arm_l     (06_arm_L): left fur sleeve
  06_arm_r     (07_arm_R): right fur sleeve
  NO eye layers (no glints in source — honest gap documented) and NO mouth
  layer: void-face character (same policy as Onyx/Echo).
Canon: KIKO pendant text kept as painted; dragon tights kept as painted;
        bare chest kept (no shirt invented).
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/kiko"
PARTS = os.path.join(OUT, "parts")
RIG = os.path.join(OUT, "rig_layers")
os.makedirs(RIG, exist_ok=True)
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115]))
fur_w = cv2.inRange(hsv, np.array([0, 0, 165]), np.array([180, 90, 255]))

def with_linework(gold_in_roi, dilate_px=7):
    near = cv2.dilate(gold_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return gold_in_roi | cv2.bitwise_and(dark, near)

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255

# ---- part masks
# chains + pendants (accessory)
chain_roi = roi_mask(330, 540, 740, 920)
chain_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, chain_roi)), FIG)
# front fur drapes (hair_side analogs) — white fur strips hanging in front,
# left and right of the chest; chains hang in front of them
drapeL_roi = roi_mask(220, 550, 430, 1300)
drapeR_roi = roi_mask(630, 550, 840, 1300)
drapeL_m = cv2.bitwise_and(cv2.bitwise_and(fur_w, drapeL_roi), FIG)
drapeL_m = cv2.bitwise_and(drapeL_m, cv2.bitwise_not(cv2.dilate(chain_m, np.ones((5, 5), np.uint8))))
drapeR_m = cv2.bitwise_and(cv2.bitwise_and(fur_w, drapeR_roi), FIG)
drapeR_m = cv2.bitwise_and(drapeR_m, cv2.bitwise_not(cv2.dilate(chain_m, np.ones((5, 5), np.uint8))))
# head: hood + void
head_roi = roi_mask(240, 0, 820, 660)
head_m = cv2.bitwise_and(FIG, head_roi)
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(chain_m, np.ones((5, 5), np.uint8))))
# arms: fur sleeves at the sides, excluding drapes
armL_m = cv2.bitwise_and(cv2.bitwise_and(fur_w, roi_mask(80, 600, 300, 1450)), FIG)
armL_m = cv2.bitwise_and(armL_m, cv2.bitwise_not(drapeL_roi))
armR_m = cv2.bitwise_and(cv2.bitwise_and(fur_w, roi_mask(760, 600, 980, 1450)), FIG)
armR_m = cv2.bitwise_and(armR_m, cv2.bitwise_not(drapeR_roi))

def clean_small(m, k=5):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

chain_m = clean_small(chain_m)
drapeL_m, drapeR_m = clean_small(drapeL_m), clean_small(drapeR_m)
head_m = clean_small(head_m, 7)
armL_m, armR_m = clean_small(armL_m, 7), clean_small(armR_m, 7)

part_union = head_m | drapeL_m | drapeR_m | chain_m | armL_m | armR_m
body_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))
holes = cv2.bitwise_and(FIG, cv2.bitwise_not(body_m))
holes = cv2.dilate(holes, np.ones((9, 9), np.uint8))
body_rgb = cv2.inpaint(clean, holes, 15, cv2.INPAINT_TELEA)
body_m = clean_small(body_m, 7)
# head holes (from chains) inpainted for self-containment
head_holes = cv2.bitwise_and(cv2.bitwise_and(FIG, head_roi), cv2.bitwise_not(head_m))
head_rgb = cv2.inpaint(clean, cv2.dilate(head_holes, np.ones((7, 7), np.uint8)),
                       10, cv2.INPAINT_TELEA)

layers = [  # (part name, rgb source, mask, rig filename)
    ("01_body",   body_rgb, body_m,   "00_torso.png"),
    ("02_head",   head_rgb, head_m,   "01_face_base.png"),
    ("03_drape_L", clean,   drapeL_m, "02_hair_side.png"),
    ("04_drape_R", clean,   drapeR_m, "03_hair_side.png"),
    ("05_chains", clean,    chain_m,  "04_accessory.png"),
    ("06_arm_L",  clean,    armL_m,   "05_arm_l.png"),
    ("07_arm_R",  clean,    armR_m,   "06_arm_r.png"),
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
    print(f"{name:10s} -> {rig_name:18s} {px:7d} px  bbox={bbox}")

import json
with open(os.path.join(PARTS, "parts_manifest.json"), "w") as f:
    json.dump({"source": "kiko_crop_source.png (1060x1945), from owner-approved kiko-tanaka-robed.webp",
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
