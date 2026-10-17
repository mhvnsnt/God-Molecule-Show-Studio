#!/usr/bin/env python3
"""Worker C Wave 7 — Echo BATTLE variant (spray can raised) part extraction, step 2.

Input: parts/_clean_bgr.npy (neighbor-free BGR) + parts/_figmask.npy
Output: parts/*.png (one RGBA layer per rig part) + parts_manifest.json.

Layer stack, bottom -> top:
  01_robe, 02_head, 03_accessory (chains + ECHO pendant + ring),
  04_arm (pink sleeve), 05_hand, 06_spray_can (prop + mist), 07_eyes

Method: ROI rectangles x HSV color masks. Occluded areas (robe under the
arm/head/can) are Telea-inpainted so each layer is self-contained.
Honest constraints: 3/4-body (rail occludes below y~655 — no legs cut);
the spray can is a scene prop on its own layer, not puppeted; Echo has no
grill/mouth art — the pipeline's "mouth simply stays shut" path applies.
Canon: ECHO name-pendant text preserved; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/echo-battle"
PARTS = os.path.join(OUT, "parts")
clean = np.load(os.path.join(PARTS, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS, "_figmask.npy"))
H, W = fig.shape
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

gold = cv2.inRange(hsv, np.array([14, 90, 110]), np.array([42, 255, 255]))
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115]))
white = cv2.inRange(hsv, np.array([0, 0, 195]), np.array([180, 80, 255]))
silver = cv2.inRange(hsv, np.array([0, 0, 165]), np.array([180, 110, 255]))
blue_cap_full = cv2.inRange(hsv, np.array([98, 90, 70]), np.array([122, 255, 210]))
cap_roi = np.zeros((H, W), np.uint8)
cap_roi[190:230, 160:216] = 255   # the can's cap is at the top; Static's blue is lower
blue_cap = cv2.bitwise_and(blue_cap_full, cap_roi)
red1 = cv2.inRange(hsv, np.array([0, 90, 90]), np.array([10, 255, 255]))
red2 = cv2.inRange(hsv, np.array([168, 90, 90]), np.array([180, 255, 255]))

def with_linework(mask_in_roi, dilate_px=7):
    near = cv2.dilate(mask_in_roi, np.ones((dilate_px, dilate_px), np.uint8))
    return mask_in_roi | cv2.bitwise_and(dark, near)

def roi_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

FIG = (fig > 0).astype(np.uint8) * 255

# ---- part masks
head_roi = roi_mask(200, 55, 365, 282)
eyeL_m = cv2.bitwise_and(white, roi_mask(278, 110, 312, 138))
eyeR_m = cv2.bitwise_and(white, roi_mask(318, 106, 350, 134))
eyes_m = cv2.bitwise_and(eyeL_m | eyeR_m, FIG)
acc_roi = roi_mask(230, 195, 352, 342)
ring_roi = roi_mask(162, 268, 198, 302)
acc_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(gold, acc_roi | ring_roi)), acc_roi | ring_roi)
acc_m = cv2.bitwise_and(acc_m, FIG)
hand_roi = roi_mask(118, 208, 214, 306)
pale = cv2.inRange(hsv, np.array([0, 0, 185]), np.array([180, 130, 255]))
can_body = silver | blue_cap | red1 | red2
hand_m = cv2.bitwise_and(pale, hand_roi)
hand_m = cv2.bitwise_and(hand_m, cv2.bitwise_not(can_body))   # can body stays on the prop layer
hand_m = cv2.bitwise_and(hand_m, FIG)
hand_m = cv2.bitwise_and(hand_m, cv2.bitwise_not(cv2.bitwise_and(gold, ring_roi)))  # ring stays on accessory
# The gripping hand is too fragmented for its own layer (27 px survive in
# FIG) — it merges into the arm as the arm's end, holding the can prop.
# The arm is PINK sleeve + PALE hand; Static's blue robe peeks into the
# ROI and must be excluded by color. Pink spans H~112-163 here, so kill
# the blue explicitly rather than keying pink.
arm_roi = roi_mask(135, 205, 262, 492)
static_blue = cv2.inRange(hsv, np.array([95, 80, 50]), np.array([125, 255, 220]))
arm_m = cv2.bitwise_and(FIG, arm_roi)
arm_m = arm_m | hand_m
arm_m = cv2.bitwise_and(arm_m, cv2.bitwise_not(static_blue))
# keep the can prop and accessory out of the arm
arm_m = cv2.bitwise_and(arm_m, cv2.bitwise_not(can_body))
arm_m = cv2.bitwise_and(arm_m, cv2.bitwise_not(cv2.bitwise_and(gold, acc_roi | ring_roi)))
# spray can prop: silver body + blue cap + red nozzle + pale mist
# (can_roi starts at x=160: Static's blue peeks left of that)
can_roi = roi_mask(160, 190, 216, 336)
mist_roi = roi_mask(120, 125, 212, 215)
mist = cv2.bitwise_and(cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 70, 255])), mist_roi)
can_m = cv2.bitwise_and(with_linework(cv2.bitwise_and(silver | blue_cap | red1 | red2, can_roi), 5), can_roi)
can_m = cv2.bitwise_and(can_m | cv2.bitwise_and(mist, FIG), FIG)
# keep the can out of the hand layer (hand grips it; can body is the top prop)
# (hand_m already excludes can_body pixels above)
head_m = cv2.bitwise_and(FIG, head_roi)
# robe = figure minus actual part masks; inpaint holes
part_union = head_m | acc_m | arm_m | can_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

def clean_small(m, k=3):
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))

eyes_m = clean_small(eyes_m)
acc_m = clean_small(acc_m)
arm_m = clean_small(arm_m, 5)
can_m = clean_small(can_m, 3)
head_m = clean_small(head_m, 5)
part_union = head_m | acc_m | arm_m | can_m
robe_m = cv2.bitwise_and(FIG, cv2.bitwise_not(part_union))

holes = cv2.bitwise_and(FIG, cv2.bitwise_not(robe_m))
holes = cv2.dilate(holes, np.ones((7, 7), np.uint8))
robe_rgb = cv2.inpaint(clean, holes, 12, cv2.INPAINT_TELEA)
robe_m = clean_small(robe_m, 5)

layers = [
    ("01_robe", robe_rgb, robe_m),
    ("02_head", clean, head_m),
    ("03_accessory", clean, acc_m),
    ("04_arm", clean, arm_m),
    ("05_spray_can", clean, can_m),
    ("06_eyes", clean, eyes_m),
]

manifest = []
for name, rgb, m in layers:
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    px = int((m > 0).sum())
    Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, f"{name}.png"))
    ys, xs = np.nonzero(m)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if px else None
    manifest.append({"layer": name, "pixels": px, "bbox_xyxy": bbox})
    print(f"{name}: {px} px  bbox={bbox}")

import json
with open(os.path.join(PARTS, "parts_manifest.json"), "w") as f:
    json.dump({"source": "echo_battle_crop_source.png (515x725)",
               "method": "ROI x HSV color segmentation + Telea inpainting",
               "note": "battle variant: spray-can-raised pose; 3/4-body (rail occlusion); can is a scene prop layer; no mouth art (pipeline no-mouth path)",
               "stack_bottom_to_top": [m["layer"] for m in manifest],
               "layers": manifest}, f, indent=2)
print("manifest written")

comp = np.zeros((H, W, 4), np.uint8)
for name, rgb, m in layers:
    rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    a = (m > 0)
    comp[a] = rgba[a]
Image.fromarray(cv2.cvtColor(comp, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "_composite_check.png"))
print("composite check saved")
