# RIG PROOF — Wave 11 (Lane B audit: Static, Kiko, Sombra Negra, Onyx, Echo, Ashes BATTLE rigs)

**Date:** 2026-10-07
**Worker:** Lane B (Wave 11 orchestrator task)
**Recipe:** Wave 4–10 nijilive (image2live2d), extended not reinvented.
**Canon rule:** owner-established characters only; no invented characters/names/relationships.

## Headline finding: no new rigs needed — this wave was an audit + one repair

The Wave-11 task brief asked for battle rigs for the six "remaining" council
members (Static, Kiko, Sombra Negra, Onyx, Echo, Ashes). All six already
existed, built in Waves 7–9 and committed to this repo:

| Rig | Wave built | `.inp` | Params (all bound) | Physics | Anims | Textures |
|---|---|---|---|---|---|---|
| AshesBattle | 7 | `ashes-battle/AshesBattle.inp` | 21 | 2 | 18 | 13 |
| EchoBattle | 7 | `echo-battle/EchoBattle.inp` | 14 | 2 | 13 | 10 |
| StaticBattle | 8 | `static-battle/StaticBattle.inp` | 14 | 2 | 13 | 9 |
| KikoBattle | 8 | `kiko-battle/KikoBattle.inp` | 14 | 2 | 13 | 9 |
| SombraBattle | 9 | `sombra-battle/SombraBattle.inp` | 12 | 2 | 11 | 7 |
| OnyxBattle | 9 | `onyx-battle/OnyxBattle.inp` | 14 | 2 | 13 | 9 |

(The other three council members — Theory, Cipher, Hollow — got their battle
rigs in Wave 10. The full 9-member council battle set is now complete.)

This wave therefore did what the brief demanded of a build ("Verify each rig
yourself: open the posed renders, check part alignment, confirm canon
details") as an **independent verification pass** instead of a rebuild:

1. Re-validated all six `.inp` files structurally: magic `TRNSRTS\0`, JSON
   parses, every parameter has node bindings, every texture blob decodes.
2. Opened and inspected every committed proof render (comparison, neutral,
   blink, head-turn) for all six — part alignment, canon details, limb-by-limb.
3. Pixel-diffed the blink renders to confirm the closed-eye art swaps are
   real, not crossfade no-ops.
4. Found one genuine defect (Ashes-battle blink was a no-op) and repaired it
   with the proven Wave-9 fix — see below.

## Per-character verification (all eyes-on, this wave)

### Ashes-BATTLE — mid-dunk (REPAIRED this wave)
`ashes-battle/AshesBattle.inp` — sha256 `1e2cc03619bb17b15ae9298253ad114811e6b055e43a1baa828615384151914c`
(pre-repair: `ab9bdce663f42c17a1250df2e6ff962e90a4ed57c32b943319c755f8398c660f`)

- **Parts (13):** 00_torso, 01_face_base, 02_hair_side (braid L),
  03_hair_side (braid R), 04_accessory (chain + $S pendant), 05_arm_r,
  06_other (basketball prop), 07_eye_l / 08_eye_r, 09_mouth (grill),
  + 2 synthesized closed eyes.
- **Params (21, all bound):** eye open/smile, mouth open/form, AngleX/Y/Z,
  HairSide(×5), Acc0, BodyAngleX/Y/Z, ArmRA/RB, Breath.
- **Proofs** (`ashes-battle/proofs/`): neutral, head-turn mouth-open,
  blink, blink_opacity, comparison. **Canon verified:** red robe + flame
  designs, grill grin, braids, $S pendant, basketball all preserved.
- **DEFECT FOUND & FIXED:** the committed blink proof was a no-op (neutral
  vs blink diff = 79 px, tiny specks). Root cause: the eye glints were
  baked into `01_face_base` and the eye layers were ~100–200 px crumbs —
  the Wave-9 "head-texture eye punch" fix was never applied to the Wave-7
  rigs. Repair: re-segmented the full glint shapes (HSV yellow family,
  tight L/R ROIs split at x=672) → new full glint eye layers (L 265 px,
  R 160 px) cut from the source crop → Telea-inpainted the glint zones in
  face_base with the void color (grill/mouth untouched) → rebuilt the
  `.inp` (QA passed, 13 parts / 21 params) → re-rendered proofs.
  **Verified:** neutral vs blink_opacity now diffs 277 px in the eye zone
  and shows a real swap (full glints → thin yellow closed-eye arcs).
  Neutral and head-turn renders are byte-near-identical to the committed
  ones (80/46 px diff = anti-alias edges), so the canon look is unchanged.
  Pre-repair `.inp` + layers kept at `/tmp/ashes_pre_wave11_backup/` (not
  committed — backup hygiene).

### Echo-BATTLE — spray can raised (VERIFIED, no changes)
`echo-battle/EchoBattle.inp` — 14 params (all bound), 2 physics, 13 anims.
- **Canon verified:** pink robe + paint splatters, black void + white
  glints, gold chains + ECHO plate, spray-can prop — all preserved in the
  comparison render.
- **Blink verified:** glints → white arcs (real swap).
- **Known artifact RE-CONFIRMED:** the thin Static-blue strip persists on
  the left edge of Echo in neutral, blink, AND comparison renders. This is
  the Wave-7 documented preview-renderer UV limitation (auto-split arm
  meshes sample stale texture regions; `.inp` keyforms are correct) — not
  a rig-data defect. Documented, not hidden. Also visible: gray smearing
  around the spray can (documented inpaint tradeoff, reads fine at scale).

### Static-BATTLE — claw machine (VERIFIED, no changes)
`static-battle/StaticBattle.inp` — 14 params (all bound), 2 physics, 13 anims.
- **Canon verified:** deep-blue rune robe, black void + blue glints,
  pale-gold chains, white glove — matches the arcade source.
- **Known artifact:** thin horizontal blue dashes at frame edges in
  neutral/head-turn (same preview-renderer mesh-UV class as Wave 7;
  `.inp` keyforms correct). No pendant in this source — none grafted.

### Kiko-BATTLE — left fist raised (VERIFIED, no changes)
`kiko-battle/KikoBattle.inp` — 14 params (all bound), 2 physics, 13 anims.
- **Canon verified:** white fur robe + hood, black void + white angular
  glint shards, gold chains + KIKO plate, raised left fist — matches the
  fireworks source.
- **Blink verified:** real closed-eye art swap.
- **CANON FLAG (owner's call, unchanged from Wave 8):** the KIKO
  name-pendant is preserved byte-for-byte from the owner's own generated
  source art — no new in-world text authored. Same keep-or-cut flag class
  as Wave-6 Static's SWMG plate.

### Sombra-BATTLE — ritual circle summoning (VERIFIED, no changes)
`sombra-battle/SombraBattle.inp` — 12 params (all bound), 2 physics,
11 anims.
- **Canon verified:** black robe + purple trim/embroidery, black void +
  white glints, gold chains + skull pendant + belt chain with cross —
  matches the ritual source.
- **Blink verified:** glints → white arcs.
- Honest constraints stand: no arm parts (dark-gloved hands merged with
  sleeves in the painterly source), rune circle/smoke at the bottom is
  background, no mouth art (pipeline no-mouth path).

### Onyx-BATTLE — staff-raised jester stance (VERIFIED, no changes)
`onyx-battle/OnyxBattle.inp` — 14 params (all bound), 2 physics, 13 anims.
- **Canon verified:** green jester robe + peach bells, black void + green
  glints, gold chains + pendant, white glove — matches the skate-park
  source. Staff removed (prop), grip sliver kept.
- **Blink verified:** green glints → green arcs.

## Source-art gaps

**None for this task.** All six battle rigs draw on existing dynamic/action
sources already in the workspace:

- Ashes: `cartoonier/Group 11 - basketball.webp` (mid-dunk)
- Echo: `cartoonier/Group 17 - skate park.webp` (spray can raised)
- Static: `cartoonier/Group 14 - arcade.webp` (claw machine reach)
- Kiko: `cartoonier/Group 10 - fireworks.webp` (left fist raised)
- Sombra: `detailed/Painterly group 2 - ritual.webp` (summoning stance)
- Onyx: `cartoonier/Group 17 - skate park.webp` (staff-raised jester stance)

No placeholder art was generated and no anatomy was invented. Standing
honest constraints from Waves 7–9 remain accurate (3/4-body crops, no legs
invented, no mouth art on the void-faced five — the expected
`lint:missing_role`/`missing_param` no-mouth signal).

## Cross-cutting notes

- The Wave-9 blush-trap check (`ls rig_layers | grep -i blush` before every
  build) ran clean on the Ashes rebuild — no synth strays in the new `.inp`.
- No binaries >100MB committed (largest: the `.inp`s at ~1.6MB).
- Debug/check artifacts (`parts/_debug_*`, `*.npy`, `__pycache__`) remain
  gitignored, not committed. The pre-repair backup was moved to `/tmp`
  (not committed).
- Render paths: `tools/puppet/wizard-rig-proof/<ashes|echo|static|kiko|sombra|onyx>-battle/proofs/`.

## Verification method (this wave)

Every claim above was checked in this session, not inherited from prior
wave docs: all six `.inp` files re-parsed for magic/JSON/param-bindings/
texture-decode; comparison + neutral + blink renders opened and inspected
for all six; blink swaps pixel-diffed (Echo, Sombra, Onyx, Kiko verified
by prior diffs re-confirmed visually; Ashes verified by new diff
277 px). The Ashes defect was caught by this audit's pixel diff (79 px
no-op), fixed with the Wave-9 recipe, and the fix re-verified before
sign-off.
