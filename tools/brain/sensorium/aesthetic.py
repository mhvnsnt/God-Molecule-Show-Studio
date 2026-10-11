#!/usr/bin/env python3
"""
aesthetic.py — "Taste": aesthetic / style judgment for animation frames.

Two scores per frame:
  taste      0..1  — general no-reference aesthetic quality
                    (sharp, well-exposed, colorful-but-balanced, clean)
  style_hold 0..1  — Wizard-Gang-specific style lock:
                    1.0 = holds 2D cartoon (flat colors, bold outlines)
                    0.0 = drifted into 3D/photoreal render

style_hold is a logistic-regression model trained on frames hand-labeled
from the EP02 AI-slop audit (2026-10-09, wizard-gang-ep02-16x9.mp4):
  BAD  (3D drift):  52s (shot 10-1), 100s (shot 12-3), 190s (shot 20-1)
  GOOD (2D hold):   55s, 64s (council), 118s (Theory), 145s (Echo claw)

taste is a calibrated heuristic (weights fit on the same labeled frames).

Temporal readouts: style_flicker = std of style_hold over a shot
(high flicker = texture/style popping within the shot — an AI tell).

CPU-only. sklearn + OpenCV + numpy.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from features import (visual_features_bgr, visual_vector, VISUAL_KEYS,
                      sample_video_frames)

MODEL_PATH = os.path.join(_HERE, "models", "style_hold.npz")

# Audit labels on wizard-gang-ep02-16x9.mp4 (4:24 cut), from EP02_AI_SLOP_AUDIT.md
BAD_TIMES = [52.0, 100.0, 190.0]     # 3D drift / photoreal creep
GOOD_TIMES = [55.0, 64.0, 118.0, 145.0]  # holding 2D cartoon

EP02_CUT = os.path.expanduser(
    "~/workspace/trippedd-studio/production/WIZARD_GANG_EP01/"
    "wizard-gang-ep02-realanim-cut.mp4")
# NOTE: wizard-gang-ep02-16x9.mp4 and wizard-gang-ep02-2D-fixed.mp4 on disk
# are both corrupt ("moov atom not found", 2026-10-10) — do NOT use them.


# ------------------------------------------------------- style-hold model ---
# ATTEMPT 1 (documented failure, see SENSORIUM.md): a logistic regression on
# GLOBAL frame stats, trained on audit-labeled timestamps, reached 0.90 train
# accuracy but only 0.40 leave-one-timestamp-out CV accuracy. It learned
# scene lighting, not style — the 3D drift is LOCALIZED (skin/faces/hands)
# and global stats are scene-confounded. Do not use global-stat classifiers
# for this defect class.
#
# ATTEMPT 2 (this one works): STILL-ANCHORED DRIFT. Every shot's approved
# still IS the 2D ground truth. Style drift = standardized feature distance
# of video frames from their own still. Within-shot comparison kills the
# scene confound. No face detection needed.

SCALER_PATH = os.path.join(_HERE, "models", "ep02_feature_scaler.npz")

SEG_DIR = os.path.expanduser(
    "~/workspace/trippedd-studio/production/WIZARD_GANG_EP01/ep02-segments")
STILL_DIR = os.path.expanduser(
    "~/workspace/trippedd-studio/production/WIZARD_GANG_EP01/ep02-stills")


def _labeled_frames(video_path=EP02_CUT, per_time=6, window=2.5):
    """Sample frames around each labeled timestamp. Returns (X, y, groups)."""
    X, y, groups = [], [], []
    for t in BAD_TIMES:
        for ft, frame in sample_video_frames(video_path, sample_fps=per_time,
                                             t0=max(0, t - window),
                                             t1=t + window):
            X.append(visual_vector(frame))
            y.append(0)
            groups.append(f"bad@{t}")
    for t in GOOD_TIMES:
        for ft, frame in sample_video_frames(video_path, sample_fps=per_time,
                                             t0=max(0, t - window),
                                             t1=t + window):
            X.append(visual_vector(frame))
            y.append(1)
            groups.append(f"good@{t}")
    return np.array(X), np.array(y), np.array(groups)


def fit_domain_scaler(video_path=EP02_CUT, save=True, sample_fps=0.5):
    """
    Fit a StandardScaler on broadly-sampled EP02 frames so drift distances
    are comparable across shots. Saved to models/ep02_feature_scaler.npz.
    """
    X = [visual_vector(f) for _, f in
         sample_video_frames(video_path, sample_fps=sample_fps)]
    X = np.array(X)
    mu, sd = X.mean(axis=0), X.std(axis=0) + 1e-9
    if save:
        os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
        np.savez(SCALER_PATH, mu=mu, sd=sd,
                 keys=np.array(VISUAL_KEYS), n=len(X))
    return mu, sd


def _load_scaler():
    if not os.path.exists(SCALER_PATH):
        mu, sd = fit_domain_scaler()
    else:
        z = np.load(SCALER_PATH)
        mu, sd = z["mu"], z["sd"]
    return mu, sd


def _standardize(X, mu, sd):
    return (np.asarray(X, dtype=np.float64) - mu) / sd


def still_anchored_drift(segment_path, still_path, sample_fps=2.0):
    """
    Per-frame standardized Euclidean distance from the approved still.
    Returns (drifts [(t, dist)], still_vec_raw).
    Higher drift = further from the approved 2D look.
    """
    import cv2
    mu, sd = _load_scaler()
    still = cv2.imread(still_path)
    if still is None:
        raise RuntimeError(f"cannot read still {still_path}")
    s_vec = _standardize(visual_vector(still), mu, sd)
    drifts = []
    for t, frame in sample_video_frames(segment_path,
                                        sample_fps=sample_fps):
        f_vec = _standardize(visual_vector(frame), mu, sd)
        drifts.append((t, float(np.linalg.norm(f_vec - s_vec))))
    return drifts, s_vec


def style_hold_score(frame_bgr, still_bgr=None, tau=3.0):
    """
    0..1 — probability the frame holds the approved 2D style.
    Requires the shot's approved still (still-anchored). tau calibrates
    the distance->score mapping (see SENSORIUM.md for calibration).
    """
    mu, sd = _load_scaler()
    if still_bgr is None:
        raise ValueError("style_hold_score needs the shot's approved still "
                         "(still_bgr). Still-anchored by design.")
    d = float(np.linalg.norm(
        _standardize(visual_vector(frame_bgr), mu, sd)
        - _standardize(visual_vector(still_bgr), mu, sd)))
    return float(np.exp(-d / tau))


def train_style_model(*a, **k):
    raise NotImplementedError(
        "Attempt-1 global classifier retired (CV acc 0.40 — see SENSORIUM.md). "
        "Use still_anchored_drift / style_hold_score with the shot's still.")


# ----------------------------------------------------------------- taste ---

# Calibrated on the EP02 labeled frames (see SENSORIUM.md for numbers).
# Each term is mapped to 0..1 then weighted; weights sum to 1.
def taste_score(frame_bgr):
    """
    0..1 — general aesthetic quality. Higher = sharper, better exposed,
    balanced color, clean encode. Calibrated on EP02 frames; not a
    universal beauty metric — a QC taste proxy.
    """
    import cv2
    d = visual_features_bgr(frame_bgr)
    terms = {
        # sharp but not crunchy
        "sharp": float(np.clip(np.log10(d["sharpness"] + 1) / 3.2, 0, 1)),
        # mid contrast, not washed out / not crushed
        "contrast": float(np.clip(1 - abs(d["contrast"] - 42) / 42, 0, 1)),
        # exposed in a sane band
        "exposure": float(np.clip(1 - abs(d["brightness"] - 52) / 52, 0, 1)),
        # colorful but not neon-clown
        "color": float(np.clip(1 - abs(d["colorfulness"] - 55) / 55, 0, 1)),
        # penalize noise
        "clean": float(np.clip(1 - d["noise_est"] / 14, 0, 1)),
        # penalize blockiness
        "encode": float(np.clip(1 - d["blockiness"] / 3, 0, 1)),
    }
    w = {"sharp": 0.22, "contrast": 0.20, "exposure": 0.18,
         "color": 0.15, "clean": 0.15, "encode": 0.10}
    score = sum(terms[k] * w[k] for k in terms)
    return float(np.clip(score, 0, 1)), terms


# ----------------------------------------------------------------- video ---

def score_video(video_path, still_path=None, sample_fps=1.0, t0=0.0,
                t1=None, tau=3.0):
    """
    Per-sampled-frame taste + still-anchored style drift.
    still_path: the shot's approved still (required for style_hold).
    Returns dict with frames [(t, taste, style_hold)], means, flicker,
    and worst moments. Without a still, style_hold is None.
    """
    import cv2
    still = cv2.imread(still_path) if still_path else None
    frames = []
    for t, frame in sample_video_frames(video_path, sample_fps=sample_fps,
                                        t0=t0, t1=t1):
        taste, _ = taste_score(frame)
        sh = (style_hold_score(frame, still, tau=tau)
              if still is not None else None)
        frames.append((t, taste, sh))
    tastes = np.array([f[1] for f in frames])
    holds = np.array([f[2] for f in frames if f[2] is not None])
    worst = sorted(((f[0], f[2]) for f in frames if f[2] is not None),
                   key=lambda x: x[1])[:5]
    return {
        "frames": frames,
        "mean_taste": float(tastes.mean()) if len(tastes) else 0.0,
        "mean_style_hold": float(holds.mean()) if len(holds) else None,
        "style_flicker": float(holds.std()) if len(holds) else None,
        "worst_style_moments": [(round(t, 1), round(s, 3))
                                for t, s in worst],
    }


def _seg_still_pairs():
    """Match seg-XX.mp4 files to ep02-shot-XX.png stills."""
    import glob
    pairs = []
    for seg in sorted(glob.glob(os.path.join(SEG_DIR, "seg-*.mp4"))):
        if "TRANSITION" in seg:
            continue
        tag = os.path.basename(seg)[4:-4]          # "10-1"
        still = os.path.join(STILL_DIR, f"ep02-shot-{tag}.png")
        if os.path.exists(still):
            pairs.append((tag, seg, still))
    return pairs


def rank_segments(sample_fps=1.5, tau=3.0):
    """
    Rank every EP02 segment by still-anchored style drift.
    Validation: the audit's known-bad shots (10-1, 12-3, 20-1) should
    rank near the top (most drifted).
    Returns [(tag, mean_drift, mean_style_hold, flicker)] sorted by
    drift descending.
    """
    rows = []
    for tag, seg, still in _seg_still_pairs():
        drifts, _ = still_anchored_drift(seg, still,
                                         sample_fps=sample_fps)
        ds = np.array([d for _, d in drifts])
        holds = np.exp(-ds / tau)
        rows.append((tag, float(ds.mean()), float(holds.mean()),
                     float(holds.std())))
    rows.sort(key=lambda r: -r[1])
    return rows


def judge(video_path, still_path=None, sample_fps=1.0):
    """One-line director's verdict for a clip."""
    r = score_video(video_path, still_path=still_path,
                    sample_fps=sample_fps)
    if r["mean_style_hold"] is None:
        verdict = "NO STILL - taste only"
    elif r["mean_style_hold"] > 0.6:
        verdict = "HOLDING 2D"
    elif r["mean_style_hold"] < 0.4:
        verdict = "DRIFTING 3D"
    else:
        verdict = "MIXED STYLE"
    if r["style_flicker"] is not None and r["style_flicker"] > 0.22:
        verdict += " + STYLE FLICKER (popping within shot)"
    sh = (f"{r['mean_style_hold']:.2f}" if r["mean_style_hold"] is not None
          else "n/a")
    fl = (f"{r['style_flicker']:.2f}" if r["style_flicker"] is not None
          else "n/a")
    return (f"{verdict} | taste {r['mean_taste']:.2f} | "
            f"style_hold {sh} | flicker {fl} | "
            f"worst@{r['worst_style_moments']}")
