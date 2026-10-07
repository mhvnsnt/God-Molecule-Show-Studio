#!/usr/bin/env python3
"""Worker C Wave 5 — Onyx part extraction, step 2: cut rig layers.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + rig_layers/{order}_{role}.png
        (headless layer-dir input for image2live2d's convert_layers).

Layer stack, bottom -> top (draw order):
  00_torso     (01_robe): green robe + staff + orb + sleeve/shoulder studs.
                          The staff is a HELD PROP rigid with the body — it
                          lives on the torso (not a separate accessory) so it
                          can never separate from the gripping hand. Holes
                          inpainted.
  01_face_base (02_head): hood + dark-blue face void. The staff crosses IN
                          FRONT of the left hood tip, so the head has a
                          staff-shaped hole; the staff (robe layer below)
                          shows through it. Bell pixels removed (bells above).
  02_hair_side (03_bell_L): left hood bell  -> sway physics (Ashes-braid analog)
  03_hair_side (04_bell_R): right hood bell -> sway physics
  04_arm_l     (05_arm_L): left crossed arm + white glove (grips staff; glove
                          drawn above the staff = correct grip)
  05_arm_r     (06_arm_R): right crossed arm + white glove
  06_eye_l     (07_eye_L): left lime glint
  07_eye_r     (07_eye_R): right lime glint
  NO accessory layer (no chain on the group-art Onyx) and NO mouth layer:
  void-face character. The black void IS the mouth interior; omitting the
  layer means synthesize_mouth_cavity is a no-op by construction (recipe
  delta vs Ashes, who kept a grill mouth layer). Blush is still skipped
  via the _safe_synth patch in build_rig.py (pink blocks on a void face =
  canon violation, same reasoning as Ashes).

Canon: NO chain on the group-art Onyx (the heavy chains live on the robed
portrait, a different style — not grafted). Two gold sleeve studs + shoulder
stud stay on the robe. Green glints kept; no grill invented (Ashes' grill is
his locked signature only).
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/onyx"
PARTS = os.path.join(OUT, "parts")
RIG = os.path.join(OUT, "rig_layers")
os.makedirs(RIG, exist_ok=True)
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115]))   # linework strokes

def with_linework(gold_in_roi, dilate_px=5):
    near = cv2.dilate(gold_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return gold_in_roi | cv2.bitwise_and(dark, near)

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255
staff_poly = (np.load(os.path.join(PARTS, "_staff_poly.npy")) > 0).astype(np.uint8) * 255

# ---- reusable color masks
face_roi = roi_mask(140, 100, 320, 320)
# glints: bright lime; tight ROI around the face void so the orb's teal glow
# (which spills to x~140) can't leak in
glint_roi = roi_mask(180, 130, 300, 220)
glints = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([50, 120, 180]), np.array([70, 255, 255])), glint_roi)
orb_roi = roi_mask(0, 0, 135, 135)
orb = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([60, 80, 100]), np.array([95, 255, 255])), orb_roi)
bellL_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, roi_mask(45, 165, 105, 220))), FIG)
bellR_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, roi_mask(335, 165, 390, 225))), FIG)

# ---- part masks
# eyes first (the head must exclude them; see below)
n, lab, stats, cent = cv2.connectedComponentsWithStats((glints > 0).astype(np.uint8), 8)
comps = sorted([(stats[i, cv2.CC_STAT_AREA], cent[i][0], i) for i in range(1, n)
                if stats[i, cv2.CC_STAT_AREA] > 40], key=lambda t: t[1])
assert len(comps) >= 2, f"expected 2 glints, found {len(comps)}"
eyeL_m = ((lab == comps[0][2]).astype(np.uint8)) * 255
eyeR_m = ((lab == comps[-1][2]).astype(np.uint8)) * 255
eyeL_m = cv2.bitwise_and(eyeL_m, FIG); eyeR_m = cv2.bitwise_and(eyeR_m, FIG)
# head: hood + face void. The staff crosses IN FRONT of the left hood tip, so
# the head gets a staff-shaped hole; the staff (on the robe layer below) shows
# through it. Bells are separate layers above. GLINT pixels are removed and
# inpainted with void color: the blink is an opacity crossfade (eye_l -> 0,
# eye_closed_l -> 1), so the head must not carry its own copy of the open
# glints or they would ghost through the blink.
head_roi = roi_mask(30, 80, 390, 400)
head_m = cv2.bitwise_and(FIG, head_roi)
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(staff_poly, np.ones((5, 5), np.uint8))))
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(bellL_m | bellR_m, np.ones((3, 3), np.uint8))))
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(eyeL_m | eyeR_m, np.ones((3, 3), np.uint8))))
armL_m = cv2.bitwise_and(FIG, roi_mask(30, 340, 215, 490))
armR_m = cv2.bitwise_and(FIG, roi_mask(215, 340, 390, 490))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

bellL_m, bellR_m = clean_small(bellL_m), clean_small(bellR_m)
armL_m, armR_m = clean_small(armL_m, 5), clean_small(armR_m, 5)
eyeL_m, eyeR_m = clean_small(eyeL_m), clean_small(eyeR_m)
head_m = clean_small(head_m, 5)
# inpaint the glint + staff holes on the head RGB with surrounding colors
# (void dark-blue for glints; the staff hole is covered by the staff layer
# above, but inpaint keeps the layer self-contained regardless)
head_holes = cv2.bitwise_and(cv2.bitwise_and(FIG, head_roi),
                             cv2.bitwise_not(head_m))
head_rgb = cv2.inpaint(clean, cv2.dilate(head_holes, np.ones((5, 5), np.uint8)),
                       8, cv2.INPAINT_TELEA)

# orb pixels join the robe layer (staff+orb are one held prop, rigid with body)
part_union = head_m | bellL_m | bellR_m | armL_m | armR_m | eyeL_m | eyeR_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

# ---- robe: inpaint holes left by removed parts so the layer is self-contained
holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

layers = [  # (part name, rgb source, mask, rig filename)
    ("01_robe",   robe_rgb, robe_m,   "00_torso.png"),
    ("02_head",   head_rgb, head_m,   "01_face_base.png"),
    ("03_bell_L", clean,    bellL_m,  "02_hair_side.png"),
    ("04_bell_R", clean,    bellR_m,  "03_hair_side.png"),
    ("05_arm_L",  clean,    armL_m,   "04_arm_l.png"),
    ("06_arm_R",  clean,    armR_m,   "05_arm_r.png"),
    ("07_eye_L",  clean,    eyeL_m,   "06_eye_l.png"),
    ("07_eye_R",  clean,    eyeR_m,   "07_eye_r.png"),
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
    json.dump({"source": "onyx_crop_source.png (390x960)",
               "method": "ROI x HSV color segmentation + Telea inpainting (Wave-4 Ashes recipe)",
               "stack_bottom_to_top": [m["rig_file"] for m in manifest],
               "layers": manifest}, f, indent=2)
print("manifest written")

# ---- composite check
comp = np.zeros((H, W, 4), np.uint8)
for name, rgb, m, rig_name in layers:
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    comp[m > 0] = rgba[m > 0]
Image.fromarray(cv2.cvtColor(comp, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "_composite_check.png"))
print("composite check saved")
