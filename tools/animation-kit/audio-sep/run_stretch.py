#!/usr/bin/env python3
"""run_stretch.py — Paulstretch extreme time-stretch sound design.
The classic Paul Nasca algorithm: huge-window STFT, randomized phases,
overlap-add. Turns a 3s cymbal into a 3-minute ambient wash.

Usage: run_stretch.py --input in.wav --output out.wav --stretch 8.0 [--window 8192]
"""
import argparse
import numpy as np
import soundfile as sf


def paulstretch(x, stretch, window_size=8192, out_hop_ratio=0.5):
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    if n < window_size:
        x = np.pad(x, (0, window_size - n))
        n = len(x)
    window = np.hanning(window_size)
    hop_out = int(window_size * out_hop_ratio)
    hop_in = max(1.0, hop_out / stretch)
    n_frames = int(np.ceil((n - window_size) / hop_in)) + 1
    out_len = (n_frames - 1) * hop_out + window_size
    out = np.zeros(out_len)
    rng = np.random.default_rng(7)
    for i in range(n_frames):
        pos = int(i * hop_in)
        frame = x[pos:pos + window_size]
        if len(frame) < window_size:
            frame = np.pad(frame, (0, window_size - len(frame)))
        spec = np.fft.rfft(frame * window)
        phases = np.exp(1j * rng.uniform(0, 2 * np.pi, len(spec)))
        y = np.fft.irfft(np.abs(spec) * phases, window_size)
        o = i * hop_out
        out[o:o + window_size] += y * window
    # normalize to the window overlap gain
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * 0.89
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--stretch", type=float, default=8.0)
    ap.add_argument("--window", type=int, default=8192)
    a = ap.parse_args()
    stretch = min(max(a.stretch, 1.0), 50.0)
    x, sr = sf.read(a.input, always_2d=True)
    mono = x.mean(axis=1)
    y = paulstretch(mono, stretch, a.window)
    max_len = sr * 600  # 10 min cap
    y = y[:max_len]
    sf.write(a.output, y, sr)
    print(f"stretched {a.stretch}x -> {len(y)/sr:.1f}s @ {sr}Hz")


if __name__ == "__main__":
    main()
