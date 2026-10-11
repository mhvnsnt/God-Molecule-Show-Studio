#!/usr/bin/env python3
"""Pollinations.ai — free, anonymous, no signup, no API key.

Tested 2026-10-10/11 from this VM (all working):
  - text:  GET https://text.pollinations.ai/{prompt}
  - image: GET https://image.pollinations.ai/prompt/{prompt}
  - tts:   GET https://gen.pollinations.ai/audio/{text}?voice=nova

Limits: ~1 anonymous request per 15s. Video (gen.pollinations.ai/video)
and chat-completions/vision on gen.pollinations.ai REQUIRE an API key
(signup at enter.pollinations.ai) — verified 401 without one.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def _get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def text(prompt: str, model: str = "openai", timeout: int = 120) -> str:
    """Free anonymous text generation. Returns the response string."""
    url = ("https://text.pollinations.ai/" + urllib.parse.quote(prompt)
           + "?model=" + urllib.parse.quote(model))
    return _get(url, timeout).decode("utf-8", errors="replace")


def image(prompt: str, width: int = 1024, height: int = 1024,
          model: str = "flux", seed: int | None = None,
          timeout: int = 300) -> bytes:
    """Free anonymous text-to-image. Returns image bytes (usually JPEG)."""
    params = {"width": width, "height": height, "model": model, "nologo": "true"}
    if seed is not None:
        params["seed"] = seed
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + "?" + urllib.parse.urlencode(params))
    return _get(url, timeout)


def save_image(prompt: str, path: str, **kwargs) -> str:
    """Generate an image and save it to path. Returns the path."""
    data = image(prompt, **kwargs)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path


def tts(text_input: str, voice: str = "nova", timeout: int = 120) -> bytes:
    """Free anonymous text-to-speech. Returns MP3 bytes."""
    url = ("https://gen.pollinations.ai/audio/" + urllib.parse.quote(text_input)
           + "?voice=" + urllib.parse.quote(voice))
    return _get(url, timeout)


def save_tts(text_input: str, path: str, voice: str = "nova") -> str:
    """Synthesize speech and save MP3 to path. Returns the path."""
    data = tts(text_input, voice=voice)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path


def main() -> None:
    print("== pollinations smoke test ==")
    t = text("Reply with exactly: POL_OK")
    print("text:", t.strip()[:60])
    img = image("a red cube on a table", width=512, height=512, seed=42)
    print("image bytes:", len(img), "| JPEG magic:", img[:3] == b"\xff\xd8\xff")
    audio = tts("Hello from Pollinations", voice="nova")
    print("tts bytes:", len(audio), "| MP3/ID3:", audio[:3] == b"ID3" or audio[:2] == b"\xff\xfb")


if __name__ == "__main__":
    main()
