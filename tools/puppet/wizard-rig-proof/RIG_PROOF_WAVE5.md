# RIG PROOF — Wave 5 (Onyx, Echo, Kiko)

Worker C, 2026-10-07. Three nijilive puppet rigs built with the Wave-4 Ashes
recipe (image2live2d / nijigenerate toolchain, BSD-2-Clause), in
`tools/puppet/wizard-rig-proof/{onyx,echo,kiko}/`.

Each rig: layered PNG parts → `.inp` (via image2live2d `convert_layers`) →
structural validation (`validate_inp.py`: magic, JSON, params bound, textures
decode) → proof renders (`render_poses.py` with the Wave-5
`render_pose_opacity` fix). All proof PNGs were opened and visually inspected
before sign-off (deliverable verification law).

Canon sources: TRUE_CANON_ROSTER / CHARACTER_ART.md in
`~/workspace/game-sweep/AshLanev2/docs/`; robe colors (Onyx green, Echo pink)
from CHARACTER_ART.md; Kiko from the owner-approved robed card
(`public/portraits/kiko-tanaka-robed.webp`, 2026-10-06). Ashes' grill smile is
his locked signature — all three here are black-void faces with eye glints
(Onyx, Echo) or pure void (Kiko, see honest gap). Nothing invented.

## Onyx — COMPLETE

`onyx/Onyx.inp` — sha256 `73b0765230509c1347ca5fba512084851415d0e8843fe2160d6485c18d7972f7`

- **Parts (12):** 00_torso (robe + staff, staff merged geometrically as a held
  prop), 01_face_base (green hood + black void, glints removed+inpainted),
  02/03_hair_side (gold hood bells, sway physics), 04/05_arm_l/r (white gloves),
  06/07_eye_l/r (green/white glints), + 2 synthesized closed eyes.
- **Params (18, all bound):** ParamEyeLOpen/R, ParamEyeLSmile/R,
  ParamAngleX/Y/Z, ParamHairSide (+variants), ParamBodyAngleX/Y/Z,
  ParamArmLA/LB, ParamArmRA/RB, ParamBreath. 2 physics rigs, 13 animations.
- **Proofs:** `proofs/onyx_pose_neutral.png`, `onyx_pose_head-turn.png`
  (AngleX 15, AngleY −10 — mild; the preview renderer artifacts past ~20°),
  `onyx_pose_blink.png` (real closed-eye art swap, verified working).
- **QA:** `lint:missing_role` ('mouth'), `lint:missing_param`
  ('ParamMouthOpenY') — expected; the linter assumes an anime face, Onyx is
  void-faced by design. No mouth layer exists (void reads as mouth interior).
- **Recipe deltas:** figure mask keeps ALL components >1500px (staff fragmented
  the robe into 55 pieces; largest-only amputated hood tips); staff hand-traced
  as a 17-waypoint polyline (width 26) because its S-curve defeated HSV
  segmentation; neighbor inpaint exempts figure zones (orb, bells).

## Echo — COMPLETE

`echo/Echo.inp` — sha256 `a814fc1cd8182d8f54444cc1a0a3d9d67cfec5a34ef2739d7712b7f1c549a066`

- **Parts (11):** 00_torso (pink splatter robe), 01_face_base (hood + black
  void), 02_accessory (gold chain + ECHO pendant, ParamAcc0 sway),
  03/04_arm_l/r (white gloves), 05/06_eye_l/r (pink glints), + 2 synthesized
  closed eyes (pink lash arcs, faithful to glint color).
- **Params (16, all bound):** eye open/smile, AngleX/Y/Z, Acc0, BodyAngleX/Y/Z,
  ArmLA/LB, ArmRA/RB, Breath. 2 physics rigs, 13 animations.
- **Proofs:** `proofs/echo_pose_neutral.png`, `echo_pose_head-turn.png`,
  `echo_pose_blink.png` (blink verified: open glints → closed pink lash arcs).
- **QA:** same expected void-face warnings as Onyx (no mouth layer).
- **Recipe deltas:** neon sign excluded via corner cuts (top-left sign spilled
  into the pink mask); glint mask caught 4 blobs (2 glints + 2 hood
  highlights) — split L/R by face-centre x=197, not by sorted extremes, else
  the highlights steal the eyes. No spray can (belongs to Echo's street-persona
  card, not the group art — not grafted).

## Kiko — COMPLETE (with honest gap)

`kiko/Kiko.inp` — sha256 `62f3daf9a4146f1431a1d04fd0647246b122c397d367fdd83a5bfbc949bedfb5`

- **Parts (9):** 00_torso (fur coat + bare chest + dragon tights + legs),
  01_face_base (white fur hood + black void), 02/03_hair_side (front fur drapes,
  sway physics), 04_accessory (gold chains + KIKO pendant + skulls + cross +
  compass, ParamAcc0 sway), 05/06_arm_l/r (fur sleeves). NO eye layers.
- **Params (18, all bound):** AngleX/Y/Z, HairSide (+4 variants) + HairSideV,
  Acc0, BodyAngleX/Y/Z, ArmLA/LB, ArmRA/RB, Breath. 2 physics rigs,
  10 animations. NO eye params (no eyes to drive).
- **Proofs:** `proofs/kiko_pose_neutral.png`, `kiko_pose_head-turn.png`.
  NO blink proof — no eye layers (see gap).
- **QA:** `lint:missing_role` ×3 (mouth, eye_l, eye_r), `lint:missing_param`
  ×3 — all expected for a pure-void face.
- **HONEST GAP — no eye glints:** the brief lists "sparkly white eye glints,"
  but the owner-approved robed card's face void is pure black at the pixel
  level (max V=90 across the void; verified on the original webp, not just the
  crop). The white eyes belong to the GROUP-ART Kiko — a different source with
  a different style and a full robe (no bare chest/tights). Painting glints in
  would invent canon detail: forbidden. Kiko ships with a pure void face, no
  blink. If the owner wants the group-art eyes composited, that's his call.
- **Recipe deltas:** source is the robed card (1060×1945 crop of the webp),
  not the group art — the card is the only source with the canon bare chest +
  dragon tights; street background excluded via body ROI + sign rect cuts +
  between-legs street subtraction (paint drips in that zone sacrificed as
  documented tradeoff); neon-sign corner cuts leave transparent (alpha=0)
  regions — correct, not a defect.

## Setup-wizard block — SOLVED (source-code analysis)

Wave 4 set `"firstrun_complete": true` in `~/.config/nijigenerate/settings.json`
and the wizard still appeared. Root cause found in nijigenerate source
(`source/app.d`, `source/nijigenerate/windows/welcome.d`):

- The first-run wizard ("Quick Setup") is gated by the setting
  **`hasDoneQuickSetup`** (bool) — NOT `firstrun_complete` (which only sets the
  default panel layout). Wave 4 set the wrong key.
- Startup logic (`app.d`): if `hasDoneQuickSetup` is true AND a file path is
  passed as `args[1]`, nijigenerate calls `incOpenProject(args[1])` directly —
  **no WelcomeWindow, no wizard**.
- There is no `--no-wizard` CLI flag; the settings key + file argument is the
  supported bypass.

**Fix applied:** `"hasDoneQuickSetup": true` added to
`~/.config/nijigenerate/settings.json`. Headless recipe:
`xvfb-run nijigenerate /path/to/rig.inp` → project opens directly, ready for
screenshot automation (xdotool/wmctrl no longer needed to dismiss anything).

**Honest caveat:** the nijigenerate binary is not currently installed on this
machine (Wave 4's build was ephemeral; `which nijigenerate` finds nothing), so
the bypass is verified by source-code reading, not by a live run. Re-verify
with a real binary before relying on it in automation.

## Files

- Rig scripts per character: `extract_parts.py`, `cut_parts.py`,
  `build_rig.py`, `render_poses.py`, `validate_inp.py` (all with provenance
  docstrings; Echo/Kiko adapted from Onyx with name/path fixes).
- `parts/` — layered PNGs + `parts_manifest.json`; `rig_layers/` — numbered
  role files fed to `convert_layers`; `proofs/` — posed renders +
  `rig_parameters.json`.
- Toolchain: image2live2d (BSD-2-Clause) via
  `/home/hatch/workspace/.venv-puppet/bin/python`; `.inp` opens in
  nijigenerate (BSD-2-Clause).
