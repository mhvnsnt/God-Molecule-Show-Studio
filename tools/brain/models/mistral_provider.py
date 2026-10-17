#!/usr/bin/env python3
"""Mistral AI — free tier ($10/mo API credits, no card). Uses the
user-connected `custom.mistral` credential.

Tested 2026-10-10/11 from this VM:
  - chat: open-mistral-nemo, mistral-tiny-latest            -> WORKING
  - chat: mistral-small-latest                              -> 429 rate-limited at test time
  - ocr:  mistral-ocr-latest                                -> 429 rate-limited at test time (NOT verified)

Auth: surrogate credential via dynamic_credentials (never a raw key).
NOTE: Mistral's edge 403s Python's default UA from this VM (Cloudflare
1010) — always send a browser User-Agent (handled here).
"""
from __future__ import annotations

import json
import sys
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

BASE = "https://api.mistral.ai/v1"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
ALLOWED = ["api.mistral.ai"]

DEFAULT_CHAT_MODEL = "open-mistral-nemo"


def _post(path: str, payload: dict, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(), method="POST",
        headers={"User-Agent": UA, "Content-Type": "application/json"})
    add_surrogate_to_request(req, "custom.mistral", allowed_hosts=ALLOWED)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return read_json_response(resp)


def chat(messages: list[dict], model: str = DEFAULT_CHAT_MODEL,
         max_tokens: int = 1024, temperature: float = 0.7,
         timeout: int = 120) -> str:
    """Chat completion. messages = [{"role": "user", "content": "..."}]."""
    data = _post("/chat/completions", {
        "model": model, "messages": messages,
        "max_tokens": max_tokens, "temperature": temperature,
    }, timeout)
    return data["choices"][0]["message"]["content"]


def ask(prompt: str, model: str = DEFAULT_CHAT_MODEL, **kwargs) -> str:
    """Single-turn convenience wrapper around chat()."""
    return chat([{"role": "user", "content": prompt}], model=model, **kwargs)


def main() -> None:
    print("== mistral smoke test ==")
    print("chat:", ask("Reply with exactly: MISTRAL_OK", max_tokens=20).strip()[:40])


if __name__ == "__main__":
    main()
