#!/usr/bin/env python3
"""Worker C Wave 6 — Theory part extraction, step 2: cut rig layers.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + rig_layers/{order}_{role}.png
        (headless layer-dir input for image2live2d's convert_layers).

Layer stack, bottom -> top (draw order):
  00_torso     (01_robe): purple robe + gold celestial runes. Holes inpainted.
  01_face_base (02_head): hood + dark void face. Chains cross IN FRONT of the
                          hood's lower part, so the head gets a chain-shaped
                          hole (inpainted with hood purple); the chains
                          (accessory layer above) show through it.
  02_arm_l     (03_arm_L): left crossed arm: purple sleeve + white glove.
  03_arm_r     (04_arm_R): right crossed arm: purple sleeve + white glove.
  04_accessory (05_chain): gold chains + THEORY name-pendant (ParamAcc0 sway).
  05_eye_l     (06_eye_L): left purple glint.
  06_eye_r     (07_eye_R): right purple glint.
  NO mouth layer: void-face character. The black void IS the mouth interior;
  omitting the layer makes synthesize_mouth_cavity a no-op by construction
  (same policy as the Wave-5 void-face rigs). Blush skipped via the
  _safe_synth patch in build_rig.py (pink blocks on a void face = canon
  violation). Closed-eye synthesis kept: real blink for the purple glints.

Canon: purple robe + THEORY pendant = Theory in-fiction (canon law: the
Narrator is voice-only in the cartoon; the purple robe on screen is Theory).
No grill invented (Ashes' grill is his locked signature only). Glint color
is purple-pink per the group-2 source (group-1 shows white — source fidelity
wins, documented in RIG_PROOF_WAVE6.md).
"""
import cv2
import numpy as np
from PIL import Image
import os
import json

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/theory"
PARTS = os.path.join(OUT, "parts")
RIG = os.path.join(OUT, "rig_layers")
os.makedirs(RIG, exist_ok=True)
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
assert (W, H) == (270, 910), (W, H)
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

# ---- eyes first (head must exclude them)
glint_roi = roi_mask(110, 85, 205, 140)
glints = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([136, 100, 90]), np.array([168, 255, 255])), glint_roi)
n, lab, stats, cent = cv2.connectedComponentsWithStats((glints > 0).astype(np.uint8), 8)
comps = sorted([(stats[i, cv2.CC_STAT_AREA], cent[i][0], i) for i in range(1, n)
                if stats[i, cv2.CC_STAT_AREA] > 30], key=lambda t: t[1])
assert len(comps) >= 2, f"expected 2 glints, found {len(comps)}"
eyeL_m = ((lab == comps[0][2]).astype(np.uint8)) * 255
eyeR_m = ((lab == comps[-1][2]).astype(np.uint8)) * 255
eyeL_m = cv2.bitwise_and(eyeL_m, FIG); eyeR_m = cv2.bitwise_and(eyeR_m, FIG)

# ---- accessory: chains + THEORY pendant (chest ROI, gold + its linework)
acc_roi = roi_mask(90, 150, 235, 350)
acc_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, acc_roi)), FIG)

# ---- head: hood + void; chain-shaped hole where the accessory crosses
head_roi = roi_mask(55, 0, 250, 240)
head_m = cv2.bitwise_and(FIG, head_roi)
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(acc_m, np.ones((5, 5), np.uint8))))
head_m = cv2.bitwise_and(head_m, cv2.bitwise_not(cv2.dilate(eyeL_m | eyeR_m, np.ones((3, 3), np.uint8))))

# ---- arms: crossed-arm band split at figure centre
armL_m = cv2.bitwise_and(FIG, roi_mask(0, 240, 135, 400))
armR_m = cv2.bitwise_and(FIG, roi_mask(135, 240, 270, 400))
# arms must not swallow the pendant/chains
armL_m = cv2.bitwise_and(armL_m, cv2.bitwise_not(cv2.dilate(acc_m, np.ones((5, 5), np.uint8))))
armR_m = cv2.bitwise_and(armR_m, cv2.bitwise_not(cv2.dilate(acc_m, np.ones((5, 5), np.uint8))))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyeL_m, eyeR_m = clean_small(eyeL_m), clean_small(eyeR_m)
# NOTE: accessory uses k=3 — the chains are thin (~8px); MORPH_OPEN with k=5
# eroded them to fragments (verified visually).
acc_m = clean_small(acc_m, 3)
armL_m, armR_m = clean_small(armL_m, 5), clean_small(armR_m, 5)
head_m = clean_small(head_m, 5)

# inpaint accessory + glint holes on the head RGB so the layer is self-contained
head_holes = cv2.bitwise_and(cv2.bitwise_and(FIG, head_roi),
                             cv2.bitwise_not(head_m))
head_rgb = cv2.inpaint(clean, cv2.dilate(head_holes, np.ones((5, 5), np.uint8)),
                       8, cv2.INPAINT_TELEA)

# ---- torso: everything else; inpaint holes left by removed parts
part_union = head_m | armL_m | armR_m | acc_m | eyeL_m | eyeR_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))
holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

layers = [  # (part name, rgb source, mask, rig filename)
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
    json.dump({"source": "theory_crop_source.png (270x910)",
               "method": "ROI x HSV color segmentation + Telea inpainting (Wave-4/5 recipe)",
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
