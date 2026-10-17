#!/usr/bin/env python3
"""piper_voice.py — Piper TTS wrapper (God Molecule character voices).

Piper: fast, local, keyless neural TTS. Voice models (.onnx + .onnx.json)
download once from HuggingFace (rhasspy/piper-voices) into ./models/.

Usage:
    python3 piper_voice.py "The council does not explain itself. It declares." -o council_line.wav
    python3 piper_voice.py "Line one." -o line1.wav --model models/en_US-lessac-medium.onnx
    python3 piper_voice.py script.txt --file -o vo.wav
    python3 piper_voice.py "..." -o vo.wav --length-scale 1.2   # slower
    python3 piper_voice.py "..." -o vo.wav --noise-scale 0.9 --noise-w 0.9  # flatter

NOTE (license): piper-tts is GPL-3.0. It runs as a separate local process —
never linked into shipping code — and stays quarantined per
docs/LICENSE_QUARANTINE.md until a license audit clears it (owner law).
"""
import argparse
import sys
import wave


def main() -> int:
    ap = argparse.ArgumentParser(description="Synthesize speech with Piper TTS.")
    ap.add_argument("text", help="Text to speak, or path when --file is given.")
    ap.add_argument("-o", "--out", required=True, help="Output WAV path.")
    ap.add_argument("--model", default="models/en_US-lessac-medium.onnx",
                    help="Path to .onnx voice model.")
    ap.add_argument("--length-scale", type=float, default=1.0,
                    help=">1 slower, <1 faster.")
    ap.add_argument("--noise-scale", type=float, default=0.667)
    ap.add_argument("--noise-w", type=float, default=0.8)
    ap.add_argument("--file", action="store_true",
                    help="Read input text from a file instead of argv.")
    args = ap.parse_args()

    text = open(args.text, encoding="utf-8").read() if args.file else args.text
    if not text.strip():
        print("error: empty input text", file=sys.stderr)
        return 2

    from piper import PiperVoice

    voice = PiperVoice.load(args.model,
                            config_path=args.model + ".json",
                            use_cuda=False)
    syn = voice.synthesize
    with wave.open(args.out, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(voice.config.sample_rate)
        try:
            # piper >= 1.2 supports synthesis kwargs
            for chunk in syn(text, length_scale=args.length_scale,
                             noise_scale=args.noise_scale, noise_w=args.noise_w):
                wav.writeframes(chunk.audio_int16_bytes)
        except TypeError:
            for chunk in syn(text):
                wav.writeframes(chunk.audio_int16_bytes)
    print(f"wrote {args.out} @ {voice.config.sample_rate}Hz, model={args.model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
