# RIG PROOF — Wave 9 (Sombra Negra BATTLE, Onyx BATTLE)

**Date:** 2026-10-07
**Worker:** Lane C (Wave 9)
**Recipe:** Wave 4–8 nijilive (image2live2d), extended not reinvented.
**Canon rule:** owner-established characters only; no invented characters/names/relationships.

Two battle-pose rig proofs, same structure as the Wave-7/8 battle rigs:
layered PNGs → part/param manifest → posed renders → comparison QC render.
All proof PNGs were opened and visually inspected limb-by-limb before
sign-off (deliverable verification law). Static + Kiko battle rigs were
completed in Wave 8; this wave does the next two priority members
(Sombra Negra, Onyx). Theory, Cipher, Hollow battle rigs remain for a
future lane.

---

## 1. SOMBRA-BATTLE — Sombra Negra at the ritual circle (summoning pose)

**Source:** `~/workspace/trippedd-studio/assets/wizard-gang-style-refs/detailed/`
`Painterly group 2 - ritual.webp`
**Crop:** `sombra-battle/sombra_battle_crop_source.png` (400×1250)

**Rig:** `SombraBattle.inp` — sha256 `3fee075fc99f2ec8…`
- **Parts (7):** 00_torso (black robe + purple trim/embroidery), 01_face_base
  (hood + hair + black void), 02_accessory (gold chains + gold skull pendant
  + belt chain with cross pendant, ParamAcc0 sway), 04/05_eye_l/r (white
  glints, split at x=186), + 2 synthesized closed eyes.
- **Params (12, all bound):** eye open/smile, AngleX/Y/Z, Acc0,
  BodyAngleX/Y/Z, Breath. 2 physics rigs, 11 animations.
- **Proofs** (`sombra-battle/proofs/`): neutral, head-turn, blink,
  comparison. Blink verified = real closed-eye art swap (glints → white
  arcs, void stays black; bright-px 590→249 in the eye region).

**Recipe deltas (all verified visually):**
1. Painterly dark-on-dark source → the figure mask is polygon-led (measured
   silhouette polygon × HSV color families), not color-led.
2. **Head-texture eye punch (Wave-8 Static precedent, re-proven):** the glints
   baked into the head texture survive the blink crossfade and make the
   blink a no-op. Fix: Telea-inpaint the glint zones into the head layer
   with the void color before assembly. Verified by pixel diff
   (neutral-vs-blink went from Δ≈13k noise to a real swap).
3. Eye layers MUST be full-canvas masked splits, not crops (Wave-8 lesson).
4. Premultiply hygiene: RGB cleared where alpha=0 (Wave-7 lesson).

**Honest constraints:**
- Hands are dark-gloved and visually merged with the robe sleeves in this
  painterly source — no separable hand pixels; no arm parts/params (same
  class as the Wave-6 Sombra "arms inside the robe" constraint).
- The rune circle / smoke at the bottom is background (figure cut at
  y≈1010, renders as transparency in the `.inp`).
- No mouth art — the pipeline's "mouth simply stays shut" path applies
  (QA `missing_role`/`missing_param` warnings are the expected no-mouth
  signal).
- Known preview artifact class (documented in Wave 7/8): the preview
  renderer's 3D head-turn breaks down past ~20°; `.inp` keyforms correct.

**Canon check:** black robe + purple trim/embroidery, black void + white
glints, gold chains + skull pendant + belt chain with cross — matches the
ritual source. No design alterations.

## 2. ONYX-BATTLE — Onyx, staff-raised jester stance

**Source:** `~/workspace/trippedd-studio/assets/wizard-gang-style-refs/cartoonier/`
`Group 17 - skate park.webp`
**Crop:** `onyx-battle/onyx_battle_crop_source.png` (470×852)

**Rig:** `OnyxBattle.inp` — sha256 `c4ee056951325678…`
- **Parts (9):** 00_torso (green jester robe), 01_face_base (jester hood +
  black void), 02_accessory (gold chains + pendant + peach jester bells,
  ParamAcc0 sway), 03_arm_r (green sleeve + white glove, auto-split
  `_lo`/`_up` two-link FK), 04/05_eye_l/r (green glints, split at x=163),
  + 2 synthesized closed eyes.
- **Params (14, all bound):** eye open/smile, AngleX/Y/Z, Acc0,
  BodyAngleX/Y/Z, ArmRA/RB, Breath. 2 physics rigs, 13 animations.
- **Proofs** (`onyx-battle/proofs/`): neutral, head-turn, blink,
  comparison. Blink verified = real closed-eye art swap (green glints →
  green arcs, void stays black).

**Recipe deltas (all verified visually):**
1. The glints share the robe's GREEN hue — a plain green+ROI mask catches
   hood edges (verified failure). Selection is by component: green
   components in the tight glint ROIs that do NOT touch the ROI border
   (Kiko-battle Wave-8 recipe). Measured: L (133,256)-(156,268);
   R (170,241)-(195,259), small and high, partially behind the hood edge
   (verified by green-in-void component map — the "second glint" first
   chased at x~200-240 was the hood edge, caught and excluded).
2. The head-texture eye punch (delta 2 above) applied again — verified
   necessary, not optional.
3. Eye layers full-canvas masked splits (Wave-8 lesson).

**Honest constraints:**
- The staff + glowing orb are props — inpainted out (claw-machine precedent,
  Wave 8); the gripping white-gloved hand stays (a sliver of staff between
  the fingers reads as the grip).
- Figure cut by the skate-park ledge (bust length, no legs in frame) —
  none invented.
- No mouth art — pipeline no-mouth path (QA warnings as above).

**Canon check:** green jester robe + bells, black void + green glints, gold
chains + pendant, white glove — matches the skate-park source. No design
alterations.

---

## Cross-wave hygiene note (found & fixed this wave)

- A stale synthesized `1_blush.png` was sitting in `ashes/rig_layers/`
  (leftover from an earlier wave's debug run). If any rebuild ran with it
  present, `from_layer_dir` would pick it up as a blush role and the `.inp`
  would ship an anime blush + ParamCheek — a canon violation on a void face.
  **Removed.** Same trap hit this wave's own Sombra build mid-debug (caught
  by the validate step: 9 textures / ParamCheek present → file deleted →
  clean 7-texture build). Lesson for future lanes: `ls rig_layers | grep -i
  blush` before every build; never leave synth byproducts in the layer dir.

## Verification method

Both `.inp` files pass `validate_inp.py` (magic `TRNSRTS\0`, JSON parses,
all params bound, all texture blobs decode). Posed renders use
`render_pose_opacity` (replicates the nijilive emitter incl. per-part
opacity from keyforms). Every render opened and inspected: robe, hood,
chains/pendant/bells, each arm segment, each glint, left/right symmetry.
Comparison renders show source vs rig side-by-side. The Wave-9 setup-wizard
re-verification (screenshot proof) is in `SETUP_WIZARD_WAVE9.md`.
