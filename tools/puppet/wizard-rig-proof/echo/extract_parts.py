#!/usr/bin/env python3
"""Worker C Wave 5 — Echo part extraction, step 1: cleanup + base isolation.

Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
        "SWMG group - cartoon 2.webp" -> echo_crop_source.png (320x960),
        Echo = pink-splatter-robed figure, 2nd from left (canon: pink robe,
        ECHO name pendant, black void face, pink glints).

Method: programmatic HSV color segmentation on the flat cartoon art
(no rembg) + OpenCV Telea inpainting for neighbor removal. Follows the
Wave-4 Ashes recipe with Wave-5 fixes:
- keep-all-components->1500px (not largest-only): the splatter paint
  fragments the robe into many pieces, same as Onyx's staff did.
- neighbor gold/white inpainted at edges (Kiko's white fur left, Onyx's
  green + orb top-right), with figure zones exempted.
Figure mask from Echo color families: pink robe, teal/yellow/purple splatter,
        dark-BLUE face void (same void color as Ashes/Onyx), bright-pink
        glints, gold (chain + ECHO pendant), white gloves.
Canon notes: the group-art Echo holds NO spray can (it belongs to her street
        persona card, echo-unused.webp — not grafted in; honest delta in
        RIG_PROOF_WAVE5.md). The ECHO pendant text is kept as painted.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/echo"
SRC = os.path.join(OUT, "echo_crop_source.png")   # 320x960
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 320x960
H, W = img.shape[:2]
assert (W, H) == (320, 960), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. neighbor removal (inpaint)
# Kiko (left): white fur. Onyx (right/top-right): green robe + teal orb.
white = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 80, 255]))
green = cv2.inRange(hsv, np.array([45, 80, 50]), np.array([90, 255, 255]))
teal = cv2.inRange(hsv, np.array([70, 80, 80]), np.array([100, 255, 255]))
neighbor = np.zeros((H, W), np.uint8)
neighbor[:, :60] = cv2.bitwise_or(neighbor[:, :60], white[:, :60])   # Kiko fur
neighbor[:, :48] = 255                                               # Kiko edge (hard)
neighbor[0:130, 255:] = cv2.bitwise_or(neighbor[0:130, 255:],        # Onyx orb
                                       (green | teal)[0:130, 255:])
neighbor[:, 292:] = cv2.bitwise_or(neighbor[:, 292:], green[:, 292:]) # Onyx fringe
neighbor[:, 296:] = 255
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 7, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Echo color families
pink = cv2.inRange(hsv, np.array([110, 80, 80]), np.array([170, 255, 255]))
teal_splat = cv2.inRange(hsv, np.array([78, 90, 80]), np.array([102, 255, 255]))
yellow_splat = cv2.inRange(hsv, np.array([18, 140, 180]), np.array([36, 255, 255]))
gold = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
glove_roi = np.zeros((H, W), np.uint8); glove_roi[360:500, 80:270] = 255
glove = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 195]), np.array([180, 70, 255])), glove_roi)
# face void: dark blue, head ROI, component nearest the face centre
# (background alley is the same dark blue)
face_roi = np.zeros((H, W), np.uint8); face_roi[80:330, 60:280] = 255
face_candidates = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([100, 150, 10]), np.array([135, 255, 80])), face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 187) + abs(fcent[i][1] - 205)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
# glints: bright pink (V>200 separates them from the robe pink)
glint_roi = np.zeros((H, W), np.uint8); glint_roi[125:195, 140:255] = 255
glints = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([138, 70, 200]), np.array([162, 220, 255])), glint_roi)

fig = pink | teal_splat | yellow_splat | gold | glove | face | glints
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
keep = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 1500:
        keep[lab == i] = 255
fig = keep
# union back small gold figure parts (chain links) near the silhouette
gold_now = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
ng, glab, gstats, _ = cv2.connectedComponentsWithStats(gold_now, 8)
dilated = cv2.dilate(fig, np.ones((31, 31), np.uint8))
for i in range(1, ng):
    comp = (glab == i).astype(np.uint8) * 255
    if (cv2.bitwise_and(comp, dilated) > 0).sum() > 20:
        fig = cv2.bitwise_or(fig, comp)
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
# subtract neighbor zones outright (documented tradeoff, same as Ashes/Onyx)
fig[:, :50] = 0
fig[0:110, :75] = 0      # neon sign, top-left corner
fig[0:56, 70:200] = 0    # neon sign spillover (hood starts at y~60)
fig[0:130, 258:] = 0
fig[:, 294:] = 0
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)

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
Image.fromarray(cv2.cvtColor(dbg, cv2.COLOR_BGR2RGB)).save(os.path.join(PARTS, "_debug_figmask.png"))
print("debug overlay saved")
