#!/usr/bin/env python3
"""RIFE frame-interpolation wrapper for the video-fix-tools pipeline.
Usage: run_rife.py --input in.mp4 --output out.mp4 [--multi 2] [--scale 0.5] [--fps 60]
Serves: smoothing hand-drawn sequences, slow-mo holds, 2x/4x interpolation.
"""
import argparse, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
VENV = "/home/hatch/workspace/video-fix-tools/venv/bin/python"
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--output", required=True)
    ap.add_argument("--multi", type=int, default=2, help="interpolation factor (2 or 4)")
    ap.add_argument("--scale", type=float, default=0.5, help="0.5 for 1080p on CPU, 1.0 for <=720p")
    ap.add_argument("--fps", type=int, default=None)
    a = ap.parse_args()
    cmd = [VENV, os.path.join(HERE, "inference_video.py"),
           "--video", a.input, "--output", a.output,
           "--multi", str(a.multi), "--scale", str(a.scale),
           "--model", os.path.join(HERE, "train_log"), "--ext", "mp4"]
    if a.fps: cmd += ["--fps", str(a.fps)]
    print("RIFE:", " ".join(cmd)); sys.stdout.flush()
    r = subprocess.run(cmd, cwd=HERE)
    sys.exit(r.returncode)
if __name__ == "__main__": main()
