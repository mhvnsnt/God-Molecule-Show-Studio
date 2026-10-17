#!/usr/bin/env python3
"""Worker C Wave 6 — Static part extraction, step 1: cleanup + base isolation.

Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
        "SWMG group - cartoon 2.webp" -> static_crop_source.png (245x910),
        Static = deep-blue-robed figure, 6th from left (canon: deep blue robe,
        blue runes, black void face, blue eye glints, layered gold chains,
        SWMG name-pendant, white gloves, crossed arms).
        CANON FLAG: the pendant reads "SWMG" in the owner-generated source art.
        The canon guard forbids rendering "Shadow Wizard Money Gang" as NEW
        in-world text; this rig preserves the source likeness byte-for-byte
        (no new text authored). Flagged for the owner's call in
        RIG_PROOF_WAVE6.md.

Method: programmatic HSV color segmentation + Telea inpainting of the thin
Theory-purple neighbor sliver (left edge). Follows the Wave-4/5/6 recipe.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/static"
SRC = os.path.join(OUT, "static_crop_source.png")   # 245x910
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 245x910
H, W = img.shape[:2]
assert (W, H) == (245, 910), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. neighbor removal (thin slivers only)
# Theory (left): purple robe sliver at x<15
purple = cv2.inRange(hsv, np.array([132, 90, 30]), np.array([165, 255, 200]))
neighbor = np.zeros((H, W), np.uint8)
neighbor[:, :18] = cv2.bitwise_or(neighbor[:, :18], purple[:, :18])
neighbor[0:910, :10] = 255
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 5, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Static color families
# robe deep blue: sampled H=113-116 S=169-193 V=113-172 (runes lighter)
robe = cv2.inRange(hsv, np.array([103, 100, 85]), np.array([124, 255, 210]))
gold = cv2.inRange(hsv, np.array([12, 80, 140]), np.array([45, 255, 255]))
# gloves: white, arm band only
glove_roi = np.zeros((H, W), np.uint8); glove_roi[230:400, 0:245] = 255
glove = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 175]), np.array([180, 90, 255])), glove_roi)
# face void: dark navy, head ROI; keep only the component containing the
# face centre (alley background is equally dark)
face_roi = np.zeros((H, W), np.uint8); face_roi[45:205, 60:190] = 255
face_candidates = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([105, 140, 8]), np.array([128, 255, 75])), face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 125) + abs(fcent[i][1] - 125)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
# glints: bright blue, tight ROI on the face
glint_roi = np.zeros((H, W), np.uint8); glint_roi[70:120, 75:170] = 255
glints = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([103, 90, 110]), np.array([122, 255, 255])), glint_roi)

fig = robe | gold | glove | face | glints
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
keep = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 1000:
        keep[lab == i] = 255
fig = keep
# Union back small gold figure parts (chain bits) near the silhouette
gold_now = cv2.inRange(hsv, np.array([12, 80, 140]), np.array([45, 255, 255]))
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
