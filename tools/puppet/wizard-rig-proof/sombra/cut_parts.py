#!/usr/bin/env python3
"""Worker C Wave 6 — Sombra Negra part extraction, step 2: cut rig layers.

Input: parts/_clean_bgr.npy + parts/_figmask.npy
Output: parts/*.png + rig_layers/{order}_{role}.png for convert_layers.

Sombra stands in 3/4 profile with arms inside the robe — no arm layers exist
(no arms visible). The rig therefore has no arm params (honest constraint,
same as Hollow).

Layer stack, bottom -> top:
  00_torso     (01_robe): black robe + purple trim + purple runes.
  01_face_base (02_head): hood + black void face (3/4 profile).
  02_accessory (03_chain): gold chains + gold skull pendant (ParamAcc0 sway).
  03_eye_l     (04_eye_L): left white glint (small).
  04_eye_r     (05_eye_R): right white glint.
  NO mouth layer: void-face character. Closed-eye synthesis kept.

Canon: black robe with purple trim = Sombra Negra. Skull pendant per the
pilot still. No grill invented (Ashes only). Council role TBD — not rendered.
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/sombra"
PARTS = os.path.join(OUT, "parts")
RIG = os.path.join(OUT, "rig_layers")
os.makedirs(RIG, exist_ok=True)
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
assert (W, H) == (600, 1040), (W, H)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([8, 90, 90]), np.array([45, 255, 255]))
dark = cv2.inRange(hsv, np.array([0, 0, 4]), np.array([180, 200, 90]))

def with_linework(gold_in_roi, dilate_px=5):
    near = cv2.dilate(gold_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return gold_in_roi | cv2.bitwise_and(dark, near)

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255

# ---- eyes: tight measured ROIs (same as extract)
glintL_roi = roi_mask(258, 108, 292, 142)
glintR_roi = roi_mask(298, 93, 342, 127)
glint_col = cv2.inRange(hsv, np.array([0, 0, 170]), np.array([180, 90, 255]))
eyeL_m = cv2.bitwise_and(glint_col, glintL_roi)
eyeR_m = cv2.bitwise_and(glint_col, glintR_roi)
eyeL_m = cv2.bitwise_and(eyeL_m, FIG); eyeR_m = cv2.bitwise_and(eyeR_m, FIG)

# ---- accessory: chains + skull pendant (chest ROI, gold + its linework)
acc_roi = roi_mask(300, 240, 440, 380)
acc_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, acc_roi)), FIG)

# ---- head: hood + void (3/4 profile). Geometric ROI; the chains hang in
# front of the lower hood, so the head gets a chain-shaped hole (inpainted).
head_roi = roi_mask(210, 70, 430, 460)
head_m = cv2.bitwise_and(FIG, head_roi)
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(acc_m, np.ones((5, 5), np.uint8))))
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(eyeL_m | eyeR_m, np.ones((3, 3), np.uint8))))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyeL_m, eyeR_m = clean_small(eyeL_m), clean_small(eyeR_m)
acc_m = clean_small(acc_m, 3)
head_m = clean_small(head_m, 5)

head_holes = cv2.bitwise_and(cv2.bitwise_and(FIG, head_roi),
                             cv2.bitwise_not(head_m))
head_rgb = cv2.inpaint(clean, cv2.dilate(head_holes, np.ones((5, 5), np.uint8)),
                       8, cv2.INPAINT_TELEA)

# ---- torso: everything else; inpaint holes
part_union = head_m | acc_m | eyeL_m | eyeR_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))
holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

layers = [
    ("01_robe",   robe_rgb, robe_m,   "00_torso.png"),
    ("02_head",   head_rgb, head_m,   "01_face_base.png"),
    ("03_chain",  clean,    acc_m,    "02_accessory.png"),
    ("04_eye_L",  clean,    eyeL_m,   "03_eye_l.png"),
    ("05_eye_R",  clean,    eyeR_m,   "04_eye_r.png"),
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
    json.dump({"source": "sombra_crop_source.png (600x1040)",
               "method": "trim-seeded black-component segmentation + Telea inpainting (Wave-4/5/6 recipe)",
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
