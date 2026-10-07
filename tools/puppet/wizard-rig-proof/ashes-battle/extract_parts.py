#!/usr/bin/env python3
"""Worker C Wave 7 — Ashes BATTLE variant (mid-dunk) part extraction, step 1.

Subject: ASHES (scarlet-red robe, diamond-grill smile, blonde braids, gold
$S pendant) in a mid-air basketball dunk pose, right arm raised holding the
ball. Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
"Group 11 - basketball.webp" -> ashes_battle_crop_source.png (780x885).
Same canon character as the Wave-4 Ashes rig, new battle pose — nothing invented.

Method (proven recipe): programmatic HSV color segmentation on flat cartoon
art + OpenCV Telea inpainting for neighbor removal.
Neighbor removal: Onyx's staff + white glove + green hat tip (left edge),
Echo's pink fringe + name plate (left edge), Theory's purple fringe
(bottom-right corner).
Canon: diamond-grill smile preserved; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/ashes-battle"
SRC = os.path.join(OUT, "ashes_battle_crop_source.png")   # 780x885
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 780x885
H, W = img.shape[:2]
assert (W, H) == (780, 885), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. neighbor removal (inpaint)
green = cv2.inRange(hsv, np.array([55, 60, 40]), np.array([100, 255, 255]))   # Onyx green
pink = cv2.inRange(hsv, np.array([150, 90, 80]), np.array([180, 255, 255]))   # Echo magenta fringe
pink2 = cv2.inRange(hsv, np.array([90, 100, 100]), np.array([118, 255, 255])) # Echo bright pink
purple = cv2.inRange(hsv, np.array([128, 40, 25]), np.array([170, 255, 255])) # Theory purple
neighbor = np.zeros((H, W), np.uint8)
neighbor[250:885, 130:225] = np.maximum(neighbor[250:885, 130:225], green[250:885, 130:225])  # Onyx staff
neighbor[430:575, 130:225] = 255          # Onyx white glove on staff
neighbor[280:375, 190:275] = np.maximum(neighbor[280:375, 190:275], green[280:375, 190:275])  # jester hat tip
neighbor[:, :68] = np.maximum(neighbor[:, :68], pink[:, :68])     # Echo fringe (left edge)
neighbor[:, :68] = np.maximum(neighbor[:, :68], pink2[:, :68])
neighbor[520:620, 0:70] = 255             # Echo name plate fragment
neighbor[770:, 750:] = np.maximum(neighbor[770:, 750:], purple[770:, 750:])   # Theory fringe
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 7, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Ashes color families
red1 = cv2.inRange(hsv, np.array([0, 70, 60]), np.array([12, 255, 255]))
red2 = cv2.inRange(hsv, np.array([168, 70, 60]), np.array([180, 255, 255]))
robe = red1 | red2
maroon = cv2.inRange(hsv, np.array([0, 45, 25]), np.array([12, 255, 90]))   # robe shadow interior
gold = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([42, 255, 255])) # braids/eyes/grill/chain/pendant
white_full = cv2.inRange(hsv, np.array([0, 0, 190]), np.array([180, 45, 255]))   # glove / sneaker white (tight S: court tan excluded)
white_roi = np.zeros((H, W), np.uint8)
white_roi[95:185, 405:505] = 255      # glove on ball
white_roi[620:800, 420:725] = 255     # sneakers (both)
white = cv2.bitwise_and(white_full, white_roi)
ball = cv2.inRange(hsv, np.array([4, 150, 150]), np.array([17, 255, 255]))  # basketball orange
face_roi = np.zeros((H, W), np.uint8)
face_roi[140:315, 600:745] = 255          # face void only valid inside head
navy = cv2.inRange(hsv, np.array([110, 120, 18]), np.array([132, 255, 80]))  # dark navy (face void + pants)
face_candidates = cv2.bitwise_and(navy, face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 672) + abs(fcent[i][1] - 230)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
pants_roi = np.zeros((H, W), np.uint8)
pants_roi[490:670, 555:700] = 255         # dark pants visible below robe (kept tight: fence is same navy)
pants_raw = cv2.bitwise_and(navy, pants_roi)
# keep only pants components connected to the torso (drops the disconnected
# chain-link fence patches that share the navy hue)
npc, plab, pstats, _ = cv2.connectedComponentsWithStats(pants_raw, 8)
pants = np.zeros((H, W), np.uint8)
for i in range(1, npc):
    x0, y0 = pstats[i, cv2.CC_STAT_LEFT], pstats[i, cv2.CC_STAT_TOP]
    x1, y1 = x0 + pstats[i, cv2.CC_STAT_WIDTH], y0 + pstats[i, cv2.CC_STAT_HEIGHT]
    if y0 < 560 and pstats[i, cv2.CC_STAT_AREA] > 1500:   # touches torso, not a fence fragment
        pants[plab == i] = 255
# sneakers: dark uppers share the navy hue; catch them in shoe ROIs
shoe_roi = np.zeros((H, W), np.uint8)
shoe_roi[625:795, 430:535] = 255    # left sneaker (dark)
shoe_roi[595:700, 615:730] = 255    # right sneaker (dark upper)
shoes_dark = cv2.bitwise_and(navy, shoe_roi)
fig = robe | maroon | gold | white | ball | face | pants | shoes_dark
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
fig = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
# Subtract the chain-link fence (shares the navy hue, sits behind the legs):
# lighter navy V-band, only valid in the lower-right background zone.
fence_roi = np.zeros((H, W), np.uint8)
fence_roi[540:885, 420:780] = 255
fence = cv2.inRange(hsv, np.array([105, 40, 66]), np.array([135, 255, 150]))
fence = cv2.bitwise_and(fence, fence_roi)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(fence))
# court floor (tan, caught via morphology bridging near the shoes)
court_roi = np.zeros((H, W), np.uint8)
court_roi[690:885, 400:780] = 255
court = cv2.inRange(hsv, np.array([15, 35, 140]), np.array([32, 140, 235]))
court = cv2.bitwise_and(court, court_roi)
# spare the shoes' gold trim (high saturation) — only dull tan goes
court = cv2.bitwise_and(court, cv2.bitwise_not(cv2.inRange(hsv, np.array([0, 140, 0]), np.array([180, 255, 255]))))
fig = cv2.bitwise_and(fig, cv2.bitwise_not(court))
# purple-ish fence shadow remnant right of the right shoe
fence2_roi = np.zeros((H, W), np.uint8)
fence2_roi[540:720, 590:780] = 255
fence2 = cv2.bitwise_and(cv2.inRange(hsv, np.array([138, 35, 55]), np.array([162, 130, 125])), fence2_roi)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(fence2))
# navy wedge of background visible between the robe's right edge and the
# pants leg: remove navy in the wedge unless it touches the robe itself
wedge_roi = np.zeros((H, W), np.uint8)
wedge_roi[520:665, 588:652] = 255
wedge = cv2.bitwise_and(navy, wedge_roi)
near_robe = cv2.dilate(robe | maroon, np.ones((9, 9), np.uint8))   # 4px halo: strip reads as bg, not robe shadow
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.bitwise_and(wedge, cv2.bitwise_not(near_robe))))
# fence diamonds left of the right shoe (connected to the leg mass, so the
# component filter can't drop them): hard kill strip, shoe starts at x~645
kill = np.zeros((H, W), np.uint8)
kill[598:706, 595:643] = 255
fig = cv2.bitwise_and(fig, cv2.bitwise_not(kill))
fig[250:885, 125:230] = 0    # staff/glove zone
fig[280:375, 185:280] = 0    # hat tip zone
fig[:, :70] = 0              # Echo fringe
fig[770:, 748:] = 0          # Theory fringe
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)

rgba = cv2.cvtColor(clean, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = fig
Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "00_base_full_figure.png"))
print("base saved; figure px:", int((fig > 0).sum()))
np.save(os.path.join(PARTS, "_figmask.npy"), fig)
np.save(os.path.join(PARTS, "_clean_bgr.npy"), clean)
