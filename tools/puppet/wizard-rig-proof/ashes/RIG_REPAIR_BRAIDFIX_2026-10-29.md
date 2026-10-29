# Ashes STANDARD rig — part-separation repair (2026-10-29)

Owner verdict on the first-use clip (2026-10-29): "don't save those as the
masters, but that's a good start… you're still doing bullshit square crops…
the braids you didn't cut the braids out as their own piece." Plus: "We have
real network rigs and files… real industry standard level tools and resources
and software fully wired up into our repos. Use those. Stop bullshitting."
Plus the binding part spec (~13:50 CDT): "Eyes are already cut out, mouth
already cut out. You need to cut out around the head, like in the jaw area.
Cut out around the braids so the braids can move — the braids be a piece of
his character sheet. Cut cleanly around the hood so it's not a square crop
moving the top of his shoulders when you move his head and neck and hood. Cut
around the outside of the hood AND around the inside of the hood so it looks
like his face — so the hood is actually moving individually from his face and
from the shoulder part. You need more parts to the neck and face and head and
hood and bust area, cut cleanly, so it can look like a cleaner animation."

This repair rebuilds the standard rig's decomposition to that spec. All six
required pieces exist as their own parts: head/jaw plate, braid L, braid R,
hood outer, hood inner (rim), neck, and the bust/shoulders separated from
the hood. Eyes and grill were already separate and are carried over.

## Audit of the Wave-4 (pre-repair) rig — measured, not eyeballed

Method: `audit_parts.py` pixel audit over `parts/` (figure = 187,870 px).

- **Head slab fusion.** `02_head` (45,678 px) is the figure ∩ rectangle
  (x50–345, y10–270) and duplicates the other parts wholesale: braid_L
  3,382 px (of its 5,317), braid_R 2,310 px (of 2,467), eyes 1,332 px
  (100%), grill 1,854 px (100%), chain 1,796 px (44%). 12,865 px are
  double-owned, 832 triple-owned; 228 figure px are owned by nobody.
- **Braid clips.** Both braid masks start at y=170 with a flat top row
  (41 opaque px on braid_L's top row) — the ROI rectangle guillotined the
  roots that rise to ~y115 under the hood rim. braid_R touches its ROI left
  edge (x=222) on 38 rows. A rectangular chain-notch (x158–242) was
  subtracted from the braids.
- **Arm guillotine.** arm_L's right edge sits at x=207/208 for all 165 band
  rows — 1 distinct value. The "split" is a vertical straightedge through
  the crossed arms and the braid tassel zone.
- **Phantom part.** `rig_layers/9_mouth_cavity.png` (the anime mouth-cavity
  synth the build recipe deliberately skips) sits in the layer folder and
  loads as a 16th part, painting a blob over the grill. Sweep of the full
  repo tree (GitHub tree API, 2026-10-29): it exists ONLY in
  `ashes/rig_layers/` — the other 17 rig folders are clean. Deleted here.

## Construction reference (what "like the network rigs" means, measurably)

From the house-style kits distilled out of the REAL network rigs
(TRIPPEDD-Animation-Studio PR #9, `_reference_only/house-style-source-kits/` —
Charlie/Pim from Smiling Friends, Frankie Foster, Gumball), and the
mystery-coast-ghosted `docs/research/PIPELINE.md` cutout doctrine:

- One master symbol per character; the scene is a single instance; the head
  is a **nested sub-rig**. → the v2 head group is face plate + rim + braids +
  eyes + grill, each independently driven, riding the head turn together.
- Every feature that moves on its own is **its own symbol on its own layer**.
  → feature art exists in exactly ONE layer (audit-verified: 0 feature px
  duplicated in the face plate, vs 1,332 eyes + 1,854 grill duplicated in v1).
- Mouth = ONE symbol, frame-addressed drawing library. → the grill stays a
  single `mouth` part driven by ParamMouthOpenY/ParamMouthForm (the mouth-set
  lane owns additional drawings; the rig keeps the same addressing).
- Plates stay complete under what moves over them (Charlie's `face_scalp` /
  Pim's `scalp`). → the face plate runs complete under the eyes/grill filled
  with the face's own flat void colour; the bust stays whole under hood/
  chain/braids/arms filled with sampled robe red. No Telea smear art is
  presented as character art; fills are the plate's own flat material.
- Seam-hiding accessories (PIPELINE.md "collar rule"). → the chain (collar)
  and the hood rim draw over the neck/jaw and braid-root seams.

## Method per part class (tools actually used)

Machinery: the rig's own stack — image2live2d 0.2.0 (`convert_layers`,
`rig_from_layer_dir`, `prepare_meshes`, `preview.render_pose`, its QA
harness and strand/dynamics analysis) — plus OpenCV segmentation in the
rewritten `cut_parts.py` (v2). No hand-cropping anywhere; every boundary
below is computed from the art. The mouth-set/part-library cuts were checked
and NOT used as a source: they are re-segmentations of the same clipped v1
masks (`parts/03_braid_L.png`), so they inherit the y=170 root clip.

- **Face void / neck** — the face is one flat-colour connected component
  (measured 10,607 px, BGR ≈ [45,1,1]). Split at a jaw arc
  (y = 198 + 26·(1−((x−195)/88)²)) with a 10 px underlap each way: above the
  arc = `face_base` (HEAD/JAW piece), below = `neck`, which receives the
  pipeline's tapered twist (weight 1 at the neck top → 0 at the shoulders).
  Void pockets inside the hood beside the face go to the hood (its dark
  interior), so the composite has no holes.
- **Eyes / grill** — Wave-4 masks carried over (owner: already cut out).
  Eyes split L/R by their two components (640 / 692 px).
- **Braids / chain (gold family)** — the gold fills of braid and chain abut
  into one blob per side, so they are split by **marker watershed on the
  gradient surface** (Sobel magnitude + drawn dark strokes boosted),
  confined to the gold territory and seeded from the eroded cores of the
  verified Wave-4 masks. Split lines follow the drawn strokes between links
  and strands. NO rectangle is subtracted: the chain simply draws above the
  braids in the stack, so the braids own their full woven columns — roots
  restored to y≈115 (they emerge from under the rim; the gold spiral clasps
  at the roots belong to the braid assembly), tassels complete to where the
  drawn strands end over the crossed arms (~y449 L / ~y404 R, extended
  through the thin linework strands with a run-width gate so the flood
  cannot spread into the robe's flame prints). Braid roots take a 9 px
  underlap of hood territory above the cut, in source pixels.
- **Hood** — the hem is the drawn dark stroke across the shoulder band
  (per-column linework components, median-smoothed; y≈271 at the sides).
  Inside that line and above it: hood territory. **Rim (hood inner)** =
  hood within 17 px of the face void — the opening's own band, following
  the void boundary; **hood outer** = the rest. Centre-front below the neck
  void's bottom (y≥250, x140–255) is chest, not hood. Shoulders are never
  in the hood: hood motion cannot drag the shoulder line.
- **Arms** — marker watershed on the same gradient surface inside the arm
  band (the crossed-arm fold and the white glove are the ridges). arm_L's
  right edge now takes 37 distinct x values in the band (v1: 1).
- **Bust** — figure minus all claimed parts, completed as a plate under the
  moving parts (flat robe-red fills), so head/hood/braid/arm motion never
  opens a hole and the shoulder line is the bust's own.

Layer stack (bottom → top) = image2live2d roles: `00_torso` ·
`01_neck` · `02_hair_back` (hood outer) · `03_face_base` (head/jaw) ·
`04_arm_l` · `05_arm_r` · `06_hair_side` (braid L) · `07_hair_side`
(braid R) · `08_hair_front` (hood rim — drawn over the braid roots so the
roots tuck under the rim, as drawn) · `09_accessory` (chain) · `10_eye_l` ·
`11_eye_r` · `12_mouth` (grill) · `13_eye_closed_l` · `14_eye_closed_r`
(carried over unchanged).

## Verification (audit, after)

- Figure coverage: **0 uncovered px** (v1: 228); moving-part overlaps all
  **0** except the declared 1,313 px jaw underlap strip (face∩neck).
- Feature duplication in the face plate: **0 px** (v1: eyes 1,332 + grill
  1,854 + braids 5,692 + chain 1,796 inside the head).
- Rest-stack composite vs source art: **0 differing px** over the full
  187,870 px figure (blink layers excluded — they are parameter-gated).
- `Ashes.inp`: **18 parts, 34 parameters** (v1: 15 parts / 24 params),
  structurally VALID per the repo's `validate_inp.py` (18/18 texture blobs
  decode, 34/34 params carry node bindings). New handles include
  ParamHairFront×4 + FrontV (rim), ParamHairSide×5 + SideV (braids, one per
  analysed strand group), ParamHairBack×5 + BackV (hood), assigned by the
  pipeline's own strand/dynamics analysis.
- Mesh density is a build parameter of this repair (`build_rig.py` pins
  `build_meshes` to a 28×28 grid; the pipeline default is 14×14). Measured
  mesh-coverage holes at 14×14: **130 px in the grill** (its left half —
  rendered as a black notch at rest, previously hidden by the head slab's
  duplicated teeth), 54 px in braid_L. At 28×28: grill 0, face 0, neck 0,
  braids 10/3 px. The pipeline's sub-mesh splits are grid-dependent (at 28
  the mouth stays one part; the chain splits L/R; arms split into
  upper/lower FK segments) — all are pipeline-internal, not layer changes.
- QA harness: one warning stands, `input:implausible_mouth_width` — the
  harness's mouth envelope (≤0.50 of face width) is calibrated on anime
  rigs; Ashes' grill verifiably spans 0.91 of his face because the wide
  grin IS the character's design (owner canon). v1 passed the same check
  only because its un-decomposed slab inflated the "face" frame to 295 px.
  The warning is accepted and documented rather than gamed by widening the
  plate. (`face_base_incomplete` from the first v2 build was real and was
  fixed by running the plate complete under the eyes.)
- Proofs (in `proofs/`, and rendered through the same preview path as the
  first-use lane): neutral, head-turn + nod at max with braids lagging,
  braid swing-through frame, blink, mouth-open, plus the on-2s animation
  `ashes_braidfix_turn_nod_20261029.mp4`. BodyAngle is held at 0 through
  the turn. Measured on the rendered frames: **bust band** (the shoulder/
  skirt region, 134,400 px) neutral vs max-turn — mean |diff| 0.68, only
  1,152 px (0.86%) change at all, i.e. the shoulders do not move with the
  head; **braid zone** (229,500 px) between the lag frame and the
  swing-through frame — 44,346 px (19.3%) change, i.e. the braids swing
  independently of the returning head.

## Name map (parts/)

`01_robe` → `01_bust` · `02_head` → split into `04_head_jaw` + `03_hood_outer`
+ `09_hood_rim` + `02_neck` · `03_braid_L` → `07_braid_L` (roots/tassels
completed) · `04_braid_R` → `08_braid_R` · `05_chain` → `10_chain` ·
`06_arm_L` → `05_arm_L` · `07_arm_R` → `06_arm_R` · `08_eyes` → split into
`11_eye_L` + `12_eye_R` · `09_grill` → `13_grill`.
Downstream citations of the old part filenames (e.g. the part-library
INDEX) should follow this map.

## Honest limits

- At combined parameter extremes (max head turn + max nod + max strand
  lag simultaneously, as in the proof's turn frame), the pipeline's strand
  warps open seams in the braid weave and the red bust shows through in
  streaks. At production amplitudes (the swing frame, the blink, the
  mouth-open frame) the braids render clean. This is the preview/stack's
  deformation behaviour, not a cut defect: the rest composite is exact and
  the braid parts are complete. The Wave-4 rig shows comparable artifacts
  in the same preview (a tear line at the neck, the chain blacking out).
- Source art is a 400×864 crop from a group shot; there is no isolated
  turnaround. The braid/chain boundary inside their contact zone follows
  the drawn strokes via watershed — a few hundred px along the contact
  line are assigned by gradient, not by a drawn separation that does not
  exist in the art.
- Small pinholes in the figure mask at the hood's upper opening edge are
  pre-existing in Wave 4's `_figmask.npy` and are unchanged.
- These are PROOF renders, not masters (owner's instruction on the
  first-use clip stands).
