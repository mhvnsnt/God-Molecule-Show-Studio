#!/usr/bin/env python3
"""Worker C Wave 8 — Kiko BATTLE variant (fists raised, victory/battle stance)
part extraction, step 1.

Subject: KIKO (white fur robe + hood, gold chains + KIKO name-pendant,
white eye glints on black void) with both fists raised.
Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
"Group 10 - fireworks.webp" -> kiko_battle_crop_source.png (500x912).
Same canon character as the Wave-6 Kiko rig, new battle pose — nothing invented.

Method (proven recipe): programmatic HSV color segmentation on flat cartoon
art + OpenCV Telea inpainting for neighbor removal.
Neighbor removal: fireworks burst (top-center-right, orange/pink/white —
behind the hood, not part of Kiko), night-sky background.
Honest constraints: figure is cut by the frame's bottom edge (~y 880, no legs
in frame — no legs cut or invented); KIKO name-pendant text preserved
byte-for-byte from the owner's source art (same keep-or-cut flag as Wave-6
Static's SWMG plate); no mouth art — pipeline no-mouth path.
Canon: white fur + KIKO pendant; black-void face + white glints; no design
alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/kiko-battle"
SRC = os.path.join(OUT, "kiko_battle_crop_source.png")   # 500x912
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 500x912
H, W = img.shape[:2]
assert (W, H) == (500, 912), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def roi(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

# ---- 1. neighbor removal (inpaint)
# fireworks burst: orange/pink/white streaks top-center-right (behind hood)
fw_roi = roi(240, 0, 440, 180)
orange = cv2.inRange(hsv, np.array([8, 90, 150]), np.array([32, 255, 255]))
pink_fw = cv2.inRange(hsv, np.array([130, 70, 150]), np.array([175, 255, 255]))
white_fw = cv2.inRange(hsv, np.array([0, 0, 210]), np.array([180, 60, 255]))
neighbor = cv2.bitwise_and(orange | pink_fw, fw_roi)
# white firework cores: only where NOT Kiko's fist (fist is x>395)
white_fw_roi = roi(240, 0, 395, 180)
neighbor |= cv2.bitwise_and(white_fw, white_fw_roi)
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 7, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Kiko color families
# white fur (lavender-white): low sat, high value
fur = cv2.inRange(hsv, np.array([0, 0, 165]), np.array([180, 70, 255]))
# gold chains + KIKO pendant
gold = cv2.inRange(hsv, np.array([14, 90, 120]), np.array([45, 255, 255]))
# face void: dark navy, largest component in the face ROI
face_roi = roi(140, 250, 410, 500)
navy = cv2.inRange(hsv, np.array([100, 100, 5]), np.array([135, 255, 90]))
face_candidates = cv2.bitwise_and(navy, face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 275) + abs(fcent[i][1] - 375)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
# eye glints: white, tight measured ROIs
glintL = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 70, 255])), roi(195, 268, 248, 308))
glintR = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 70, 255])), roi(292, 272, 352, 312))

fig = fur | gold | face | glintL | glintR
fig = cv2.bitwise_and(fig, cv2.bitwise_not(neighbor))  # keep fireworks out
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
fig = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)

rgba = cv2.cvtColor(clean, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = fig
Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "00_base_full_figure.png"))
print("base saved; figure px:", int((fig > 0).sum()))
np.save(os.path.join(PARTS, "_figmask.npy"), fig)
np.save(os.path.join(PARTS, "_clean_bgr.npy"), clean)
