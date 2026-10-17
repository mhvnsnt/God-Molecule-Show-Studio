#!/usr/bin/env python3
"""Worker C Wave 6 — Hollow part extraction, step 1: cleanup + base isolation.

Source: trippedd-studio/production/WIZARD_GANG_SHORT_01/stills/
        media-generation-shot06-hollow (pilot still) -> hollow_crop_source.png
        (960x872), Hollow = orange-robed figure (canon: orange robe, darker
        runes, black void face, orange eye glints, layered gold chains +
        HOLLOW name-pendant).
        HONEST CONSTRAINT: the pilot still is a HALF-BODY bust (cut at
        mid-torso). No full-body Hollow source exists in the style refs or
        stills. This rig is a bust puppet — documented in RIG_PROOF_WAVE6.md.

Method: programmatic HSV color segmentation. No neighbor people; the
background is a purple alley with orange bokeh street lights (H~15, same as
the robe) — excluded via a figure x-ROI + component-size filtering. Follows
the Wave-4/5/6 recipe.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/hollow"
SRC = os.path.join(OUT, "hollow_crop_source.png")   # 960x872
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 960x872
H, W = img.shape[:2]
assert (W, H) == (960, 872), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- no neighbor people; background handled in the figure mask
clean = img.copy()

# ---- figure mask from Hollow color families
# robe/hood orange: H~6-10. Bokeh lights share the hue -> x-ROI + size filter.
fig_roi = np.zeros((H, W), np.uint8); fig_roi[:, :690] = 255
robe = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([3, 110, 70]), np.array([22, 255, 255])), fig_roi)
gold = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([5, 100, 120]), np.array([28, 255, 255])), fig_roi)
# face void: dark navy, head ROI; keep only the component containing the
# face centre
face_roi = np.zeros((H, W), np.uint8); face_roi[100:430, 150:570] = 255
face_candidates = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([105, 140, 12]), np.array([132, 255, 75])), face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 360) + abs(fcent[i][1] - 270)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
# glints: bright orange. ROIs measured from the zoomed face (the right
# "glint" first identified was actually the hood edge — verified visually):
# left glint ~(135-225, 198-248), right glint ~(275-355, 200-242).
glintL_roi = np.zeros((H, W), np.uint8); glintL_roi[198:248, 135:225] = 255
glintR_roi = np.zeros((H, W), np.uint8); glintR_roi[200:242, 275:355] = 255
glints = cv2.bitwise_or(
    cv2.bitwise_and(cv2.inRange(hsv, np.array([3, 140, 110]), np.array([18, 255, 255])), glintL_roi),
    cv2.bitwise_and(cv2.inRange(hsv, np.array([3, 140, 110]), np.array([18, 255, 255])), glintR_roi))

fig = robe | gold | face | glints
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
keep = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 2500:
        keep[lab == i] = 255
fig = keep
# Union back the glints explicitly: they are small (<2500px) and often
# disconnected from the void, so the size filter drops them. The tight ROIs
# are figure-exclusive (verified visually).
fig = cv2.bitwise_or(fig, glints)
# Union back small gold figure parts (chain bits) near the silhouette
gold_now = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([5, 100, 120]), np.array([28, 255, 255])), fig_roi)
ng, glab, gstats, _ = cv2.connectedComponentsWithStats(gold_now, 8)
dilated = cv2.dilate(fig, np.ones((31, 31), np.uint8))
for i in range(1, ng):
    comp = (glab == i).astype(np.uint8) * 255
    if (cv2.bitwise_and(comp, dilated) > 0).sum() > 20:
        fig = cv2.bitwise_or(fig, comp)
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
