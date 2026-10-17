# RIG PROOF — Wave 8 (Static BATTLE, Kiko BATTLE)

**Date:** 2026-10-07
**Worker:** Lane C (Wave 8)
**Recipe:** Wave 4–7 nijilive (image2live2d), extended not reinvented.
**Canon rule:** owner-established characters only; no invented characters/names/relationships.

Two battle-pose rig proofs, same structure as the Wave-7 battle rigs
(Ashes dunk, Echo spray-can): layered PNGs → part/param manifest → posed
renders → comparison QC render. All proof PNGs were opened and visually
inspected limb-by-limb before sign-off (deliverable verification law).

---

## 1. STATIC-BATTLE — Static reaching for the claw machine

**Source:** `~/workspace/trippedd-studio/assets/wizard-gang-style-refs/cartoonier/Group 14 - arcade.webp`
**Crop:** `static-battle/static_battle_crop_source.png` (540×740)

**Rig:** `StaticBattle.inp` — sha256 `71580aae64cce2f1…`
- **Parts (9):** 00_torso (deep-blue rune robe), 01_face_base (blue hood +
  black void), 02_accessory (pale-gold chains, ParamAcc0 sway),
  03_arm_r (blue sleeve + white glove, auto-split `_lo`/`_up` two-link FK),
  04/05_eye_l/r (muted-blue glints, split at x=244), + 2 synthesized
  closed eyes (4_eye_closed_l, 5_eye_closed_r).
- **Params (14, all bound):** eye open/smile, AngleX/Y/Z, Acc0,
  BodyAngleX/Y/Z, ArmRA/RB, Breath. 2 physics rigs, 13 animations.
- **Proofs** (`static-battle/proofs/`): neutral, head-turn, blink,
  comparison. Blink verified = real closed-eye art swap (glints vanish,
  void stays black).

**Recipe deltas (all verified visually):**
1. Static's chains are washed pale gold (H 23-29, S 64-136, V 178-254) —
   the strict gold range missed them; a `clean_small` k=3 open fragmented
   the thin strands, so chains use close-k3 + open-k2 only.
2. The claw machine's glowing frame has a BLUE component (H~120, in the
   robe family) at x 95-130 — killed spatially (95,275)-(130,368), then by
   color below y=368 sparing the white glove (S<90). The magenta neon
   component was also keyed. Verified: no machine pixels in any part layer.
3. Eye layers MUST be full-canvas masked splits, not crops — cropped eye
   PNGs shift the eye nodes and trip the `face_base_incomplete` QA warning
   (caught, fixed, warning cleared; Wave-7 used full-canvas).
4. Premultiply hygiene: RGB cleared where alpha=0 (Wave-7 lesson).

**Honest constraints:**
- Full body visible; the claw machine is background (inpainted out) — the
  hand/arm stay. The inpainted zone renders as transparency in the `.inp`.
- **No pendant in this source** (chains only) — none grafted (Cipher
  Wave-6 precedent: nothing invented).
- No mouth art — the pipeline's "mouth simply stays shut" path applies
  (QA `missing_role`/`missing_param` warnings are the expected no-mouth
  signal, same as Echo battle).
- Known preview artifact: thin horizontal blue dashes at the frame edges
  in neutral/head-turn (stray arm-mesh triangle UVs — same class as the
  Wave-7 documented preview-renderer limitation; `.inp` keyforms correct).

**Canon check:** deep-blue rune robe, black void + blue glints, pale-gold
chains, white glove — matches the arcade source. No design alterations.

## 2. KIKO-BATTLE — Kiko, left fist raised (victory/battle stance)

**Source:** `~/workspace/trippedd-studio/assets/wizard-gang-style-refs/cartoonier/Group 10 - fireworks.webp`
**Crop:** `kiko-battle/kiko_battle_crop_source.png` (500×912)

**Rig:** `KikoBattle.inp` — sha256 `b261c3f088ea618d…`
- **Parts (9):** 00_torso (white fur robe), 01_face_base (fur hood + black
  void), 02_accessory (gold chains + **KIKO name-pendant**, ParamAcc0 sway),
  03_arm_l (raised left arm + fist, auto-split `_lo`/`_up`),
  04/05_eye_l/r (white angular glint shards, split at x=300), + 2
  synthesized closed eyes.
- **Params (14, all bound):** eye open/smile, AngleX/Y/Z, Acc0,
  BodyAngleX/Y/Z, ArmLA/LB, Breath. 2 physics rigs, 13 animations.
- **Proofs** (`kiko-battle/proofs/`): neutral, head-turn, blink,
  comparison. Blink verified = real closed-eye art swap.

**Recipe deltas (all verified visually):**
1. **Correction:** Kiko has ONE raised arm (left) — the top-right white is
   the hood, not a second fist (verified by zoom; the first cut wrongly made
   a right-arm layer from hood fur, caught and removed).
2. The glints are white angular shards, same color as the fur — a plain
   white+ROI mask catches hood fur (verified failure). Selection is by
   component: white components in the tight glint ROI (250,270)-(380,325)
   that touch the dilated void, area 300-600 px, interior (not touching the
   ROI edge — fur intrudes from the edge). Verified: L (266-298, 278-298),
   R (332-367, 294-317).
3. Fireworks burst (top-center-right) inpainted out; zero figure-mask
   pixels in the firework zone (verified).

**Honest constraints:**
- Figure cut by the frame's bottom edge (no legs in frame — no legs cut or
  invented).
- Arm/shoulder boundary is a spatial cut in flat white fur (documented).
- **CANON FLAG (owner's call):** the KIKO name-pendant is preserved
  byte-for-byte from the owner's own generated source art — no new in-world
  text was authored. Same keep-or-cut flag as Wave-6 Static's SWMG plate.
- No mouth art — pipeline no-mouth path (QA warnings as above).
- Known preview artifact: thin vertical dark line in head-turn at
  15°/-10° (preview-renderer 3D head-turn limitation per Wave-7; `.inp`
  keyforms correct).

**Canon check:** white fur + hood, black void + white glints, gold chains +
KIKO pendant, raised left fist — matches the fireworks source.

---

## Verification method

Both `.inp` files pass `validate_inp.py` (magic `TRNSRTS\0`, JSON parses,
all params bound, all texture blobs decode). Posed renders use
`render_pose_opacity` (replicates the nijilive emitter incl. per-part
opacity from keyforms). Every render opened and inspected: robe, hood,
chains/pendant, each arm segment, each glint, left/right symmetry.
Comparison renders show source vs rig side-by-side.
