#!/usr/bin/env python3
"""kokoro_voice.py — Kokoro TTS wrapper (God Molecule character voices).

Kokoro-82M: Apache-2.0, keyless, fully local. ~300MB of weights download
once from HuggingFace (hexgrad/Kokoro-82M) to $HF_HOME / ~/.cache/huggingface.

Usage:
    python3 kokoro_voice.py "The council does not explain itself. It declares." -o council_line.wav
    python3 kokoro_voice.py "Line one." --voice af_heart -o line1.wav
    python3 kokoro_voice.py script.txt --file -o vo.wav        # read text from file
    python3 kokoro_voice.py "..." -o vo.wav --speed 0.9       # slower delivery

Voices (lang_code 'a' = American English, 'b' = British):
    af_heart, af_bella, af_nicole, af_sarah, am_adam, am_michael,
    bf_emma, bf_isabella, bm_george, bm_lewis, ...
"""
import argparse
import sys

import numpy as np


def main() -> int:
    ap = argparse.ArgumentParser(description="Synthesize speech with Kokoro TTS.")
    ap.add_argument("text", help="Text to speak, or path when --file is given.")
    ap.add_argument("-o", "--out", required=True, help="Output WAV path.")
    ap.add_argument("--voice", default="af_heart", help="Kokoro voice id.")
    ap.add_argument("--lang", default="a", help="Lang code: a=US English, b=UK English.")
    ap.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier.")
    ap.add_argument("--file", action="store_true",
                    help="Read input text from a file instead of argv.")
    args = ap.parse_args()

    text = open(args.text, encoding="utf-8").read() if args.file else args.text
    if not text.strip():
        print("error: empty input text", file=sys.stderr)
        return 2

    from kokoro import KPipeline
    import soundfile as sf

    pipeline = KPipeline(lang_code=args.lang)  # first run downloads weights
    chunks = []
    for _gs, _ps, audio in pipeline(text, voice=args.voice, speed=args.speed):
        chunks.append(audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio))
    if not chunks:
        print("error: kokoro produced no audio", file=sys.stderr)
        return 1

    wav = np.concatenate(chunks).astype(np.float32)
    sf.write(args.out, wav, 24000)
    print(f"wrote {args.out}: {len(wav) / 24000:.2f}s @ 24kHz, voice={args.voice}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
