#!/usr/bin/env python3
"""voiceover.py — bulk voiceover/dialogue renderer via Piper TTS (keyless).

Usage:
    python3 voiceover.py script.json -o vo_track.wav
    python3 voiceover.py lines.txt -o vo_track.wav        # one line per cue

script.json: [{"id": "intro", "text": "...", "pause_after": 0.5}, ...]
Outputs: one wav per cue in <out_dir> + a concatenated full track.

Piper voice model: ~/.local/share/piper-voices/en_US-lessac-medium.onnx
(override with --voice / --voice-json).
Public-domain/MIT chain: piper (GPLv3 — prototype use; voice model CC).
"""
import argparse, json, os, subprocess, sys, tempfile, wave

SR = 22050


def synth(text, voice, voice_json, out_wav):
    p = subprocess.run(
        ["piper", "--model", voice, "--config", voice_json,
         "--output_file", out_wav],
        input=text.encode(), capture_output=True)
    if p.returncode != 0 or not os.path.exists(out_wav):
        raise RuntimeError(f"piper failed: {p.stderr.decode()[:400]}")
    return out_wav


def concat_wavs(wavs, out, pause=0.35):
    data = []
    for w in wavs:
        with wave.open(w, "rb") as f:
            data.append(f.readframes(f.getnframes()))
        data.append(b"\x00" * int(SR * 2 * pause))  # 16-bit mono silence
    with wave.open(out, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(b"".join(data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", help="script.json or lines.txt")
    ap.add_argument("-o", "--out", required=True, help="final wav path")
    ap.add_argument("--out-dir", default=None, help="per-cue wav dir")
    ap.add_argument("--voice",
                    default=os.path.expanduser(
                        "~/.local/share/piper-voices/en_US-lessac-medium.onnx"))
    ap.add_argument("--voice-json",
                    default=os.path.expanduser(
                        "~/.local/share/piper-voices/en_US-lessac-medium.onnx.json"))
    a = ap.parse_args()

    if a.script.endswith(".json"):
        cues = json.load(open(a.script))
    else:
        cues = [{"id": f"line{i:02d}", "text": ln.strip(), "pause_after": 0.35}
                for i, ln in enumerate(open(a.script))
                if ln.strip()]

    out_dir = a.out_dir or os.path.join(os.path.dirname(a.out) or ".", "cues")
    os.makedirs(out_dir, exist_ok=True)

    wavs = []
    for cue in cues:
        path = os.path.join(out_dir, f"{cue['id']}.wav")
        synth(cue["text"], a.voice, a.voice_json, path)
        wavs.append(path)
        print(f"cue {cue['id']}: {path}")

    pause = cues[0].get("pause_after", 0.35) if cues else 0.35
    concat_wavs(wavs, a.out, pause=pause)
    print(f"WROTE {a.out} ({len(wavs)} cues)")


if __name__ == "__main__":
    main()
