#!/usr/bin/env python3
"""concept_batch.py — Pollinations.ai concept-art batch script (no key, via curl).

Usage:
    python3 concept_batch.py prompts.txt -d concept_out/
    python3 concept_batch.py --prompt "a neon street brawler" -d concept_out/

Endpoint: https://image.pollinations.ai/prompt/{url-encoded prompt}
Params: width, height, seed, model (flux), nologo.
qrng_seeds.py from ~/workspace/api-wiring is used for auditable seeds
(marketing: "quantum-seeded concept batches").

Pollinations is free/keyless. Be polite: 2s between requests.
"""
import argparse, os, subprocess, sys, time, urllib.parse

sys.path.insert(0, os.path.expanduser("~/workspace/api-wiring"))
try:
    from qrng_seeds import get_seed
except Exception:
    import random
    def get_seed(): return random.randrange(2**31)

API = "https://image.pollinations.ai/prompt/{p}?width={w}&height={h}&seed={s}&model=flux&nologo=true"


def fetch(prompt, out, w=1024, h=1024):
    seed = get_seed()
    url = API.format(p=urllib.parse.quote(prompt), w=w, h=h, s=seed)
    r = subprocess.run(["curl", "-sL", "--max-time", "180", "-o", out, url],
                       capture_output=True)
    ok = r.returncode == 0 and os.path.getsize(out) > 20000
    return ok, seed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompts", nargs="?", help="prompts.txt (one per line)")
    ap.add_argument("--prompt", default=None, help="single prompt")
    ap.add_argument("-d", "--dir", default="concept_out")
    ap.add_argument("--w", type=int, default=1024)
    ap.add_argument("--h", type=int, default=1024)
    a = ap.parse_args()

    os.makedirs(a.dir, exist_ok=True)
    if a.prompt:
        items = [a.prompt]
    else:
        items = [ln.strip() for ln in open(a.prompts) if ln.strip()
                 and not ln.startswith("#")]

    log = []
    for i, pr in enumerate(items):
        out = os.path.join(a.dir, f"concept_{i:03d}.jpg")
        ok, seed = fetch(pr, out, a.w, a.h)
        print(("WROTE " if ok else "FAIL ") + f"{out}  seed={seed}  :: {pr[:60]}")
        log.append({"file": out, "seed": seed, "prompt": pr, "ok": ok})
        time.sleep(2)

    with open(os.path.join(a.dir, "batch_log.json"), "w") as f:
        import json
        json.dump(log, f, indent=1)
    print(f"done: {sum(l['ok'] for l in log)}/{len(log)}")


if __name__ == "__main__":
    main()
