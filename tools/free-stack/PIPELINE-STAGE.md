# Pipeline Stage — God-Molecule-Show-Studio

Staged 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Each tool's exact slot in THIS show's pipeline. Source: this repo's own
`tools/video_pipeline/README.md` (promo production) + the sibling
`tools/animation-kit/` (2D hand-drawn + rotoscope kit) + dream-girl
branch `tools/production-stack-free` `PIPELINE.md`.

## This repo's pipeline (what already exists)

- **`tools/video_pipeline/`** — reproducible promo production in-repo
  (same zero-cost stack as TRIPPEDD / money-machine-hq; promos are build
  artifacts from a shot list + script; storyboard first, no procedural
  bone-wiggling promos, no fake gameplay):
  `promo_assemble.py` (shotlist → promo mp4), `voiceover.py` (Piper TTS,
  keyless), `sfx.py` (12-recipe SFX kit), `auto_caption.py`
  (faster-whisper word timestamps), `concept_batch.py` (Pollinations
  storyboards, no key). Box deps: moviepy 2.1.2, ffmpeg 8.1.2, piper-tts,
  faster-whisper, Pillow, numpy. Proven 2026-10-06
  (`money-machine-hq/pipeline/video/proof/el_toro_recut_50s.mp4`).
- **`tools/animation-kit/`** — the 2D hand-drawn + rotoscope toolkit
  (EbSynth, RIFE, white-box cartoonize, AnimeGANv2, Real-ESRGAN,
  clean-kit, rembg, tracing, sticker-kit, loop-kit, Grease Pencil FX,
  pose-extract, audio-kit, wan-animate; full ladder in
  `tools/animation-kit/TOOLS-REGISTRY.md`).

The new tools below FEED `tools/video_pipeline/` — they make the shots,
boards, and finished cuts that the promo pipeline assembles. Nothing here
replaces the pipeline; the pipeline is the assembly point.

## Stage map — Draw → Rig/Tween → Motion → Composite → Finish → video_pipeline

| Stage | Tool | Slot in THIS pipeline |
|---|---|---|
| Draw | Pencil2D 0.7.2 | Hand-drawn frame-by-frame roughs, timing tests, simple cel cuts. Lightweight pen-first seat; feeds boards + clean-up. |
| Draw | Douga build 1116 (Windows-only) | Pen-first cel animation with a real dope sheet (keys, holds, loops, exposure on ones/twos). Free exports carry a small "made with douga.app" watermark. Windows seat; pairs with Pencil2D. |
| Draw | Wick Editor 1.19.0 | Fast Flash-style vector cartoons + interactive/game-like clips (in-editor JavaScript). Desktop builds stale since 2020 — web editor live; quick-sketch seat only. |
| Rig / Tween | Synfig Studio 1.5.5 | **Best new pull.** Bone-rigged cut-out characters + automatic vector tweening — the gap-closer Tahoma2D doesn't cover at the same depth. Actively maintained. |
| Rig / Tween | Rigby2D 0.5.1 | 2D skeletal/mesh/IK/physics rigs, JSON/.skel export, game runtimes. The live Spine/Moho cover. GPU route for runs: Kaggle GPU / Colab / Lightning AI / Oracle. |
| Rig / Tween | AniCraft 0.2.1 | Clean-room Adobe Animate (Rust, XFL/FLA/SWF per project description). Shape tweens, Bone tool, camera layer; `anicraft-cli` renders headless. FLA-compat test still owed. |
| Rig / Tween (spare) | Enve (continuous d919d4d) | **STALE — last push 2022-09-25.** Real vector+rigging seat, kept as a spare/fallback only. Prefer Synfig for anything new. |
| Motion | Glaxnimate 0.6.0 | Motion graphics + Lottie / animated SVG / GIF / WebP. Titles, UI motion, Kdenlive companion. NOT a character-rigging tool. |
| Composite | (existing) animation-kit EbSynth + Blender/Grease Pencil | Rotoscope keyframe propagation, authored FX, cartoon ladders. New tools feed frames INTO this; they don't replace it. |
| Finish | Kdenlive 26.08.3 | **Primary NLE.** Cut episodes, assemble renders, subtitles, colour, scopes. Then `tools/video_pipeline/promo_assemble.py` builds the promo from the finished cut. GPU route for accelerated preview/effects: Kaggle GPU / Colab / Lightning AI / Oracle. |
| Finish | Olive 0.2.0-nightly | Secondary/alpha NLE, node-based experiments + fallback. **PAUSED upstream** — do NOT cut deadline work in it. |
| Finish | (existing) video_pipeline | `promo_assemble.py` + `voiceover.py` + `sfx.py` + `auto_caption.py` + ffmpeg = promo assembly + VO + SFX + captions + final encode. |

## Get the binaries

```bash
bash tools/free-stack/fetch-verify.sh   # all 10 tools, size + sha256 verified
```

Binaries live on mhvnsnt/dream-girl releases `harmony-equivalents-20261120`
and `production-stack-free-20261120`. Per-tool version, licence, size, and
SHA-256 are in each tool's README under `tools/harmony/` and
`tools/free-stack/`. Licence never gated a pull; licences are logged
honestly next to each item.
