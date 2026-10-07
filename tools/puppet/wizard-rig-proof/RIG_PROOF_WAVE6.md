# RIG PROOF — Wave 6 (Theory, Cipher, Static, Hollow, Sombra Negra)

Worker C, 2026-10-07. Five nijilive puppet rigs completing the 9-member
Wizard Gang council, built with the Wave-4 Ashes recipe (image2live2d /
nijigenerate toolchain, BSD-2-Clause), in
`tools/puppet/wizard-rig-proof/{theory,cipher,static,hollow,sombra}/`.

Each rig: source still → layered PNG parts (`extract_parts.py`,
`cut_parts.py`: HSV segmentation + Telea inpainting) → `.inp` (via
image2live2d `convert_layers`, with `_safe_synth` monkeypatched to skip the
anime mouth-cavity + blush synthesis while keeping closed-eye synthesis) →
structural validation (`validate_inp.py`: magic `TRNSRTS\0`, JSON, params
bound, textures decode) → proof renders (`render_poses.py`: neutral,
head-turn, blink via `render_pose_opacity`, + comparison against the canon
source). All proof PNGs were opened and visually inspected before sign-off
(deliverable verification law).

Canon sources: `~/workspace/trippedd-studio/assets/wizard-gang-style-refs/cartoonier/`
+ pilot stills `~/workspace/trippedd-studio/production/WIZARD_GANG_SHORT_01/stills/`;
canon doc `~/workspace/trippedd-studio/docs/series/WIZARD-GANG.md`. All five
are black-void faces with eye glints (grill smile is Ashes-only, not used).
Nothing invented.

## Theory — COMPLETE

`theory/Theory.inp` — sha256 `579724317e745094…`

- **Parts (11):** 00_torso (purple robe, gold chains inpainted out of the
  accessory's footprint), 01_face_base (purple hood + black void),
  02_accessory (gold chains + THEORY name-pendant, ParamAcc0 sway),
  03/04_eye_l/r (purple glints), + 2 synthesized closed eyes.
- **Params (16, all bound):** eye open/smile, AngleX/Y/Z, Acc0,
  BodyAngleX/Y/Z, ArmLA/LB, ArmRA/RB, Breath. 2 physics rigs, 13 animations.
- **Proofs:** `proofs/theory_pose_{neutral,head-turn,blink,comparison}.png`.
  Blink verified = real closed-eye art swap. Comparison matches the canon
  purple-robed figure (Theory, NOT the Narrator — Narrator is voice-only in
  the cartoon; canon law).
- **Canon note:** glint brightness is asymmetric in the source art (left
  dimmer V~96, right V~248) — preserved as-is for source fidelity rather
  than normalized to the group-1 white.
- **Recipe deltas:** accessory cut with `clean_small` k=3 (not k=5) to avoid
  eroding the thin gold chains.

## Cipher — COMPLETE

`cipher/Cipher.inp` — sha256 `20f7ef84d62f647c…`

- **Parts (11):** 00_torso (yellow robe), 01_face_base (yellow hood + void),
  02_accessory (gold chains, ParamAcc0 sway), 03/04_eye_l/r (yellow glints),
  03/04_arm_l/r (white gloves), + 2 synthesized closed eyes.
- **Params (16, all bound).** Proofs: neutral/head-turn/blink/comparison.
  Blink verified = real closed-eye art swap.
- **Recipe deltas:** chains NOT color-separable from the robe (chain-band
  gold med H=20 vs robe H=21) — accessory cut via black-outline proximity
  (`gold ∩ dilate(dark,13)` in the chest ROI), 9118px clean chains.
- **Canon note:** no pendant on the group-2 source art → none grafted
  (nothing invented). Minor gray mottling in the chains at zoom reads as
  shading at scale.

## Static — COMPLETE

`static/Static.inp` — sha256 `e1279b74dc047285…`

- **Parts (11):** 00_torso (deep blue robe), 01_face_base (blue hood + void),
  02_accessory (gold chains + **SWMG pendant**, ParamAcc0 sway),
  03/04_eye_l/r (blue-white glints), arms (white gloves),
  + 2 synthesized closed eyes.
- **Params (16, all bound).** Proofs: neutral/head-turn/blink/comparison.
  Blink verified = real closed-eye art swap.
- **Recipe deltas:** eye extraction needed measured tight ROIs from the
  zoomed source (hood blue ≈ glint blue; automated void-interior logic
  failed). Minor dark smudge at the left shoulder (inpaint tradeoff,
  documented; reads as shadow).
- **CANON FLAG (owner's call):** the SWMG pendant is preserved byte-for-byte
  from the owner's own generated source art — no new in-world text was
  authored. Flagged in the script docstrings; the standing "no Shadow Wizard
  Money Gang as in-world text" rule applies to NEW text, but the owner
  should confirm keep-or-cut.

## Hollow — COMPLETE (bust-only honest constraint)

`hollow/Hollow.inp` — sha256 `16fcbb3cc8fa0ef2…`

- **Parts (9):** 00_torso (orange robe + layered gold chains + HOLLOW
  name-pendant merged — see delta), 01_face_base (orange hood + dark-navy
  void), 02/03_eye_l/r (orange angular glints),
  + 2 synthesized closed eyes.
- **Params (12, all bound):** eye open/smile, AngleX/Y/Z, BodyAngleX/Y/Z,
  Breath. **No arm params** — the pilot still is a half-body bust (cut at
  mid-torso); no arms exist in any source. **No ParamAcc0** — see delta.
- **Proofs:** `proofs/hollow_pose_{neutral,head-turn,blink,comparison}.png`.
  Blink verified = real closed-eye art swap (orange arcs).
- **Recipe deltas:** (1) The figure mask's 2500px component filter dropped the
  small disconnected glints — fixed by OR-ing the tight-ROI glint mask back
  explicitly. (2) The right "glint" first identified from the grid was
  actually the hood's orange edge; true glint positions were re-measured
  from a gridded eye zoom (L ~(135–225, 198–248), R ~(275–355, 200–242)).
  (3) The outline-proximity chain cut caught too much robe (runes/folds
  share the dark outlines) — verified visually, accessory layer dropped;
  chains + HOLLOW pendant stay on the torso (Onyx staff precedent).

## Sombra Negra — COMPLETE (3/4 profile, no visible arms)

`sombra/Sombra.inp` — sha256 `5ceb934f649603ab…`

- **Parts (7):** 00_torso (black robe + purple trim + purple rune
  embroidery), 01_face_base (hood + black void, 3/4 profile),
  02_accessory (gold chains + gold **skull pendant**, ParamAcc0 sway),
  03/04_eye_l/r (small white glints), + 2 synthesized closed eyes.
- **Params (12, all bound):** eye open/smile, AngleX/Y/Z, Acc0,
  BodyAngleX/Y/Z, Breath. **No arm params** — arms are inside the robe in
  the source; none visible.
- **Proofs:** `proofs/sombra_pose_{neutral,head-turn,blink,comparison}.png`.
  Blink verified = real closed-eye art swap (white arcs; white px 366→172).
- **Recipe deltas:** the trim HSV range also catches the purple night sky —
  fixed with a geometric figure ROI + a hand-measured left/right boundary
  polygon following the robe's diagonal trim edges (documented in
  `extract_parts.py`). Council role TBD per canon — the rig renders no role
  text.

## Cross-cutting notes

- QA lints `lint:missing_role` / `lint:missing_param` ('mouth',
  'ParamMouthOpenY') fire on all five — expected; the linter assumes an
  anime face, these are void-faced by design. No mouth layers exist.
- The known nijigenerate setup-wizard headless block stands (Xvfb + D-Bus
  recipe in `tools/puppet/PROOFS.md`); this wave used the same image2live2d
  API path as Waves 4–5 and did not need to re-solve it.
- Debug/check artifacts (`parts/_debug_*`, `_chk*`, `__pycache__`) are
  gitignored, not committed.
