#!/usr/bin/env python3
"""Groq — free tier, no card. Uses the user-connected `custom.groq` credential.

Tested 2026-10-10/11 from this VM:
  - chat:  openai/gpt-oss-20b, openai/gpt-oss-120b, qwen/qwen3.8-27b  -> WORKING
  - stt:   whisper-large-v3-turbo / whisper-large-v3               -> WORKING
  - tts:   canopylabs/orpheus-v1-english                           -> BLOCKED
           (org admin must accept model terms in the Groq console first)

Auth: surrogate credential via dynamic_credentials (never a raw key).
NOTE: Groq's Cloudflare edge 403s Python's default UA from this VM —
always send a browser User-Agent (handled here).

Free-tier limits (per Groq docs, Oct 2026): ~30 RPM / 1K req/day on most
chat models; Whisper ~20 RPM / 2K req/day. No vision models are currently
exposed on the free tier (checked 2026-10-11).
"""
from __future__ import annotations

import io
import json
import os
import sys
import urllib.request
import uuid

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

BASE = "https://api.groq.com/openai/v1"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
ALLOWED = ["api.groq.com"]

DEFAULT_CHAT_MODEL = "openai/gpt-oss-20b"


def _json_request(path: str, payload: dict, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(), method="POST",
        headers={"User-Agent": UA, "Content-Type": "application/json"})
    add_surrogate_to_request(req, "custom.groq", allowed_hosts=ALLOWED)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return read_json_response(resp)


def chat(messages: list[dict], model: str = DEFAULT_CHAT_MODEL,
         max_tokens: int = 1024, temperature: float = 0.7,
         timeout: int = 120) -> str:
    """Chat completion. messages = [{"role": "user", "content": "..."}]."""
    data = _json_request("/chat/completions", {
        "model": model, "messages": messages,
        "max_tokens": max_tokens, "temperature": temperature,
    }, timeout)
    return data["choices"][0]["message"]["content"]


def ask(prompt: str, model: str = DEFAULT_CHAT_MODEL, **kwargs) -> str:
    """Single-turn convenience wrapper around chat()."""
    return chat([{"role": "user", "content": prompt}], model=model, **kwargs)


def transcribe(audio_path: str, model: str = "whisper-large-v3-turbo",
               timeout: int = 180) -> str:
    """Speech-to-text. Returns the transcript string."""
    with open(audio_path, "rb") as f:
        audio = f.read()
    ext = os.path.splitext(audio_path)[1].lower().lstrip(".") or "mp3"
    boundary = uuid.uuid4().hex
    body = io.BytesIO()
    for k, v in {"model": model, "response_format": "json"}.items():
        body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"'
                   f"\r\n\r\n{v}\r\n".encode())
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
               f'filename="audio.{ext}"\r\nContent-Type: audio/{ext}\r\n\r\n'.encode())
    body.write(audio)
    body.write(f"\r\n--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        BASE + "/audio/transcriptions", data=body.getvalue(), method="POST",
        headers={"User-Agent": UA,
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    add_surrogate_to_request(req, "custom.groq", allowed_hosts=ALLOWED)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return read_json_response(resp)["text"]


def list_models() -> list[str]:
    req = urllib.request.Request(BASE + "/models", method="GET",
                                 headers={"User-Agent": UA})
    add_surrogate_to_request(req, "custom.groq", allowed_hosts=ALLOWED)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = read_json_response(resp)
    return [m["id"] for m in data.get("data", [])]


def main() -> None:
    print("== groq smoke test ==")
    print("models:", len(list_models()))
    # NOTE: gpt-oss is a reasoning model — keep max_tokens generous or the
    # whole budget goes to reasoning tokens and content comes back empty.
    print("chat:", ask("Reply with exactly: GROQ_OK").strip()[:40])


if __name__ == "__main__":
    main()
