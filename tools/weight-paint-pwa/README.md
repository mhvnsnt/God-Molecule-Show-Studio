# God Molecule Weight Paint PWA

Mobile-first web tool for hand-painting skin weights on the studio's 3D
characters. Same verified build already shipped to Bannon, AshLanev2,
ConcreteDragon, Brutal-Fist, AshLane-prototype, and URBAN-MAYHEM — now wired
to God-Molecule-Show-Studio for its 3D character/facial work.

## Use (on phone)

1. Open the link. The default model loads from this repo:
   `.trippedd_assets/mars_proxy.glb` (the Mars character proxy — the best
   character GLB currently in the repo).
2. Pick a bone (shoulders/arms pinned at top). Heat view: red = full weight, blue = none.
3. Drag on the model to paint. Add/Remove, radius, strength controls.
4. Drag the **Angle** slider (0–90°) to pose-test the arm raise live. Fix what tears.
5. **Export GLB** → send the file back to the pipeline.

**Note:** `mars_proxy.glb` is unrigged, so guided mode reports "unavailable"
on the default load. Load any **rigged** character GLB via `?model=<url>`
(or the 📁 upload button) for real weight-paint work — the studio's facial
and character pipeline is exactly where this earns its keep.

## Send-back loop

1. Export downloads `GOD_MOLECULE_painted.glb` with new weights baked in.
2. Hand the file to the pipeline (chat attach or repo).
3. Pipeline probe-renders the painted weights at 15/30/45/60/90° to prove zero webbing.
4. Clean → lands as the new model via PR. Not clean → probe frames come back
   showing where it still tears.

## Tech

Single `index.html`, Three.js r160 (vendored in `lib/`), ES modules + importmap.
No build step. Painting edits `skinIndex`/`skinWeight` in place (bind pose),
renormalizes to sum 1.0, GLTFExporter writes the result.

## Guided fix mode (for first-timers)

Tap **🧭 Start guided fix**. It walks you through in plain language:

1. Drag the **Angle** slider up (try 45°) until the shoulder looks stretched.
2. Tap **🔍 Find bad spots** — the tool scans the shoulder region, finds verts
   that move differently from their neighbors (the tear signature), and makes
   them pulse. It auto-selects the right bone (usually the shoulder).
3. Paint the glowing spots. They turn red as you fix them.
4. Tap **🔍 Check again** — if the glow is gone, you fixed it. Export the GLB.

Detection: per-vertex displacement (posed vs rest, via CPU skinning) restricted
to a 0.38-unit radius around the shoulder joints; flags verts exceeding
mean + 2.5σ of neighbor-displacement variance. Headless test: `?autotest=1&model=<url>`.

## Self-test (2026-10-09, headless Chromium + SwiftShader, localhost)

Run on the Bannon build of this same code (all deploys are the identical build):

- Load: 12,633 verts / 58 bones, renders correct heat view.
- Paint: real pointer stroke changed 558 verts (max delta 0.82) on LeftArm.
- Pose: slider drives `LeftArm.rotation.x` to −1.047 rad at 60°, visually confirmed.
- Export: GLB re-parsed — 32,348 weight components differ, all vert weight sums = 1.0.
