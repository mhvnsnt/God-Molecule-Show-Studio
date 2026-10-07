#!/usr/bin/env python3
"""Worker C Wave 8 — Static BATTLE variant (arm extended, hand on claw-machine
button) part extraction, step 1.

Subject: STATIC (deep-blue rune robe, pale-gold chains, white glove,
blue-white eye glints on black void) reaching for a claw machine.
Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
"Group 14 - arcade.webp" -> static_battle_crop_source.png (540x740).
Same canon character as the Wave-6 Static rig, new battle pose — nothing invented.

Method (proven recipe): programmatic HSV color segmentation on flat cartoon
art + OpenCV Telea inpainting for neighbor removal.
Neighbor removal: claw machine (left edge; yellow frame, screen, panel —
the HAND overlaps it and is spared via hand_keep), Hollow's red robe + gold
chains (right edge).
Honest constraints: full-body visible (no occlusion cut); the claw machine
is background, inpainted out — the hand/arm stay. This source shows NO
pendant plate (chains only) — none grafted (Cipher Wave-6 precedent).
Canon: blue rune embroidery rides on the robe; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/static-battle"
SRC = os.path.join(OUT, "static_battle_crop_source.png")   # 540x740
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 540x740
H, W = img.shape[:2]
assert (W, H) == (540, 740), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def roi(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

# ---- 1. neighbor removal (inpaint)
neighbor = np.zeros((H, W), np.uint8)
# claw machine: everything x<108 except the hand zone
machine_zone = roi(0, 0, 108, H)
hand_keep = roi(60, 340, 175, 435)         # white glove on the button
neighbor |= cv2.bitwise_and(machine_zone, cv2.bitwise_not(hand_keep))
# machine's vertical yellow frame strip inside Static's zone
frame_roi = roi(155, 0, 210, 215)
yellow = cv2.inRange(hsv, np.array([14, 90, 120]), np.array([45, 255, 255]))
neighbor |= cv2.bitwise_and(yellow, frame_roi)
# Hollow: red robe + gold chains on the right edge
red = cv2.inRange(hsv, np.array([5, 110, 70]), np.array([30, 255, 230]))
hollow_zone = roi(445, 0, W, H)
neighbor |= cv2.bitwise_and(red | yellow, hollow_zone)
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 7, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Static color families
blue = cv2.inRange(hsv, np.array([98, 95, 55]), np.array([124, 255, 235]))
# pale-gold chains (washed gold: H 20-40, S 30-120, V 180-255) in the chest ROI
chest_roi = roi(180, 140, 380, 340)
pale_gold = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([20, 30, 180]), np.array([40, 120, 255])), chest_roi)
# white glove in the hand ROI
glove = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 190]), np.array([180, 90, 255])), hand_keep)
# eye glints: muted blue ovals on the void (measured from gridded zoom)
glintL = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([95, 40, 110]), np.array([130, 150, 210])), roi(190, 128, 238, 162))
glintR = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([95, 40, 110]), np.array([130, 150, 210])), roi(250, 125, 308, 160))
# face void: dark navy, largest component in the face ROI
face_roi = roi(170, 60, 370, 230)
navy = cv2.inRange(hsv, np.array([100, 110, 8]), np.array([135, 255, 95]))
face_candidates = cv2.bitwise_and(navy, face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 265) + abs(fcent[i][1] - 140)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)

fig = blue | pale_gold | glove | glintL | glintR | face
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
# subtract neighbor zones outright (sparing the hand)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.bitwise_and(machine_zone, cv2.bitwise_not(hand_keep))))
fig = cv2.bitwise_and(fig, cv2.bitwise_not(frame_roi))
fig = cv2.bitwise_and(fig, cv2.bitwise_not(hollow_zone))
# largest component = Static
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
