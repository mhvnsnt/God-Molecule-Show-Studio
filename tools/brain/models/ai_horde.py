#!/usr/bin/env python3
"""AI Horde (stablehorde.net) — crowdsourced GPU network, free.
Uses the user-connected `custom.ai-horde` credential (user Mhvnsnt#544274).

Tested 2026-10-10/11 from this VM:
  - image generation (stable_diffusion, 512x512) -> WORKING, completed
    instantly, real 512x512 WebP downloaded and verified.
  - text generation (KoboldAI) -> submitted OK but returned EMPTY text;
    treated as UNRELIABLE, no wrapper exposed.

How it works: submit an async job, poll status until done, download from
the returned R2 URL. With 0 kudos the queue can be slow; our test job
completed with wait_time=0.
Auth: surrogate credential via dynamic_credentials, sent in the `apikey`
header per the AI Horde API.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

BASE = "https://stablehorde.net/api/v2"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
ALLOWED = ["stablehorde.net"]


def _req(url: str, payload: dict | None = None, timeout: int = 60):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method="POST" if data else "GET",
        headers={"User-Agent": UA, "Content-Type": "application/json"})
    add_surrogate_to_request(req, "custom.ai-horde", allowed_hosts=ALLOWED)
    return req


def submit_image(prompt: str, width: int = 512, height: int = 512,
                 steps: int = 25, seed: str = "",
                 models: list[str] | None = None) -> str:
    """Submit an image job. Returns the job id."""
    payload = {
        "prompt": prompt,
        "params": {"sampler_name": "k_euler", "width": width,
                   "height": height, "steps": steps, "seed": seed},
        "models": models or ["stable_diffusion"],
        "r2": True, "shared": False, "nsfw": False,
    }
    with urllib.request.urlopen(_req(BASE + "/generate/async", payload),
                                timeout=60) as resp:
        return read_json_response(resp)["id"]


def poll_image(job_id: str, poll_interval: int = 10,
               timeout_s: int = 900) -> dict:
    """Poll until done. Returns the first generation dict (img url, seed...)."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        with urllib.request.urlopen(
                _req(BASE + f"/generate/status/{job_id}"),
                timeout=30) as resp:
            status = read_json_response(resp)
        if status.get("done"):
            gens = status.get("generations", [])
            if not gens:
                raise RuntimeError("job done but no generations returned")
            return gens[0]
        time.sleep(poll_interval)
    raise TimeoutError(f"AI Horde job {job_id} not done after {timeout_s}s")


def generate_image(prompt: str, path: str, poll_interval: int = 10,
                   timeout_s: int = 900, **kwargs) -> str:
    """Generate an image and save it to path. Returns the path."""
    job_id = submit_image(prompt, **kwargs)
    gen = poll_image(job_id, poll_interval, timeout_s)
    img_req = urllib.request.Request(gen["img"], headers={"User-Agent": UA})
    with urllib.request.urlopen(img_req, timeout=120) as resp:
        data = resp.read()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path


def main() -> None:
    print("== ai_horde smoke test ==")
    job_id = submit_image("a small red cube on a table, simple",
                          width=512, height=512, steps=20)
    print("job:", job_id)
    gen = poll_image(job_id)
    print("done. model:", gen.get("model"), "| seed:", gen.get("seed"),
          "| img:", gen.get("img", "")[:70])


if __name__ == "__main__":
    main()
