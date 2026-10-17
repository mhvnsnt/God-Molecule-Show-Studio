# Wave 7 Rig Proofs — Battle Poses (Lane C)

**Date:** 2026-10-07  
**Worker:** Lane C (Wave 7 orchestrator e1f9445a)  
**Recipe:** Wave 4–6 nijilive (image2live2d), extended not reinvented.  
**Canon rule:** owner-established characters only; no invented characters/names/relationships.

Two battle-pose rig proofs, same structure as the Ashes (Wave 4) proof:
layered PNGs → part/param manifest → posed renders → comparison QC render.

---

## 1. ASHES-BATTLE — Ashes mid-dunk

**Source:** `~/workspace/trippedd-studio/assets/wizard-gang-style-refs/cartoonier/Group 11 - basketball.webp`  
**Crop:** `ashes-battle/ashes_battle_crop_source.png` (780×885)

**Rig:** `AshesBattle.inp` — 13 parts, 21 params (all bound), 2 physics, 18 animations. QA pass. Magic `TRNSRTS\0` valid; all textures decode.

**Layers** (bottom→top): `00_torso`, `01_face_base`, `02_hair_side` (braid L), `03_hair_side` (braid R), `04_accessory` (chain + $S pendant), `05_arm_r` (auto-split `_lo`/`_up` two-link FK), `06_other` (basketball prop), `07_eye_l` / `08_eye_r` (split at x=672), `09_mouth` (grill).

**Proofs** (`ashes-battle/proofs/`): neutral, head-turn mouth-open (grill stretches open — matches Wave-4 behavior), blink, blink_opacity, comparison (source vs rig — grill smile, braids, $S pendant, ball all preserved).

**Honest constraints:** single visible arm; ball is a scene prop layer; braid kept out of the chain via actual-pixel (not ROI-rect) subtraction.

## 2. ECHO-BATTLE — Echo with spray can raised

**Source:** `Group 17 - skate park.webp` (same canon Echo as Wave-6 rig)  
**Crop:** `echo-battle/echo_battle_crop_source.png` (515×725)

**Rig:** `EchoBattle.inp` — 10 parts (arm auto-splits to 11 nodes), 14 params (all bound), 2 physics, 13 animations. Structurally valid. QA linter warns `missing_role` (mouth) + `missing_param` (ParamMouthOpenY) — **expected and honest**: Echo is a void-face character with no mouth art; the pipeline's no-mouth path applies (same as Wave-6 Echo).

**Layers** (bottom→top): `00_torso` (robe + paint splatters), `01_face_base` (hood + void), `02_accessory` (gold chains + ECHO pendant + ring), `03_arm_r` (pink sleeve + gripping hand, auto-split `_lo`/`_up`), `04_other` (spray-can prop + mist), `05_eye_l` / `06_eye_r` (white glints, split).

**Proofs** (`echo-battle/proofs/`): neutral, head-turn, blink (eyes close via synthesized closed-eye layers), comparison (source vs rig — ECHO pendant text, pink robe, spray can preserved).

**Honest constraints:**
- 3/4-body (rail occludes below y~655 — no legs cut, documented not faked).
- Spray can is a scene prop layer, not puppeted.
- The gripping hand was too fragmented for its own layer (27 px) — merged into the arm as the arm's end.
- Neighbor removal: Static (blue robe + gold chains + "MG" plate) left, Sombra (black) right edge, Hollow (red fringe) right — all keyed out spatially/colorimetrically (see `extract_parts.py`).
- **Known preview artifact:** a thin Static-blue strip persists on the left edge of preview renders. Root cause: the auto-split arm meshes (`03_arm_r_up`/`_lo`) have UVs offset from their verts (measured `max|vert-uv|` ≈ 0.41), so the preview samples stale texture regions. The `.inp` keyforms are correct; this is a preview-renderer limitation, not rig data. Documented, not hidden.

---

## Recipe lessons learned (Wave 7)

1. **The preview renderer ignores the `.inp`'s per-parameter OPACITY bindings.** Proof renders must replicate the emitter: exclude `07_eye_l`/`08_eye_r` for blink (leaves synthesized closed-eye art); exclude blush at rest. Verified against `.inp` keyforms.
2. **`from_layer_dir` / `prepare_meshes` re-run synthesis**, writing stray `1_blush.png`, `5/6_eye_closed_*.png`, `9_mouth_cavity.png` into `rig_layers/`. Filter `stack.layers` to `_INP_PARTS` before `prepare_meshes`; delete strays before `build_rig`.
3. **Chain kills must run AFTER final morphological close/dilate** — the 5×5 close regrows thin killed strands from surviving seeds.
4. **Clear RGB where alpha=0** in final layer PNGs (premultiply hygiene) to avoid transparent-pixel color bleeding in previews.
5. **Eyes must be split L/R** — a combined layer defaults to `eye_l`, breaking right-eye blink.
6. **nijigenerate setup wizard:** the dismiss key is `hasDoneQuickSetup` in `settings.json`, NOT `firstrun_complete` (previous waves set the wrong key). See `SETUP_WIZARD_WAVE7.md`.
