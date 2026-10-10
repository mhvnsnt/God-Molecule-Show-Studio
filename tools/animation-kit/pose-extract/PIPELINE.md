# Pose-Guided 2D Animation Pipeline — Wizard Gang EP02 Repair

## Purpose
Convert the 19 photorealistic-drifted EP02 shots back to 2D cartoon style while
preserving the original motion. Extract skeletons from drifted clips → use as
ControlNet conditioning → regenerate in flat 2D cartoon style.

## Pipeline Stages

### Stage 1: Pose Extraction (WORKING — installed and tested)
**Tool:** MediaPipe Tasks PoseLandmarker (heavy model)
**Location:** `~/workspace/video-fix-tools/pose-extract/`
- `extract_pose.py` — main script
- `venv/` — Python 3.12 venv with mediapipe, opencv, numpy
- `models/pose_landmarker_heavy.task` — downloaded model (~150MB)

**Usage:**
```bash
cd ~/workspace/video-fix-tools/pose-extract
./venv/bin/python extract_pose.py --input clip.mp4 --out-dir ./pose-out/ [--max-frames N]
```

**Outputs:**
- `skeleton.mp4` — ControlNet-ready pose video (black bg, white bones, colored joints)
- `poses.json` — per-frame landmark data (normalized x/y/z coords, multi-person)
- `preview.png` — side-by-side original vs skeleton

**Test results (2026-10-10):**
- Tested on `ep02-retest/media-generation-ep02-14-1-realanim-*.mp4` (1248x704 @ 24fps)
- 48/60 frames had detectable poses (80% detection rate)
- Multi-person supported (up to 5 simultaneous)
- CPU-only, ~1 sec/frame on this VM

**Limitations found:**
- Struggles with heavily stylized/cartoon faces (trained on photorealistic)
- Occluded bodies → partial skeletons
- Only detects people, not the robed/hooded characters well (faces hidden)
- For better results on cartoon/anime: DWPose is preferred (see Stage 1b)

### Stage 1b: DWPose (RECOMMENDED for production, needs GPU)
**Why:** DWPose (from ControlNet authors) is trained on diverse data including
anime/cartoon. It's the standard for ControlNet pose conditioning.

**Install (requires CUDA GPU):**
```bash
# Via ControlNet Aux (ComfyUI custom node)
# https://github.com/Fannovel16/comfyui_controlnet_aux
# Or standalone:
pip install controlnet-aux
# Models auto-download: yolox_l.onnx + dw-ll_ucoco_384_bs5.torchscript.pt
```

**Key advantage:** DWPose draws the exact skeleton format ControlNet OpenPose
was trained on (18-point body + hands + face). MediaPipe uses 33 points with
different topology — needs conversion for best ControlNet compatibility.

**Recommendation:** Run DWPose on a GPU machine (Modal, RunPod, Colab) for the
actual EP02 repair. MediaPipe pipeline above is the CPU fallback.

### Stage 2: ControlNet Pose Conditioning
**Model:** `control_v11p_sd15_openpose` (for SD 1.5) or `control_v11p_sdxl_openpose`
- Source: lllyasviel/ControlNet on HuggingFace
- Also: `xinsir/controlnet-openpose-sdxl-1.0` (Apache 2.0)

**⭐ BEST FOR 2D/ANIME: Chenkin-UniControl-XL**
- Source: https://huggingface.co/ChenkinNoob/Chenkin-UniControl-XL
- 8-in-1 ControlNet (OpenPose, Depth, Canny, Lineart, etc.) trained specifically for anime/2D
- Key advantage: "Native Style Preservation" — doesn't degrade colors or add AI look like standard ControlNets
- Requires ComfyUI-Advanced-ControlNet custom node
- **This is the top pick for Wizard Gang** — preserves the flat cartoon aesthetic

**How it works:**
1. Skeleton video frames → ControlNet preprocessor (already done in Stage 1)
2. Each skeleton frame conditions the diffusion model to match that pose
3. Text prompt specifies the 2D cartoon style
4. Output: new frames with same poses, new style

**Key parameters:**
- `strength`: 0.8–1.0 for strict pose matching
- `start_percent`: 0.0, `end_percent`: 0.8 (let model refine details at end)

### Stage 3: Generation (needs GPU)

**Option A: AnimateDiff + ControlNet (ComfyUI) — RECOMMENDED**
- Base: Stable Diffusion 1.5 with AnimateDiff motion module
- Workflow: `LoadVideo` → DWPose Preprocessor → ControlNet Apply → AnimateDiff Sampler
- Reference: https://www.runcomfy.com/comfyui-workflows/transform-video-into-flat-anime-style-using-animatediff-controlnet-in-comfyui
- This is the proven path for "realistic video → anime/cartoon" conversion

**Option B: Wan 2.2 Animate (character replacement)**
- Input: character reference image + driving video (or pose sequence)
- Output: your character performing the same motion
- Best for: replacing a specific realistic character with a 2D version
- ComfyUI workflow: https://comfy.org/workflows/gsc_advanced_3_2-86efedaffa3e/

**Option C: LTX-Video 2.3 IC-LoRA (newer, faster)**
- First-frame image locks character appearance
- DWPose + depth guide the motion
- 9-step distilled inference (fast)
- Repo: https://github.com/jetaime2/comfyui-ltx-2.3-iclora-depth-pose

### Stage 4: 2D Style Control

**2D/Flat Cartoon Checkpoints (SD 1.5):**
| Model | Source | Notes |
|-------|--------|-------|
| `flat2DAnimerge_v45` | CivitAI | Flat anime style |
| `ToonYou` | CivitAI | Cartoon style |
| `Disney Pixar Cartoon` | CivitAI | Western cartoon |

**2D/Flat Cartoon Checkpoints (SDXL):**
| Model | Source | Notes |
|-------|--------|-------|
| `Animagine XL` | CivitAI | Anime, high quality |
| `Juggernaut XL + Toon LoRA` | CivitAI + LoRA | Cartoon |

**Style prompt template for Wizard Gang:**
```
Positive: "flat 2D cartoon, bold outlines, cel shaded, Shadow Wizard Money Gang style,
           vibrant colors, simple shapes, no photorealism, no 3D render, no realistic skin"

Negative: "photorealistic, 3D, CGI, realistic skin texture, photograph, detailed pores,
           subsurface scattering, octane render, unreal engine"
```

### Stage 5: Assembly
```bash
# Frames → video
ffmpeg -framerate 24 -i frames/frame-%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4
```

## Hardware Requirements

| Stage | CPU-only? | GPU needed? | Notes |
|-------|-----------|-------------|-------|
| Pose extraction (MediaPipe) | ✅ Yes | No | ~1 sec/frame on this VM |
| Pose extraction (DWPose) | Slow | Recommended | CUDA for reasonable speed |
| ControlNet + AnimateDiff | No | **Yes** | Min 8GB VRAM (SD1.5), 12GB+ (SDXL) |
| Wan 2.2 | No | **Yes** | 12GB+ VRAM recommended |

**This VM:** 7GB RAM, no GPU → can do Stage 1 (MediaPipe) only.
**For Stages 2-4:** Use Modal (T4), RunPod, Google Colab, or ComfyUI Cloud.

## LivePortrait (Face-Specific Transfer)

**What:** MIT-licensed portrait animation. Takes 1 still image + driving video,
transfers head pose + expression + lip movement onto the still.

**Repo:** https://github.com/KwaiVGI/LivePortrait

**Use case for EP02:** For close-up shots where the face drifted to photorealistic
but the body motion is fine. Extract the 2D character face still → drive it with
the original clip's facial motion → composite back.

**Install:**
```bash
git clone https://github.com/KwaiVGI/LivePortrait
cd LivePortrait
# Requires GPU for reasonable speed, CPU works but slow
```

**Complementary to pose pipeline:** Pose handles body motion, LivePortrait handles
face detail. Use both for hero shots.

## Quick-Start Commands

```bash
# 1. Extract poses from a drifted clip
cd ~/workspace/video-fix-tools/pose-extract
./venv/bin/python extract_pose.py \
    --input /path/to/drifted-clip.mp4 \
    --out-dir ./shot-XX-pose/

# 2. skeleton.mp4 is now ready as ControlNet input
# 3. On GPU machine: load into ComfyUI AnimateDiff+ControlNet workflow
# 4. Set 2D cartoon checkpoint + style prompts
# 5. Generate → assemble → QC
```

## Status (2026-10-10)
- [x] MediaPipe pose extraction installed and tested
- [x] Skeleton visualization verified (ControlNet-compatible format)
- [x] Multi-person support added
- [x] Pipeline documented
- [ ] DWPose setup (needs GPU machine)
- [ ] ComfyUI workflow tested (needs GPU machine)
- [ ] First EP02 shot repaired via this pipeline
