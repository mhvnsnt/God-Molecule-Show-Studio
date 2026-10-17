# MARS Head Rig — RIG-REPORT.md (v1)

**Date:** 2026-10-10
**Asset:** `tools/character/Marshead_Tripo_63779a1f.glb` → `Marshead_rigged_v1.blend`
**Status:** RIGGED + POSE-VERIFIED. Animation-ready for head/jaw performance. Known limitations listed below — nothing hidden.

## Diagnosis (before any repair)

Ran the diagnostic pass on the source GLB (`/tmp/diagnose_mars.py` measurements + the repo's `diagnose_rig.py` suite located at `bannon-video-pipe/repo/tools/rig-repair/diagnose_rig.py`):

- **1,114,516 verts / 1,940,858 faces** — raw Tripo scan density, far too heavy to rig or animate directly.
- **NO skeleton** (0 skins), **NO morph targets**, no JOINTS/WEIGHTS attributes.
- 1 mesh, 1 material, 3 textures, has normals + UVs.
- **Verdict:** not a broken rig — a *missing* rig. Static statue. Nothing to repair; a rig had to be built from zero.

## What was built

1. **Decimation** (trimesh, outside Blender — the full mesh OOM-killed Blender twice): 1,114,516 → **58,423 verts / 100,000 faces**. Original GLB untouched.
2. **Armature** (`MARS_rig`, 4 bones):
   - `root` — floating-head position (Mars is a floating head per Bible A; no body).
   - `neck` → `head` — head orientation / gaze.
   - `jaw` — child of head, hinge placed ~30% up from chin, slightly behind face center.
3. **Binding:** automatic weights first, then **region-based jaw weight fix** — auto-weights gave the whole head to the head bone (jaw-open render showed zero mouth movement). Reweighted 9,219 chin/lower-face verts to the jaw bone with a smooth falloff, front-face only (dreads excluded).
4. **Pose verification (measured, not eyeballed):**
   - Jaw open 20°: max vert displacement **0.1234** local units, **9,217 verts** moving >1mm.
   - Jaw open 15° + head turn −12°: max coord 0.490 vs head height 0.844 — **no explosion, no flyaway verts.**
5. **Proof renders** (in `proofs/`): rest, jaw open (10° dialogue range + 20°), head turn, side view. Read them — the geometry is intact, the triangle forehead mark survived decimation.

## Animation-ready for

- Head turns, nods, tilts (rigid, clean).
- Jaw articulation for dialogue at normal speech range (5–12°). Voice-first pipeline: audio carries the performance, jaw sells it.
- Floating-head positioning via root bone.

## Known limitations (v2 follow-ups, not defects being hidden)

1. **No mouth interior.** The Tripo mesh has fused lips — opening the jaw stretches lip geometry rather than revealing a mouth. The GNM oral-donor bridge (`tools/character/build_mars_oral_bridge.py`) is the v2 path for close-up speech.
2. **Textures not linked in v1.** Renders are clay-white; the decimation pass dropped the material link. Re-link the 3 source textures from the original GLB before beauty renders.
3. **No separate eye bones.** Gaze is via the head bone. Mars's glowing-white-eye lookups are a v2 addition (separate eye meshes + eye bones).
4. **Blender 4.0 GLB exporter bug.** Exporting the rigged file to GLB crashes in `gltf2_blender_gather_joints` (`'NoneType' object has no attribute 'joints'`) — a Blender 4.0 exporter defect, not a rig defect. **The `.blend` is the canonical v1 asset** (Blender is the production tool). Re-export from Blender 4.2+ when a GLB is needed.
5. Jaw motion past ~15° shows weight-transition stretching — keep dialogue in the 5–12° range.

## Files

- `Marshead_rigged_v1.blend` — the rigged, pose-verified asset (canonical).
- `proofs/proof_rest.png` — rest pose.
- `proofs/proof_jawopen_10deg.png` — jaw at dialogue range.
- `proofs/proof_jawopen_v2.png` — jaw at 20° (shows the stretch limit honestly).
- `proofs/proof_headturn.png` — head turn.
- `proofs/proof_side.png` — side view.
- Original `Marshead_Tripo_63779a1f.glb` preserved untouched.
