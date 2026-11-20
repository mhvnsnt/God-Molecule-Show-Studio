# AnimLab pipeline stage — God-Molecule-Show-Studio

Staged 2026-11-20 on branch `tools/animlab-wireup-20261120` (AnimLab wire-up, binaries UNFETCHED — see
`tools/animlab/README.md`).

## Where AnimLab slots in

This repo holds docs/research/wave2/PRODUCTION-PIPELINES.md and tools/video_pipeline/README.md (promo assembly, captions, SFX, voiceover). AnimLab slots in as Draw -> Rig/Tween -> Composite -> Finish, feeding the video pipeline: vector drawing, Bone/Game Bone/Curve/Envelope rigging and tweening, node-graph compositing, multi-camera timeline, audio mixer, MP4/PNG export — rigging/compositing experiments whose output goes into tools/video_pipeline for assembly.

## Stages AnimLab covers (for this show)

1. **Draw** — vector drawing, pegs.
2. **Rig/Tween** — Bone / Game Bone / Curve / Envelope rigging, tweening.
3. **Composite** — node-graph compositing, multi-camera timeline, audio mixer.
4. **Finish** — MP4 / PNG export.

## What AnimLab does NOT do here

- It does not replace this show's existing core pipeline or its locked rules.
- It does not ship unproofed: AnimLab output goes through the same own-eyes / proof
  gate as every other stage before it reaches the owner.
- Binaries are UNFETCHED as of 2026-11-20 (itch 429). Until `fetch-animlab.sh` lands
  them on Release `animlab-v0.2.26`, this stage is docs + fetch route only.
