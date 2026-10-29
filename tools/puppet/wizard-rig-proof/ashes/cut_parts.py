#!/usr/bin/env python3
"""Ashes part extraction v2 — outline-following decomposition (2026-10-29 repair).

Replaces the Wave-4 rectangle-ROI cutter (cut_parts.py v1), whose head part
was the figure intersected with a rectangle (x50-345, y10-270): it fused the
braid roots, both eyes, the grill and the chain top inside the "head" slab and
dragged the shoulder tops with every head move, and whose arm split was a
straight vertical line at x=208 through the torso.

v2 construction, mirroring the house-style kits (TRIPPEDD-Animation-Studio
PR #9, distilled from the real Charlie/Pim network rigs) and the
mystery-coast PIPELINE.md cutout doctrine (separated levels, clean joint
separation points, seam-hiding accessories):
  * one master character; the head is a nested sub-rig of single-owned parts
  * every feature that moves on its own is its own part on its own layer —
    feature ART exists in exactly one layer (verified by audit)
  * plates stay complete under the parts that move over them, filled with
    the plate's own flat material colour (face plate = void, bust = robe)
  * seams hide under the part that covers them (chain = collar rule)

Owner's required pieces (2026-10-29): head/jaw cut at the jaw line, braids as
their own character-sheet pieces, hood OUTER and hood INNER (rim) as separate
pieces so the hood moves as a garment (hood != face, hood != shoulders),
a neck piece between head and bust, and the bust/shoulders separated from the
hood so head motion never drags the shoulder line.

Method: HSV segmentation (the rig's proven ranges) + marker watersheds on
the gradient surface for the fused gold family (braids/chain) and the arm
split — boundaries follow the drawn strokes, no rectangle ever clips or
notches a part — a connected-component face void split at a jaw arc, a
linework-following hood hem, and flat material-colour fills only for plate
completion. Anchors for the gold watershed are the Wave-4 part masks (pre-
repair parts/, preserved in git history): run against a rig folder whose
parts/ still holds the Wave-4 set; output goes to parts_v2/ + rig_layers_v2/
for audit before promotion to parts/ + rig_layers/.
"""
import cv2
import numpy as np
from PIL import Image
import json
import os
import sys

RIG = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
PARTS_IN = os.path.join(RIG, "parts")
OUT_PARTS = os.path.join(RIG, "parts_v2")
OUT_LAYERS = os.path.join(RIG, "rig_layers_v2")
os.makedirs(OUT_PARTS, exist_ok=True)
os.makedirs(OUT_LAYERS, exist_ok=True)

clean = np.load(os.path.join(PARTS_IN, "_clean_bgr.npy"))
fig = np.load(os.path.join(PARTS_IN, "_figmask.npy"))
H, W = fig.shape
FIG = fig > 0
hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)

yy, xx = np.mgrid[0:H, 0:W]
gold = cv2.inRange(hsv, np.array([10, 70, 80]), np.array([50, 255, 255])) > 0
dark = cv2.inRange(hsv, np.array([0, 0, 8]), np.array([180, 170, 115])) > 0
white = cv2.inRange(hsv, np.array([0, 0, 195]), np.array([180, 70, 255])) > 0
red1 = cv2.inRange(hsv, np.array([0, 70, 60]), np.array([12, 255, 255])) > 0
red2 = cv2.inRange(hsv, np.array([168, 70, 60]), np.array([180, 255, 255])) > 0
maroon = cv2.inRange(hsv, np.array([0, 45, 25]), np.array([12, 255, 90])) > 0
red = (red1 | red2 | maroon) & FIG

def components(mask):
    n, lab, stats, cent = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    return n, lab, stats, cent

def comp_mask(lab, ids):
    return np.isin(lab, list(ids))

# ---------------------------------------------------------------- figure void
face_blue = cv2.inRange(hsv, np.array([100, 80, 10]), np.array([130, 255, 78])) > 0
zone = np.zeros((H, W), bool); zone[30:345, 40:360] = True
n, lab, stats, cent = components(face_blue & zone & FIG)
face_id = min(range(1, n), key=lambda i: abs(cent[i][0] - 190) + abs(cent[i][1] - 140))
VOID = comp_mask(lab, [face_id])
VOID = cv2.dilate(VOID.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
VOID &= FIG
void_color = np.median(clean[VOID], axis=0)  # BGR flat plate colour
print("void px:", int(VOID.sum()), "void colour BGR:", void_color)

# ------------------------------------------------------- gold feature claiming
goldish = (gold | (dark & (cv2.dilate(gold.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0))) & FIG
n, lab, stats, cent = components(goldish)
claimed = {}
used = set()

def claim(name, seed_pts=None, centroid_test=None, grow=False, grow_x=None, grow_y=None):
    ids = set()
    for i in range(1, n):
        if i in used:
            continue
        cx, cy = cent[i]
        if seed_pts and any(lab[int(py), int(px)] == i for px, py in seed_pts):
            ids.add(i)
        elif centroid_test and centroid_test(cx, cy, stats[i]):
            ids.add(i)
    if grow and ids:
        acc = comp_mask(lab, ids)
        while True:
            near = cv2.dilate(acc.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            grown = False
            for i in range(1, n):
                if i in used or i in ids:
                    continue
                cx, cy = cent[i]
                if grow_x and not (grow_x[0] <= cx <= grow_x[1]):
                    continue
                if grow_y and not (grow_y[0] <= cy <= grow_y[1]):
                    continue
                if (comp_mask(lab, [i]) & near).any():
                    ids.add(i); grown = True
            if not grown:
                break
            acc = comp_mask(lab, ids)
    used.update(ids)
    claimed[name] = comp_mask(lab, ids)
    print(f"{name}: comps={sorted(ids)} px={int(claimed[name].sum())}")
    return claimed[name]

# Gold-family split by MARKER WATERSHED restricted to the gold territory.
# The goldish field fuses each braid with the chain into one blob per side
# (abutting same-class fills), but the drawn strokes between links and
# strands are gradient ridges: a watershed seeded from the eroded cores of
# the Wave-4 masks (whose composite was visually verified in Wave 4) and
# confined to the goldish territory splits the blobs along those strokes.
# No rectangle is involved anywhere: v1's chain-notch is NOT subtracted from
# the braids (the chain simply draws above them in the stack), and the
# braids' roots (above v1's y=170 clip) and tassels (below its y=400 clip)
# are inside the territory, so the floods claim them whole.
def v1_alpha(name):
    im = Image.open(os.path.join(PARTS_IN, f"{name}.png")).convert("RGBA")
    return np.array(im)[:, :, 3] > 0

eyes_all = v1_alpha("08_eyes")
grill = v1_alpha("09_grill")

gray0 = cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY)
grad0 = cv2.magnitude(cv2.Sobel(gray0, cv2.CV_32F, 1, 0, ksize=3),
                      cv2.Sobel(gray0, cv2.CV_32F, 0, 1, ksize=3))
grad0[dark] += 500.0
surf0 = (255 - cv2.normalize(grad0, None, 0, 255, cv2.NORM_MINMAX)).astype(np.uint8)
surf03 = cv2.cvtColor(surf0, cv2.COLOR_GRAY2RGB)

def erode3(m):
    return cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0

T = goldish & ~eyes_all & ~grill
v1b_L, v1b_R = v1_alpha("03_braid_L"), v1_alpha("04_braid_R")
seed_braid_L = erode3(v1b_L) & T
seed_braid_R = erode3(v1b_R) & T
seed_chain = erode3(v1_alpha("05_chain")) & T
markers = np.zeros((H, W), np.int32)
markers[~T] = 4
markers[seed_braid_L] = 1
markers[seed_braid_R] = 2
markers[seed_chain] = 3
cv2.watershed(surf03, markers)
braid_L = (markers == 1) & T
braid_R = (markers == 2) & T
chain = (markers == 3) & T

# tassel tips: below the gold body each braid ends in thin dark strands
# (mostly linework, little gold) hanging over the crossed arms. Extend each
# braid down its own tip columns through gold-or-dark figure pixels, gated
# by run width so the flood cannot spread into the robe's wide flame prints.
def extend_tassel(braid, v1b):
    cols = np.nonzero(v1b[330:400].any(axis=0))[0]
    if len(cols) == 0:
        return braid
    x0, x1 = int(cols.min()), int(cols.max())
    zone = np.zeros((H, W), bool)
    zone[390:450, x0:x1 + 1] = True
    cand = zone & FIG & (goldish | dark) & ~braid
    out = braid.copy()
    frontier = braid & zone
    while frontier.any():
        near = cv2.dilate(frontier.astype(np.uint8),
                          np.ones((3, 3), np.uint8)) > 0
        new = cand & near & ~out
        if not new.any():
            break
        keep = np.zeros((H, W), bool)
        for y0 in range(390, 450):
            xs = np.nonzero(new[y0])[0]
            if len(xs) and xs.max() - xs.min() <= 20:
                keep[y0, xs] = True
        if not keep.any():
            break
        out |= keep
        cand &= ~keep
        frontier = keep
    return out

braid_L = extend_tassel(braid_L, v1b_L)
braid_R = extend_tassel(braid_R, v1b_R)
# split the proven eyes mask into L/R: the two largest components are the
# eyes; any flecks go to the nearer eye; a bridged single component splits
# at the emptiest column between the halves.
ne, labe, statse, cente = components(eyes_all)
big = sorted(range(1, ne), key=lambda i: -statse[i][cv2.CC_STAT_AREA])[:2]
if len(big) == 2 and statse[big[1]][cv2.CC_STAT_AREA] > 250:
    big.sort(key=lambda i: cente[i][0])
    eye_L = comp_mask(labe, [big[0]])
    eye_R = comp_mask(labe, [big[1]])
    rest = eyes_all & ~eye_L & ~eye_R
    eye_L |= rest & (xx < (cente[big[0]][0] + cente[big[1]][0]) / 2)
    eye_R |= rest & (xx >= (cente[big[0]][0] + cente[big[1]][0]) / 2)
else:
    colsum = eyes_all.sum(axis=0)
    lo, hi = 170, 215
    valley = lo + int(np.argmin(colsum[lo:hi]))
    eye_L = eyes_all.copy(); eye_L[:, valley:] = False
    eye_R = eyes_all.copy(); eye_R[:, :valley] = False
for nm, m in (("eye_L", eye_L), ("eye_R", eye_R), ("grill", grill), ("chain", chain),
              ("braid_L", braid_L), ("braid_R", braid_R)):
    ys, xs = np.nonzero(m)
    bb = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if m.any() else None
    print(f"{nm}: px={int(m.sum())} bbox={bb}")

# gradient surface for the arm watershed below (flat = plain, line = barrier)
gray = cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY)
grad = cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3),
                     cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
grad[dark] += 500.0
surf = (255 - cv2.normalize(grad, None, 0, 255, cv2.NORM_MINMAX)).astype(np.uint8)
surf3 = cv2.cvtColor(surf, cv2.COLOR_GRAY2RGB)

# ------------------------------------------------------------------ hood hem
# follow the drawn hem stroke: dark linework in the shoulder band, long and
# near-horizontal components only; per-column y, median-smoothed.
band = dark & FIG.copy()
band[:205, :] = False; band[335:, :] = False
n, lab, stats, cent = components(band)
hem_ids = [i for i in range(1, n)
           if stats[i][cv2.CC_STAT_WIDTH] > 22 and stats[i][cv2.CC_STAT_HEIGHT] < 26]
hem = comp_mask(lab, hem_ids)
hem_y = np.full(W, np.nan)
for x in range(W):
    ys = np.nonzero(hem[:, x])[0]
    if len(ys):
        hem_y[x] = np.median(ys)
xs = np.nonzero(~np.isnan(hem_y))[0]
hem_y = np.interp(np.arange(W), xs, hem_y[xs])
hem_y = np.array([np.median(hem_y[max(0, x - 7):x + 8]) for x in range(W)])
hem_y = np.clip(hem_y, 215, 330)
print("hem_y at x=60,120,195,270,340:", [round(float(hem_y[x]), 1) for x in (60, 120, 195, 270, 340)])

yy, xx = np.mgrid[0:H, 0:W]
above_hem = yy <= hem_y[xx] + 2
below_hem_ext = yy <= hem_y[xx] + 12          # bust underlap band under the hood

hood_zone = FIG & above_hem & (yy < 400)
# centre-front below the neck void's bottom is chest, not hood: the hood's
# front opening ends at the chin; robe pixels there belong to the bust so
# head motion never slides a chest band
hood_zone &= ~((xx >= 140) & (xx <= 255) & (yy >= 250))
for m in (VOID, eyes_all, grill, chain, braid_L, braid_R):
    hood_zone &= ~m
# rim = hood within reach of the face opening (follows the void boundary)
dist_to_void = cv2.distanceTransform((~VOID).astype(np.uint8), cv2.DIST_L2, 5)
rim = hood_zone & (dist_to_void <= 17)
hood_outer = hood_zone & ~rim

# braid root underlap: 9px of hood territory directly above each braid root,
# assigned to the braid (hidden under the rim at rest, revealed as braid art
# when the braid swings — never a hole, never a copy of another part's art).
for braid in (braid_L, braid_R):
    pass  # applied after rim split below via mask surgery
def add_underlap(part, cover_mask, px=9):
    up = part.copy()
    shifted = np.zeros_like(part)
    shifted[px:, :] = part[:-px, :]
    ext = shifted & ~part & cover_mask & FIG
    return part | ext, ext

braid_L, ext_L = add_underlap(braid_L, hood_zone)
braid_R, ext_R = add_underlap(braid_R, hood_zone)
rim &= ~(ext_L | ext_R)
hood_outer &= ~(ext_L | ext_R)

# ------------------------------------------------------------------ face/neck
jaw = 198 + 26 * np.clip(1 - ((xx - 195) / 88.0) ** 2, 0, 1)   # shallow jaw arc
face_plate = VOID & (yy < jaw + 10)          # plate incl. 10px under the jaw line
face = face_plate.copy()                     # feature zones stay plate (flat void RGB)
neck = VOID & (yy >= jaw - 10)               # 10px underlap strip shared with face zone
neck |= VOID & (yy >= jaw)
# void pockets lateral to the face/neck, inside the hood above the hem:
# they read as the hood's dark interior beside the face -> hood_outer owns
# them (v1's head slab used to own them; leaving them unowned holes the
# composite at the face's lower sides)
hood_outer |= VOID & above_hem & ~face_plate & ~neck

# face-plate underlay beneath the eyes: Ashes' oval eyes are wider than the
# void and sit on the hood opening's edge; the plate runs complete beneath
# them (plate principle) so the face_base frame covers its features — the
# patches come from rim/hood pixels the eyes cover at rest.
eye_under = cv2.dilate(eyes_all.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
eye_under &= (rim | hood_outer) & ~braid_L & ~braid_R & ~chain
face |= eye_under
rim &= ~eye_under
hood_outer &= ~eye_under

# ------------------------------------------------------------------ arm split
band_mask = FIG & (yy >= 275) & (yy <= 475)
markers = np.zeros((H, W), np.int32)
markers[band_mask & (xx < 110)] = 1          # arm L seed
markers[band_mask & (xx > 290)] = 2          # arm R seed
markers[band_mask & (yy < 292)] = 3          # chest (torso) seed
markers[band_mask & (yy > 462)] = 3          # skirt (torso) seed
markers[~band_mask] = 4
seg = cv2.watershed(surf3, markers.copy())   # same gradient surface as the gold split
arm_L = band_mask & (seg == 1)
arm_R = band_mask & (seg == 2)
print("arm_L px:", int(arm_L.sum()), "arm_R px:", int(arm_R.sum()))

# ------------------------------------------------------------------ torso plate
claimed_all = (eyes_all | grill | chain | braid_L | braid_R | rim | hood_outer
               | face_plate | neck | arm_L | arm_R)
torso = FIG & ~claimed_all
# plate completion: bust stays whole under the parts that move over it
robe_color = np.median(clean[red & (yy > 400)], axis=0)
plate_under = FIG & ~torso & (yy >= 240)     # everything below the hood line
torso_plate = torso | plate_under

# ------------------------------------------------------------- RGB assembly
def layer_rgb(mask, base_rgb, fills=()):
    rgb = base_rgb.copy()
    for fmask, color in fills:
        rgb[fmask & mask] = color
    return rgb

def save_layer(folder, fname, mask, rgb):
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[:, :, :3] = rgb[:, :, ::-1]         # BGR -> RGB
    rgba[:, :, 3] = (mask.astype(np.uint8)) * 255
    Image.fromarray(rgba).save(os.path.join(folder, fname))

# nearest-colour fill for braid underlap extensions (braid's own edge colour)
def nearest_fill(rgb, part, ext):
    if not ext.any():
        return rgb
    _, labels = cv2.distanceTransformWithLabels((~part).astype(np.uint8), cv2.DIST_L2, 5,
                                                labelType=cv2.DIST_LABEL_PIXEL)
    src = labels[ext]
    rgb[ext] = rgb.ravel()[src] if False else rgb[tuple(np.unravel_index(src, (H, W)))]
    return rgb

# underlap extensions keep the source art itself (the strip above the cut is
# the root's real continuation in the drawing; smearing a neighbour colour
# over real pixels only costs fidelity)
braid_L_rgb = clean
braid_R_rgb = clean
face_rgb = layer_rgb(face, clean, [(eyes_all, void_color), (grill, void_color)])
torso_rgb = layer_rgb(torso_plate, clean, [
    (chain & torso_plate, robe_color), (braid_L & torso_plate, robe_color),
    (braid_R & torso_plate, robe_color), (arm_L & torso_plate, robe_color),
    (arm_R & torso_plate, robe_color), (neck & torso_plate, void_color),
    (rim & torso_plate, robe_color), (hood_outer & torso_plate, robe_color)])

parts_out = [
    ("01_bust", torso_plate, torso_rgb),
    ("02_neck", neck, clean),
    ("03_hood_outer", hood_outer, clean),
    ("04_head_jaw", face, face_rgb),
    ("05_arm_L", arm_L, clean),
    ("06_arm_R", arm_R, clean),
    ("07_braid_L", braid_L, braid_L_rgb),
    ("08_braid_R", braid_R, braid_R_rgb),
    ("09_hood_rim", rim, clean),
    ("10_chain", chain, clean),
    ("11_eye_L", eye_L, clean),
    ("12_eye_R", eye_R, clean),
    ("13_grill", grill, clean),
]
for name, m, rgb in parts_out:
    save_layer(OUT_PARTS, f"{name}.png", m, rgb)

layers_out = [
    ("00_torso", torso_plate, torso_rgb),
    ("01_neck", neck, clean),
    ("02_hair_back", hood_outer, clean),
    ("03_face_base", face, face_rgb),
    ("04_arm_l", arm_L, clean),
    ("05_arm_r", arm_R, clean),
    ("06_hair_side", braid_L, braid_L_rgb),
    ("07_hair_side", braid_R, braid_R_rgb),
    ("08_hair_front", rim, clean),
    ("09_accessory", chain, clean),
    ("10_eye_l", eye_L, clean),
    ("11_eye_r", eye_R, clean),
    ("12_mouth", grill, clean),
]
for name, m, rgb in layers_out:
    save_layer(OUT_LAYERS, f"{name}.png", m, rgb)
# closed-eye layers carried over unchanged (synth art of the unchanged eyes)
for src_name, dst_name in [("7_eye_closed_l", "13_eye_closed_l"), ("8_eye_closed_r", "14_eye_closed_r")]:
    Image.open(os.path.join(RIG, "rig_layers", f"{src_name}.png")).save(
        os.path.join(OUT_LAYERS, f"{dst_name}.png"))

manifest = {"source": "ashes_crop_source.png (400x864)",
            "method": "v2 outline decomposition: HSV segmentation, face-void split at a jaw arc, marker watersheds on the gradient surface for the gold family (braids/chain) and the arm split, linework hood hem, plate completion fills",
            "stack_bottom_to_top": [n for n, _, _ in layers_out] + ["13_eye_closed_l", "14_eye_closed_r"],
            "layers": []}
for name, m, _ in parts_out:
    ys, xs = np.nonzero(m)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if m.any() else None
    manifest["layers"].append({"layer": name, "pixels": int(m.sum()), "bbox_xyxy": bbox})
with open(os.path.join(OUT_PARTS, "parts_manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)
for e in manifest["layers"]:
    print(e)
print("saved to", OUT_PARTS, "and", OUT_LAYERS)
