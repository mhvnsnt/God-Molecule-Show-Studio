#!/usr/bin/env python3
"""
sync.py — Cross-modal reasoning: does what we SEE match what we HEAR?

  av_sync(video, t0, t1):
    visual envelope = mouth-openness series (MediaPipe FaceLandmarker,
      via ai-qc's video_qc) where faces are found; falls back to a
      frame-difference motion envelope where the detector doesn't fire
      (it barely fires on this cartoon style — see SENSORIUM.md).
    audio envelope  = RMS energy per 100ms (+ energy-VAD speech mask,
      via ai-qc's audio_qc; webrtcvad is broken in the venv so the
      energy fallback is used).
    Lag search ±1.0s at 100ms steps: normalized cross-correlation of
    the two envelopes -> best_lag_s (A/V offset) and sync_score 0..1.

  mismatch flags:
    - "talking head, no speech": mouth moving while audio is silent
      (muted line, lost dialogue)
    - "speech, frozen face": speech present while the mouth/motion
      envelope is flat (disembodied voice, slideshow frame)

  Viseme-level sync ("mouth shape doesn't match phonemes") needs
  SyncNet / AV-HuBERT — torch + GPU, documented in SENSORIUM.md as
  roadmap, not claimed here.

CPU-only.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.expanduser("~/workspace/tools/ai-qc"))
from features import sample_video_frames, extract_audio_mono


def _mouth_envelope(video_path, t0, t1, sample_fps=5.0):
    """
    [(t, openness)] for frames in [t0, t1], plus face-present ratio.
    Seeks straight to t0 (ai-qc's mouth_openness_series reads from frame
    0, which is far too slow for windowed sync — so we drive the
    landmarker directly here using video_qc's helpers).
    Returns (series, face_ratio).
    """
    import cv2
    import mediapipe as mp
    from video_qc import _landmarker, _mouth_openness, open_video
    cap = open_video(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, int(round(src_fps / sample_fps)))
    start_idx = max(0, int((t0 - 1.0) * src_fps))
    end_idx = int((t1 + 1.0) * src_fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_idx)
    landmarker = _landmarker()
    series, faces, idx, ms = [], 0, start_idx, 0
    try:
        while idx <= end_idx:
            ok, frame = cap.read()
            if not ok:
                break
            if (idx - start_idx) % step == 0:
                t = idx / src_fps
                mp_img = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                ms += 200
                res = landmarker.detect_for_video(mp_img, ms)
                fl = (res.face_landmarks or [None])[0]
                if fl is not None:
                    h, w = frame.shape[:2]
                    series.append((t, _mouth_openness(fl, w, h)))
                    faces += 1
                else:
                    series.append((t, 0.0))
            idx += 1
    finally:
        cap.release()
        try:
            landmarker.close()
        except Exception:
            pass
    n = len(series)
    return series, (faces / n if n else 0.0)


def _motion_envelope(video_path, t0, t1, sample_fps=5.0):
    """Fallback visual envelope: mean abs frame difference."""
    import cv2
    env, prev = [], None
    for t, frame in sample_video_frames(video_path,
                                        sample_fps=sample_fps,
                                        t0=max(0, t0 - 1.0), t1=t1 + 1.0):
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(
            np.float32) / 255.0
        if prev is not None:
            env.append((t, float(np.abs(g - prev).mean())))
        prev = g
    return env


def _audio_envelope(video_path, t0, t1, sr=16000, hop_s=0.1):
    """[(t, rms)] RMS energy envelope per hop_s."""
    y, _sr, tmp = extract_audio_mono(video_path, sr=sr)
    try:
        w = int(_sr * hop_s)
        a0 = max(0, int((t0 - 1.0) * _sr))
        a1 = int((t1 + 1.0) * _sr)
        seg = y[a0:a1]
        env = [(round((a0 + i) / _sr, 2),
                float(np.sqrt(np.mean(seg[i:i + w] ** 2)) + 1e-9))
               for i in range(0, len(seg) - w, w)]
        return env
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _resample_envelope(env, t0, t1, dt=0.1):
    """Resample an envelope to a uniform grid [t0, t1]."""
    if not env:
        return np.array([])
    ts = np.array([t for t, _ in env])
    vs = np.array([v for _, v in env])
    grid = np.arange(t0, t1 + 1e-9, dt)
    return np.interp(grid, ts, vs, left=vs[0], right=vs[-1])


def _ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    denom = np.linalg.norm(a) * np.linalg.norm(b) + 1e-9
    return float(np.dot(a, b) / denom)


def av_sync(video_path, t0, t1, max_lag_s=1.0, dt=0.1):
    """
    Cross-modal A/V sync for window [t0, t1].
    Returns dict:
      visual_kind: 'mouth' or 'motion' (which visual envelope was used)
      face_ratio:  fraction of sampled frames with a detected face
      best_lag_s:  audio lag vs video at max correlation
                   (+ means audio LAGS video)
      sync_score:  0..1 normalized cross-correlation at best lag
      speech_ratio: fraction of window with speech-like energy
      flags:       list of mismatch strings
    """
    audio_env = _audio_envelope(video_path, t0, t1)
    mouth_env, face_ratio = _mouth_envelope(video_path, t0, t1)
    if face_ratio >= 0.3:
        visual_env, kind = mouth_env, "mouth"
    else:
        visual_env, kind = _motion_envelope(video_path, t0, t1), "motion"

    a = _resample_envelope(audio_env, t0, t1, dt)
    v = _resample_envelope(visual_env, t0, t1, dt)
    flags = []
    if len(a) < 10 or len(v) < 10:
        return {"visual_kind": kind, "face_ratio": round(face_ratio, 3),
                "best_lag_s": 0.0, "sync_score": 0.0,
                "speech_ratio": 0.0,
                "flags": ["insufficient data in window"]}

    # speech proxy: energy above the window's own median.
    # (True VAD via webrtcvad is broken in this venv — pkg_resources
    # missing — so this is an energy proxy, documented as such.)
    med = np.median(a)
    speech = a > max(med * 1.15, 1e-4)
    speech_ratio = float(speech.mean())

    # lag search
    max_lag = int(max_lag_s / dt)
    best_lag, best_score = 0, -2.0
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            aa, vv = a[:lag], v[-lag:]
        elif lag > 0:
            aa, vv = a[lag:], v[:-lag]
        else:
            aa, vv = a, v
        if len(aa) < 8:
            continue
        s = _ncc(aa, vv)
        if s > best_score:
            best_score, best_lag = s, lag
    sync_score = float(np.clip((best_score + 1) / 2, 0, 1))

    # mismatch flags
    v_active = v > (np.percentile(v, 75) * 0.8 + 1e-9)
    if kind == "mouth":
        if v_active.mean() > 0.25 and speech_ratio < 0.1:
            flags.append("talking head, no speech "
                         "(mouth moving over silence)")
        if speech_ratio > 0.3 and v_active.mean() < 0.08:
            flags.append("speech over frozen face "
                         "(voice with no mouth motion)")
    else:
        if speech_ratio > 0.4 and v.std() < 1e-4:
            flags.append("speech over frozen picture")

    return {
        "visual_kind": kind,
        "face_ratio": round(float(face_ratio), 3),
        "best_lag_s": round(best_lag * dt, 2),
        "sync_score": round(sync_score, 3),
        "speech_ratio": round(float(speech_ratio), 3),
        "flags": flags,
    }


def sync_report(video_path, windows):
    """Run av_sync over a list of (label, t0, t1) windows; print table."""
    lines = [f"{'window':>28} {'vis':>6} {'lag':>6} "
             f"{'sync':>5} {'speech':>6}  flags"]
    for label, t0, t1 in windows:
        r = av_sync(video_path, t0, t1)
        fl = "; ".join(r["flags"]) if r["flags"] else "-"
        lines.append(f"{label:>28} {r['visual_kind']:>6} "
                     f"{r['best_lag_s']:>6} {r['sync_score']:>5} "
                     f"{r['speech_ratio']:>6}  {fl}")
    return "\n".join(lines)
