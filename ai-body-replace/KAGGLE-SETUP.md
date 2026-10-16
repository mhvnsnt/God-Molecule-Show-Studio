# Kaggle Setup Guide — Viggle-Animate

## One-Time Setup

### 1. Kaggle Account
You need a Kaggle account (free). Sign in at https://www.kaggle.com/

### 2. GPU Quota
- Free tier: **30 hours/week** of T4 GPU
- Check usage: Kaggle → Settings → Quota
- This notebook uses ~30-45 min per render (including model download first time)

### 3. Notebook Settings (CRITICAL)
Before clicking Run All:
- **Accelerator:** GPU T4 x2
- **Internet:** ON (needed to download models)

If you forget, the first cell will fail with "NO GPU VISIBLE".

## Model Downloads

First run downloads ~25GB:
| Model | Size | Source |
|-------|------|--------|
| Pruned INT8 diffusion | 21 GB | `drbaph/Viggle-Animate-ComfyUI` |
| DMD LoRA r64 | 0.94 GB | `drbaph/Viggle-Animate-ComfyUI` |
| Text conditioning | ~50 MB | `drbaph/Viggle-Animate-ComfyUI` |
| INT8 VAE | 3.17 GB | `Kijai/MiniMax-H3-experimental` |

Kaggle caches these in `/kaggle/working/` for the session. If the session
restarts, they re-download (takes ~10-15 min on Kaggle's fast network).

## Performance on T4

| Clip length | Render time (est.) |
|-------------|-------------------|
| 60 frames (~2.5s) | ~3-5 min |
| 124 frames (~5s) | ~5-10 min |
| 200+ frames | Use chunked workflow (not in this notebook) |

The INT8 model uses CPU offloading on T4's 16GB VRAM. It's slower than
a 24GB+ GPU but it works and it's free.

## Going Faster

If you get access to a bigger GPU (Colab Pro, Lightning AI, etc.):
1. Swap `minimax_h3_ref2va_viggle_pruned_int8_convrot.safetensors` for
   `minimax_h3_ref2va_viggle_bf16.safetensors` (66GB, max quality)
2. Remove `--lowvram` flag from the ComfyUI server startup
3. Expect 2-3x faster renders

## Internet Access

Kaggle's free tier includes internet access for notebooks. Must be
enabled in Settings. Without it, model downloads fail.

## Session Persistence

- `/kaggle/working/` persists for the session duration
- Models stay downloaded until the session ends
- Uploaded videos/images need re-upload if session restarts
- **Tip:** Keep the tab open. Don't let the session idle-timeout during renders.
