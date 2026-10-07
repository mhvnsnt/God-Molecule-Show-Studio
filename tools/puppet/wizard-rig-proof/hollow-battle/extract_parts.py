#!/usr/bin/env python3
"""Worker C Wave 10 — HOLLOW BATTLE variant (bust) part extraction, step 1.

Subject: HOLLOW (orange robe, layered gold chains + HOLLOW name-pendant,
angular orange eye glints on dark-navy void). Bust: the pilot still is a
half-body shot (cut at mid-torso); no arms exist in any source.
Source: trippedd-studio/production/WIZARD_GANG_SHORT_01/stills/
media-generation-shot06-hollow (pilot still) -> hollow_battle_crop_source.png
(940x872). Same canon character as the Wave-6 Hollow base rig — nothing
invented.

Method (proven recipe): polygon silhouette x HSV color masks + OpenCV Telea
inpainting for background removal (blurred carnival background).
Honest constraints (documented, as prior waves did): BUST-ONLY — no
full-body battle source of Hollow exists in any asset (all group shots are
static lineups; the arcade "mask-raise" pose obscures the face). No arms in
any source — no arm parts/params. No ParamAcc0 (Wave-6 Hollow precedent:
the outline-proximity chain cut catches too much robe, so chains + HOLLOW
pendant stay merged on the torso). Figure cut at mid-torso — none invented.
Canon: orange robe, orange glints, gold chains + HOLLOW plate — matches the
pilot still; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/hollow-battle"
SRC = os.path.join(OUT, "hollow_battle_crop_source.png")   # 940x872
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 940x872
H, W = img.shape[:2]
assert (W, H) == (940, 872), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def roi(x0, y0, x1, y1):
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = 255
    return m

def poly(pts):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
    return m

# ---- 1. background removal (inpaint) — figure polygon defines the subject
fig_poly = poly([(270, 20), (670, 20), (700, 400), (720, 872),
                 (220, 872), (240, 400)])
bg = cv2.bitwise_not(fig_poly)
bg = cv2.dilate(bg, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, bg, 9, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask: color families x polygon
orange = cv2.inRange(hsv, np.array([6, 90, 110]), np.array([28, 255, 255]))
void = cv2.inRange(hsv, np.array([95, 40, 5]), np.array([150, 220, 90]))
gold = cv2.inRange(hsv, np.array([12, 90, 80]), np.array([45, 255, 255]))
# orange glints on the void (tight ROIs, measured from gridded zoom:
# L (365,200)-(440,250), R (485,200)-(565,250))
_glint = cv2.inRange(hsv, np.array([8, 140, 170]), np.array([28, 255, 255]))
glintL = cv2.bitwise_and(_glint, roi(365, 200, 440, 250))
glintR = cv2.bitwise_and(_glint, roi(485, 200, 565, 250))

fig = cv2.bitwise_and(orange | void | gold | glintL | glintR, fig_poly)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.dilate(bg, np.ones((3, 3), np.uint8))))

fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
fig = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
# Wave-6 Hollow fix: the largest-component filter drops the small
# disconnected glints — OR the tight-ROI glint mask back in explicitly
fig = cv2.bitwise_or(fig, cv2.bitwise_and(glintL | glintR, fig_poly))
# re-apply background exclusion post-component (inpaint smear guard)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.dilate(bg, np.ones((5, 5), np.uint8))))
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
