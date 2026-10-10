# Wan 2.2 Animate — Character Replacement for EP02 Repair

**Status:** RESEARCHED 2026-10-10. Cannot run on our VM (no GPU). Free cloud path identified.

## What it is

Wan 2.2 Animate (Alibaba Wan-AI) does **character replacement via driving video**:
- Input: character reference image + driving video (person performing actions)
- Two modes: `animate` (reference character performs the video's motion) and `replace` (swap character into the video, keep background)
- This is the exact technology for "person dancing in a music video → replaced with our 2D character"

## Hardware requirements

| Setup | VRAM | Notes |
|---|---|---|
| FP16 full model | 24GB+ | RTX 4090 recommended |
| FP8 quantized | 16GB | RTX 4080 SUPER works with `blocks_to_swap` |
| GGUF Q3_K_M | ~10-12GB | Runs on **Kaggle T4 (16GB)** — the free path |

**Our VM:** No GPU, 7GB RAM. Cannot run. Not close.

## Model files (HuggingFace)

- Main: `Kijai/WanVideo_comfy_fp8_scaled` → `Wan22Animate/Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors` (~14-18GB)
- GGUF (for T4): `QuantStack/Wan2.2-Animate-14B-GGUF` → `Wan2.2-Animate-14B-Q3_K_M.gguf`
- VAE: `Kijai/WanVideo_comfy` → `Wan2_1_VAE_bf16.safetensors`
- Text encoder: `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` → `umt5_xxl_fp16.safetensors`
- CLIP Vision: `Comfy-Org/Wan_2.1_ComfyUI_repackaged` → `clip_vision`
- Detection: `Wan-AI/Wan2.2-Animate-14B` → `process_checkpoint/det/yolov10m.onnx` + ViTPose wholebody ONNX
- LoRAs: LightX2V speedup + WanAnimate relight LoRA (optional but recommended)

## Free GPU paths (ranked)

### 1. Kaggle T4 — BEST FREE OPTION
- 16GB VRAM, ~30 hrs/week free, 9-hour sessions
- Ready-made repo: https://github.com/architectum/wan-2.2-animate-comfyui-kaggle
- Uses GGUF Q3_K_M quantized model specifically tuned for T4
- Upload driving video + character image → download result
- **This is the recommended path for EP02 repair**

### 2. Google Colab (free tier)
- T4 GPU, ~12 hrs/day but sessions unreliable, gets preempted
- Same ComfyUI setup works but less stable than Kaggle

### 3. Modal (free tier)
- $30/month free credits, T4 available
- Good for scripted batch jobs
- Requires account setup

### 4. Lightning AI
- Free tier with T4, limited hours

## Paid APIs (NOT free — documented for reference only)

- **wavespeed.ai**: $0.04/sec at 480p, $0.08/sec at 720p. A 10s clip = $0.40-$0.80.
- **Replicate**: per-second billing, similar range.
- For 19 EP02 shots (~5-10s each): $8-15 total. Violates free-only constraint.

## How to use (once on GPU)

See `colab-wan-animate.ipynb` in this directory for a ready-to-run notebook.

Quick version:
1. Upload driving video (the photorealistic EP02 clip) + 2D character reference image
2. Mode: `replace` (keeps background, swaps character)
3. Prompt: "2D cartoon character, Shadow Wizard Money Gang style, flat colors, bold outlines"
4. Resolution: 480p for tests, 720p for final
5. Match aspect ratio between image and video

## Alternatives compared

| Tool | Type | Quality | GPU needed | Free? | Notes |
|---|---|---|---|---|---|
| **Wan 2.2 Animate** | Character replacement | Best in class (2025-26) | 16GB+ VRAM | Kaggle/Colab free | Successor to Animate Anyone. Two modes. Our pick. |
| **MimicMotion** (Tencent) | Pose-guided animation | Very good, better hands/faces | 16GB+ VRAM | Open-source, needs own GPU | Confidence-aware pose guidance. Good alternative if Wan fails. |
| **Animate Anyone** (Alibaba 2023) | Pose-guided animation | Good but dated | 16GB+ VRAM | Open-source | The original. Struggles with eyes/hands/turns. Superseded by Wan 2.2. |
| **MagicAnimate** | Pose-guided animation | Good | 16GB+ VRAM | Open-source | Similar category, less community support than Wan. |
| **LivePortrait** | Face/expression transfer | Excellent for faces | 8GB VRAM | Open-source | Faces only, not full body. Good for close-ups. |
| **EbSynth** | Keyframe style propagation | Excellent for style | **CPU only!** | **Free download** | Paint 1 frame in 2D → propagates to whole video. **Windows/Mac only** (no Linux). Best for "good motion, wrong style" shots. |
| **Viggle** | Web-based character remix | Decent | None (cloud) | 5 free videos/day | Consumer tool, watermark on free. Not a pipeline. |
| **ReActor** | Face swap | Good for faces | 8GB+ VRAM | Open-source | Faces only. In our apob-clone already. |

## Recommended EP02 repair strategy

For the 19 photorealistic shots, use a **combination**:

1. **EbSynth** (if Windows/Mac available): Paint keyframes in 2D style → propagate. Cheapest, most controllable. No GPU needed.
2. **Wan 2.2 Animate on Kaggle T4** (free): For shots where EbSynth can't fix it — full character replacement with 2D reference.
3. **Regeneration** (media generation API): For shots where motion is also bad — new clip with hard 2D style lock.
4. **Manual rotoscope** (OpenToonz/Krita): Hero shots only, most labor-intensive.

## Files in this directory

- `README.md` — this file
- `colab-wan-animate.ipynb` — ready-to-run Colab/Kaggle notebook
- `compare-alternatives.md` — detailed alternative comparison (TODO)
