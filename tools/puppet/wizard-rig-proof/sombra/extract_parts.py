#!/usr/bin/env python3
"""Worker C Wave 6 — Sombra Negra part extraction, step 1: cleanup + base.

Source: trippedd-studio/production/WIZARD_GANG_SHORT_01/stills/
        media-generation-shot07-sombra-v2 (pilot still) -> sombra_crop_source.png
        (600x1040), Sombra Negra = black-robed figure, 3/4 profile (canon:
        black robe with purple trim/edges, purple rune embroidery, black void
        face, small white eye glints, gold chains + gold skull pendant).
        Council role TBD per canon — the rig is just the figure, no role text.

Method: programmatic HSV segmentation. The robe/void/hood are all near-black
(V~38-60); the purple trim (H~122-141) is figure-exclusive and seeds the mask:
black components touching the dilated trim = figure. Background tombs/mist
are brighter (V 105-143) and excluded by the V<55 black range. No neighbor
people. Follows the Wave-4/5/6 recipe.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/sombra"
SRC = os.path.join(OUT, "sombra_crop_source.png")   # 600x1040
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 600x1040
H, W = img.shape[:2]
assert (W, H) == (600, 1040), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

clean = img.copy()   # no neighbor people

# ---- figure mask: the figure is the dominant dark mass inside a geometric
# ROI (x 190-600, y 60-1040). The purple trim range catches the night sky,
# so the trim is restricted to the ROI (the sky there is minimal); the black
# body is the largest dark components in the ROI.
fig_roi = np.zeros((H, W), np.uint8); fig_roi[60:1040, 190:600] = 255
trim = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([112, 70, 25]), np.array([152, 255, 230])), fig_roi)
black = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 4]), np.array([180, 255, 62])), fig_roi)
n, lab, stats, _ = cv2.connectedComponentsWithStats(black, 8)
body = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, 4] > 2500:
        body[lab == i] = 255
print("body px:", int((body > 0).sum()))
# gold: chains + skull pendant
gold = cv2.inRange(hsv, np.array([8, 90, 90]), np.array([45, 255, 255]))
# glints: white. Tight ROIs from the gridded head zoom:
# left glint ~(260-290, 110-140), right glint ~(300-340, 95-125).
glintL_roi = np.zeros((H, W), np.uint8); glintL_roi[108:142, 258:292] = 255
glintR_roi = np.zeros((H, W), np.uint8); glintR_roi[93:127, 298:342] = 255
glints = cv2.bitwise_or(
    cv2.bitwise_and(cv2.inRange(hsv, np.array([0, 0, 170]), np.array([180, 90, 255])), glintL_roi),
    cv2.bitwise_and(cv2.inRange(hsv, np.array([0, 0, 170]), np.array([180, 90, 255])), glintR_roi))

fig = body | trim | gold | glints
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
# Union the trim back explicitly (thin trim lines can fragment below the
# component filter)
fig = cv2.bitwise_or(fig, trim)
# ---- left+right boundaries: the robe's edges are diagonal trim lines.
# Measured from the source (crop coords). Background (tomb/sky/mist) is
# outside this polygon.
BOUNDARY_L = [(250,60),(240,300),(220,500),(200,700),(180,900),(170,1040)]
BOUNDARY_R = [(430,60),(470,300),(525,500),(555,700),(565,900),(575,1040)]
bound = np.zeros((H, W), np.uint8)
pts = np.array(BOUNDARY_L + BOUNDARY_R[::-1], np.int32)
cv2.fillPoly(bound, [pts], 255)
fig = cv2.bitwise_and(fig, bound)
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)

rgba = cv2.cvtColor(clean, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = fig
Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "00_base_full_figure.png"))
print("base saved; figure px:", int((fig > 0).sum()))
np.save(os.path.join(PARTS, "_figmask.npy"), fig)
np.save(os.path.join(PARTS, "_clean_bgr.npy"), clean)
dbg = clean.copy()
red = np.zeros_like(clean); red[:, :] = (0, 0, 255)
dbg = cv2.addWeighted(clean, 0.45, red, 0.55, 0)
dbg[fig == 0] = clean[fig == 0]
Image.fromarray(cv2.cvtColor(dbg, cv2.COLOR_BGR2RGB)).save(os.path.join(PARTS, "_debug_figmask.png"))
print("debug overlay saved")
