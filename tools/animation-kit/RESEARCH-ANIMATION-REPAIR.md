# Animation Repair Research — Wizard Gang EP02

**Date:** 2026-10-10
**Purpose:** Broad research (vertical + horizontal) on techniques to repair AI-generated 2D cartoon footage that drifted into photorealistic/3D.
**Context:** 19 of 29 EP02 shots drifted realistic. Approved styles ONLY: 2D cartoon (Shadow Wizard Money Gang base) and painterly (dramatic beats). Repair must be co-authored (manual + AI), not fully AI.

---

## 1. CARTOONIZATION FILTERS (Vertical — deeper)

### 1a. White-box Cartoonization (RECOMMENDED for our pipeline)

- **Paper:** "Learning to Cartoonize Using White-box Cartoon Representations" (CVPR 2020)
- **What it does:** Decomposes images into three cartoon representations — surface (smooth color blocks), structure (segmentation-like superpixels), texture (high-frequency line detail) — and trains a GAN to reproduce them.
- **Why it fits us:** Explicitly designed to produce flat-color, clean-edge cartoon output rather than painterly/anime output. The "white-box" design means the cartoon effect is controllable and interpretable, not a black-box style.
- **Video support:** YES — the PyTorch implementation includes `inference.py` with direct video input support (`-s input.mp4`), batch processing (default batch_size 32).
- **Speed:** Paper reports ~17ms per 720×1280 frame on GPU — real-time capable.
- **Temporal consistency:** This is the known weakness. Frame-by-frame cartoonization flickers. Research ("Unsupervised Coherent Video Cartoonization with Perceptual Motion Consistency") benchmarked WhiteboxGAN against CartoonGAN, CycleGAN, CUT: WhiteboxGAN alone has moderate warping error, but **WhiteboxGAN + DVP (Deep Video Prior) post-processing achieved the lowest short-term warping error** of all tested methods while preserving cartoon edges. Plain post-processing (blind temporal smoothing) reduces flicker but hurts the cartoon effect (blurs clear edges).
- **Implementation:** https://github.com/vinesmsuic/White-box-Cartoonization-PyTorch
- **License note:** Original repo is SystemErrorWang/White-box-Cartoonization; check license before commercial use.
- **Action:** Clone into `~/workspace/video-fix-tools/`, benchmark on one drifted clip (e.g. shot 1:40 street crew). Compare with/without DVP temporal smoothing.

### 1b. AnimeGAN / AnimeGANv2 / AnimeGANv3

- **What it does:** GAN-based photo-to-anime conversion. v2 improved facial feature handling; v3 (2022) improved temporal smoothness for video.
- **Fit for us:** POOR fit. AnimeGAN produces anime-style output (Japanese animation look), not the Shadow Wizard Money Gang / Western 2D cartoon look. Would introduce a *different* style drift.
- **Verdict:** Do not use for EP02 repair. May be useful for future anime-styled projects.

### 1c. CartoonGAN

- **What it does:** Earlier GAN cartoonizer (2018). Produces Hayao Miyazaki / Shinkai / Paprika / Hosoda styles.
- **Fit:** Same problem as AnimeGAN — wrong style family. Also worse temporal consistency than White-box per the PMC benchmark.
- **Verdict:** Skip.

### 1d. DCT-Net / InST (Instruction-based Style Transfer)

- **What it does:** Newer diffusion-based style transfer with content calibration network (CCN) to preserve identity and a geometry expansion module (GEM) for scale/rotation robustness.
- **Fit:** Interesting for *identity preservation* during style transfer — the CCN explicitly keeps content symmetric between source and target domains. Could help keep character likenesses stable while cartoonizing.
- **Maturity:** Research-stage (arXiv 2504.02875). Not a drop-in tool yet.
- **Verdict:** Watch, don't adopt yet.

### Cartoonization comparison summary

| Method | Style fit (WG 2D) | Video support | Temporal consistency | Speed | Verdict |
|---|---|---|---|---|---|
| White-box Cartoonization | HIGH (flat cartoon) | Yes (built-in) | Medium (fix w/ DVP) | Real-time GPU | **ADOPT — benchmark first** |
| AnimeGAN v2/v3 | LOW (anime look) | v3 yes | Medium | Fast | Skip for EP02 |
| CartoonGAN | LOW (anime look) | No | Poor | Fast | Skip |
| DCT-Net/InST | Unknown | Research | Unknown | Slow | Watch |

---

## 2. TEMPORAL CONSISTENCY (Vertical — deeper)

The core problem: any frame-by-frame filter flickers. Five approaches, in order of recommendation:

### 2a. EbSynth — keyframe propagation (RECOMMENDED primary method)

- **What it does:** You paint/style ONE frame (keyframe). EbSynth propagates that exact style across the entire video using optical-flow-guided patch synthesis. No flicker *by design* — every frame derives from your hand-authored keyframes.
- **Why it's perfect for us:** This is the co-authored workflow the owner wants. Paint one 2D keyframe per shot (or per motion segment), EbSynth fills in the rest. Style is 100% human-controlled; AI only does the in-between propagation.
- **Cost:** FREE (beta). Windows + macOS.
- **Workflow:**
  1. Export drifted clip as PNG sequence (ffmpeg).
  2. Pick representative keyframe(s) — one per distinct pose/motion segment. Add more keyframes where motion is complex (EbSynth docs recommend this for fast movement).
  3. Paint the keyframe in 2D cartoon style (Krita/GIMP/Photoshop) — OR generate it with White-box cartoonization and clean it up by hand.
  4. Run EbSynth: point it at video frames + keyframe(s), set output folder, hit synth.
  5. Reassemble with ffmpeg.
- **Pro tips from tutorials:** Use track mattes / alpha channels to reduce warping on complex backgrounds. For shots with lots of movement, add keyframes every ~10-20 frames instead of just one.
- **ComfyUI integration:** https://github.com/gcd0318/comfyui-ebsynth — runs EbSynth inside ComfyUI via the Ezsynth Python library. Useful if we build a ComfyUI pipeline.
- **Limitation:** EbSynth is NOT open-source (free but proprietary). Per the owner's clarified rule ("free and accessible counts"), this is acceptable — but note license status honestly.
- **Action:** Download EbSynth, test on one 5-second drifted clip with a hand-painted keyframe.

### 2b. RIFE — frame interpolation for smoothing

- **What it does:** Generates intermediate frames between existing frames using learned optical flow (ECCV 2022).
- **Use for us:** NOT as a style tool — as a *smoothing* tool. If White-box cartoonization produces flickery output, running RIFE 2x interpolation *after* cartoonization can smooth temporal jitter (interpolated frames average out per-frame variation).
- **Repo:** https://github.com/hzwer/ECCV2022-RIFE (also megvii-research original)
- **CLI:** `python3 inference_video.py --exp=1 --video=video.mp4` (2x), `--exp=2` (4x)
- **Also:** Google FILM (Frame Interpolation for Large Motion) — similar, handles larger motion better.
- **Action:** Test RIFE 2x on White-box output to measure flicker reduction.

### 2c. DVP (Deep Video Prior) post-processing

- **What it does:** Trains a small network on the video itself to learn its temporal prior, then uses it to enforce consistency on per-frame processed output.
- **Evidence:** The PMC benchmark paper found WhiteboxGAN+DVP had the *lowest* short-term warping error of all methods tested.
- **Maturity:** Research code, not a polished tool.
- **Action:** Lower priority than EbSynth/RIFE. Revisit if flicker persists.

### 2d. Optical-flow-guided blending (DIY)

- **What it does:** Compute optical flow between consecutive cartoonized frames (OpenCV Farneback or RAFT), warp previous frame forward, blend with current frame (e.g. 80/20). Cheap temporal smoothing.
- **Fit:** We already have OpenCV. This is a ~30-line script. Good enough as a quick fix; less principled than DVP.
- **Action:** Implement as fallback in the pipeline script.

### 2e. Deflicker via temporal median

- **What it does:** For each pixel, take the median across a 3-5 frame window. Kills high-frequency flicker, slightly softens motion.
- **Fit:** Nuclear option. Use only if nothing else works — it can make motion look smeary.
- **Verdict:** Last resort.

### Recommended temporal stack (in order)

1. **EbSynth** (keyframe method — no flicker by construction) ← primary
2. **White-box + RIFE 2x** (filter method + interpolation smoothing) ← secondary
3. **Optical-flow blending** (DIY fallback)
4. **DVP** (research-grade, if needed)

---

## 3. ROTOSCOPING TOOLS (Vertical — deeper)

### 3a. OpenRotoscope / OpenRoto (RECOMMENDED for masking)

- **What:** Local, open-source rotoscoping workflow for DaVinci Resolve (Free and Studio). Uses **SAM 2.1** for AI-assisted subject selection and tracking.
- **Workflow:** Playhead over clip → Workspace > Scripts > OpenRoto → click subject (left-click include, right-click exclude) → scrub and add correction points → track (Fast/Balanced/High) → Render & Apply as Fusion compound.
- **Why it matters:** This is the fastest free roto workflow found. SAM 2.1's video memory mechanism tracks masks across frames automatically — you click once, it propagates. Traditional roto requires drawing splines on every keyframe.
- **Repo:** https://github.com/ninocss/OpenRotoscope (already cloned in `~/workspace/video-fix-tools/OpenRotoscope`)
- **Status:** Developer preview, but Resolve Free round-trip validated.
- **Action:** Already cloned — needs actual install/test, not just the clone.

### 3b. Sammie-Roto-2

- **What:** Standalone SAM-based rotoscoping GUI (not tied to Resolve).
- **Workflow:** Load video → click to create mask in Segmentation view → "Track objects" propagates across all frames → "Deduplicate masks" for animation (stabilizes masks on hold frames) → refine in Matting view → export.
- **The "Deduplicate masks" feature is gold for us:** animation often holds on 2s/3s — this button makes masks stable on static frames instead of jittering.
- **Wiki:** https://github.com/Zarxrax/Sammie-Roto-2/wiki
- **Action:** Evaluate as alternative to OpenRoto if Resolve integration is problematic.

### 3c. SAM 2.1 directly (facebookresearch/sam2)

- **What:** Meta's Segment Anything Model v2.1. Promptable image AND video segmentation with streaming memory.
- **Key capability:** Click an object in frame 1 → memory mechanism auto-tracks it through the whole video, handling occlusions and fast motion.
- **License:** Apache-2.0. Fully open-source.
- **Use for us:** (1) Character/background separation masks for compositing fixes. (2) Input to EbSynth workflows (mask the character, style-transfer only the character, keep painted background). (3) Fixing morphing backgrounds by locking background regions.
- **Action:** Install sam2, build a mask-extraction script for EP02 clips.

### 3d. Lester method (SAM + DeAOT + Douglas-Peucker → retro 2D)

- **Paper:** "Lester: Rotoscope Animation through Video Object Segmentation and Tracking" (MDPI Algorithms)
- **What:** Complete pipeline: SAM segments → DeAOT tracks through video → Douglas-Peucker algorithm simplifies mask contours → optional facial traits, pixelation, rim light → outputs retro-style 2D animation.
- **Why it matters:** This is *exactly* our use case formalized as a research method — video → 2D cartoon via segmentation + contour simplification. More deterministic than diffusion-based video-to-video (which the paper explicitly calls out for temporal consistency problems).
- **Action:** Read the paper's implementation details; the Douglas-Peucker contour simplification step could be added to our pipeline as a "cartoon line extraction" stage.

### 3e. Blender Grease Pencil (manual)

- **What:** Blender's 2D animation toolset. Draw vector strokes directly over video reference.
- **Use for us:** Hero-shot manual cleanup — when AI methods fail on a specific shot, an artist (or the owner on his phone per the co-authoring split) traces keyframes in Grease Pencil.
- **Verdict:** Keep as the manual backstop, not the primary method (too slow for 19 shots).

### 3f. OpenToonz (manual)

- **What:** Open-source 2D animation software (used by Studio Ghibli).
- **Use for us:** Same as Grease Pencil — manual backstop. Already cloned in `~/workspace/video-fix-tools/opentoonz` but not installed/verified.
- **Verdict:** Manual backstop only.

### Roto speed ranking (fastest → slowest)

1. **SAM 2.1 auto-tracking** (click once, propagates) — minutes per shot
2. **OpenRoto / Sammie-Roto-2** (GUI over SAM 2.1) — minutes per shot
3. **Lester pipeline** (auto-segment → simplify → 2D) — minutes per shot, more setup
4. **Blender Grease Pencil / OpenToonz** (manual trace) — hours per shot

---

## 4. PROFESSIONAL AI-ASSISTED CLEANUP (Horizontal)

What studios actually do (from AWN, Moople Institute, Medium industry pieces):

| Pipeline stage | What AI does | What the artist still owns |
|---|---|---|
| Rotoscoping / paint-outs | Faster first-pass mattes and cleanup | Edge quality, shot-specific fixes, approval |
| In-betweening | Motion cleanup, AI in-betweening (Autodesk MotionMaker: 60-70% time reduction) | Acting, timing, weight, emotion |
| Cleanup / line consistency | Stabilize line weights, minimize jitter across frames | Original artistic intent |
| Stylization / look-dev | **Style transfer and fine-tuned models that enforce a show-specific look across many shots** | Artists provide keyframes and corrections |
| Roto / mattes | **Training show-specific models from a limited hand-rotoscoped set** → production-grade mattes | QC and approval |

**Key insight for us:** The professional pattern is *show-specific models trained from artist keyframes*. For EP02, this means:
- Hand-paint 3-5 keyframes in the locked 2D style (the "style bible" frames).
- Use those as the style reference for every repair method (EbSynth keyframes, White-box fine-tuning target, ControlNet reference).
- Never let the AI invent the style — it only propagates what the artist defined.

**Autodesk MotionMaker** (Maya, June 2025): AI in-betweening from key poses. Relevant if we ever do 3D-assisted 2D, but not directly applicable to EP02 repair (we're fixing existing footage, not animating from scratch).

---

## 5. LIVE-ACTION → 2D IN REAL PRODUCTION (Horizontal)

### The EbSynth professional workflow (used in music videos, commercials)

1. Shoot / generate live-action (or in our case: use the drifted AI clip as "live-action" source).
2. Roto the subject (After Effects Roto Brush, or SAM 2.1 now).
3. Trace over keyframes in Photoshop/Krita — outlines, flat colors, shadows on separate layers.
4. Feed traced keyframes + original video into EbSynth.
5. EbSynth propagates the hand-drawn style across all frames.
6. Composite in After Effects / Natron / Blender VSE — fix color discrepancies, blend between keyframe regions.

**Direct mapping to EP02:** Our "live-action" is the photorealistic drifted clips. Steps are identical.

### The Lester workflow (research, deterministic)

1. SAM segments each frame → DeAOT tracks → Douglas-Peucker simplifies contours.
2. Optional: facial trait overlays, pixelation, rim light.
3. Output: clean retro 2D with excellent temporal consistency.

**Advantage over diffusion:** Deterministic. No hallucinated details, no morphing faces. The paper explicitly positions this against diffusion-based video-to-video which "suffers from temporal consistency problems."

### What this means for us

We have TWO proven live-action→2D paths that don't rely on generative AI inventing details:
- **EbSynth** (artist paints keyframe, AI propagates) — best quality, needs artist input per shot.
- **Lester** (auto-segment, simplify contours) — fully automatic, more "flat vector" look, may need style tuning for SWMG aesthetic.

---

## 6. STYLE-LOCK PROMPTING (Horizontal)

Best practices collected from production prompting guides (venice-video-harness, videoexpress-scripting, Higgsfield, MiniMax guides). These apply to ANY regeneration we do:

### 6a. FRONT-LOAD the style description

> "Style descriptions must be **front-loaded** in the prompt to prevent style drift between angles. Anti-pattern: Putting aesthetic at the END causes the model to commit to a rendering style before seeing style instructions, producing inconsistent angles (e.g., front is cartoon, profile is photorealistic)."

**Our template must start with style, not end with it.**

### 6b. Negative constraints are half the battle

> "Most advice is about what to tell the model to do. The underused half is what to tell it to stop doing. A negative constraint removes a specific drift artifact in real time."

**Required negatives for every EP02 regeneration:**
```
no 3D rendering, no photorealism, no realistic skin texture, no realistic fabric texture,
no live-action look, no realistic lighting, no volumetric shading, no subsurface scattering,
no photographic depth of field, no CGI, no Unreal Engine, no Octane render
```

### 6c. Repeat the style line in every segment

For multi-part prompts, end EVERY section with the same style anchor line. Don't describe it fresh each time — copy-paste the identical string.

### 6d. Use a reference library, don't redescribe

> "Decide the style once, and don't redescribe it in every prompt. Pick a specific style reference early and point every later generation back at it. Typing out a style description fresh each time just means hoping the model interprets it the same way twice."

We have `EP02_LIKENESS_BIBLE.md` and approved stills — these ARE the reference library. Regeneration prompts should reference the approved still by description, not invent new style words.

### 6e. Proven style-lock prompt template for EP02 regeneration

```
STYLE (front-loaded, do not alter):
Flat 2D cartoon animation, Shadow Wizard Money Gang art style.
Bold clean black ink outlines, flat cel colors, two-tone cel shading
with hard shadow edges. Hand-drawn, not rendered. Strictly
two-dimensional. Painterly treatment ONLY at dramatic beats.

[SHOT DESCRIPTION: characters, action, composition, using locked
likeness descriptions from EP02_LIKENESS_BIBLE.md — full description
every time, no abbreviations, no "same as before"]

STYLE REMINDER: 2D cartoon, flat colors, ink outlines, hand-drawn.
NEGATIVES: no 3D rendering, no photorealism, no realistic skin or
fabric textures, no live-action look, no realistic lighting, no CGI,
no volumetric shading, no photographic depth of field.
```

### 6f. For image-to-video specifically

> "The source image already defines composition and appearance. Focus on what begins moving, how much it moves, how the camera behaves, and what must remain untouched. Re-describing the entire image with different adjectives can unintentionally request a redesign."

**Our image-to-video prompts should:** start with the STYLE block, then describe ONLY the motion ("Static raises his hand, mouth moves as he speaks, background holds static"), then the negatives. Don't redescribe the characters — the approved still already shows them.

---

## 7. NEW 2025-2026 TOOLS (Horizontal)

### Adopt / evaluate now

| Tool | What | Cost | Relevance |
|---|---|---|---|
| **Wan 2.2 Animate** | Character replacement: reference image + driving video → character performs the video's motion | Free/open | HIGH — replace photorealistic characters with 2D versions doing same actions |
| **ComfyUI-EbSynth** | EbSynth as ComfyUI node | Free | HIGH — integrates EbSynth into our ComfyUI pipeline |
| **Stable Video Diffusion** | Open-source image-to-video | Free/open | MEDIUM — local generation without API limits, needs 8GB+ VRAM |
| **DomoAI** (video-to-anime) | Video-to-video stylization, preserves motion | Paid ($9-13/mo) | MEDIUM — good but paid; use only if free methods fail |
| **Wan 2.6 V2V** | Video-to-video restyling (via DramaPixel etc.) | Paid platforms | LOW — paid, wait for open release |

### Watch (not yet actionable)

- **DCT-Net / InST** — diffusion style transfer with identity preservation (research stage).
- **AniMatrix** — anime video generation model (wrong style family for us, but the temporal-consistency research is relevant).
- **Autodesk MotionMaker** — Maya-only, not applicable to our 2D repair.

### Already in our stack (verify, don't just clone)

From `~/workspace/video-fix-tools/`: OpenRotoscope ✓ (needs install/test), apob-clone, arsenal-style-transfer, opentoonz, synfig — all currently just cloned, not verified working. Krita src cloned but build not verified. **Action: verification sprint on all of these.**

---

## ACTIONABLE PIPELINE RECOMMENDATION

### Phase 1: Per-shot triage (do first)

For each of the 19 drifted shots, classify:
- **Type A (good motion, wrong style):** → EbSynth with hand-painted 2D keyframe. Fastest high-quality fix.
- **Type B (bad motion AND wrong style):** → Regenerate with style-lock template (§6e), then EbSynth if still drifty.
- **Type C (character drift but background OK):** → SAM 2.1 mask character → White-box cartoonize character only → composite over original background.

### Phase 2: Tool verification sprint

1. Install + benchmark White-box Cartoonization on one clip.
2. Download EbSynth, test keyframe propagation on one 5-second clip.
3. Install SAM 2.1, build mask extraction script.
4. Test OpenRoto or Sammie-Roto-2 for masking workflow.
5. Verify existing clones (OpenToonz, Synfig, Krita, APOB) actually run.

### Phase 3: Repair execution

1. Start with worst 3 shots (1:40 street crew, 3:20 basketball, 4:30 podcast).
2. Apply Phase 1 triage per shot.
3. QC frame-by-frame against likeness bible.
4. Roll proven method across remaining 16.

### Phase 4: Prevention

- All future generations use the §6e style-lock template.
- Log every prompt in PROMPT_LOG.md (already created).
- Build the approved-still reference library into every image-to-video call.

---

## SOURCES

- White-box Cartoonization paper: http://arxiv.org/pdf/2107.04551
- White-box PyTorch impl: https://github.com/vinesmsuic/White-box-Cartoonization-PyTorch
- Coherent Video Cartoonization (PMC): http://arxiv.org/pdf/2204.00795v1
- EbSynth: https://ebsynth.com/ (official)
- EbSynth beginners tutorial: https://aiimagegenerator.is/blog-ebsynth-beginners-tutorial-50501
- ComfyUI-EbSynth: https://github.com/gcd0318/comfyui-ebsynth
- OpenRotoscope: https://github.com/ninocss/OpenRotoscope
- Sammie-Roto-2 wiki: https://github.com/Zarxrax/Sammie-Roto-2/wiki
- SAM 2.1: facebookresearch/sam2 (Apache-2.0)
- Lester paper: https://Www.Mdpi.com/1999-4893/17/8/330
- RIFE: https://github.com/hzwer/ECCV2022-RIFE/blob/main/README.md
- Character consistency skill: https://github.com/jordanurbs/venice-video-harness/blob/HEAD/.agents/skills/character-consistency/SKILL.md
- Video prompting guide: https://github.com/ratava/videoexpress-scripting-skill/blob/HEAD/claude/videoexpress-scripting/SKILL.md
- Higgsfield consistency guide: https://higgsfield.ai/blog/keep-characters-consistent-ai-animated-series
- AWN on AI in VFX pipelines: https://www.awn.com/vfxworld/how-ai-rewriting-vfx-pipelines
- AI animation tools 2025: https://darvideo.tv/blog/ai-animation-tools-2025-the-future-of-ai-generated-video-and-creative-production/

---

*Research completed 2026-10-10. Next: tool verification sprint (§Phase 2) before repairing any shots.*
