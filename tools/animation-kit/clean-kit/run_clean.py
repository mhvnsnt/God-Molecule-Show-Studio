#!/usr/bin/env python3
"""clean-kit — denoise/deflicker tier above ffmpeg hqdn3d/deflicker.
Modes:
  denoise  : OpenCV fastNlMeansDenoisingColored (stronger than hqdn3d) on image/folder
  temporal : motion-adaptive temporal denoise for frame folders (smoothing EbSynth output)
  deflicker: per-frame luminance normalization for flickery sequences
Usage:
  run_clean.py denoise --input in.png --output out.png [--strength 7]
  run_clean.py denoise --input frames_in/ --output frames_out/
  run_clean.py temporal --input frames_in/ --output frames_out/ [--radius 1]
  run_clean.py deflicker --input frames_in/ --output frames_out/ [--window 15]
"""
import argparse, os, sys
import numpy as np
import cv2
from PIL import Image


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB"))


def save_rgb(a, p):
    Image.fromarray(a.astype(np.uint8)).save(p)


def denoise_img(img, strength=7):
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    out = cv2.fastNlMeansDenoisingColored(bgr, None, strength, strength, 7, 21)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


def iter_frames(d):
    return sorted(f for f in os.listdir(d) if f.lower().endswith((".png", ".jpg", ".jpeg")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["denoise", "temporal", "deflicker"])
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--strength", type=float, default=7)
    ap.add_argument("--radius", type=int, default=1)
    ap.add_argument("--window", type=int, default=15)
    a = ap.parse_args()

    if a.mode == "denoise" and not os.path.isdir(a.input):
        save_rgb(denoise_img(load_rgb(a.input), a.strength), a.output)
        print("denoised", a.output)
        return

    os.makedirs(a.output, exist_ok=True)
    files = iter_frames(a.input)
    frames = [load_rgb(os.path.join(a.input, f)).astype(np.float32) for f in files]

    if a.mode == "denoise":
        for f, fr in zip(files, frames):
            save_rgb(denoise_img(fr.astype(np.uint8), a.strength),
                     os.path.join(a.output, f))
    elif a.mode == "temporal":
        r = a.radius
        for i, f in enumerate(files):
            lo, hi = max(0, i - r), min(len(frames), i + r + 1)
            avg = np.mean(frames[lo:hi], axis=0)
            # motion-adaptive: keep original where it differs a lot (edges/motion)
            diff = np.abs(frames[i] - avg).mean(axis=2, keepdims=True)
            w = np.clip(diff / 25.0, 0, 1)
            save_rgb(frames[i] * w + avg * (1 - w), os.path.join(a.output, f))
    elif a.mode == "deflicker":
        w = a.window
        lumas = np.array([0.299 * f[:, :, 0] + 0.587 * f[:, :, 1] + 0.114 * f[:, :, 2]
                          for f in frames])
        means = lumas.reshape(len(frames), -1).mean(axis=1)
        tgt = np.convolve(means, np.ones(w) / w, mode="same")
        for f, fr, m, t in zip(files, frames, means, tgt):
            g = t / max(m, 1e-6)
            g = np.clip(g, 0.7, 1.43)
            save_rgb(np.clip(fr * g, 0, 255), os.path.join(a.output, f))
    print(f"{a.mode}: {len(files)} frames -> {a.output}")


if __name__ == "__main__":
    main()
