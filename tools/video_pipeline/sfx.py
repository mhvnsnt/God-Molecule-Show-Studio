#!/usr/bin/env python3
"""sfx.py — jsfxr-style SFX synthesizer (numpy, public domain algorithms).

Reimplements the classic sfxr/jsfxr generator recipes in numpy so the
pipeline has zero heavy deps and no license baggage (jsfxr itself is
public domain; this is a clean-room reimplementation of the well-known
recipes: square/saw/noise with pitch slides and ADSR-ish envelopes).

Usage:
    python3 sfx.py hit -o hit.wav
    python3 sfx.py --all -d sfx_out/        # render the whole kit

Generators: blip, hit, thud, whoosh, riser, fall, pickup, explode,
            crowd (filtered noise swell), bell, gunshot.
"""
import argparse, math, os
import numpy as np
import wave

SR = 44100


def env_ad(n, a=0.005, d=0.05, s=0.6, r=0.08):
    t = np.arange(n) / SR
    dur = n / SR
    e = np.ones(n) * s
    na = int(a * SR); nd = int(d * SR); nr = int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, nd)
    e[-nr:] = np.linspace(s, 0, nr)
    return e


def tone(f0, f1, dur, wave="square", duty=0.5, vib=0.0, vib_rate=30.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    if vib:
        f *= 1 + vib * np.sin(2 * np.pi * vib_rate * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    if wave == "square":
        s = np.sign(np.sin(ph)) * duty * 2 - (1 - duty)
        s = np.clip(s, -1, 1)
    elif wave == "saw":
        s = 2 * ((ph / (2 * np.pi)) % 1) - 1
    elif wave == "sine":
        s = np.sin(ph)
    else:
        s = np.sin(ph)
    return s * env_ad(n)


def noise(dur, low=0.0, high=1.0, slide=0.0):
    n = int(dur * SR)
    s = np.random.default_rng(7).standard_normal(n)
    # crude bandpass-ish: cumulative smoothing scaled by slide
    k = int(2 + 20 * (1 - high))
    ker = np.ones(k) / k
    s = np.convolve(s, ker, mode="same")
    s *= env_ad(n)
    return s / (np.abs(s).max() + 1e-9)


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out / (np.abs(out).max() + 1e-9)


def write_wav(path, s):
    s = np.clip(s, -1, 1)
    pcm = (s * 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(pcm.tobytes())


RECIPES = {
    "blip":    lambda: tone(880, 1320, 0.12),
    "pickup":  lambda: tone(520, 1560, 0.18, wave="square"),
    "hit":     lambda: mix(0.7 * tone(180, 60, 0.25, wave="sine"), 0.5 * noise(0.18, high=0.4)),
    "thud":    lambda: tone(120, 40, 0.35, wave="sine"),
    "whoosh":  lambda: noise(0.6, high=0.7, slide=1.0),
    "riser":   lambda: tone(110, 880, 1.2, wave="saw"),
    "fall":    lambda: tone(880, 110, 1.0, wave="saw"),
    "explode": lambda: mix(0.8 * noise(1.1, high=0.5), 0.6 * tone(90, 30, 1.0, wave="sine")),
    "crowd":   lambda: noise(2.5, high=0.3) * 0.9,
    "bell":    lambda: mix(tone(660, 655, 0.8, wave="sine"), 0.4 * tone(1320, 1310, 0.6, wave="sine")),
    "gunshot": lambda: mix(noise(0.3, high=0.9), 0.7 * tone(220, 50, 0.2, wave="square")),
    "ko":      lambda: mix(0.7 * tone(200, 45, 0.9, wave="sine"), 0.5 * noise(0.7, high=0.5)),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", help="recipe name")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("-d", "--dir", default="sfx_out")
    a = ap.parse_args()

    if a.all:
        os.makedirs(a.dir, exist_ok=True)
        for name, fn in RECIPES.items():
            p = os.path.join(a.dir, f"{name}.wav")
            write_wav(p, fn())
            print(f"WROTE {p}")
    else:
        if a.name not in RECIPES:
            raise SystemExit(f"unknown recipe '{a.name}'. choices: {sorted(RECIPES)}")
        out = a.out or f"{a.name}.wav"
        write_wav(out, RECIPES[a.name]())
        print(f"WROTE {out}")


if __name__ == "__main__":
    main()
