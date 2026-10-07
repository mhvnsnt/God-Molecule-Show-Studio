#!/usr/bin/env python3
"""Worker C Wave 10 — CIPHER BATTLE variant (fist raised) part extraction, step 1.

Subject: CIPHER (yellow robe with rune designs, gold chains, manic yellow
eye glints on black void, left fist raised high — fist cut by the crop's top
edge). Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
"Group 10 - fireworks.webp" -> cipher_battle_crop_source.png (469x882).
Same canon character as the Wave-6 Cipher base rig, new battle pose —
nothing invented.

Method (proven recipe): polygon silhouette x HSV color masks + OpenCV Telea
inpainting for neighbor removal (Sombra's black robe + purple trim + skull
pendant + white fist on the left, stone ledge at the bottom, fireworks sky).
Honest constraints: the raised fist is cut by the crop's top edge (the arm
layer is sleeve + partial fist) — none invented; this source shows NO
pendant plate (chains only) — none grafted (Wave-6 Cipher precedent);
figure cut by the stone ledge (3/4-body, no legs) — none invented.
Canon: yellow robe + runes, manic yellow glints, gold chains — matches the
fireworks source; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/cipher-battle"
SRC = os.path.join(OUT, "cipher_battle_crop_source.png")   # 469x882
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 469x882
H, W = img.shape[:2]
assert (W, H) == (469, 882), (W, H)
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
# Sombra: black robe + purple trim + skull pendant + white fist (left side).
# Zone is x<210: Sombra's robe edge is at ~x215; Cipher's robe starts at ~x210
# and the left glint is at x238+ — both must be spared.
sombra_zone = roi(0, 0, 210, H)
neighbor |= sombra_zone
# stone ledge at the bottom (figure cut there)
neighbor |= roi(0, 700, W, H)
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 9, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask: polygon silhouette x color families
# raised left arm (sleeve + partial fist, screen-right)
arm_poly = poly([(385, 0), (W, 0), (W, 210), (385, 210)])
head_poly = poly([(220, 90), (405, 90), (405, 280), (220, 280)])
body_poly = poly([(190, 260), (W, 260), (W, 705), (190, 705)])
fig_poly = arm_poly | head_poly | body_poly

yellow = cv2.inRange(hsv, np.array([18, 100, 130]), np.array([38, 255, 255]))
void = cv2.inRange(hsv, np.array([95, 50, 5]), np.array([150, 220, 95]))
gold = cv2.inRange(hsv, np.array([12, 90, 60]), np.array([45, 255, 255]))
glove = cv2.inRange(hsv, np.array([0, 0, 185]), np.array([180, 95, 255]))
# yellow glints share the robe's hue — tight ROIs only (measured from zoom:
# L (235,145)-(280,175), R (297,145)-(343,175)); component-filtered in cut
glint_zone = roi(235, 145, 343, 175)
_glint = cv2.inRange(hsv, np.array([18, 120, 150]), np.array([38, 255, 255]))
glints = cv2.bitwise_and(_glint, glint_zone)

fig = cv2.bitwise_and(yellow | void | gold | glove | glints, fig_poly)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.dilate(neighbor, np.ones((3, 3), np.uint8))))
# figure cut by the ledge: nothing below y=700
fig = cv2.bitwise_and(fig, cv2.bitwise_not(roi(0, 700, W, H)))

fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
fig = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
# re-apply the neighbor exclusion AFTER the component filter: the Telea
# inpaint smears figure colors into the neighbor zone and the smear can join
# the largest component. A 5px margin keeps the smeared edge out.
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.dilate(neighbor, np.ones((5, 5), np.uint8))))
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
