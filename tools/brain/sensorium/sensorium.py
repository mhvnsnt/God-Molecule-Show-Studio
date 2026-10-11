#!/usr/bin/env python3
"""
sensorium.py — CLI for the sensorium: the director's-brain senses.

Usage (run with the ai-qc venv):
  V=~/workspace/tools/ai-qc/venv/bin/python
  S=~/workspace/tools/brain/sensorium/sensorium.py

  $V $S sense episode.mp4 [--still shot.png] [--t0 50 --t1 70]
      Full director's-brain pass: taste, style-hold (needs the shot's
      approved still), smell (anomalies), sync, multimodal coherence.

  $V $S rank
      Rank all EP02 segments by still-anchored style drift.

  $V $S taste image.png
      Taste score for a single still/frame.

  $V $S sync episode.mp4 t0 t1
      A/V sync check on one window.

  $V $S smell episode.mp4
      Unsupervised anomaly report.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

VENV_PY = os.path.expanduser("~/workspace/tools/ai-qc/venv/bin/python")
if sys.executable != VENV_PY and os.path.exists(VENV_PY):
    sys.stderr.write(
        f"NOTE: sensorium is built for the ai-qc venv ({VENV_PY}); "
        f"running under {sys.executable} — imports may fail.\n")


def cmd_sense(args):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--still", default=None)
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=None)
    ns = ap.parse_args(args)

    from aesthetic import score_video, judge
    from anomaly import smell, report as smell_report
    from sync import av_sync
    from multimodal import JointEmbedder

    t1 = ns.t1
    print(f"=== SENSORIUM: {os.path.basename(ns.video)} "
          f"[{ns.t0}-{t1 if t1 else 'end'}s] ===\n")

    print("--- TASTE + STYLE ---")
    print(judge(ns.video, still_path=ns.still))

    print("\n--- SMELL ---")
    print(smell_report(smell(ns.video)))

    print("\n--- SYNC (first dialogue-heavy 20s window) ---")
    r = av_sync(ns.video, ns.t0, (t1 or ns.t0 + 20))
    for k, v in r.items():
        print(f"  {k}: {v}")

    print("\n--- MULTIMODAL COHERENCE ---")
    je = JointEmbedder()
    coh, n = je.coherence(ns.video, t0=ns.t0,
                          t1=t1 if t1 else ns.t0 + 60)
    print(f"  sound-follows-action r={coh:.3f} (n={n} points)")
    print("  " + ("tightly glued" if coh > 0.5 else
                   "loosely glued" if coh > 0.25 else
                   "sound floats free of picture"))


def cmd_rank(args):
    from aesthetic import rank_segments
    rows = rank_segments()
    print(f"{'tag':>6} {'drift':>7} {'hold':>6} {'flicker':>8}")
    for tag, drift, hold, flick in rows:
        print(f"{tag:>6} {drift:7.2f} {hold:6.3f} {flick:8.3f}")


def cmd_taste(args):
    import cv2
    from aesthetic import taste_score
    for p in args:
        img = cv2.imread(p)
        if img is None:
            print(f"{p}: unreadable")
            continue
        s, terms = taste_score(img)
        print(f"{os.path.basename(p)}: taste={s:.3f} "
              + " ".join(f"{k}={v:.2f}" for k, v in terms.items()))


def cmd_sync(args):
    video, t0, t1 = args[0], float(args[1]), float(args[2])
    from sync import av_sync
    r = av_sync(video, t0, t1)
    for k, v in r.items():
        print(f"{k}: {v}")


def cmd_smell(args):
    from anomaly import smell, report
    print(report(smell(args[0])))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, rest = sys.argv[1], sys.argv[2:]
    {"sense": cmd_sense, "rank": cmd_rank, "taste": cmd_taste,
     "sync": cmd_sync, "smell": cmd_smell}[cmd](rest)


if __name__ == "__main__":
    main()
