# EbSynth — Video Style Propagation for EP02 Repair

## What it is
EbSynth takes **one hand-painted keyframe** and propagates that style across a
whole video, following the motion. For EP02: paint one frame in 2D cartoon style,
EbSynth converts the entire photorealistic-drifted clip to 2D.

**License:** The binary here is built from [jamriska/ebsynth](https://github.com/jamriska/ebsynth),
released into the **public domain** by the author. (Note: the code implements
PatchMatch, patented by Adobe — internal production use is fine; consult legal
before commercial redistribution.)
The official ebsynth.com product is now a web service (uploads to their servers)
— we do NOT use that; this local build keeps everything on-machine.

## Install (exact steps, verified 2026-10-10)
```bash
mkdir -p ~/workspace/video-fix-tools/ebsynth
cd ~/workspace/video-fix-tools/ebsynth
git clone https://github.com/jamriska/ebsynth.git src
cd src
sh build-linux-cpu_only.sh     # needs g++ with OpenMP; ~4-5 min with -O6
cd ..
ln -sf src/bin/ebsynth ebsynth
./ebsynth                      # prints usage if working
```
Binary: `~/workspace/video-fix-tools/ebsynth/ebsynth` (3.2 MB, CPU backend).
GPU/CUDA build exists (`build-linux-cpu+cuda.sh`) but was not needed.

## How to run (manual)
```bash
# 1. Extract frames
ffmpeg -i input.mp4 -vf "fps=10,scale=640:360" frames/frame-%04d.png

# 2. Paint keyframe: take frames/frame-0001.png, paint it in 2D style,
#    save as keyframe-styled.png (MUST align with source frame shapes)

# 3. Propagate style to each target frame
./ebsynth -style keyframe-styled.png \
  -guide frames/frame-0001.png frames/frame-0010.png \
  -output out-0010.png

# 4. Reassemble
ffmpeg -framerate 10 -i out-%04d.png -c:v libx264 -pix_fmt yuv420p out.mp4
```

## How to run (wrapper)
```bash
python run_ebsynth.py --input clip.mp4 --keyframe key.png --output fixed.mp4
# options: --keyframe-index N, --fps 10, --scale 640:360,
#          --keyframes k2.png@150,k3.png@300, --ebsynth-args "-patchsize 7",
#          --keep-frames
```

## Keyframe tips (from ebsynth.com docs + testing)
- One keyframe is often enough for short clips; add more for long/complex motion.
- The painted keyframe MUST align with the source frame shapes — misalignment
  causes stretchy/ripple artifacts.
- Pick keyframes showing the most content and clear poses, not mid-motion blur.
- For characters vs background moving independently, process on separate tracks.
- Fix broken areas by painting corrections on the output frame and adding it as
  a new keyframe.

## Test results (2026-10-10)
- Clip: EP02 shot 12-3 (war fund, 10 s), 100 frames @ 10 fps, 640×360.
- Keyframe: frame-0001 cartoon-filtered via OpenCV (bilateral + edge mask +
  saturation boost) — see test in /tmp/ebsynth-test/.
- Single-frame propagation to frame-0010: **worked** — 2D style preserved,
  motion followed, no major artifacts (~40 s/frame on CPU).
- 30-frame batch: ran to completion; output reassembled to video.
- Speed: ~40 s/frame @ 640×360 on CPU. A 10 s clip @ 10 fps = ~100 frames ≈
  65 min. Use lower fps/scale for drafts, full res for finals. CUDA build would
  be much faster (not attempted — CPU was sufficient for proof).

## What worked / didn't
- ✅ Build on Linux, CLI runs, style propagation works, output is clean 2D.
- ✅ Cartoon-filter keyframes are good enough for the "de-realistic" pass;
  hand-painted keyframes would be better for hero shots.
- ⚠️ CPU is slow — batch long clips or build the CUDA version.
- ⚠️ Single keyframe drifts on long clips with big motion changes — add
  keyframes every ~3-5 s for safety.
- ❌ ebsynth.com web version NOT used (uploads to external servers; also now
  paywalled for high-res). Local build has no such limits.

## Pipeline role
Step in the EP02 19-shot repair: `photorealistic clip` → (cartoon keyframe) →
`ebsynth` → `2D-styled clip` → QC → replace in timeline. Combine with
regeneration (for bad motion) and rotoscope (for hero shots) per the
combination-attack plan.
