#!/usr/bin/env python3
"""Worker C Wave 9 — Onyx BATTLE variant (staff-raised jester stance) part
extraction, step 1.

Subject: ONYX (green jester robe + hood with bells, dark void face with
green glints, gold chains + pendant, white glove gripping the staff), bust
length (figure cut by the skate-park ledge, no legs in frame).
Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
"Group 17 - skate park.webp" -> onyx_battle_crop_source.png (470x852).
Same canon character as the Wave-6 Onyx base rig, new battle pose — nothing
invented.

Method (proven recipe): polygon silhouette x HSV color masks + OpenCV Telea
inpainting for neighbor removal (staff shaft + glowing orb, Cipher's yellow
robe on the right, Sombra's black robe sliver on the left).
Honest constraints: the staff is a prop — inpainted out (claw-machine
precedent, Wave 8); the gripping hand stays. No legs in frame (ledge cut) —
none invented. Canon: green robe, green glints, gold chains — matches the
skate-park source; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/onyx-battle"
SRC = os.path.join(OUT, "onyx_battle_crop_source.png")   # 470x852
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 470x852
H, W = img.shape[:2]
assert (W, H) == (470, 852), (W, H)
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
# staff shaft: brown vertical bar the hand grips (hand zone spared)
staff_zone = roi(45, 440, 115, H)
hand_keep = roi(30, 375, 110, 480)         # white glove gripping the staff
staff_brown = cv2.inRange(hsv, np.array([5, 60, 30]), np.array([30, 200, 130]))
neighbor |= cv2.bitwise_and(cv2.bitwise_and(staff_brown, staff_zone),
                            cv2.bitwise_not(hand_keep))
# glowing green orb top-left (x<80, y<200) — part of the staff prop
orb_zone = roi(0, 90, 85, 210)
orb_glow = cv2.inRange(hsv, np.array([55, 40, 120]), np.array([90, 255, 255]))
neighbor |= cv2.bitwise_and(orb_glow, orb_zone)
# Cipher: yellow robe on the right edge
yellow = cv2.inRange(hsv, np.array([18, 120, 120]), np.array([35, 255, 255]))
cipher_zone = roi(330, 0, W, H)
neighbor |= cv2.bitwise_and(yellow, cipher_zone)
# Sombra: black robe sliver on the left edge
neighbor |= roi(0, 0, 22, H)
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 9, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask: polygon silhouette x color families
head_poly = poly([(95, 110), (340, 110), (345, 300), (90, 300)])
body_poly = poly([(90, 280), (345, 280), (365, 800), (55, 800), (40, 500)])
fig_poly = head_poly | body_poly

green = cv2.inRange(hsv, np.array([52, 80, 60]), np.array([75, 255, 220]))
void = cv2.inRange(hsv, np.array([90, 80, 8]), np.array([150, 255, 90]))
gold = cv2.inRange(hsv, np.array([12, 90, 60]), np.array([45, 255, 255]))
bells = cv2.inRange(hsv, np.array([0, 60, 150]), np.array([20, 180, 255]))  # peach bells
glove = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 100, 255])), hand_keep)
# green glints on the void (same hue as robe — tight ROIs, measured from zoom)
glintL = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([52, 100, 100]), np.array([75, 255, 255])), roi(125, 260, 170, 295))
glintR = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([52, 100, 100]), np.array([75, 255, 255])), roi(190, 260, 235, 295))

fig = cv2.bitwise_and(green | void | gold | bells | glove | glintL | glintR, fig_poly)
# subtract neighbor zones outright (sparing the hand)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.bitwise_and(staff_zone, cv2.bitwise_not(hand_keep))))
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cipher_zone))
fig = cv2.bitwise_and(fig, cv2.bitwise_not(roi(0, 0, 22, H)))
# figure cut by the ledge: nothing below y=800
fig = cv2.bitwise_and(fig, cv2.bitwise_not(roi(0, 800, W, H)))

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
