#!/bin/bash
# fetch_models.sh — one-command pull for animation-kit model binaries.
# The kit ships scripts + docs only; models are NEVER committed to git.
# Run from the animation-kit root:  bash fetch_models.sh [--gpu]
#   --gpu also pulls the heavy GPU-tier models (birefnet, RMBG-2.0).
set -e
KIT_DIR="$(cd "$(dirname "$0")" && pwd)"
GPU=0
[ "${1:-}" = "--gpu" ] && GPU=1

have() { command -v "$1" >/dev/null 2>&1; }
fetch() { # fetch <url> <dest>
  if have curl; then curl -L --fail -o "$2" "$1";
  elif have wget; then wget -O "$2" "$1";
  else echo "need curl or wget for $1"; return 1; fi
}

echo "== rembg models (auto-cached to ~/.rembg/models/) =="
python3 -c "
from rembg import new_session
for m in ['u2net', 'isnet-general-use', 'isnet-anime']:
    print('warming', m); new_session(m)
" || echo "WARN: rembg pre-warm failed (pip install rembg onnxruntime first)"

echo "== pose landmark =="
mkdir -p "$KIT_DIR/pose-extract/models"
[ -f "$KIT_DIR/pose-extract/models/pose_landmarker_heavy.task" ] || \
fetch "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task" \
      "$KIT_DIR/pose-extract/models/pose_landmarker_heavy.task"

echo "== whitebox cartoonize (17.6MB) =="
mkdir -p "$KIT_DIR/whitebox-pytorch/weights"
if [ ! -f "$KIT_DIR/whitebox-pytorch/weights/sceneryonly.pth.tar" ]; then
  echo "MANUAL: sceneryonly.pth.tar is not on a stable public mirror."
  echo "Copy it from any existing install into whitebox-pytorch/weights/ (17.6MB)."
fi

echo "== AnimeGANv2 face_paint_512_v2 (8.6MB) =="
mkdir -p "$KIT_DIR/animeganv3/weights"
[ -f "$KIT_DIR/animeganv3/weights/face_paint_512_v2.pt" ] || \
fetch "https://github.com/bryandlee/animegan2-pytorch/raw/main/weights/face_paint_512_v2.pt" \
      "$KIT_DIR/animeganv3/weights/face_paint_512_v2.pt"

echo "== Real-ESRGAN x4plus_anime_6B (18MB) =="
mkdir -p "$KIT_DIR/upscale/weights"
[ -f "$KIT_DIR/upscale/weights/RealESRGAN_x4plus_anime_6B.pth" ] || \
fetch "https://huggingface.co/amd/realesrgan-x4plus-anime-6b/resolve/main/RealESRGAN_x4plus_anime_6B.pth" \
      "$KIT_DIR/upscale/weights/RealESRGAN_x4plus_anime_6B.pth"

echo "== RIFE flownet.pkl (24MB, Practical-RIFE 4.26 bundle) =="
mkdir -p "$KIT_DIR/rife/train_log"
if [ ! -f "$KIT_DIR/rife/train_log/flownet.pkl" ]; then
  echo "MANUAL: download the 4.26 bundle from the Practical-RIFE releases"
  echo "(https://github.com/hzwer/Practical-RIFE) and place flownet.pkl in rife/train_log/."
fi

echo "== arnndn speech-denoise models (~300KB each) =="
mkdir -p "$KIT_DIR/audio-kit/weights"
if [ ! -f "$KIT_DIR/audio-kit/weights/std.rnnn" ]; then
  echo "MANUAL: std.rnnn / mp.rnnn are the standard arnndn upstream models (300KB each)."
  echo "Place both in audio-kit/weights/ (source: arnndn project model set)."
fi

if [ "$GPU" = "1" ]; then
  echo "== GPU tier =="
  python3 -c "from rembg import new_session; print('warming birefnet-general'); new_session('birefnet-general')" \
    || echo "WARN: birefnet pre-warm failed"
  if have huggingface-cli; then
    huggingface-cli download briaai/RMBG-2.0 --local-dir "$KIT_DIR/upscale/weights/RMBG-2.0" \
      || echo "WARN: RMBG-2.0 is gated — accept terms at huggingface.co/briaai/RMBG-2.0 first"
  else
    echo "install huggingface_hub for RMBG-2.0: pip install huggingface_hub"
  fi
else
  echo "(skip: GPU-tier models — re-run with --gpu on a GPU runner)"
fi

echo "done. pip requirements per tool are documented in TOOLS-REGISTRY.md."
