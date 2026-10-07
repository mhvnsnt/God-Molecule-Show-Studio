# RIG PROOF — Wave 10 (Theory BATTLE, Cipher BATTLE, Hollow BATTLE)

**Date:** 2026-10-07
**Worker:** Lane C (Wave 10)
**Recipe:** Wave 4–9 nijilive (image2live2d), extended not reinvented.
**Canon rule:** owner-established characters only; no invented characters/names/relationships.
**Branch:** `wave10-laneC` (commits `97ead2b`, `1a4c392`, `aa81a13`; no push — coordinator merges).

Three battle-pose rig proofs completing the council battle set (Ashes, Echo,
Static, Kiko, Onyx, Sombra Negra done in Waves 7–9). Same structure as prior
battle rigs: layered PNGs → part/param manifest → posed renders → comparison
QC render. All proof PNGs were opened and visually inspected limb-by-limb
before sign-off (deliverable verification law). The venv is
`~/workspace/.venv-puppet` (image2live2d + cv2 live there, not in system
python3).

---

## 1. THEORY-BATTLE — Theory, fist raised (fireworks)

**Source:** `~/workspace/trippedd-studio/assets/wizard-gang-style-refs/cartoonier/`
`Group 10 - fireworks.webp`
**Crop:** `theory-battle/theory_battle_crop_source.png` (430×882)

**Rig:** `TheoryBattle.inp` — sha256 `fec1e5a2a43e3d0a…`
- **Parts (9):** 00_torso (purple robe + rune trim), 01_face_base (purple hood
  + black void, glint-punched), 02_accessory (gold chains + THEORY
  name-pendant, ParamAcc0 sway), 03_arm_r (raised right arm: purple sleeve +
  white-glove fist, auto-split `_lo`/`_up` two-link FK), 04/05_eye_l/r (white
  glints, split at x=309), + 2 synthesized closed eyes.
- **Params (14, all bound):** eye open/smile, AngleX/Y/Z, Acc0,
  BodyAngleX/Y/Z, ArmRA/RB, Breath. 2 physics rigs, 13 animations.
- **Proofs** (`theory-battle/proofs/`): neutral, head-turn, blink,
  comparison. Blink verified = real closed-eye art swap (glints → white
  arcs, void stays black; 1260 px changed).

**Recipe deltas (all verified visually):**
1. Ashes' red hood + yellow grill grin peek between Theory's raised arm and
   hood — inpainted out (zone x80–245, y80–285) and the original Ashes pixels
   explicitly excluded from the figure mask (Theory has no red in canon).
2. Fireworks-sky corner touching the fist caught purple sparkles in the arm
   mask — fixed with a notched arm polygon cutting the (132–150, 20–120) sky
   corner (fist knuckles start at x~152, verified intact).
3. Glint ROIs measured from zoomed overlays (the "left glint" first chased
   was the hood's purple rim highlight; true glints: L (245,225)–(309,258),
   R (309,225)–(358,258), split at x=309).
4. Head-texture eye punch (Wave-9 fix) applied — verified necessary.
5. Eye layers are full-canvas masked splits (Wave-8 lesson).

**Honest constraints:**
- Figure cut by the stone ledge (3/4-body, no legs in frame) — none invented.
- No mouth art — pipeline no-mouth path (QA `missing_role`/`missing_param`
  warnings are the expected no-mouth signal).
- Known preview artifact class (documented in Wave 7/8): the preview
  renderer's 3D head-turn breaks down past ~20°; `.inp` keyforms correct.

**Canon check:** purple robe + rune trim, black void + white glints, gold
chains + THEORY plate, white glove — matches the fireworks source. The
raised fist reads as her battle pose (schemer's triumph). No design
alterations.

## 2. CIPHER-BATTLE — Cipher, fist raised (fireworks)

**Source:** `~/workspace/trippedd-studio/assets/wizard-gang-style-refs/cartoonier/`
`Group 10 - fireworks.webp`
**Crop:** `cipher-battle/cipher_battle_crop_source.png` (469×882)

**Rig:** `CipherBattle.inp` — sha256 `761cd7f162e97622…`
- **Parts (9):** 00_torso (yellow robe + rune designs), 01_face_base (yellow
  hood + black void, glint-punched), 02_accessory (gold chains, ParamAcc0
  sway — NO pendant plate in this source, none grafted per Wave-6 Cipher
  precedent), 03_arm_l (raised left arm: yellow sleeve + partial white-glove
  fist, auto-split `_lo`/`_up` two-link FK), 04/05_eye_l/r (manic yellow
  glints, split at x=290), + 2 synthesized closed eyes.
- **Params (14, all bound):** eye open/smile, AngleX/Y/Z, Acc0,
  BodyAngleX/Y/Z, ArmLA/LB, Breath. 2 physics rigs, 13 animations.
- **Proofs** (`cipher-battle/proofs/`): neutral, head-turn, blink,
  comparison. Blink verified = real closed-eye art swap (glints → yellow
  arcs, void stays black; 1093 px changed).

**Recipe deltas (all verified visually):**
1. Glints share the robe's YELLOW hue AND the hood rim is yellow — selection
   is by tight ROIs + y-position (rim sits at y<148, excluded): L
   (247,148)–(280,178) [x<247 is the hood's vertical edge strip], R
   (297,148)–(343,178). The R glint was fragmented into 2 components —
   merged via 9×9 morphological close (L/R stay separate: 24px gap).
2. Head-texture eye punch (Wave-9 fix) applied — verified necessary.
3. Eye layers full-canvas masked splits (Wave-8 lesson).
4. Sombra exclusion zone narrowed to x<210 (from 245) to spare the left
   glint (x238+); neighbor exclusion re-applied post-component-filter to
   kill Telea inpaint smear (Wave-10 new hygiene step).
5. **False alarm documented:** mid-build the preview was misread as having
   black-bar mesh artifacts; binary-search isolation proved the "bars" were
   transparent background + a misread chain shadow. The arm auto-split
   meshes (`_up`/`_lo`) render correctly. No rig change needed.

**Honest constraints:**
- The raised fist is CUT by the crop's top edge (arm = sleeve + partial
  fist) — none invented.
- **No feral-crouch Cipher art exists.** The `cipher-refs/` folder holds Lio
  Rush *photo* references (pose/voice direction), not yellow-robed Cipher
  art. Every Cipher render in every asset is a standing group lineup; the
  fireworks fist-raise is the most dynamic existing pose. The "feral" read
  comes from the manic glint shapes + pose, not a crouch — documented, not
  fabricated.
- This source shows NO pendant plate (chains only) — none grafted.
- Figure cut by the stone ledge (3/4-body, no legs) — none invented.
- No mouth art — pipeline no-mouth path.

**Canon check:** yellow robe + rune designs, black void + manic yellow
glints, gold chains — matches the fireworks source. No design alterations.

## 3. HOLLOW-BATTLE — Hollow, bust (pilot still)

**Source:** `~/workspace/trippedd-studio/production/WIZARD_GANG_SHORT_01/stills/`
`media-generation-shot06-hollow-0-4c7e9e05-1d3c-4e59-9005-38800667117c.webp`
**Crop:** `hollow-battle/hollow_battle_crop_source.png` (940×872)

**Rig:** `HollowBattle.inp` — sha256 `3e9308a7dfbf793c…`
- **Parts (6):** 00_torso (orange robe + layered gold chains + HOLLOW
  name-pendant MERGED — Wave-6 Hollow precedent), 01_face_base (orange hood
  + dark-navy void, glint-punched), 02/03_eye_l/r (angular orange glints,
  split at x=462), + 2 synthesized closed eyes.
- **Params (11, all bound):** eye open/smile, AngleX/Y/Z, BodyAngleX/Y/Z,
  Breath. **No arm params, no ParamAcc0** — bust-only by source constraint.
- **Proofs** (`hollow-battle/proofs/`): neutral, head-turn, blink,
  comparison. Blink verified = real closed-eye art swap (glints → orange
  arcs, void stays black; 1877 px changed).

**Recipe deltas (all verified visually):**
1. Wave-6 Hollow fix re-applied: the largest-component filter drops the
   small disconnected glints — OR'd back explicitly via tight ROIs.
2. R glint dimmer (V~149) than L — V threshold lowered to 120 for the glint
   selector.
3. Head-texture eye punch (Wave-9 fix) applied — verified necessary.
4. Background exclusion re-applied post-component (inpaint smear guard).
5. Render-script `_INP_PARTS` corrected to Hollow's layer IDs (`02_eye_l`,
   `03_eye_r`, `2/3_eye_closed_*`) — a copy-paste from Theory initially
   filtered the eyes out of the preview (caught by visual inspection: dark
   glint smudges instead of orange).

**Honest constraints (documented, as prior waves did):**
- **BUST-ONLY** — no full-body battle source of Hollow exists in any asset.
  All group shots (cartoonier + painterly) are static lineups; the arcade
  "mask-raise" pose obscures the face behind a gold mask. The pilot still
  bust is the cleanest Hollow source available.
- No arms exist in any Hollow source — no arm parts/params.
- No ParamAcc0 (Wave-6 precedent: chain-cut catches too much robe).
- Figure cut at mid-torso — none invented.
- No mouth art — pipeline no-mouth path.

**Canon check:** orange robe, dark-navy void + angular orange glints, gold
chains + HOLLOW plate — matches the pilot still. No design alterations.

---

## Cross-cutting notes

- QA lints `lint:missing_role` / `lint:missing_param` ('mouth',
  'ParamMouthOpenY') fire on all three — expected; the linter assumes an
  anime face, these are void-faced by design. No mouth layers exist.
- `validate_inp.py` copies carry a hardcoded path + label from the template
  — each was sed-corrected to its own `.inp` before the validation run
  (Wave-10 lesson: the Theory run initially re-validated Onyx's file;
  caught and re-run).
- The Wave-9 blush-trap check (`ls rig_layers | grep -i blush` before every
  build) is now baked into `build_rig.py` as an assert — clean on all three.
- Debug/check artifacts (`parts/_debug_*`, `*.npy`, `__pycache__`) are
  gitignored, not committed.
- No binaries >100MB committed (largest file: the `.inp`s at ~600KB).
- The `trippedd-studio/AGENTS.md` production contract was read per the
  runtime notice; it governs MARS/Rocket/Blender work and does not alter
  this task (proven nijilive recipe reused, no new geometry authored, no
  competing implementations). No foreign autonomous-directive blocks were
  acted on.

## Verification method

All three `.inp` files pass `validate_inp.py` (magic `TRNSRTS\0`, JSON
parses, all params bound, all texture blobs decode). Posed renders use
`render_pose_opacity` (replicates the nijilive emitter incl. per-part
opacity from keyforms). Every render opened and inspected: robe, hood,
chains/pendant, each arm segment, each glint, left/right symmetry.
Comparison renders show source vs rig side-by-side. Blink verified by pixel
diff on all three (Theory 1260 px, Cipher 1093 px, Hollow 1877 px changed —
real closed-eye art swaps, not crossfade no-ops).
