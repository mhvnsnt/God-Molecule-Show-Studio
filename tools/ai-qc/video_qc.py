#!/usr/bin/env python3
"""
video_qc.py — Video analysis for episode QC.

Gives an AI agent "eyes": face detection, mouth-openness tracking
(is a character talking? which one?), and scene-change detection.

Uses MediaPipe Tasks API (FaceLandmarker: 478 landmarks incl. lips) + OpenCV.
No torch needed. Model: models/face_landmarker.task (~3.7MB).
"""
import os

import cv2
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "models", "face_landmarker.task")

# FaceLandmarker lip landmark indices (478-point set)
UPPER_LIP_IDX = [0, 37, 39, 40, 267, 269, 270]
LOWER_LIP_IDX = [17, 84, 91, 146, 181, 314, 405]
MOUTH_LEFT = 61
MOUTH_RIGHT = 291


def _landmarker(running_mode=None):
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    base = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    if running_mode is None:
        running_mode = mp_vision.RunningMode.VIDEO
    opts = mp_vision.FaceLandmarkerOptions(
        base_options=base,
        running_mode=running_mode,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=3)
    return mp_vision.FaceLandmarker.create_from_options(opts)


def open_video(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {path}")
    return cap


def _mouth_openness(landmarks, w, h):
    up = np.mean([[landmarks[i].x * w, landmarks[i].y * h]
                  for i in UPPER_LIP_IDX], axis=0)
    lo = np.mean([[landmarks[i].x * w, landmarks[i].y * h]
                  for i in LOWER_LIP_IDX], axis=0)
    c0 = np.array([landmarks[MOUTH_LEFT].x * w, landmarks[MOUTH_LEFT].y * h])
    c1 = np.array([landmarks[MOUTH_RIGHT].x * w, landmarks[MOUTH_RIGHT].y * h])
    mouth_w = np.linalg.norm(c1 - c0) + 1e-6
    return float(np.linalg.norm(lo - up) / mouth_w)


def mouth_openness_series(video_path, sample_fps=5, max_frames=2000):
    """
    Per sampled frame: mouth openness ratio (0=closed, higher=open).
    Returns [(t_seconds, openness, face_present)].
    """
    import mediapipe as mp
    cap = open_video(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, int(round(src_fps / sample_fps)))
    landmarker = _landmarker()
    out, idx, ms = [], 0, 0
    while len(out) < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            t = idx / src_fps
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                              data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            ms += 33
            res = landmarker.detect_for_video(mp_img, ms)
            if res.face_landmarks:
                h, w = frame.shape[:2]
                op = _mouth_openness(res.face_landmarks[0], w, h)
                out.append((round(t, 2), round(op, 3), True,
                            len(res.face_landmarks)))
            else:
                out.append((round(t, 2), 0.0, False, 0))
        idx += 1
    cap.release()
    landmarker.close()
    # trim to (t, openness, face_present) for compat
    return [(t, o, f) for t, o, f, _ in out]


def talking_regions(video_path, open_thresh=0.08, min_talk_s=1.0, sample_fps=5):
    """
    Merge mouth-open frames into talking regions.
    Returns [(start_s, end_s)] where a face is visibly talking.
    Compare against dialogue audio: talking with no audio = missing line.
    """
    series = mouth_openness_series(video_path, sample_fps=sample_fps)
    regions, start = [], None
    for t, op, face in series:
        talking = face and op > open_thresh
        if talking and start is None:
            start = t
        elif not talking and start is not None:
            if t - start >= min_talk_s:
                regions.append((round(start, 1), round(t, 1)))
            start = None
    if start is not None and series and series[-1][0] - start >= min_talk_s:
        regions.append((round(start, 1), round(series[-1][0], 1)))
    return regions


def scene_changes(video_path, threshold=0.4, sample_fps=2):
    """Return [t_seconds] of hard scene cuts via frame differencing."""
    cap = open_video(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, int(round(src_fps / sample_fps)))
    prev, cuts, idx = None, [], 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            small = cv2.resize(gray, (64, 36)).astype(np.float32) / 255.0
            if prev is not None:
                if float(np.mean(np.abs(small - prev))) > threshold:
                    cuts.append(round(idx / src_fps, 1))
            prev = small
        idx += 1
    cap.release()
    return cuts


def face_count_at(video_path, t_seconds):
    """Number of faces detected at a timestamp."""
    import mediapipe as mp
    from mediapipe.tasks.python import vision as mp_vision
    cap = open_video(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t_seconds * fps))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return 0
    landmarker = _landmarker(running_mode=mp_vision.RunningMode.IMAGE)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                      data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    res = landmarker.detect(mp_img)
    n = len(res.face_landmarks) if res.face_landmarks else 0
    landmarker.close()
    return n


if __name__ == "__main__":
    import sys, json
    video = sys.argv[1]
    if "--talking" in sys.argv:
        print(json.dumps(talking_regions(video), indent=1))
    elif "--scenes" in sys.argv:
        print(json.dumps(scene_changes(video), indent=1))
    elif "--faces" in sys.argv:
        t = float(sys.argv[sys.argv.index("--faces") + 1])
        print(json.dumps({"t": t, "faces": face_count_at(video, t)}))
    else:
        print(json.dumps(talking_regions(video), indent=1))
