#!/usr/bin/env python3
"""run_demucs.py — vocal/source separation via Demucs (hybrid transformer).
Splits a mix into vocals / drums / bass / other stems.

Usage: run_demucs.py --input mix.wav --outdir stems/ [--model htdemucs]
Models: htdemucs (default, best), hdemucs_mmi, mdx_extra (slower, sharper).
CPU-friendly; on this box expect ~1-2 min per minute of audio.
"""
import argparse
import os
import subprocess
import sys

VENVPY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "venv", "bin", "python")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--model", default="htdemucs")
    ap.add_argument("--stem", default="",
                    help="optional: only keep one stem (vocals|drums|bass|other)")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    cmd = [sys.executable, "-m", "demucs.separate",
           "--mp3", "--mp3-bitrate", "192",
           "-n", a.model, "-o", a.outdir, a.input]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(r.returncode)
    base = os.path.splitext(os.path.basename(a.input))[0]
    stemdir = os.path.join(a.outdir, a.model, base)
    if a.stem and os.path.isdir(stemdir):
        keep = [f for f in os.listdir(stemdir)
                if f.startswith(a.stem + ".")]
        for f in os.listdir(stemdir):
            if f not in keep:
                os.remove(os.path.join(stemdir, f))
        print("kept stem:", keep)
    print("stems in:", stemdir)


if __name__ == "__main__":
    main()
