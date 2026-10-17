#!/usr/bin/env python3
"""Worker C Wave 7 — Echo BATTLE variant (spray can raised) part extraction, step 1.

Subject: ECHO (pink robe with paint splatters, gold chains + ECHO name-pendant,
white eye glints on black void) holding a spray can aloft in her right hand.
Source: trippedd-studio/assets/wizard-gang-style-refs/cartoonier/
"Group 17 - skate park.webp" -> echo_battle_crop_source.png (515x725).
Same canon character as the Wave-6 Echo rig, new battle pose — nothing invented.

Method (proven recipe): programmatic HSV color segmentation on flat cartoon
art + OpenCV Telea inpainting for neighbor removal.
Neighbor removal: Static's blue robe + SWMG plate + chains (left edge),
Sombra's black robe (right edge), Hollow's red fringe (left edge).
The spray can overlaps Static's zone — the can is silver/low-sat, Static is
saturated blue, so the blue is keyed out while the can survives.
Honest constraint: a foreground rail occludes the robe below y~655 — the rig
is 3/4-body; no legs are cut or invented.
Canon: ECHO name-pendant text preserved; no design alterations.
"""
import cv2
import numpy as np
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/echo-battle"
SRC = os.path.join(OUT, "echo_battle_crop_source.png")   # 515x725
PARTS = os.path.join(OUT, "parts")
os.makedirs(PARTS, exist_ok=True)

img = cv2.imread(SRC)                      # BGR, 515x725
H, W = img.shape[:2]
assert (W, H) == (515, 725), (W, H)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# ---- 1. neighbor removal (inpaint)
static_blue = cv2.inRange(hsv, np.array([102, 130, 80]), np.array([118, 255, 220]))
sombra_black = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 55]))
neighbor = np.zeros((H, W), np.uint8)
neighbor[:, :102] = 255                                    # Static zone (can starts ~x108)
blue_zone = np.zeros((H, W), np.uint8)
blue_zone[:, 100:145] = static_blue[:, 100:145]             # Static's blue inside the can's x-range
neighbor = np.maximum(neighbor, blue_zone)
neighbor[:, 448:] = np.maximum(neighbor[:, 448:], sombra_black[:, 448:])  # Sombra (right edge)
neighbor[180:620, 0:42] = 255                              # Hollow red fringe (left edge)
neighbor = cv2.dilate(neighbor, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(img, neighbor, 7, cv2.INPAINT_TELEA)
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

# ---- 2. figure mask from Echo color families
pink_hi = cv2.inRange(hsv, np.array([93, 120, 120]), np.array([118, 255, 255]))    # bright pink robe
pink_sh = cv2.inRange(hsv, np.array([150, 90, 90]), np.array([178, 255, 255]))     # magenta shade
pink = pink_hi | pink_sh
gold = cv2.inRange(hsv, np.array([14, 100, 120]), np.array([40, 255, 255]))         # chains/pendant/ring
yellow_splat = cv2.inRange(hsv, np.array([20, 140, 180]), np.array([36, 255, 255])) # paint splatter
white = cv2.inRange(hsv, np.array([0, 0, 195]), np.array([180, 80, 255]))           # eye glints / can highlight
face_roi = np.zeros((H, W), np.uint8)
face_roi[60:280, 200:360] = 255
navy = cv2.inRange(hsv, np.array([100, 140, 10]), np.array([138, 255, 85]))
face_candidates = cv2.bitwise_and(navy, face_roi)
nfc, flab, _, fcent = cv2.connectedComponentsWithStats(face_candidates, 8)
face = np.zeros((H, W), np.uint8)
best, bestd = -1, 1e9
for i in range(1, nfc):
    d = abs(fcent[i][0] - 280) + abs(fcent[i][1] - 170)
    if d < bestd:
        bestd, best = d, i
if best > 0:
    face = (flab == best).astype(np.uint8) * 255
    face = cv2.dilate(face, np.ones((5, 5), np.uint8))
    face = cv2.bitwise_and(face, face_roi)
# spray can: silver body + blue cap + red nozzle, all inside the can ROI
can_roi = np.zeros((H, W), np.uint8)
can_roi[190:335, 100:215] = 255
silver = cv2.inRange(hsv, np.array([0, 0, 165]), np.array([180, 110, 255]))
blue_cap = cv2.inRange(hsv, np.array([98, 90, 70]), np.array([122, 255, 210]))
red1 = cv2.inRange(hsv, np.array([0, 90, 90]), np.array([10, 255, 255]))
red2 = cv2.inRange(hsv, np.array([168, 90, 90]), np.array([180, 255, 255]))
can = cv2.bitwise_and(silver | blue_cap | red1 | red2, can_roi)
# spray mist: pale wisps above the can
mist_roi = np.zeros((H, W), np.uint8)
mist_roi[130:215, 70:210] = 255
mist = cv2.bitwise_and(cv2.inRange(hsv, np.array([0, 0, 150]), np.array([180, 70, 255])), mist_roi)
# hand: pale glove holding the can
hand_roi = np.zeros((H, W), np.uint8)
hand_roi[212:305, 118:212] = 255
hand = cv2.bitwise_and(white | cv2.inRange(hsv, np.array([0, 30, 150]), np.array([180, 120, 255])), hand_roi)

fig = pink | gold | yellow_splat | white | face | can | mist | hand
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(fig, 8)
fig = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8) * 255
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
# Subtract neighbor zones outright + the rail (foreground occlusion, y>655).
fig[:, :104] = 0
fig[180:620, 0:44] = 0
fig[:, 446:] = 0
fig[652:725, :] = 0              # rail: 3/4-body honest constraint
# Static's zone (x 100-215): his saturated blue robe shares Echo's pink hue
# band, so key it out spatially, sparing only Echo's actual parts.
static_zone = np.zeros((H, W), np.uint8)
static_zone[35:625, 100:215] = 255
can_keep = np.zeros((H, W), np.uint8)
can_keep[195:335, 135:210] = 255      # spray can body
hand_keep = np.zeros((H, W), np.uint8)
hand_keep[210:305, 125:212] = 255     # hand on the can
mist_keep = np.zeros((H, W), np.uint8)
mist_keep[130:200, 95:205] = 255      # spray mist (above the chains)
sleeve_roi = np.zeros((H, W), np.uint8)
sleeve_roi[290:490, 150:260] = 255    # Echo's pink sleeve (Static's blue peeks left of x~150)
robe_keep = np.zeros((H, W), np.uint8)
robe_keep[200:300, 165:215] = 255     # Echo's shoulder, left of the chains' end
keep = can_keep | hand_keep | mist_keep | sleeve_roi | robe_keep
fig = cv2.bitwise_and(fig, cv2.bitwise_not(cv2.bitwise_and(static_zone, cv2.bitwise_not(keep))))
fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
fig = cv2.dilate(fig, np.ones((3, 3), np.uint8), iterations=1)
# Static's gold chains drape left of the can: kill gold there outright
# (the can is silver/low-sat; Echo's ring sits at x~178, outside the kill).
# Chain gold saturation dips to ~95, so key on hue in this zone, not the
# strict gold range.
# NOTE: chain kill lives AFTER the final close/dilate — the 5x5 close
# regrows thin killed strands from surviving seeds.
chain_hue = cv2.inRange(hsv, np.array([14, 60, 100]), np.array([42, 255, 255]))
chain_kill_roi = np.zeros((H, W), np.uint8)
chain_kill_roi[150:315, 100:175] = 255
chain_kill = cv2.bitwise_and(chain_hue, chain_kill_roi)
chain_kill = cv2.dilate(chain_kill, np.ones((3, 3), np.uint8), iterations=1)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(chain_kill))
# dark inter-chain shadows left behind by the hue kill
shadow_roi = np.zeros((H, W), np.uint8)
shadow_roi[155:310, 105:150] = 255
shadows = cv2.bitwise_and(cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 80])), shadow_roi)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(shadows))
# Static's blue robe peeking between the chains (protected by mist_keep)
blue_remnant = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([98, 80, 60]), np.array([122, 255, 165])), chain_kill_roi)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(blue_remnant))
# thin blue strip of Static's robe left of the can/sleeve, below the chains.
# His blue runs V~240 here, too close to Echo's pink to split by value —
# so kill blue spatially. The silver can (low-sat) and pink sleeve (x>=150)
# are unaffected by a blue-only kill.
strip_roi = np.zeros((H, W), np.uint8)
strip_roi[35:430, 100:153] = 255     # Static's hood (top) + robe strip; mist is low-sat, safe
strip = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([95, 80, 50]), np.array([125, 255, 255])), strip_roi)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(strip))
# Static's blue robe in the x[150:190] gap (between the strip kill and
# Echo's can/sleeve). Echo's parts here are silver (can) and pink (sleeve),
# so a blue-only kill is safe.
gap_roi = np.zeros((H, W), np.uint8)
gap_roi[150:632, 140:190] = 255
gap_blue = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([95, 80, 50]), np.array([125, 255, 255])), gap_roi)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(gap_blue))
# Static's "MG" name-plate fragment (gold text, not Echo's)
mg_roi = np.zeros((H, W), np.uint8)
mg_roi[305:350, 105:155] = 255
mg = cv2.bitwise_and(cv2.inRange(hsv, np.array([14, 60, 100]), np.array([42, 255, 255])), mg_roi)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(mg))
# blue contamination in the spray-mist zone (Static's robe behind the wisps);
# the pale mist itself is low-sat and survives a blue-only kill
mist_blue_roi = np.zeros((H, W), np.uint8)
mist_blue_roi[125:205, 95:205] = 255
mist_blue = cv2.bitwise_and(
    cv2.inRange(hsv, np.array([95, 80, 50]), np.array([125, 255, 255])), mist_blue_roi)
fig = cv2.bitwise_and(fig, cv2.bitwise_not(mist_blue))

rgba = cv2.cvtColor(clean, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = fig
Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(os.path.join(PARTS, "00_base_full_figure.png"))
print("base saved; figure px:", int((fig > 0).sum()))
np.save(os.path.join(PARTS, "_figmask.npy"), fig)
np.save(os.path.join(PARTS, "_clean_bgr.npy"), clean)
