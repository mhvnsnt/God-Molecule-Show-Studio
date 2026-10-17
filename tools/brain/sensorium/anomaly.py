#!/usr/bin/env python3
"""
anomaly.py — "Smell": unsupervised anomaly detection on video + audio.

Nothing is labeled. The episode is its own baseline; frames/windows that
don't look/sound like the rest get flagged. Techniques:

  video:
    - IsolationForest on per-frame visual features (global oddballs:
      black frames, glitch frames, render failures)
    - temporal pop: each frame vs the rolling median of its neighbors
      (catches morph pops, texture pop, single-frame glitches — the
      classic AI-video tells — without any labels)
  audio:
    - IsolationForest on per-window audio features (dropouts, mic bumps,
      encode glitches)
    - clipping + sudden level jumps (from ai-qc's audio_deep ideas,
      reimplemented dependency-light)

CPU-only: sklearn + numpy + OpenCV + librosa.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from features import (visual_vector, audio_vector, VISUAL_KEYS,
                      sample_video_frames, extract_audio_mono)


def frame_feature_matrix(video_path, sample_fps=2.0, t0=0.0, t1=None):
    """(times, X) — visual feature matrix for sampled frames."""
    ts, Xs = [], []
    for t, frame in sample_video_frames(video_path, sample_fps=sample_fps,
                                        t0=t0, t1=t1):
        ts.append(t)
        Xs.append(visual_vector(frame))
    return np.array(ts), np.array(Xs)


def isolation_anomalies(video_path, sample_fps=2.0, contamination=0.05,
                        t0=0.0, t1=None):
    """
    IsolationForest over frame features. Returns [(t, anomaly_score)]
    sorted by most-anomalous first. Score = -decision_function
    (higher = weirder).
    """
    from sklearn.ensemble import IsolationForest
    ts, X = frame_feature_matrix(video_path, sample_fps, t0, t1)
    if len(X) < 10:
        return []
    clf = IsolationForest(n_estimators=200, contamination=contamination,
                          random_state=7)
    clf.fit(X)
    scores = -clf.decision_function(X)
    order = np.argsort(-scores)
    return [(round(float(ts[i]), 2), round(float(scores[i]), 3))
            for i in order]


def temporal_pop(video_path, sample_fps=4.0, window_s=3.0, t0=0.0,
                 t1=None):
    """
    Each frame vs the rolling median of its temporal neighbors.
    Flags single-frame/morph pops: a frame that looks nothing like the
    frames right before/after it. Returns [(t, pop_score)] sorted
    most-pop first. pop_score = standardized distance from neighbor median.
    """
    ts, X = frame_feature_matrix(video_path, sample_fps, t0, t1)
    if len(X) < 9:
        return []
    mu, sd = X.mean(axis=0), X.std(axis=0) + 1e-9
    Xs = (X - mu) / sd
    half = max(2, int(window_s * sample_fps / 2))
    out = []
    for i in range(half, len(Xs) - half):
        neigh = np.median(np.vstack([Xs[i - half:i], Xs[i + 1:i + half + 1]]),
                          axis=0)
        d = float(np.linalg.norm(Xs[i] - neigh))
        out.append((round(float(ts[i]), 2), round(d, 3)))
    out.sort(key=lambda x: -x[1])
    return out


def audio_feature_matrix(y, sr=16000, win_s=1.0):
    """(times, X) — audio feature matrix per window."""
    n = int(win_s * sr)
    ts, Xs = [], []
    for i in range(0, len(y) - n, n // 2):
        ts.append(i / sr)
        Xs.append(audio_vector(y[i:i + n], sr=sr))
    return np.array(ts), np.array(Xs)


def audio_anomalies(video_path, win_s=1.0, contamination=0.05,
                    sr=16000):
    """
    IsolationForest over audio windows + hard detectors (clipping,
    dropouts). Returns dict {iforest: [(t, score)], clipping: [...],
    dropouts: [...]}.
    """
    from sklearn.ensemble import IsolationForest
    y, _sr, tmp = extract_audio_mono(video_path, sr=sr)
    try:
        ts, X = audio_feature_matrix(y, _sr, win_s)
        out = {"iforest": [], "clipping": [], "dropouts": []}
        if len(X) >= 10:
            clf = IsolationForest(n_estimators=200,
                                  contamination=contamination,
                                  random_state=7)
            clf.fit(X)
            scores = -clf.decision_function(X)
            order = np.argsort(-scores)
            out["iforest"] = [(round(float(ts[i]), 2),
                               round(float(scores[i]), 3))
                              for i in order[:10]]
        # clipping: fraction of samples within 1% of digital max
        peak = np.abs(y).max()
        if peak > 0.99:
            frac = float((np.abs(y) > 0.99).mean())
            out["clipping"] = [("global", round(frac, 4))]
        # dropouts: 100ms windows >60dB below median energy
        win = _sr // 10
        e = np.array([np.sqrt(np.mean(y[i:i + win] ** 2)) + 1e-9
                      for i in range(0, len(y) - win, win)])
        med = np.median(e)
        drops = np.nonzero(e < med * 1e-3)[0]
        out["dropouts"] = [round(float(i * 0.1), 2) for i in drops[:20]]
        return out
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def smell(video_path, sample_fps=2.0, top_n=8):
    """
    Full smell report for a clip. Returns dict with the top visual
    oddballs, top temporal pops, and audio anomalies.
    """
    iso = isolation_anomalies(video_path, sample_fps=sample_fps)
    pops = temporal_pop(video_path, sample_fps=min(4.0, sample_fps * 2))
    aud = audio_anomalies(video_path)
    return {
        "visual_oddballs": iso[:top_n],
        "temporal_pops": pops[:top_n],
        "audio": aud,
    }


def report(smell_dict):
    """Human-readable smell report."""
    lines = ["--- SMELL (unsupervised anomalies) ---"]
    vo = smell_dict["visual_oddballs"]
    lines.append("visual oddballs: " + (
        ", ".join(f"{t}s({s})" for t, s in vo) if vo else "none"))
    tp = smell_dict["temporal_pops"]
    lines.append("temporal pops: " + (
        ", ".join(f"{t}s({s})" for t, s in tp) if tp else "none"))
    a = smell_dict["audio"]
    lines.append("audio oddballs: " + (
        ", ".join(f"{t}s({s})" for t, s in a["iforest"])
        if a["iforest"] else "none"))
    if a["clipping"]:
        lines.append(f"CLIPPING: {a['clipping']}")
    if a["dropouts"]:
        lines.append(f"dropouts at: {a['dropouts'][:8]}")
    return "\n".join(lines)
