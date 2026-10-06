#!/usr/bin/env python3
"""auto_caption.py — word-timestamp auto-caption via faster-whisper (keyless).

Usage:
    python3 auto_caption.py audio.wav -o captions.srt
    python3 auto_caption.py audio.wav -o captions.json --format json
    python3 auto_caption.py video.mp4 -o captions.srt   # audio extracted via ffmpeg

Outputs SRT (default) or JSON word list [{word, start, end}].
Model: tiny (fast, CPU) by default; --model base/small/medium for quality.
First run downloads the model (~40-500MB) to ~/.cache/huggingface.

License: faster-whisper (MIT), whisper models (MIT-ish). Prototype freely.
"""
import argparse, json, os, subprocess, sys, tempfile


def extract_audio(src, tmpwav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src,
                    "-ac", "1", "-ar", "16000", tmpwav], check=True)
    return tmpwav


def to_srt(segments):
    def ts(t):
        h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    out = []
    for i, s in enumerate(segments, 1):
        out.append(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text'].strip()}\n")
    return "\n".join(out)


def load_audio_16k(wav_path):
    """Decode to 16kHz mono float32 numpy (avoids PyAV version issues)."""
    import numpy as np
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", wav_path, "-ac", "1", "-ar", "16000",
         "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--format", choices=["srt", "json"], default="srt")
    ap.add_argument("--model", default="tiny")
    ap.add_argument("--model-dir", default=None,
                    help="local model dir (avoids HF download, e.g. behind broken proxy)")
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()

    from faster_whisper import WhisperModel
    model_id = a.model_dir or a.model
    wav = a.src
    tmp = None
    if not a.src.lower().endswith(".wav"):
        tmp = tempfile.mktemp(suffix=".wav", dir=os.path.expanduser("~/workspace/tmp"))
        wav = extract_audio(a.src, tmp)

    model = WhisperModel(model_id, device="cpu", compute_type="int8")
    audio = load_audio_16k(wav)
    segments, _ = model.transcribe(audio, language=a.lang, word_timestamps=True)

    words, segs = [], []
    for s in segments:
        segs.append({"start": s.start, "end": s.end, "text": s.text})
        for w in (s.words or []):
            words.append({"word": w.word, "start": w.start, "end": w.end})

    if a.format == "json":
        json.dump({"words": words, "segments": segs}, open(a.out, "w"), indent=1)
    else:
        open(a.out, "w").write(to_srt(segs))
    if tmp:
        os.unlink(tmp)
    print(f"WROTE {a.out}: {len(words)} words, {len(segs)} segments (model={a.model})")


if __name__ == "__main__":
    main()
