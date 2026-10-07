#!/usr/bin/env python3
"""Worker C Wave 5 — Kiko part extraction, step 1: cleanup + base isolation.

Source: game-sweep/AshLanev2/public/portraits/kiko-tanaka-robed.webp
        (owner-approved robed card, 2026-10-06) -> kiko_crop_source.png
        (1060x1945; card border + title cropped out).
        Kiko = white-fur-hooded figure (canon: white fur hooded robe, black
        face, gold chains on bare chest, gold KIKO pendant, colorful dragon
        tights).

Method: programmatic HSV color segmentation + Telea inpainting. Follows the
Wave-4 Ashes recipe with Wave-5 fixes (keep-all->1500px, neighbor inpaint).

SOURCE DECISION (documented recipe delta): the cartoonier group-art Kiko was
rejected — its full-length white robe hides the canon bare chest + dragon
tights. The robed card is the only source with the full canon costume.

GLINT DECISION (honest gap): the brief lists "sparkly white eye glints", but
the card's face void is pure black at the pixel level (max V=80 in the void;
verified on the original webp, not just the crop). The white eyes belong to
the GROUP-ART Kiko (different source). Painting glints in would INVENT canon
detail — forbidden. Kiko ships with a pure void face: NO eye layers, NO blink
param. Documented in RIG_PROOF_WAVE5.md.

Figure mask from Kiko color families: white fur, black void, gold (chains +
pendants), skin (bare chest), saturated tights colors, dark linework.
Background (neon street) excluded via body ROI + color.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/kiko"
SRC = os.path.join(OUT, "kiko_crop_source.png")   # 1060x1945
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 1060x1945
H, W = img.shape[:2]
assert (W, H) == (1060, 1945), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. no neighbor inpaint needed (single-figure card art); the background
# is removed via the figure mask itself. The card border/title were cropped
# out at the source stage.
clean = img.copy()

# ---- 2. figure mask from Kiko color families
# body ROI: the figure is centered; neon signs live at the extreme edges/top
body_roi = np.zeros((H, W), np.uint8)
cv2.fillPoly(body_roi, [np.array([
    (120, 0), (940, 0), (900, 700), (880, 1945), (180, 1945), (160, 700),
], np.int32)], 255)

fur = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 165]), np.array([180, 90, 255])), body_roi)
void = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 70])), body_roi)
gold = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255])), body_roi)
skin = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([4, 55, 95]), np.array([22, 160, 230])), body_roi)
# tights: any saturated color (the dragon print is multicolor)
tights = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 85, 80]), np.array([180, 255, 255])), body_roi)
# dark linework (outlines) — part of the figure
linework = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 5]), np.array([180, 255, 55])), body_roi)

fig = fur | void | gold | skin | tights | linework
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
keep = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 4000:
        keep[lab == i] = 255
fig = keep
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
# subtract neon signs (background) at the top corners. The hood does not
# extend into these rects (verified visually).
fig[30:220, 130:240] = 0    # left 新宿 sign
fig[100:260, 850:980] = 0   # right 龍 sign
# subtract the street visible between the legs (center bottom). The legs are
# at the sides; the wet-street reflections in the middle are background.
# (documented tradeoff: paint drips hanging in this zone are sacrificed —
# they read as street reflections, not figure.)
street_roi = np.zeros((H, W), np.uint8)
cv2.fillPoly(street_roi, [np.array([
    (440, 1480), (620, 1480), (630, 1945), (430, 1945),
], np.int32)], 255)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(street_roi))
fig = cv2.dilate(fig, np.ones((5, 5), np.uint8), iterations=1)

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
# downscale debug for viewing
dbg_small = cv2.resize(dbg, (424, 778))
Image.fromarray(cv2.cvtColor(dbg_small, cv2.COLOR_BGR2RGB)).save(os.path.join(PARTS, "_debug_figmask.png"))
print("debug overlay saved")
