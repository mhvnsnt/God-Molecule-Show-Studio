# Character Replacement / Motion Transfer — Alternatives Compared

Research date: 2026-10-10. For Wizard Gang EP02 photorealistic shot repair.

## The category

**Character replacement** (aka motion transfer / pose-guided animation): take a video of a person performing actions, replace them with a different character performing the same actions. This is the technology behind "person dancing in a music video → swapped with an AI character."

## Head-to-head

### Wan 2.2 Animate (Alibaba) — OUR PICK
- **What:** Character image + driving video → character performs the video's motion. Two modes: `animate` and `replace`.
- **Quality:** Best in class as of 2025-2026. Successor to Animate Anyone.
- **Requirements:** 16GB VRAM min (FP8), 24GB recommended. ~27GB disk.
- **Free path:** Kaggle T4 with GGUF Q3_K_M quantized model.
- **License:** Check Wan-AI repo for current terms.
- **Why pick it:** Most mature, best community support, ComfyUI workflows ready-made, handles full-body well.

### MimicMotion (Tencent) — BACKUP PICK
- **What:** Pose-guided character animation. Reference image + pose sequence → animated video.
- **Quality:** Very good. Key innovation: confidence-aware pose guidance (weights high-confidence keypoints more) + regional loss amplification (reduces distortion, especially hands/faces).
- **Requirements:** Similar GPU needs (~16GB VRAM).
- **Free path:** Same Kaggle/Colab approach.
- **License:** Open-source.
- **When to use:** If Wan 2.2 produces artifacts on hands/faces, try MimicMotion — its confidence weighting specifically targets those areas.

### Animate Anyone (Alibaba, 2023) — DATED
- **What:** The original pose-guided character animation paper.
- **Quality:** Good for its time, but struggles with eyes, hands, and character turns. Significantly improved upon by Wan 2.2.
- **Requirements:** 16GB+ VRAM.
- **Verdict:** Superseded. Only use if you need the specific paper implementation for research.

### MagicAnimate — NICHE
- **What:** Pose-guided animation, similar approach.
- **Quality:** Good, comparable to Animate Anyone era.
- **Requirements:** 16GB+ VRAM.
- **Verdict:** Less community support than Wan. No strong reason to pick over Wan 2.2.

### LivePortrait — FACES ONLY
- **What:** Transfers facial expression and head motion from driving video to a reference face.
- **Quality:** Excellent for faces. Very fast.
- **Requirements:** ~8GB VRAM (lighter than full-body models).
- **Free path:** Easier to run — might work on smaller GPUs.
- **When to use:** Close-up shots where only the face needs replacing. Already in our apob-clone stack.

### EbSynth — DIFFERENT APPROACH, CPU ONLY
- **What:** Paint ONE frame in 2D style → AI propagates it across the entire video using optical flow.
- **Quality:** Excellent for style transfer. Preserves original motion perfectly (it's not regenerating, it's repainting).
- **Requirements:** CPU only, no GPU needed. **But: Windows/Mac only, no Linux build.**
- **Free:** Yes, free download (beta).
- **When to use:** "Good motion, wrong style" shots. Paint a 2D keyframe, let EbSynth do the rest. Most controllable option.
- **Limitation:** Can't run on our Linux VM. Needs a Windows/Mac machine.

### ReActor — FACES ONLY
- **What:** Face swap (not animation). Replaces face in image/video with a reference face.
- **Quality:** Good for static face replacement.
- **Requirements:** 8GB+ VRAM.
- **When to use:** Already in apob-clone. For shots where body is fine but face needs swapping.

### Viggle — CONSUMER WEB TOOL
- **What:** Web-based character motion remix.
- **Quality:** Decent for short clips.
- **Free:** 5 videos/day, but watermark on free tier.
- **Verdict:** Not a pipeline. Useful for quick tests, not production.

## Decision matrix for EP02

| Shot problem | Best tool | Why |
|---|---|---|
| Full body photorealistic, motion is good | EbSynth (if Win/Mac) or Wan 2.2 replace mode | Preserve motion, fix style |
| Full body photorealistic, motion is bad | Wan 2.2 animate mode or regeneration | New motion needed |
| Face close-up photorealistic | LivePortrait or ReActor | Lighter, face-specific |
| Hands/faces artifacting in Wan output | MimicMotion | Better confidence handling |
| Quick test / proof of concept | Viggle (free tier) | Fast, no setup |

## Bottom line

**Wan 2.2 Animate on free Kaggle T4** is the primary path for full character replacement.
**EbSynth** is the best tool for style-only fixes but needs Windows/Mac.
**MimicMotion** is the backup if Wan struggles with hands/faces.
Everything else is situational.
