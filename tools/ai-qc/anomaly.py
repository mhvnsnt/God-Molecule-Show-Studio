#!/usr/bin/env python3
"""
anomaly.py — The NOSE. Detects things that are off.

Cross-modal anomaly detection: finds inconsistencies BETWEEN senses
that single-modality checks miss.

- AV sync drift: mouth moving with no audio, audio with no mouth
- Lighting jumps at cuts: brightness shift between adjacent scenes
- Likeness drift: face embedding changes across scenes (character
  looks different = style drift or wrong asset)
- Audio scene mismatch: BGM/speech label changes without a visual cut
- Duration anomalies: shots that are suspiciously long/short

"Smell" = statistical surprise. Flags get human review.
"""
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_qc
import audio_deep
import video_qc
import visual_deep


def av_sync_anomalies(video_path, sample_fps=5):
    """
    Windows where mouth moves but no speech audio, or speech audio
    with no mouth moving. Returns [{"window": [t0,t1], "kind": ...}].
    """
    wav = audio_qc.extract_audio(video_path, "/tmp/aiqc_anom.wav")
    y = audio_qc.load_audio(wav)
    sr = 16000
    talking = video_qc.talking_regions(video_path, sample_fps=sample_fps)
    # speech-active windows from VAD
    vad = audio_qc.speech_activity(y, sr)
    frame_s = 0.03  # 30ms frames
    out = []
    for ts, te in talking:
        i0, i1 = int(ts / frame_s), int(te / frame_s)
        seg = vad[i0:i1] if i1 < len(vad) else vad[i0:]
        if len(seg) == 0:
            continue
        speech_frac = float(seg.mean())
        if speech_frac < 0.15:
            out.append({"window": [ts, te], "kind": "mouth_no_audio",
                        "speech_frac": round(speech_frac, 2)})
    # reverse: speech with no talking region
    # (coarse: check 5s windows)
    for w0 in np.arange(0, len(y) / sr, 5.0):
        i0, i1 = int(w0 / frame_s), int((w0 + 5) / frame_s)
        seg = vad[i0:i1] if i1 < len(vad) else vad[i0:]
        if len(seg) and seg.mean() > 0.5:
            # is any talking region overlapping?
            overlap = any(not (te < w0 or ts > w0 + 5) for ts, te in talking)
            if not overlap:
                out.append({"window": [round(float(w0), 1),
                                       round(float(w0 + 5), 1)],
                            "kind": "audio_no_mouth",
                            "speech_frac": round(float(seg.mean()), 2)})
    return out


def lighting_jumps(video_path, sample_fps=1, jump_thresh=0.2):
    """
    Brightness jumps at scene cuts (lighting inconsistency between
    adjacent shots). Returns [{"t": cut_t, "delta": x}].
    """
    cuts = video_qc.scene_changes(video_path)
    prof = {t: b for t, b, s, w, c in
            visual_deep.color_profile(video_path, sample_fps=sample_fps)}
    out = []
    for ct in cuts:
        # nearest profile samples before/after
        before = [b for t, b in prof.items() if t < ct]
        after = [b for t, b in prof.items() if t >= ct]
        if before and after:
            d = abs(after[0] - before[-1])
            if d > jump_thresh:
                out.append({"t": ct, "kind": "lighting_jump",
                            "delta": round(float(d), 3)})
    return out


def _face_embedding(frame_bgr):
    """
    Lightweight face embedding: normalized 64x64 grayscale face crop
    flattened. Not a neural embedding, but catches gross likeness
    changes (different art style, wrong character asset).
    """
    import mediapipe as mp
    from mediapipe.tasks.python import vision as mp_vision
    lm = video_qc._landmarker(running_mode=mp_vision.RunningMode.IMAGE)
    mp_img = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    res = lm.detect(mp_img)
    lm.close()
    if not res.face_landmarks:
        return None
    h, w = frame_bgr.shape[:2]
    pts = np.array([[p.x * w, p.y * h] for p in res.face_landmarks[0]])
    x0, y0 = pts.min(0).astype(int)
    x1, y1 = pts.max(0).astype(int)
    pad = 10
    crop = frame_bgr[max(0, y0-pad):y1+pad, max(0, x0-pad):x1+pad]
    if crop.size == 0:
        return None
    small = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), (64, 64))
    v = small.astype(np.float32).ravel()
    return (v - v.mean()) / (v.std() + 1e-9)


def likeness_drift(video_path, sample_fps=0.5, drift_thresh=0.55):
    """
    Track face appearance across the episode. Flags timestamps where
    the visible face looks substantially different from the episode's
    dominant face embedding (style drift / wrong asset / filter).
    Returns [{"t": t, "distance": x}].
    """
    cap = cv2.VideoCapture(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, int(round(src_fps / sample_fps)))
    embs, idx = [], 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            e = _face_embedding(frame)
            if e is not None:
                embs.append((round(idx / src_fps, 1), e))
        idx += 1
    cap.release()
    if len(embs) < 5:
        return [{"note": "too few faces for drift analysis",
                 "n": len(embs)}]
    # dominant embedding = medoid
    X = np.stack([e for _, e in embs])
    dists = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=2)
    medoid = int(np.argmin(dists.sum(0)))
    ref = X[medoid]
    out = []
    for t, e in embs:
        d = float(np.linalg.norm(e - ref) / np.sqrt(len(e)))
        if d > drift_thresh:
            out.append({"t": t, "kind": "likeness_drift",
                        "distance": round(d, 3)})
    # compress consecutive
    comp = []
    for f in out:
        if comp and f["t"] - comp[-1]["t"] < 5:
            comp[-1]["t"] = f["t"]
        else:
            comp.append(f)
    return comp


def audio_scene_mismatch(video_path):
    """
    Places where the audio content type (speech/music/sfx) changes
    without a corresponding visual scene cut (or vice versa).
    Returns [{"t": t, "kind": ...}].
    """
    wav = audio_qc.extract_audio(video_path, "/tmp/aiqc_anom2.wav")
    y = audio_qc.load_audio(wav)
    sr = 16000
    segs = audio_deep.music_vs_speech(y, sr)
    cuts = set(video_qc.scene_changes(video_path))
    out = []
    for i in range(1, len(segs)):
        if segs[i][2] != segs[i-1][2]:
            t = segs[i][0]
            # is there a visual cut within 3s?
            near_cut = any(abs(c - t) < 3 for c in cuts)
            if not near_cut and segs[i][2] in ("music", "speech"):
                out.append({"t": t, "kind": "audio_shift_no_cut",
                            "from": segs[i-1][2], "to": segs[i][2]})
    return out


def shot_duration_anomalies(video_path, min_s=1.0, max_s=30.0):
    """
    Shots shorter than min_s (flash frames) or longer than max_s
    (dwell). Returns [{"window": [t0,t1], "kind": ...}].
    """
    cuts = [0.0] + video_qc.scene_changes(video_path)
    cap = cv2.VideoCapture(video_path)
    dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or 30)
    cap.release()
    cuts.append(round(dur, 1))
    out = []
    for i in range(1, len(cuts)):
        d = cuts[i] - cuts[i-1]
        if d < min_s:
            out.append({"window": [cuts[i-1], cuts[i]],
                        "kind": "flash_shot", "dur_s": round(d, 2)})
        elif d > max_s:
            out.append({"window": [cuts[i-1], cuts[i]],
                        "kind": "long_dwell", "dur_s": round(d, 2)})
    return out


if __name__ == "__main__":
    import json
    video = sys.argv[1]
    if "--av" in sys.argv:
        print(json.dumps(av_sync_anomalies(video), indent=1))
    elif "--light" in sys.argv:
        print(json.dumps(lighting_jumps(video), indent=1))
    elif "--likeness" in sys.argv:
        print(json.dumps(likeness_drift(video), indent=1))
    elif "--mismatch" in sys.argv:
        print(json.dumps(audio_scene_mismatch(video), indent=1))
    elif "--shots" in sys.argv:
        print(json.dumps(shot_duration_anomalies(video), indent=1))
    else:
        print(json.dumps({
            "av_sync": av_sync_anomalies(video),
            "lighting_jumps": lighting_jumps(video),
            "audio_mismatch": audio_scene_mismatch(video),
            "shot_anomalies": shot_duration_anomalies(video),
        }, indent=1))
