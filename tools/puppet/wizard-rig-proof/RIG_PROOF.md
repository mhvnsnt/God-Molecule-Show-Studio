# RIG PROOF — Ashes (Wizard Gang) nijilive puppet

Worker C, TRIPPEDD Resource Pull Wave 4, 2026-10-07.
Character: **ASHES** — scarlet red robe, diamond-grill smile, blonde braids,
gold chains. Canon: the grill smile is kept in every style; no design changes.

## What was built

A real, loadable **nijilive `.inp` puppet** (`ashes/Ashes.inp`, 1.9 MB,
sha256 `dc4c8994d616706b…`): **15 parts, 24 parameters, 2 physics rigs,
18 animations**, all 24 parameters carrying real per-vertex deform bindings
(validated by `validate_inp.py` against the nijilive serialization spec:
magic `TRNSRTS\0`, JSON payload, `TEX_SECT` with 15 decodable textures).

## Source art

No isolated Ashes turnaround exists. Source:
`trippedd-studio/assets/wizard-gang-style-refs/cartoonier/SWMG group - cartoon 2.webp`
— Ashes is the red-robed figure, 4th from left. Used the full-body group shot,
cropped to `ashes/ashes_crop_source.png` (400×864), hood peak included.

## Recipe

### 1. Parts — `extract_parts.py` + `cut_parts.py`
Method: **programmatic HSV color segmentation on the flat cartoon art**
(no rembg — u2net is photo-trained and fringes on cel art) + **OpenCV Telea
inpainting** for neighbor removal and occluded-area fill. All ROI bounds were
set from measured blob centroids, verified by re-opening every output.

- **Neighbor removal** (green jester left, purple council member right):
  color-keyed masks + explicit exclusion rects, inpainted. The left-edge
  white glove was verified by zoom to rest on the GREEN sleeve — the jester's
  hand, not Ashes' — and removed. His gold hat-bell likewise.
- **Figure mask** from Ashes color families (robe red, maroon shadow, gold,
  white glove, dark-blue face void). Gotcha found: the face is **dark blue**
  (HSV ~120,255,46), not neutral black — the first mask dropped the whole
  face. Fixed with a blue range restricted to the **single face-void
  component** (background alley is the same blue).
- **9 layers** (`parts/01_robe … 09_grill`, see `parts_manifest.json`),
  bottom→top: robe, head, braid_L, braid_R, chain, arm_L, arm_R, eyes, grill.
  Gold parts include their dark linework (gold ∪ dark-near-gold). Robe holes
  behind removed parts are inpainted so every layer is self-contained.

### 2. Rig — `build_rig.py` (image2live2d, Apache-2.0, installed from GitHub source)
Headless layer-dir → `.inp` conversion. One targeted monkeypatch of the
pipeline's `_safe_synth`: **skip `synthesize_mouth_cavity` and
`synthesize_blush`**, keep `synthesize_closed_eyes`. Reason: the painters
assume an anime face — the cavity painted a giant anime mouth over Ashes'
grill (canon violation) and the blush painted pink blocks on the void face.
The black face void already reads as the mouth interior; the grill IS the
mouth. Documented in the script header.

### 3. Proof renders — `render_poses.py`
`proofs/ashes_pose_neutral.png`, `proofs/ashes_pose_head-turn_mouth-open.png`
(ParamAngleX=30, ParamAngleY=-15, ParamMouthOpenY=1.0 — head turned, grill
visibly stretched open), `proofs/ashes_pose_blink.png` (ParamEyeLOpen/R=0 —
real closed-eye art swap, not a squash), plus `proofs/ashes_pose_comparison.png`.
Rendered with the pipeline's own preview renderer, which mirrors the
nijilive emitter's node hierarchy — these are deformations of the actual
rig data in `Ashes.inp`, not mockups. (One preview bug patched in-script:
it skipped params at value 0.0 assuming "0 = rest", which silently dropped
the blink since EyeOpen rests at 1.0.)

### 4. Parameters (24)
Eyes: ParamEyeLOpen/ROpen [0,1] (blink), ParamEyeLSmile/R [0,1] ·
Mouth: ParamMouthOpenY [0,1] (grill open), ParamMouthForm [-1,1] ·
Head: ParamAngleX/Y/Z [-30,30] · Hair: ParamHairSide 1–5 + V [-1,1]
(braid sway/physics) · Accessory: ParamAcc0 [-1,1] (chain) ·
Body: ParamBodyAngleX/Y/Z [-10,10] · Arms: ParamArmLA/LB, ParamArmRA/RB
[-10,10] (crossed-arm pose limits travel — honest constraint) ·
Breath: ParamBreath [0,1]. Full table: `proofs/rig_parameters.json`.

### 5. QA
`lint_warnings=0`, param sweep PASS. One plausibility warning:
`input:implausible_mouth_width` — the tool expects mouth/face-width ratios
for anime faces; Ashes' grill is canonically huge and `face_base` includes
the hood. Correct per character design, not a defect.

## What failed / honest gaps

1. **nijigenerate GUI automation (headless)**: the editor runs under
   Xvfb+D-Bus (replicated the Wave 3 recipe, screenshot-verified), but the
   first-run Quick Setup wizard could not be dismissed — synthetic xdotool
   clicks/keys don't register (no window manager; `firstrun_complete=true`
   is set but the wizard still shows) and the CLI ignores a `.inp` argument.
   Proof of the attempt: `proofs/nijigenerate_editor_gui-blocked.png`.
   **The `.inp` was therefore validated structurally** (`validate_inp.py`)
   **instead of by editor screenshot.** It has never been opened in
   nijigenerate; a human should open `Ashes.inp` once to confirm.
2. **No PSD produced**: pytoshop's write API (`LayerRecord`) proved too
   low-level to timebox; the 9 PNG layers + manifest serve a human rigger
   the same purpose for PSD reassembly.
3. **Arm raise**: crossed-arm source pose means ParamArmL/R mostly produce
   subtle shifts, not big swings — the parameter exists and is bound, but
   the pose limits it. A T-pose/A-pose source would rig better.
4. **Mouth open without cavity**: ParamMouthOpenY stretches the grill
   (no interior to reveal). Fine for a fixed-grin character; true jaw-drop
   would need painted open-mouth art.

## Full 9-character pass needs

1. Per-character source art cleaner than a group crop (isolated turnarounds;
   neighbor-removal was 40% of this task).
2. A human open of one `.inp` in nijigenerate to close gap #1, then the
   pipeline (`extract_parts.py` generalized per character color script +
   `build_rig.py` unchanged) runs headless for the other 8.
3. Character-specific `_safe_synth` policy: hooded/void-face characters skip
   cavity+blush; normal faces keep them.
4. The `v==0.0` preview skip and the mouth-pair false-positive split
   (`split_bundled_pairs` split the 2-component grill until the middle teeth
   were recovered) are upstream image2live2d issues worth filing.
