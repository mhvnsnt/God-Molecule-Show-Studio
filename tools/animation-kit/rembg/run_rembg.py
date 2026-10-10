#!/usr/bin/env python3
"""rembg performer-matting wrapper (CPU/onnxruntime).
Model ladder (light -> heavy):
  u2net               170MB fast baseline
  isnet-general-use   178MB finer edges (default for quality photo work)
  isnet-anime         168MB anime-domain specialist (cartoon character art)
  birefnet-general    928MB best edges -- OOM on this box, QUEUED-GPU
Add --alpha-matting for the edge-quality upgrade on photo mattes.
Usage: run_rembg.py --input in.png --output out.png [--model isnet-general-use] [--alpha-matting]
       run_rembg.py --input frames_in --output frames_out   (folder mode)
"""
import argparse, sys, os, subprocess
VENVPY = "/home/hatch/workspace/video-fix-tools/venv/bin/python"
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="isnet-general-use",
                    choices=["u2net", "isnet-general-use", "isnet-anime",
                             "birefnet-general", "u2net_human_seg"])
    ap.add_argument("--alpha-matting", action="store_true",
                    help="trimap-based alpha matting post-pass (photo edges)")
    a = ap.parse_args()
    am = ("dict(alpha_matting=True, alpha_matting_foreground_threshold=240,"
          "alpha_matting_background_threshold=10, alpha_matting_erode_size=11)"
          if a.alpha_matting else "dict()")
    code = (
        "from rembg import new_session, remove\n"
        "from PIL import Image\n"
        "import os, glob\n"
        f"sess = new_session({a.model!r})\n"
        f"kw = {am}\n"
        "pairs = []\n"
        f"INP={a.input!r}; OUT={a.output!r}\n"
        "if os.path.isdir(INP):\n"
        "    os.makedirs(OUT, exist_ok=True)\n"
        "    files=[f for e in ('*.png','*.jpg','*.jpeg','*.webp') for f in glob.glob(os.path.join(INP,e))]\n"
        "    pairs=[(f, os.path.join(OUT, os.path.splitext(os.path.basename(f))[0]+'.png')) for f in sorted(files)]\n"
        "else:\n"
        "    pairs=[(INP, OUT)]\n"
        "for src, dst in pairs:\n"
        "    remove(Image.open(src), session=sess, **kw).save(dst)\n"
        "    print('matted', dst)\n"
    )
    sys.exit(subprocess.run([VENVPY, "-c", code]).returncode)
if __name__ == "__main__": main()
import argparse, sys, os, subprocess
VENVPY = "/home/hatch/workspace/video-fix-tools/venv/bin/python"
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="u2net")
    a = ap.parse_args()
    code = (
        "from rembg import new_session, remove\n"
        "from PIL import Image\n"
        "import os, glob\n"
        f"sess = new_session({a.model!r})\n"
        "pairs = []\n"
        f"INP={a.input!r}; OUT={a.output!r}\n"
        "if os.path.isdir(INP):\n"
        "    os.makedirs(OUT, exist_ok=True)\n"
        "    files=[f for e in ('*.png','*.jpg','*.jpeg','*.webp') for f in glob.glob(os.path.join(INP,e))]\n"
        "    pairs=[(f, os.path.join(OUT, os.path.splitext(os.path.basename(f))[0]+'.png')) for f in sorted(files)]\n"
        "else:\n"
        "    pairs=[(INP, OUT)]\n"
        "for src, dst in pairs:\n"
        "    remove(Image.open(src), session=sess).save(dst)\n"
        "    print('matted', dst)\n"
    )
    sys.exit(subprocess.run([VENVPY, "-c", code]).returncode)
if __name__ == "__main__": main()
