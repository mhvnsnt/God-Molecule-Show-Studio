# Animation Kit

The TRIPPEDD 2D hand-drawn + rotoscope pipeline toolkit. Every tool is
**free and open-source** — no paid APIs, no cards, standing law.

Proven end-to-end on the Luck of the Irish commercial v3
(EbSynth rotoscope + painted keyframes + authored cartoon FX).

## What's inside

| Tool | Dir | Does |
|---|---|---|
| EbSynth | `ebsynth/` | Propagates a painted keyframe's style across real motion (optical-flow, non-generative). The core of the rotoscope mix. |
| RIFE 4.26 | `rife/` | 2x/4x motion-interpolated frames (smoothing, slow-mo holds) |
| White-box cartoonize | `whitebox-pytorch/` | Photo → clean cartoon (flat color, inked edges) |
| AnimeGANv2 | `animeganv3/` | Photo → painterly anime (different style family) |
| Real-ESRGAN | `upscale/` | 4x anime-aware upscaling/restoration |
| clean-kit | `clean-kit/` | Denoise / temporal denoise / deflicker (OpenCV) |
| rembg | `rembg/` | Background removal ladder: u2net → isnet-general-use → isnet+alpha-matting → birefnet (GPU) |
| tracing / trace-kit | `tracing/` | Raster → SVG vector tracing; mascot-grade posterize-first pipeline |
| sticker-kit | `sticker-kit/` | Alpha cleanup, matting refine, white-border sticker compositing |
| loop-kit | `loop-kit/` | Seamless loops: bob/breathe, ping-pong, crossfade |
| Blender Grease Pencil | `grease-pencil/` | Scripted headless 2D hand-drawn FX |
| pose-extract | `pose-extract/` | MediaPipe pose extraction → motion-transfer driving |
| audio-kit | `audio-kit/` | Dialogue cleanup: spectral NR → arnndn → loudnorm (commercial chain) |
| wan-animate | `wan-animate/` | Colab notebooks / research for pose-driven animation |

Full per-tool docs, invoke lines, and the tool ladder: **`TOOLS-REGISTRY.md`**.

## Install

```bash
bash fetch_models.sh          # CPU-tier models
bash fetch_models.sh --gpu    # + GPU-tier heavies (birefnet, RMBG-2.0)
pip install -r <tool>/requirements.txt   # per tool, as documented in TOOLS-REGISTRY.md
```

Model binaries are NEVER committed — `fetch_models.sh` pulls them.

## Provenance rule (owner law)

Never claim hand-drawn when AI generation was involved. Document per-step
AI vs manual provenance in each job's METHODS file.

## How the tools compose

```
live footage
  ├─ clean-kit → denoise/deflicker footage + EbSynth output
  ├─ rembg (ladder) → performer matte → composite over clean plate
  ├─ EbSynth ← hand-drawn OR AI-styled keyframe (keyframe-agnostic)
  ├─ upscale → restore/enlarge keyframes pre-stylization
  ├─ cartoon ladder: whitebox (clean cartoon) / AnimeGANv2 (painterly anime)
  ├─ tracing ladder: vtracer → trace-kit → SVG character art
  ├─ sticker-kit ← rembg cutouts → merch-ready stickers
  ├─ Grease Pencil → authored FX (starbursts, speedlines, poofs)
  ├─ RIFE → smooth sequences / slow-mo holds
  ├─ loop-kit → seamless holds/idles
  ├─ audio-kit → dialogue cleanup, broadcast loudness
  └─ ffmpeg → deflicker, denoise, color-match, final assembly
```
