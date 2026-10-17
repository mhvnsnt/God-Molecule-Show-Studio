#!/usr/bin/env python3
"""Worker C Wave 6 — Cipher part extraction, step 1: cleanup + base isolation.

Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
        "SWMG group - cartoon 2.webp" -> cipher_crop_source.png (305x910),
        Cipher = yellow-robed figure, 8th from left (canon: yellow robe,
        darker-gold runes, black void face, yellow eye glints, heavy gold
        chains, white glove, crossed arms).

Method: programmatic HSV color segmentation + Telea inpainting of the thin
Sombra neighbor sliver (black robe + purple trim, left edge). Follows the
Wave-4/5/6 recipe.

Cipher-specific: the robe yellow (H~21) and the chain gold are NOT
color-separable (measured: chain-band gold med H=20 vs robe H=21). The
accessory cut therefore uses black-outline proximity (cut_parts.py); if the
chains fragment, they stay on the torso (documented fallback, same
precedent as Onyx's staff-on-torso).
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/cipher"
SRC = os.path.join(OUT, "cipher_crop_source.png")   # 305x910
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 305x910
H, W = img.shape[:2]
assert (W, H) == (305, 910), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. neighbor removal (thin slivers only)
# Sombra (left): black robe + purple trim at x<18
black = cv2.inRange(hsv, np.array([0, 0, 5]), np.array([180, 255, 70]))
ptrim = cv2.inRange(hsv, np.array([110, 50, 25]), np.array([150, 255, 160]))
neighbor = np.zeros((H, W), np.uint8)
neighbor[:, :20] = cv2.bitwise_or(neighbor[:, :20], (black | ptrim)[:, :20])
neighbor[0:910, :10] = 255
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 5, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Cipher color families
# robe yellow: sampled H=20-21 S=172-255 V=197-252
robe = cv2.inRange(hsv, np.array([15, 110, 130]), np.array([28, 255, 255]))
# gloves: white, arm band only
glove_roi = np.zeros((H, W), np.uint8); glove_roi[250:380, 150:305] = 255
glove = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 175]), np.array([180, 90, 255])), glove_roi)
# face void: dark blue, head ROI; keep only the component containing the
# face centre (alley background is equally dark)
face_roi = np.zeros((H, W), np.uint8); face_roi[55:215, 95:210] = 255
face_candidates = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([100, 130, 8]), np.array([135, 255, 70])), face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 152) + abs(fcent[i][1] - 135)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
# glints: bright yellow. Tight ROIs measured from the zoomed source:
# left glint ~(110-140, 90-118), right glint ~(150-182, 88-115).
glintL_roi = np.zeros((H, W), np.uint8); glintL_roi[88:120, 108:142] = 255
glintR_roi = np.zeros((H, W), np.uint8); glintR_roi[86:118, 148:184] = 255
glints = cv2.bitwise_or(
    cv2.bitwise_and(cv2.inRange(hsv, np.array([20, 100, 180]), np.array([38, 255, 255])), glintL_roi),
    cv2.bitwise_and(cv2.inRange(hsv, np.array([20, 100, 180]), np.array([38, 255, 255])), glintR_roi))

fig = robe | glove | face | glints
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
keep = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 1000:
        keep[lab == i] = 255
fig = keep
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
