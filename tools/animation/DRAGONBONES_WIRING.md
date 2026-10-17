# DragonBones — free Spine replacement (Wave 2 wiring)

Date: 2026-10-07. Repo: god-molecule (character/creative lane).

## License (verified 2026-10-07)
- **Runtimes: MIT** — confirmed in the cloned repo (`tools/animation/upstream/dragonbones-js/LICENSE`: "The MIT License (MIT), Copyright (c) 2012-2025 The DragonBones team and other contributors").
- **Editor: free** (no commercial restriction, no runtime fees).
- **Maintenance: alive** — DragonBonesJS Jan 2026, DragonBonesCSharp May 2026, Godot GDExtension Jun 2026 commits (Wave-1 "slowed" concern re-checked).

## Wiring status
- **WIRED (reference clone)**: `tools/animation/upstream/dragonbones-js/` — shallow clone, runtimes present for Cocos / Egret / Hilo / Phaser / Pixi (HEAD 64b6c69).
- Runtimes are MIT — safe to integrate into shipping code paths (unlike Spine, which is proprietary commercial).

## Pipeline slot
Reusable skeletal/cutout 2D character rigs for the Wizard Gang cast: rig once in the DragonBones editor (Pro free), animate via any MIT runtime. Primary free answer to Spine.

## Proof
- `tools/animation/upstream/dragonbones-js/LICENSE` — MIT text present.
- Runtime dirs present: Cocos, Egret, Hilo, Phaser, Pixi.
