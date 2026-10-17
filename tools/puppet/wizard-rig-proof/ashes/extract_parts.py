#!/usr/bin/env python3
"""Worker C Wave 4 — Ashes part extraction, step 1: cleanup + base isolation.

Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
        "SWMG group - cartoon 2.webp" -> ashes_crop_source.png (400x864),
        Ashes = red-robed figure, 4th from left. No isolated turnaround
        exists; this group shot is the cleanest full-body Ashes source.

Method: programmatic HSV color segmentation on flat cartoon art +
        OpenCV Telea inpainting for neighbor removal. No rembg (flat
        cartoon colors segment cleanly in HSV; rembg's u2net is trained
        on photos and fringes on cel art).
Neighbor removal: green jester (left edge) + purple council member
        (right edge). The left-edge white glove was verified by zoom to
        rest on the GREEN sleeve = the jester's hand, not Ashes' -> removed.
Canon: diamond-grill smile preserved; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/ashes"
SRC = os.path.join(OUT, "ashes_crop_source.png")   # 400x864
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 400x864
H, W = img.shape[:2]
assert (W, H) == (400, 864), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. neighbor removal (inpaint)
green = cv2.inRange(hsv, np.array([35, 60, 40]), np.array([95, 255, 255]))
purple = cv2.inRange(hsv, np.array([128, 40, 25]), np.array([170, 255, 255]))  # wide: dark purple robe
neighbor = np.zeros((H, W), np.uint8)
neighbor[:, :70] = green[:, :70]            # jester hat fringe (left edge)
neighbor[:, 335:] = purple[:, 335:]         # purple figure fringe (right edge)
neighbor[10:190, 10:70] = 255               # jester gold bell (top-left)
neighbor[285:420, 0:38] = 255              # jester white glove (mid-left)
neighbor[0:864, 340:400] = 255             # purple figure: robe + gold rune strip
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 7, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Ashes color families
red1 = cv2.inRange(hsv, np.array([0, 70, 60]), np.array([12, 255, 255]))
red2 = cv2.inRange(hsv, np.array([168, 70, 60]), np.array([180, 255, 255]))
robe = red1 | red2
maroon = cv2.inRange(hsv, np.array([0, 45, 25]), np.array([12, 255, 90]))   # robe shadow interior
gold = cv2.inRange(hsv, np.array([14, 90, 100]), np.array([48, 255, 255]))  # braids/chain/flames/grill/eyes
glove = cv2.inRange(hsv, np.array([0, 0, 195]), np.array([180, 70, 255]))    # white glove
face_blue = cv2.inRange(hsv, np.array([100, 80, 10]), np.array([130, 255, 78]))  # dark-blue face void
face_roi = np.zeros((H, W), np.uint8)
face_roi[40:265, 50:345] = 255              # face black only valid inside head
face_candidates = cv2.bitwise_and(face_blue, face_roi)
# Keep ONLY the face-void component containing the face centre: the alley
# background is the same dark blue and would otherwise merge in.
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 190) + abs(fcent[i][1] - 140)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
fig = robe | maroon | gold | glove | face
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
fig = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
# Subtract the neighbor zones outright (with 2px margin): inpaint smears
# neighbor hues into these rects, and morphological bleed would otherwise
# re-admit them. Cost: a few px trimmed off Ashes' own silhouette edges
# (documented tradeoff; invisible at rig scale).
fig[8:192, 8:72] = 0        # jester bell zone
fig[283:422, 0:40] = 0      # jester glove zone
fig[0:864, 338:400] = 0     # purple figure strip
fig[420:864, 0:16] = 0      # background wedge, left edge
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)   # catch edge pixels

rgba = cv2.cvtColor(clean, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = fig
Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "00_base_full_figure.png"))
print("base saved; figure px:", int((fig > 0).sum()))
np.save(os.path.join(PARTS, "_figmask.npy"), fig)
np.save(os.path.join(PARTS, "_clean_bgr.npy"), clean)
