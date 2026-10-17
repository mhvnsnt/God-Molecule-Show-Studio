#!/usr/bin/env python3
"""run_beats.py — fast beat/onset detection via aubio (lighter than librosa).
Outputs beats.txt (BPM + beat times) and clicks.wav (metronome click track).

Usage: run_beats.py --input song.wav --outdir beats_out/
"""
import argparse
import os
import numpy as np
import soundfile as sf

try:
    import aubio
    HAVE_AUBIO = True
except ImportError:
    HAVE_AUBIO = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    y, sr = sf.read(a.input, always_2d=True)
    mono = y.mean(axis=1).astype(np.float32)

    if HAVE_AUBIO:
        win, hop = 1024, 512
        o = aubio.tempo("default", win, hop, sr)
        beats = []
        for i in range(0, len(mono) - hop, hop):
            frame = mono[i:i + hop]
            if len(frame) < hop:
                frame = np.pad(frame, (0, hop - len(frame)))
            if o(frame):
                beats.append(o.get_last_s())
        bpm = o.get_bpm()
    else:  # fallback: librosa
        import librosa
        tempo, beats_f = librosa.beat.beat_track(y=mono, sr=sr)
        bpm = float(tempo)
        beats = (librosa.frames_to_time(beats_f, sr=sr)).tolist()

    beats = sorted(beats)
    with open(os.path.join(a.outdir, "beats.txt"), "w") as f:
        f.write(f"bpm: {bpm:.1f}\ncount: {len(beats)}\n")
        f.write("\n".join(f"{b:.3f}" for b in beats))

    # click track
    n = len(mono)
    clicks = np.zeros(n)
    cl = int(.03 * sr)
    t = np.arange(cl)
    click = np.sin(2 * np.pi * 2000 * t / sr) * np.exp(-t / (cl / 4))
    for b in beats:
        i = int(b * sr)
        if i + cl < n:
            clicks[i:i + cl] += click * .8
    sf.write(os.path.join(a.outdir, "clicks.wav"), clicks, sr)
    print(f"bpm {bpm:.1f}, {len(beats)} beats -> {a.outdir}")


if __name__ == "__main__":
    main()
