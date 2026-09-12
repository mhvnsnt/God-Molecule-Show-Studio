# EP01 Prompt-First Animation Lane

This lane is the operator-facing path for building Episode 01 before full autonomous agents are online.

## Operating model

`operator prompt -> planner -> canonical assets -> Blender/MCP -> animation -> render -> actual-pixel review -> QC -> repair -> evidence`

The same production contracts will later be driven autonomously. No second implementation is created for autonomous mode.

## Opening sequence

The first production target is the simple 2D Mars introduction:

1. Mars looks left.
2. Mars looks away.
3. Mars looks right.
4. Mars turns toward camera.
5. Operator supplies the final voice recording.
6. Rhubarb generates mouth cues from the recording.
7. Blender applies mouth/pose animation.
8. Mars accelerates away from camera.
9. The 2D representation transitions through the established purple geometric layer.
10. The representation resolves into a Gaussian-splat/world layer.
11. The shot continues into the editable 3D world with canonical Mars.

## Voice and lip sync

Use the operator's recording as the performance source. Rhubarb Lip Sync is the timing/viseme extractor; Blender Rhubarb Lip Sync NG is the preferred Blender integration candidate because it supports modern Blender versions and pose-library/shape-key workflows. Neither tool is allowed to alter canonical identity.

## Animation control

Use an animation-specialized Blender MCP where possible. The candidate currently exposes exact frame rendering, contact sheets, rig inspection, keyframe editing, F-curves, NLA, constraints, video-reference alignment, and evaluated transform checks. This is especially useful because animation must be reviewed from rendered pixels rather than transform values alone.

## World transition

The Gaussian stage is an environment representation layer. It does not replace canonical character geometry. `gsplat` is the primary high-performance research/runtime candidate; OpenSplat is the portable CPU/GPU alternative. The transition should be authored as a visible production effect: 2D reference -> particles -> Gaussian layer -> fused/editable world.

## Motel / storyboard lane

The existing Episode 01 storyboard is the shot authority for the motel prayer sequence. The prompt-first system must preserve the established beats and permit the operator to request individual shots, blocking changes, camera changes, animation passes, and hybrid real-footage/2D/3D transitions.

## Kevin portal lane

Kevin is treated as a persistent spatial character/environment, not a decal or face texture. The forehead symbol becomes a physical slot/door. Opening it exposes a real interior room containing the canonical Kevin asset. This requires its own model/scan ingest, rig, facial animation, room environment, portal animation, continuity, and actual-pixel review.

## Evidence rules

No prompt execution can produce a PASS merely by completing tool calls. A production claim requires the actual output pixels to be reopened, hashed, measured where applicable, visually reviewed, and lineage-recorded. Unknown remains blocked.
