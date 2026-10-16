# Viggle-Animate — Free Unlimited AI Body Replacement

**Never hit a Viggle paywall again.** This runs the open-source Viggle-Animate
on YOUR Kaggle T4 GPU. Free. Unlimited. No login walls. No 24-hour waits.

## What It Does

You upload:
1. **`driving_video.mp4`** — a video of YOU doing something (dancing, fighting, walking, whatever)
2. **`character.png`** — a picture of a character (Cape Jones, or anyone)

You get back:
- **`cape-jones-body-replace.mp4`** — the character doing YOUR exact motion

## How To Use (Dead Simple)

### Step 1: Open the notebook
Go to https://www.kaggle.com/code/new (sign in as usual)

### Step 2: Upload the notebook file
- Click **File → Import Notebook**
- Upload `cape_jones_viggle_kaggle.ipynb` (from this folder)

### Step 3: Enable GPU
- Right panel → **Accelerator: GPU T4 x2**
- **Internet: ON**

### Step 4: Run All
Click **Run All**. The notebook will:
1. ✅ Check GPU (2 sec)
2. ⬇️ Install ComfyUI + Viggle nodes (~5 min)
3. ⬇️ Download models ~25GB (~10-15 min, one-time)
4. ⏸️ **STOP and wait for you to upload your files**

### Step 5: Upload your files
In the right file panel, upload to `/kaggle/working/`:
- `driving_video.mp4` — you doing the motion (under 10 sec works best)
- `character.png` — the character image

### Step 6: Run the rest
Run the remaining cells. The notebook:
1. ✅ Verifies your uploads
2. 🎬 Starts ComfyUI + runs Viggle-Animate (~5-10 min for 124 frames)
3. ✅ Saves output to `/kaggle/working/cape-jones-body-replace.mp4`

### Step 7: Download
Right panel → find `cape-jones-body-replace.mp4` → Download.

**That's it. Unlimited renders, whenever you want.**

## Tips for Best Results

- **Driving video:** Good lighting, full body visible, simple background. Under 10 seconds.
- **Character image:** Clear, front-facing. The better the reference, the better the result.
- **Length:** 124 frames @ 24fps (~5 sec) is the sweet spot. Longer clips work but take more time.
- **First run** downloads 25GB of models. After that, Kaggle caches them.

## What's Under the Hood

- **Model:** Viggle-Animate (33.1B MiniMax-H3 finetune, open-source 2026)
- **Quantization:** Pruned INT8 (21GB — fits T4 with CPU offloading)
- **Sampler:** DMD2-distilled, 4 sigma points = 3 Euler steps (fast!)
- **Framework:** ComfyUI + custom Viggle-Animate nodes

## Files in This Folder

| File | What |
|------|------|
| `cape_jones_viggle_kaggle.ipynb` | The Kaggle notebook — upload this |
| `gen_notebook.py` | Regenerates the .ipynb after edits |
| `viggle_workflow_api.json` | The ComfyUI workflow (API format) |
| `viggle_workflow.json` | Original frontend-format workflow (reference) |
| `README.md` | This file |
| `KAGGLE-SETUP.md` | Detailed Kaggle setup troubleshooting |

## Troubleshooting

**"NO GPU VISIBLE"** → Settings → Accelerator → GPU T4 x2. Must be set BEFORE Run All.

**Out of memory** → Use a shorter driving video. 124 frames max for T4.

**Slow rendering** → Normal. T4 + CPU offloading = ~5-10 min per 124 frames. It's free though!

**Model download fails** → Check Internet is ON in Settings. Retry the cell.
