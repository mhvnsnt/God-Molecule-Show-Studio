#!/usr/bin/env python3
"""Worker C Wave 10 — THEORY BATTLE variant (fist raised) part extraction, step 1.

Subject: THEORY (purple robe with rune trim, gold chains + THEORY name-pendant,
white eye glints on black void, right fist raised high in a white glove).
Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
"Group 10 - fireworks.webp" -> theory_battle_crop_source.png (430x882).
Same canon character as the Wave-6 Theory base rig, new battle pose —
nothing invented.

Method (proven recipe): polygon silhouette x HSV color masks + OpenCV Telea
inpainting for neighbor removal (Ashes' red robe at left edge, Static's blue
arm at top-right corner, stone ledge at bottom, fireworks sky background).
Honest constraints: fist slightly near crop top (y~30) but fully in frame;
figure cut by the stone ledge (3/4-body, no legs) — none invented.
Canon: purple robe + rune trim, white glints, gold chains + THEORY plate —
matches the fireworks source; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/theory-battle"
SRC = os.path.join(OUT, "theory_battle_crop_source.png")   # 430x882
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 430x882
H, W = img.shape[:2]
assert (W, H) == (430, 882), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def roi(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

def poly(pts):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
    return m

# ---- 1. neighbor removal (inpaint)
neighbor = np.zeros((H, W), np.uint8)
# Ashes: red hood + yellow grill grin peeking between Theory's raised arm
# and hood (zone x80-245, y80-285). Theory's own arm (purple/white) sits in
# the same zone, so only the RED/YELLOW pixels are inpainted, and the
# original Ashes pixels are explicitly excluded from the figure mask later.
ashes_zone = roi(80, 80, 245, 285)
red = cv2.inRange(hsv, np.array([0, 80, 60]), np.array([10, 255, 255]))
red |= cv2.inRange(hsv, np.array([160, 80, 60]), np.array([179, 255, 255]))
grill = cv2.inRange(hsv, np.array([20, 150, 150]), np.array([40, 255, 255]))
ashes_px = cv2.bitwise_and(red | grill, ashes_zone)
neighbor |= ashes_px
# Static: blue arm at the top-right corner
blue = cv2.inRange(hsv, np.array([95, 90, 60]), np.array([120, 255, 220]))
neighbor |= cv2.bitwise_and(blue, roi(370, 0, W, 160))
# stone ledge at the bottom (figure cut there)
neighbor |= roi(0, 795, W, H)
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 9, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask: polygon silhouette x color families
arm_poly = poly([(150, 20), (222, 20), (222, 300), (132, 300), (132, 120), (150, 120)])
head_poly = poly([(140, 165), (345, 165), (345, 345), (140, 345)])
body_poly = poly([(125, 320), (W, 320), (W, 800), (125, 800)])
fig_poly = arm_poly | head_poly | body_poly

purple = cv2.inRange(hsv, np.array([125, 55, 55]), np.array([168, 255, 210]))
void = cv2.inRange(hsv, np.array([95, 50, 5]), np.array([150, 220, 100]))
gold = cv2.inRange(hsv, np.array([12, 90, 60]), np.array([45, 255, 255]))
glove = cv2.inRange(hsv, np.array([0, 0, 185]), np.array([180, 95, 255]))
# white glints on the void (tight ROIs, measured from face overlay check:
# L (218,225)-(278,265), R (293,225)-(352,265)); both clean white slashes
_glint = cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 150, 255]))
glintL = cv2.bitwise_and(_glint, roi(218, 225, 278, 265))
glintR = cv2.bitwise_and(_glint, roi(293, 225, 352, 265))

fig = cv2.bitwise_and(purple | void | gold | glove | glintL | glintR, fig_poly)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.dilate(neighbor, np.ones((3, 3), np.uint8))))
# Ashes' original pixels (red hood + yellow grill) are excluded outright —
# the inpainted fill between Theory's arm and hood is background
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.dilate(ashes_px, np.ones((3, 3), np.uint8))))
# figure cut by the ledge: nothing below y=795
fig = cv2.bitwise_and(fig, cv2.bitwise_not(roi(0, 795, W, H)))

fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
fig = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)

dbg = clean.copy()
dbg[fig == 0] = dbg[fig == 0] // 3
cv2.imwrite(os.path.join(PARTS, "_debug_figmask.png"), dbg)

rgba = cv2.cvtColor(clean, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = fig
Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "00_base_full_figure.png"))
print("base saved; figure px:", int((fig > 0).sum()))
np.save(os.path.join(PARTS, "_figmask.npy"), fig)
np.save(os.path.join(PARTS, "_clean_bgr.npy"), clean)
