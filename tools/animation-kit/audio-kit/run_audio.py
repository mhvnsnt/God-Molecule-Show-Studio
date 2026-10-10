#!/usr/bin/env python3
"""audio-kit — dialogue cleanup ladder for commercial work (all free, CPU).
Tiers:
  nr   : noisereduce spectral gating (light, fast)
  rnn  : ffmpeg arnndn neural speech denoise (medium, RNN model)
  loud : ffmpeg loudnorm EBU R128 dual-pass (broadcast loudness)
  full : nr -> rnn -> highpass/lowpass -> loudnorm (the commercial chain)
Usage:
  run_audio.py nr   --input in.wav --output out.wav [--strength 0.7]
  run_audio.py rnn  --input in.wav --output out.wav [--model mp|cb]
  run_audio.py loud --input in.wav --output out.wav [--lufs -16]
  run_audio.py full --input in.wav --output out.wav
DeepFilterNet (heavy tier): pip build fails in this container (maturin/Rust).
  QUEUED for GPU runners: pip install deepfilternet && deepfilternet enhance in.wav
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENVPY = "/home/hatch/workspace/video-fix-tools/venv/bin/python"
MODELS = {"std": os.path.join(HERE, "weights", "std.rnnn"),
          "mp": os.path.join(HERE, "weights", "mp.rnnn")}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr)
        sys.exit(r.returncode)


def nr_stage(inp, out, strength):
    code = (
        "import noisereduce as nr, soundfile as sf, sys\n"
        f"y, sr = sf.read({inp!r})\n"
        "ch = y.T if y.ndim > 1 else [y]\n"
        "import numpy as np\n"
        "outs = [nr.reduce_noise(y=c, sr=sr, prop_decrease=%f) for c in "
        "([y] if y.ndim == 1 else [y[:, i] for i in range(y.shape[1])])]\n"
        "o = np.stack(outs, axis=1) if y.ndim > 1 else outs[0]\n"
        f"sf.write({out!r}, o, sr)\n" % strength
    )
    run([VENVPY, "-c", code])
    print("nr ->", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["nr", "rnn", "loud", "full"])
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--strength", type=float, default=0.7)
    ap.add_argument("--model", default="std", choices=["std", "mp"])
    ap.add_argument("--lufs", type=float, default=-16.0)
    a = ap.parse_args()

    if a.stage == "nr":
        nr_stage(a.input, a.output, a.strength)
    elif a.stage == "rnn":
        run(["ffmpeg", "-v", "error", "-y", "-i", a.input, "-af",
             f"arnndn=m={MODELS[a.model]}", a.output])
        print("rnn ->", a.output)
    elif a.stage == "loud":
        run(["ffmpeg", "-v", "error", "-y", "-i", a.input, "-af",
             f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11:print_format=none",
             "-ar", "48000", a.output])
        print("loud ->", a.output)
    elif a.stage == "full":
        t1, t2 = "/tmp/audio-kit-nr.wav", "/tmp/audio-kit-rnn.wav"
        nr_stage(a.input, t1, a.strength)
        run(["ffmpeg", "-v", "error", "-y", "-i", t1, "-af",
             f"arnndn=m={MODELS[a.model]},highpass=f=80,lowpass=f=12000", t2])
        run(["ffmpeg", "-v", "error", "-y", "-i", t2, "-af",
             f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11:print_format=none",
             "-ar", "48000", a.output])
        print("full ->", a.output)


if __name__ == "__main__":
    main()
