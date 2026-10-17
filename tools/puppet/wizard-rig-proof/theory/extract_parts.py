#!/usr/bin/env python3
"""Worker C Wave 6 — Theory part extraction, step 1: cleanup + base isolation.

Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
        "SWMG group - cartoon 2.webp" -> theory_crop_source.png (270x910),
        Theory = purple-robed figure, 5th from left (canon: purple robe,
        gold celestial runes, black void face, purple eye glints,
        gold chains + THEORY name-pendant, white gloves, crossed arms).
        NOTE: purple robe in-cartoon = Theory (THEORY pendant), NOT the
        Narrator — the Narrator is voice-only in the cartoon per canon law.

Method: programmatic HSV color segmentation on the flat cartoon art
(no rembg — u2net is photo-trained and fringes on cel art) + OpenCV Telea
inpainting for thin neighbor slivers. Follows the Wave-4/5 recipe.

Crop geometry (learned the hard way): the first crop (x=990) caught Ashes'
whole left side (red robe + braid + her white glove); Telea inpaint cannot
fill a 75px-wide strip, so the source was re-cropped tighter at x=1060.
Only thin neighbor slivers remain at the left edge (Ashes' red H~178 sliver
x<25, her glove remnant x<48 in the arm band) — inpaint handles those.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/theory"
SRC = os.path.join(OUT, "theory_crop_source.png")   # 270x910
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 270x910
H, W = img.shape[:2]
assert (W, H) == (270, 910), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. neighbor removal (thin slivers only)
red = cv2.inRange(hsv, np.array([168, 100, 60]), np.array([180, 255, 255]))
neighbor = np.zeros((H, W), np.uint8)
neighbor[:, :25] = cv2.bitwise_or(neighbor[:, :25], red[:, :25])
neighbor[0:910, :12] = 255                                # hard left edge
# Ashes' white glove remnant at the left edge of the arm band (Theory's own
# right glove lives at x~180-230 — untouched). Her flame trim (orange H~13,
# caught by the gold mask) also intrudes at the top-left.
flame = cv2.inRange(hsv, np.array([8, 100, 100]), np.array([32, 255, 255]))
neighbor[:, :55] = cv2.bitwise_or(neighbor[:, :55], flame[:, :55])
glove_band = np.zeros((H, W), np.uint8); glove_band[250:330, 0:48] = 255
neighbor = cv2.bitwise_or(neighbor, cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 80, 255])), glove_band))
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 5, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Theory color families
# robe purple: sampled H=147 S=200 V=88 (hood peak darker, rune gold separate)
robe = cv2.inRange(hsv, np.array([136, 85, 32]), np.array([163, 255, 180]))
gold = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
# gloves: white (sampled S=25 V=255), arm band only
glove_roi = np.zeros((H, W), np.uint8); glove_roi[230:400, 0:270] = 255
glove = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 175]), np.array([180, 90, 255])), glove_roi)
# face void: dark navy-purple, head ROI; keep only the component containing
# the face centre (alley background is equally dark)
face_roi = np.zeros((H, W), np.uint8); face_roi[55:215, 100:220] = 255
face_candidates = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([95, 55, 5]), np.array([175, 255, 80])), face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 160) + abs(fcent[i][1] - 140)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
# glints: bright purple/pink, tight ROI on the face. NOTE: the LEFT glint is
# dimmer (V~96) than the right (V~248) in the source art — V floor is 90.
glint_roi = np.zeros((H, W), np.uint8); glint_roi[85:140, 110:205] = 255
glints = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([136, 100, 90]), np.array([168, 255, 255])), glint_roi)

fig = robe | gold | glove | face | glints
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
keep = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 1000:
        keep[lab == i] = 255
fig = keep
# Union back small gold figure parts (rune tips) near the silhouette
gold_now = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
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
