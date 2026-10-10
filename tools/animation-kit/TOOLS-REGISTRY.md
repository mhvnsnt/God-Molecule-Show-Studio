# Video Fix Tools — Registry

Open-source animation pipeline tools for the TRIPPEDD 2D hand-drawn + rotoscope
pipeline (LOTI v3, EP01 full-episode assembly). All tools are FREE, no card,
no paid APIs — standing law.

Shared Python environment: `venv/` (torch 2.14 CPU, torchvision, opencv,
rembg/onnxruntime, albumentations, scikit-video, pillow, numpy, gdown, tqdm).
Activate per-command via `venv/bin/python` — see each wrapper.

**Status key:** WIRED = pulled, installed, and verified executing on a real
test input. QUEUED = pulled or identified, not yet runnable here (reason given).
NOT-HEADLESS = GUI/plugin only, cannot run in this environment.

---

## WIRED

### 1. EbSynth — rotoscope / motion propagation (BASELINE)- **Path:** `ebsynth/` — wrapper `ebsynth/run_ebsynth.py`, binary `ebsynth/src/bin/ebsynth`
- **Does:** propagates a painted keyframe's style across real motion (optical-flow, non-generative)
- **Invoke:** `ebsynth/run_ebsynth.py --input in.mp4 --keyframe k.png --keyframe-index 0 --output out.mp4 [--keyframes k2.png@150] [--fps 12] [--scale 960:540]`
- **Verified:** wrapper `--help` clean; binary present; already proved end-to-end on LOTI v3 footage (5 painted part-keyframes → full transformation, segments segA–segE)
- **Stage:** propagation (the core of the rotoscope mix)
- **Note:** official repo, compiled from source. Keyframes are style-agnostic — AI-styled OR truly hand-drawn PNGs both work.

### 2. RIFE 4.26 — frame interpolation
- **Path:** `rife/` — wrapper `rife/run_rife.py`
- **Does:** 2x/4x motion-interpolated frames (smoothing hand-drawn sequences, slow-mo holds)
- **Invoke:** `rife/run_rife.py --input in.mp4 --output out.mp4 --multi 2 --scale 0.5 --fps 30`
  (`--scale 0.5` for 1080p on CPU, `1.0` for ≤720p; `--fps` sets output rate)
- **Verified:** 30f/15fps test clip → 59f/30fps, ~5 it/s CPU @320x180; interpolated frame inspected — clean, no tearing. Weights: `rife/train_log/flownet.pkl` (24MB, RIFE_HDv3 arch synced from weight bundle)
- **Stage:** FX / assembly (smoothing), EP01 (slow-mo holds)
- **Local patches (ours):** fixed upstream crash on audio-less inputs; synced `RIFE_HDv3.py`/`IFNet_HDv3.py` arch files from the weight bundle into `model/`; patched vendored `scikit-video` for NumPy 2.x (`np.float` removals)
- **Weights source:** https://github.com/hzwer/Practical-RIFE (4.26 Drive bundle)

### 3. White-box Cartoonization (PyTorch port) — cartoon stylization
- **Path:** `whitebox-pytorch/` — wrapper `whitebox-pytorch/run_cartoonize.py`
- **Does:** photo→clean-cartoon (flat color blocks, inked edges, smooth surfaces). Style-matches AI keyframes and hand-drawn frames into one cartoon world; cartoonizes rotoscoped backgrounds
- **Invoke:** `whitebox-pytorch/run_cartoonize.py --input in.jpg --output out.png`
  folder mode: `--input frames_in/ --output frames_out/` (batch, `--batch 4`)
- **Verified:** on a real LOTI v3 keyframe (1080p, ~16s CPU) — character identity preserved (green eyes, elf ear, dreads, hoodie), pushed visibly further into clean cartoon territory. Output inspected by eye.
- **Stage:** keyframe gen (style-matching), propagation prep, EP01 backgrounds
- **Weights:** `whitebox-pytorch/weights/sceneryonly.pth.tar` (17.6MB, shipped in repo)
- **Note:** official TF repo's `test_code` is TF1-only (dead on py3.12) and its Drive weights link now serves VGG training weights, not the generator — the PyTorch port is the working route. Wrapper works around upstream's output-path quirk (single-file mode ignores `--dest_folder`).

### 4. Blender Grease Pencil — hand-drawn FX, scripted headless
- **Path:** `grease-pencil/` — `gp_smoke_test.py`, `gp_test.png`
- **Blender:** `~/workspace/tools/blender/blender-4.0.2-linux-x64/blender` (run with `env -u PYTHONPATH`)
- **Does:** scriptable 2D hand-drawn strokes → PNG/RGBA renders. The lane for REAL hand-drawn FX (starbursts, speedlines, poofs) drawn by script or by an artist in Blender's GUI and rendered headless
- **Invoke:** `env -u PYTHONPATH <blender> --background --python your_gp_script.py` (see `gp_smoke_test.py` for the pattern: scene setup, GP stroke, camera, transparent PNG render)
- **Verified:** headless stroke render → PNG with alpha (7,336 visible px, colored stroke). Quirk: 4.0.2 ships 6 default GP materials (Black/White/Red/Green/Blue/Grey) — recolor the slot you use; material-color API otherwise works
- **Stage:** FX (authored cartoon effects), keyframe gen (artist-drawn hero frames)

### 5. rembg (u2net) — performer matting
- **Path:** `rembg/` — wrapper `rembg/run_rembg.py`
- **Does:** AI background removal → RGBA cutout. Cuts the performer out of live footage for the rotoscope mix (painted/cartoon body over clean plates, garbage-matte cleanup)
- **Invoke:** `rembg/run_rembg.py --input in.png --output out.png [--model u2net]` or folder mode `--input frames_in/ --output frames_out/`
- **Verified:** u2net on a real LOTI frame (640x360) — clean edge matte: head, dreads, elf ear, hoodie isolated, 14.9% foreground. Inspected by eye.
- **Stage:** propagation prep (mattes), compositing
- **Note:** first run downloads the model to `~/.rembg/models/`, cached after. Model ladder: `u2net` (170MB, fast) → `isnet-general-use` (178MB, finer edges — verified: dreadlock strands individually resolved, ~6s @1080p CPU) → `birefnet-general` (973MB, best edges). **birefnet status: model downloaded but OOM-killed on this 7.7GB box at every resolution (320p–1080p) — QUEUED for GPU runners (Kaggle/Colab).** Default to isnet-general-use for quality work.

### 5b. vtracer — raster-to-vector tracing
- **Path:** `tracing/` — wrapper `tracing/run_trace.py`
- **Does:** raster → SVG vector tracing (color or binary). Clean mascot/character edges — infinitely scalable crisp-edged character art for merch, title cards
- **Invoke:** `tracing/run_trace.py --input cut.png --output mascot.svg [--mode color|binary] [--detail 8]`
- **Verified:** mascot cutout (1920x1080) → 2.2MB valid SVG, 2,822 spline paths. XML validated.
- **Stage:** keyframe gen (character art), merch
- **Note:** `pip install vtracer` (Rust binary wheel). potrace NOT wired — needs apt/C toolchain unavailable here; vtracer covers the lane.

### 5c. sticker-kit — clean cutting / sticker compositing (PIL, purpose-built)
- **Path:** `sticker-kit/` — `sticker-kit/run_sticker.py`
- **Does:** `cleanup` (alpha threshold + edge smoothing), `refine` (erode/feather alpha matting refinement), `sticker` (white-border outline + optional drop shadow), `cutout` (all-in-one merch-ready)
- **Invoke:** `sticker-kit/run_sticker.py cutout --input cut.png --output sticker.png --border 28 --shadow`
- **Verified:** mascot cutout → white-border + shadow sticker, inspected by eye — clean edge-following border, merch-ready.
- **Stage:** compositing, merch, cards

### 5d. loop-kit — seamless loops for animation holds (PIL + ffmpeg, purpose-built)
- **Path:** `loop-kit/` — `loop-kit/run_loop.py`
- **Does:** `bob` (single hold frame → sinusoidal bob + scale "breathe" seamless loop), `pingpong` (clip → forward+reverse loop), `crossfade` (clip → head/tail crossfade seamless loop)
- **Invoke:** `loop-kit/run_loop.py bob --input hold.png --output bob.mp4 --frames 48 --fps 24 --bob-px 10 --breathe 0.02`
- **Verified:** bob 24f — first/last frame phase-identical (mean abs diff 6.4/255, h264 noise only); pingpong 20f→39f; crossfade 20f/blend-6→14f. All frame counts exact.
- **Stage:** FX (holds, idles), EP01 bumpers/cards

### 6. ffmpeg 8.1.2 — cleanup/compositing helpers (already present)
- **Wired filters for the assembly chain:**
  - `deflicker` — removes flicker from frame sequences / EbSynth output
  - `hqdn3d` / `nlmeans` — denoise (light `hqdn3d` before stylization)
  - `tblend=all_mode=average` — motion-blur / frame blending for holds
  - `minterpolate` — fallback CPU interpolation when RIFE is overkill (`minterpolate=fps=60:mi_mode=mci`)
  - `geq`, `curves`, `eq` — color matching hand-drawn frames to footage
- **Stage:** assembly, cleanup
- **Note:** system binary, no install needed.

---

## TOOL LADDER — new tiers wired 2026-10-10 (power drill + jackhammer)

### 11. rembg ladder upgrade — alpha matting + isnet-anime (bg removal, medium+ tier)
- **Path:** `rembg/` — wrapper `rembg/run_rembg.py` (updated: `--model` choices + `--alpha-matting` flag)
- **New default:** `isnet-general-use` (was `u2net`)
- **Tiers:** `u2net` (170MB, light/fast) → `isnet-general-use` (178MB, medium — verified dreadlock-strand edges) → `isnet-general-use --alpha-matting` (medium+, trimap matting post-pass — verified +38% soft-edge detail on performer frame) → `isnet-anime` (168MB, anime-domain specialist for cartoon character art) → `birefnet-general` (928MB, heavy — QUEUED-GPU, OOM on this box)
- **Invoke:** `rembg/run_rembg.py --input in.png --output out.png --model isnet-general-use --alpha-matting`
- **Verified:** wrapper runs all models end-to-end, RGBA out; edge-detail metrics measured per tier
- **Stage:** propagation prep (mattes), compositing

### 12. AnimeGANv2 (face_paint_512_v2) — anime stylization (heavy tier above whitebox)
- **Path:** `animeganv3/` — wrapper `animeganv3/run_animegan2.py`, arch `animeganv3/model_animegan2.py` (hand-reverse-engineered from weight keys, STRICT load 0 missing/0 unexpected)
- **Does:** photo→painterly-anime (flatter anime look vs whitebox's clean-cartoon). Different style family, not a replacement — pick per shot
- **Invoke:** `animeganv3/run_animegan2.py --input in.jpg --output out.png` (folder mode supported; any `--weights` .pt with same arch)
- **Verified:** 640x360 test frame → painterly anime output, inspected by eye — working
- **Weights:** `animeganv3/weights/face_paint_512_v2.pt` (8.6MB, bryandlee/animegan2-pytorch)
- **Stage:** keyframe gen (style variants), EP01 backgrounds
- **Note:** AnimeGANv3 Hayao ONNX was hunted (official repo is Git-LFS, no clean mirror) — v2 is the wired tier; v3 stays a QUEUED-GPU/nice-to-have

### 13. Real-ESRGAN (x4plus_anime_6B) — upscaling/restoration (new family)
- **Path:** `upscale/` — `upscale/run_upscale.py`, hand-rolled RRDBNet `upscale/rrdbnet.py` (no basicsr dependency)
- **Does:** 4x anime-aware upscaling + restoration. Cleans and enlarges cartoon frames/keyframes before stylization; restores soft phone footage
- **Invoke:** `upscale/run_upscale.py --input in.png --output out.png [--scale-out 2] [--tile 256]` (`--scale-out 2` = 4x then Lanczos down = sharper than native 2x; tiled for CPU memory)
- **Verified:** 640x360 2D keyframe → 1280x720, strict weight load, sane output
- **Weights:** `upscale/weights/RealESRGAN_x4plus_anime_6B.pth` (18MB, HF mirror `amd/realesrgan-x4plus-anime-6b`)
- **Stage:** keyframe prep, restoration, EP01

### 14. clean-kit — denoise/deflicker (new family, above ffmpeg hqdn3d/deflicker)
- **Path:** `clean-kit/` — `clean-kit/run_clean.py` (OpenCV, purpose-built)
- **Does:** `denoise` (fastNlMeansDenoisingColored — stronger than hqdn3d), `temporal` (motion-adaptive temporal denoise for smoothing EbSynth output), `deflicker` (luminance-normalization deflicker)
- **Invoke:** `clean-kit/run_clean.py denoise --input in.png --output out.png [--strength 7]` / `temporal|deflicker --input frames/ --output frames/`
- **Verified:** all three modes run on real frames; outputs sane dimensions/mode
- **Stage:** cleanup (EbSynth output smoothing), assembly

### 15. trace-kit — mascot-grade vectorization pipeline (above raw vtracer)
- **Path:** `tracing/` — `tracing/trace_kit.py` (presets: `mascot`/`logo`/`scene`)
- **Does:** rembg-ready input → median-cut posterize → vtracer with mascot-tuned params. Posterizing first collapses painterly gradients into flat cartoon regions = far cleaner character traces
- **Invoke:** `tracing/trace_kit.py --input mascot.png --output mascot.svg --preset mascot`
- **Verified:** painterly test image — 3,384 paths vs 5,752 raw vtracer (41% fewer), 28% smaller file, valid SVG
- **Stage:** keyframe gen (character art), merch
- **Note:** research confirms vtracer is best-in-class for color tracing (beats potrace/autotrace); the ladder step here is the tuned pipeline, not a new tracer

### 16. audio-kit — dialogue cleanup ladder (new family, commercial work)
- **Path:** `audio-kit/` — `audio-kit/run_audio.py` (stages: `nr`/`rnn`/`loud`/`full`)
- **Tiers:** `nr` = noisereduce spectral gating (light, pip-wired) → `rnn` = ffmpeg `arnndn` neural speech denoise (medium, `weights/std.rnnn`+`mp.rnnn`) → `loud` = ffmpeg `loudnorm` EBU R128 dual-pass → `full` = nr→rnn→highpass/lowpass→loudnorm (the commercial chain)
- **Invoke:** `audio-kit/run_audio.py full --input in.wav --output out.wav`
- **Verified:** synthetic noisy speech (1.0 dB SNR) → full chain → 5.9 dB SNR (+4.9 dB), 48kHz, loudnorm applied
- **Stage:** commercial audio (dialogue cleanup, broadcast loudness)
- **QUEUED (heavy):** DeepFilterNet — pip build fails in this container (maturin/Rust). On GPU runners: `pip install deepfilternet && deepfilternet enhance in.wav`

### 17. Interpolation note — RIFE is top tier
- Research confirms Practical-RIFE 4.26 (already wired) is the latest practical release; forks (rife-metal, rife-mlx, rife-ncnn-vulkan) all pin 4.25/4.26. No upgrade exists — RIFE stays the top tier with `minterpolate` fallback already documented.

### 18. QUEUED-GPU heavies (code pulled or documented, one-command fetch)
- **RMBG-2.0** (briaai, BiRefNet-arch, ~844MB weights, gated HF): the bg-removal jackhammer. Fetch: `huggingface-cli download briaai/RMBG-2.0` (accept terms first) then transformers `AutoModelForImageSegmentation`. Queued: 844MB too heavy at 83% disk + gated.
- **BiRefNet full** (`birefnet-general` 928MB already in `~/.rembg/models/`): OOM on this 7.7GB box at all resolutions — runs fine on Kaggle/Colab GPU via existing `rembg/run_rembg.py --model birefnet-general`.
- **AnimeGANv3** (Hayao ONNX): no clean CPU mirror found; revisit if one appears.

---

## QUEUED (pulled or identified — not runnable here yet)

### 7. Synfig — vector-tween 2D FX, headless `.sif` rendering
- **Blocker:** no apt sources in this environment; AppImage (v1.5.5, 115MB) downloaded but unrunnable — no libfuse2 and no `/dev/fuse` in container (FUSE mount impossible); source build needs dev deps apt can't provide.
- **Target:** `video-fix-tools/synfig/` — render `.sif` → PNG sequence headless for authored cartoon FX (starbursts, speedlines as vector tweens).
- **Note:** Blender Grease Pencil (WIRED above) covers the same headless-2D-FX need today. Revisit if a static synfig CLI binary appears.

### 8. OpenToonz — 2D animation (Ghibli's tool)
- **Path:** `opentoonz/` (source tree present)
- **Blocker:** GUI application; source build is very heavy (Qt). No headless batch story better than Grease Pencil.
- **Target:** artist workstation use; export PNG sequences → EbSynth/RIFE pipeline.

### 9. Krita — 2D painting/animation
- **Blocker:** not installed; GUI-focused, minimal headless value (krita has no real CLI animation render).
- **Target:** artist workstation for hand-painted keyframes → drop into `v3/hand-drawn/` lane.

### 10. apob-clone — ComfyUI node set
- **Path:** `apob-clone/`
- **Blocker:** ComfyUI workflow; needs GPU to be practical. CPU-only here.
- **Target:** revisit on GPU runners (Kaggle/Colab).

## NOT APPLICABLE / NOT HEADLESS

- **OpenRotoscope** (`OpenRotoscope/`) — DaVinci Resolve OFX plugin. Cannot run headless; no Resolve here. Roto need is covered by EbSynth + rembg.
- **arsenal-style-transfer** (`arsenal-style-transfer/`) — Arsenal FC highlights toy; stylization path requires local Stable Diffusion or Gemini API (paid). Out of scope for the 2D pipeline.
- **Tahoma2D / Pencil2D** — not pulled; GUI-only 2D animation, no CLI render story. Same lane as OpenToonz.

---

## How the wired tools compose (the hand-drawn mix)

```
live footage
  ├─ clean-kit ──→ denoise/deflicker phone footage + EbSynth output
  ├─ rembg (ladder: u2net → isnet → isnet+alpha-matting → birefnet[GPU])
  │     └─→ performer matte ──→ composite painted body over clean plate
  ├─ EbSynth ← hand-drawn OR AI-styled keyframe (keyframe-agnostic)
  ├─ upscale (Real-ESRGAN anime_6B) ──→ restore/enlarge keyframes pre-stylization
  ├─ cartoon ladder: whitebox (clean cartoon) / AnimeGANv2 (painterly anime)
  │     └─→ unify AI + hand-drawn frames to one look; cartoonize backgrounds
  ├─ tracing ladder: vtracer → trace-kit (posterize-first mascot pipeline) → SVG
  ├─ sticker-kit ← rembg cutouts ──→ merch-ready stickers
  ├─ Blender Grease Pencil ──→ authored FX (starbursts, speedlines, poofs)
  ├─ RIFE (top tier, 4.26) ──→ smooth hand-drawn sequences / slow-mo holds
  ├─ loop-kit ──→ seamless holds/idles from single frames
  ├─ audio-kit (nr → arnndn → loudnorm) ──→ dialogue cleanup, broadcast loudness
  └─ ffmpeg ──→ deflicker, hqdn3d, color-match, final assembly
```

## Provenance rule (owner 2026-10-10)
Never claim hand-drawn when AI generation was involved. Document per-step
AI vs manual provenance in each job's METHODS file.
