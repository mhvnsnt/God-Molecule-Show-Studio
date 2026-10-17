#!/usr/bin/env python3
"""Worker C Wave 9 — Sombra Negra BATTLE variant (ritual-circle summoning pose)
part extraction, step 1.

Subject: SOMBRA NEGRA (black robe, purple trim/embroidery, gold chains +
gold skull pendant + belt chain with cross pendant, white eye glints on
black void, dark-gloved hands), full body, standing at the ritual circle.
Source: trippedd-studio/assets/wizard-gang-style-refs/detailed/
"Painterly group 2 - ritual.webp" -> sombra_battle_crop_source.png (400x1250).
Same canon character as the Wave-6 Sombra rig, new battle pose — nothing invented.

Method (proven recipe): geometric polygon silhouette x HSV color masks +
OpenCV Telea inpainting for neighbor removal (Hollow's red robe, right edge).
Painterly dark-on-dark background means the figure mask is polygon-led;
colors only confirm membership. Honest constraints documented in the
docstring of cut_parts.py / the proof doc.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/sombra-battle"
SRC = os.path.join(OUT, "sombra_battle_crop_source.png")   # 400x1250
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 400x1250
H, W = img.shape[:2]
assert (W, H) == (400, 1250), (W, H)
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
# Hollow: red robe + gold chains on the right edge (x>300)
red = cv2.inRange(hsv, np.array([0, 90, 60]), np.array([15, 255, 200])) | \
      cv2.inRange(hsv, np.array([160, 90, 60]), np.array([180, 255, 200]))
gold = cv2.inRange(hsv, np.array([12, 90, 70]), np.array([45, 255, 255]))
hollow_zone = roi(296, 180, W, H)
neighbor |= cv2.bitwise_and(red | gold, hollow_zone)
neighbor |= roi(330, 0, W, 185)            # Hollow's hood upper right
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 9, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask: polygon silhouette x color families
head_poly = poly([(92, 95), (298, 95), (300, 335), (88, 335)])
body_poly = poly([(88, 300), (298, 300), (318, 950), (272, 1012),
                  (92, 1012), (42, 905), (8, 745), (14, 395)])
fig_poly = head_poly | body_poly

robe_dark = cv2.inRange(hsv, np.array([95, 40, 8]), np.array([165, 220, 100]))
hair = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 60, 26]))
trim = cv2.inRange(hsv, np.array([118, 60, 18]), np.array([158, 230, 140]))
glint = cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 100, 255]))
acc_gold = cv2.inRange(hsv, np.array([12, 90, 60]), np.array([45, 255, 255]))

fig = cv2.bitwise_and(robe_dark | hair | trim | acc_gold, fig_poly)
# eye glints only inside the face zone (avoid white background specks)
face_zone = roi(110, 190, 270, 260)
fig |= cv2.bitwise_and(glint, face_zone)
# rune circle glow at bottom right is background: kill below y=1010
fig = cv2.bitwise_and(fig, cv2.bitwise_not(roi(0, 1010, W, H)))
# hollow zone subtraction (sparing nothing — neighbor already inpainted)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(hollow_zone))

fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
fig = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)

# debug: silhouette vs figure
dbg = clean.copy()
dbg[fig == 0] = dbg[fig == 0] // 3
cv2.imwrite(os.path.join(PARTS, "_debug_figmask.png"), dbg)

rgba = cv2.cvtColor(clean, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = fig
Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "00_base_full_figure.png"))
print("base saved; figure px:", int((fig > 0).sum()))
np.save(os.path.join(PARTS, "_figmask.npy"), fig)
np.save(os.path.join(PARTS, "_clean_bgr.npy"), clean)
