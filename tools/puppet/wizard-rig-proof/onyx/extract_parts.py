#!/usr/bin/env python3
"""Worker C Wave 5 — Onyx part extraction, step 1: cleanup + base isolation.

Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
        "SWMG group - cartoon 2.webp" -> onyx_crop_source.png (390x960),
        Onyx = green-robed jester figure, 3rd from left (canon: green robe,
        jester-bell hood flourish, black void face, green eye glints).
        Crop widened to x=870 (vs Ashes' tighter crop) to include the RIGHT
        hood bell at group-x ~830-855 — verified visually, it exists.

Method: programmatic HSV color segmentation on the flat cartoon art
(no rembg — u2net is photo-trained and fringes on cel art) + OpenCV Telea
inpainting for neighbor removal. Follows the Wave-4 Ashes recipe.

Neighbor removal: Echo's pink robe (left edge) + Ashes' red robe sliver
        (right edge). Inpainted.
Figure mask from Onyx color families: robe green, dark-green shadow,
        dark-BLUE face void (same as Ashes' face: the void reads dark blue,
        not neutral black), lime-green glints, gold (bells/studs/orb spirals),
        white gloves, pink-brown staff, teal orb.
Canon notes: the group-art Onyx wears NO chain (the heavy gold chains live
        on the robed portrait, a different style — not grafted in, honest
        delta documented in RIG_PROOF_WAVE5.md). Two gold sleeve studs + one
        shoulder stud kept on the robe layer. Staff kept whole on its own
        accessory layer (drawn above the hood tip it crosses in front of).
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/onyx"
SRC = os.path.join(OUT, "onyx_crop_source.png")   # 390x960
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 390x960
H, W = img.shape[:2]
assert (W, H) == (390, 960), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. neighbor removal (inpaint)
# Echo (left): pink robe + gold chain. Ashes (right): red robe + gold trim.
# The orb lives at top-left (0,0,135,135) — exempt it from the left-edge
# inpaint so the orb's own gold spirals survive.
pink = cv2.inRange(hsv, np.array([140, 120, 150]), np.array([170, 255, 255]))
red1 = cv2.inRange(hsv, np.array([0, 70, 60]), np.array([10, 255, 255]))
red2 = cv2.inRange(hsv, np.array([170, 70, 60]), np.array([180, 255, 255]))
gold_raw = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
neighbor = np.zeros((H, W), np.uint8)
# Echo's pink fringe: x<55, all y (orb zone exempt). Echo's gold chain lives
# at y>700 — the left hood BELL (60-89, 179-204) is gold but must survive, so
# gold inpaint is restricted to y>230.
left_pink = pink.copy(); left_pink[0:135, :] = 0
neighbor[:, :55] = cv2.bitwise_or(neighbor[:, :55], left_pink[:, :55])
left_gold = gold_raw.copy(); left_gold[0:230, :] = 0
neighbor[:, :70] = cv2.bitwise_or(neighbor[:, :70], left_gold[:, :70])
neighbor[135:, :45] = 255                                        # Echo robe edge (hard)
right_edge = ((red1 | red2) | gold_raw); right_edge[0:250, :] = 0  # keep right bell
neighbor[:, 365:] = cv2.bitwise_or(neighbor[:, 365:], right_edge[:, 365:])
neighbor[250:, 372:] = 255
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 7, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Onyx color families
robe = cv2.inRange(hsv, np.array([45, 100, 70]), np.array([78, 255, 255]))
robe_shadow = cv2.inRange(hsv, np.array([45, 60, 35]), np.array([78, 255, 100]))
gold = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
glove_roi = np.zeros((H, W), np.uint8); glove_roi[330:490, 60:365] = 255
glove = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([0, 0, 195]), np.array([180, 70, 255])), glove_roi)
# staff: the shaft curves (S-shape) and its pink-tan paint fragments in HSV,
# so it is defined GEOMETRICALLY as a hand-traced polyline (waypoints measured
# from the staff centerline, verified against the source crop). Width 26px
# matches the shaft; the orb is handled separately below.
STAFF_PTS = [(80,105),(100,160),(113,200),(120,240),(135,300),(155,355),
             (172,420),(185,475),(200,515),(212,555),(226,595),(240,635),
             (255,690),(268,745),(276,790),(270,830),(258,875)]
staff_poly = np.zeros((H, W), np.uint8)
for i in range(len(STAFF_PTS)-1):
    cv2.line(staff_poly, STAFF_PTS[i], STAFF_PTS[i+1], 255, 26)
staff_poly = cv2.dilate(staff_poly, np.ones((3,3), np.uint8))
green_all = cv2.inRange(hsv, np.array([45, 60, 35]), np.array([78, 255, 255]))
staff = cv2.bitwise_and(staff_poly,
        cv2.bitwise_not(green_all | gold | cv2.inRange(hsv, np.array([0,0,195]), np.array([180,70,255]))))
np.save(os.path.join(PARTS, "_staff_poly.npy"), (staff_poly > 0))
# orb: teal-green glow, restricted to the orb corner
orb_roi = np.zeros((H, W), np.uint8); orb_roi[0:135, 0:135] = 255
orb = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([60, 80, 100]), np.array([95, 255, 255])), orb_roi)
# face void: dark blue, restricted to head ROI; keep only the component
# containing the face centre (background alley is the same dark blue)
face_roi = np.zeros((H, W), np.uint8); face_roi[100:330, 140:320] = 255
face_candidates = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([100, 150, 10]), np.array([135, 255, 75])), face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 230) + abs(fcent[i][1] - 198)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
# glints: bright lime, restricted to the face ROI
glints = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([50, 120, 180]), np.array([70, 255, 255])), face_roi)

fig = robe | robe_shadow | gold | glove | staff | orb | face | glints
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
# Keep ALL figure-color components above a speck threshold. (Ashes used
# largest-component-only, but Onyx's staff — a different color — fragments the
# green robe into 55 pieces; largest-only would amputate the hood tips.
# Every color family here is figure-exclusive except the dark-blue face void,
# which is already restricted to the head ROI + nearest-to-face-centre.)
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
keep = np.zeros((H, W), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 1500:
        keep[lab == i] = 255
fig = keep
# Union back small gold figure parts the largest-component filter drops:
# the hood bells + shoulder/sleeve studs hang a few px off the silhouette.
# (Neighbor gold was inpainted away above, so surviving gold is Onyx's.)
gold_now = cv2.inRange(hsv, np.array([12, 90, 100]), np.array([45, 255, 255]))
ng, glab, gstats, _ = cv2.connectedComponentsWithStats(gold_now, 8)
dilated = cv2.dilate(fig, np.ones((31, 31), np.uint8))
for i in range(1, ng):
    comp = (glab == i).astype(np.uint8) * 255
    if (cv2.bitwise_and(comp, dilated) > 0).sum() > 20:
        fig = cv2.bitwise_or(fig, comp)
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
# Subtract the neighbor zones outright (inpaint smears neighbor hues into
# these rects; same documented tradeoff as Ashes: a few px trimmed off the
# silhouette, invisible at rig scale). The orb (top-left) and right bell
# (y<250) are exempt.
fig[135:, :47] = 0
fig[250:, 370:] = 0
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)

rgba = cv2.cvtColor(clean, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = fig
Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "00_base_full_figure.png"))
print("base saved; figure px:", int((fig > 0).sum()))
np.save(os.path.join(PARTS, "_figmask.npy"), fig)
np.save(os.path.join(PARTS, "_clean_bgr.npy"), clean)
# debug overlay: figure mask in red over clean image
dbg = clean.copy()
red = np.zeros_like(clean); red[:, :] = (0, 0, 255)
dbg = cv2.addWeighted(clean, 0.45, red, 0.55, 0)
dbg[fig == 0] = clean[fig == 0]
Image.fromarray(cv2.cvtColor(dbg, cv2.COLOR_BGR2RGB)).save(os.path.join(PARTS, "_debug_figmask.png"))
print("debug overlay saved")
