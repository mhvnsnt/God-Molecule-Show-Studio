#!/usr/bin/env python3
"""Local + keyless voice: $0, no accounts, no credentials.

Tested 2026-10-10/11 from this VM:
  - espeak-ng TTS            -> WORKING (1.8s WAV verified)
  - Google Translate TTS     -> WORKING keyless (2.6s MP3 verified)
  - faster-whisper STT       -> WORKING (perfect transcript of test clip)
  - edge-tts (Microsoft)     -> BLOCKED: its websocket handshake is mangled
    by this VM's egress proxy (WSServerHandshakeError 101). May work from
    other networks; not wired here.

faster-whisper QUIRK (see ~/TOOLS.md): this VM's no_proxy contains IPv6
literals that crash huggingface_hub's httpx parsing. Strip any no_proxy
entry containing "::" before importing faster_whisper (handled here).
"""
from __future__ import annotations

import os
import subprocess
import urllib.parse
import urllib.request

# --- proxy quirk fix for huggingface_hub ---
for _var in ("no_proxy", "NO_PROXY"):
    _val = os.environ.get(_var, "")
    os.environ[_var] = ",".join(p for p in _val.split(",") if "::" not in p)

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

ESPEAK = "espeak-ng"


def espeak_tts(text: str, path: str, voice: str = "en+f3",
               speed: int = 160) -> str:
    """Robotic-but-free local TTS. Writes WAV to path. Returns path."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        subprocess.run([ESPEAK, "-v", voice, "-s", str(speed), text,
                        "--stdout"], stdout=f, check=True,
                       stderr=subprocess.DEVNULL)
    return path


def google_tts(text: str, path: str, lang: str = "en",
               timeout: int = 60) -> str:
    """Google Translate TTS, keyless. Writes MP3 to path. Returns path.

    Max ~200 chars per request; longer text is chunked on sentence
    boundaries automatically.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    chunks: list[str] = []
    for sentence in text.replace("?", ".").replace("!", ".").split("."):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) > 190:
            # hard-split long sentences
            chunks.extend(sentence[i:i + 190]
                          for i in range(0, len(sentence), 190))
        else:
            chunks.append(sentence)
    if not chunks:
        chunks = [text[:190]]
    audio = b""
    for chunk in chunks:
        url = ("https://translate.google.com/translate_tts?ie=UTF-8&q="
               + urllib.parse.quote(chunk) + "&tl=" + lang + "&client=tw-ob")
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            audio += resp.read()
    with open(path, "wb") as f:
        f.write(audio)
    return path


_WHISPER_MODEL = None


def transcribe(audio_path: str, model_size: str = "tiny") -> str:
    """Local speech-to-text with faster-whisper. Returns transcript text.

    First call downloads the model from Hugging Face (~75MB for tiny).
    Larger sizes ("base", "small", "medium") are more accurate but slower.
    """
    global _WHISPER_MODEL
    from faster_whisper import WhisperModel
    if _WHISPER_MODEL is None:
        _WHISPER_MODEL = WhisperModel(model_size, device="cpu")
    segments, _info = _WHISPER_MODEL.transcribe(audio_path)
    return " ".join(s.text.strip() for s in segments).strip()


def main() -> None:
    print("== local_voice smoke test ==")
    p = espeak_tts("Hello from espeak", "/tmp/lv_espeak.wav")
    print("espeak:", p, os.path.getsize(p), "bytes")
    p = google_tts("Hello from Google translate TTS", "/tmp/lv_google.mp3")
    print("google tts:", p, os.path.getsize(p), "bytes")
    print("whisper:", transcribe("/tmp/lv_google.mp3")[:80])


if __name__ == "__main__":
    main()
