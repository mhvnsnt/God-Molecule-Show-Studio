#!/usr/bin/env python3
"""
motion.py — Motion and body analysis for episode QC.

- Optical flow: motion magnitude/direction per region (catches frozen
  characters, unintended stillness, motion discontinuities)
- Full-body pose: MediaPipe Pose (33 landmarks) — where are bodies,
  are they moving, T-pose/A-pose detection
- Hand tracking: MediaPipe Hands — hand presence, openness
- Stabilization analysis: global motion vectors (shaky cam detection)
- Gesture basics: arm raise, pointing (from pose landmarks)

All CPU. Uses cv2 + mediapipe (already in venv).
"""
import os

import cv2
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


def _frames(video_path, sample_fps=5, width=320):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {video_path}")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, int(round(src_fps / sample_fps)))
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            h, w = frame.shape[:2]
            small = cv2.resize(frame, (width, int(h * width / w)))
            yield round(idx / src_fps, 2), small
        idx += 1
    cap.release()


def optical_flow_series(video_path, sample_fps=5, grid=4):
    """
    Per-sample mean optical flow magnitude in a grid.
    Returns [(t, mean_mag, max_cell_mag, dominant_direction_deg)].
    Low magnitude everywhere = frozen/still (slideshow?).
    """
    out = []
    prev_gray = None
    for t, frame in _frames(video_path, sample_fps=sample_fps, width=320):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag, ang = cv2.cartToPolar(flow[:, :, 0], flow[:, :, 1])
            h, w = mag.shape
            ch, cw = h // grid, w // grid
            cell_mags = []
            for i in range(grid):
                for j in range(grid):
                    cell_mags.append(mag[i*ch:(i+1)*ch, j*cw:(j+1)*cw].mean())
            mean_mag = float(mag.mean())
            max_cell = float(max(cell_mags))
            # dominant direction: angle at max-motion cell
            mi = int(np.argmax(cell_mags))
            ci, cj = divmod(mi, grid)
            dom_ang = float(ang[ci*ch + ch//2, cj*cw + cw//2] * 180 / np.pi)
            out.append((t, round(mean_mag, 3), round(max_cell, 3),
                        round(dom_ang, 1)))
        prev_gray = gray
    return out


def still_regions(video_path, sample_fps=5, mag_thresh=0.15, min_still_s=4.0):
    """
    [(t_start, t_end)] where nothing moves — stronger than frozen_regions
    because optical flow catches subtle motion that frame-diff misses.
    """
    series = optical_flow_series(video_path, sample_fps=sample_fps)
    out, start = [], None
    for t, mean_mag, _, _ in series:
        if mean_mag < mag_thresh and start is None:
            start = t
        elif mean_mag >= mag_thresh and start is not None:
            if t - start >= min_still_s:
                out.append((round(start, 1), round(t, 1)))
            start = None
    if start is not None and series:
        out.append((round(start, 1), round(series[-1][0], 1)))
    return out


def _pose_landmarker():
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    # Use PoseLandmarker with full model if available, else lite
    for name in ("pose_landmarker_full.task", "pose_landmarker_lite.task",
                 "pose_landmarker_heavy.task"):
        p = os.path.join(MODEL_DIR, name)
        if os.path.exists(p):
            base = mp_python.BaseOptions(model_asset_path=p)
            opts = mp_vision.PoseLandmarkerOptions(
                base_options=base,
                running_mode=mp_vision.RunningMode.VIDEO,
                num_poses=2)
            return mp_vision.PoseLandmarker.create_from_options(opts)
    return None


def pose_at(video_path, t_seconds):
    """
    Full-body pose at a timestamp. Returns list of poses, each with
    key landmarks (nose, shoulders, elbows, wrists, hips, knees, ankles)
    as normalized (x, y, visibility).
    """
    import mediapipe as mp
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t_seconds * fps))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return []
    lm = _pose_landmarker()
    if lm is None:
        return [{"note": "pose model not downloaded"}]
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                      data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    res = lm.detect_for_video(mp_img, int(t_seconds * 1000))
    lm.close()
    out = []
    KEY = {0: "nose", 11: "l_shoulder", 12: "r_shoulder", 13: "l_elbow",
           14: "r_elbow", 15: "l_wrist", 16: "r_wrist", 23: "l_hip",
           24: "r_hip", 25: "l_knee", 26: "r_knee", 27: "l_ankle",
           28: "r_ankle"}
    for pose in (res.pose_landmarks or []):
        d = {}
        for idx, name in KEY.items():
            p = pose[idx]
            d[name] = (round(p.x, 3), round(p.y, 3),
                       round(getattr(p, "visibility", 1.0), 2))
        out.append(d)
    return out


def tpose_check(pose):
    """
    Is this pose a T-pose or A-pose? (rigging rest-pose detection)
    Returns (is_tpose, is_apose, arm_angle_deg).
    """
    try:
        ls = np.array(pose["l_shoulder"][:2])
        rs = np.array(pose["r_shoulder"][:2])
        le = np.array(pose["l_elbow"][:2])
        re = np.array(pose["r_elbow"][:2])
        # arm direction vs horizontal
        lang = abs(np.degrees(np.arctan2(le[1] - ls[1], le[0] - ls[0])))
        rang = abs(np.degrees(np.arctan2(re[1] - rs[1], re[0] - rs[0])))
        # T-pose: arms ~horizontal (angle near 0 or 180)
        tpose = (lang < 25 or lang > 155) and (rang < 25 or rang > 155)
        # A-pose: arms ~30-60 deg down
        apose = (25 < lang < 65 or 115 < lang < 155) and \
                (25 < rang < 65 or 115 < rang < 155)
        return bool(tpose), bool(apose), round(float((lang + rang) / 2), 1)
    except (KeyError, TypeError):
        return False, False, 0.0


def hand_tracking_at(video_path, t_seconds):
    """
    Hand detection at a timestamp. Returns [{handedness, openness}].
    openness 0..1: 1 = open palm, 0 = fist.
    """
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    model = os.path.join(MODEL_DIR, "hand_landmarker.task")
    if not os.path.exists(model):
        return [{"note": "hand model not downloaded"}]
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t_seconds * fps))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return []
    base = mp_python.BaseOptions(model_asset_path=model)
    opts = mp_vision.HandLandmarkerOptions(
        base_options=base,
        running_mode=mp_vision.RunningMode.IMAGE, num_hands=4)
    lm = mp_vision.HandLandmarker.create_from_options(opts)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                      data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    res = lm.detect(mp_img)
    lm.close()
    out = []
    for i, hand in enumerate(res.hand_landmarks or []):
        # openness: fingertip spread vs palm size
        tips = [8, 12, 16, 20]
        wrist = np.array([hand[0].x, hand[0].y])
        palm = np.linalg.norm(
            np.array([hand[9].x, hand[9].y]) - wrist) + 1e-6
        spread = np.mean([np.linalg.norm(
            np.array([hand[t].x, hand[t].y]) - wrist) for t in tips])
        openness = float(np.clip(spread / (palm * 2.5), 0, 1))
        handed = "unknown"
        if res.handedness and i < len(res.handedness):
            handed = res.handedness[i][0].category_name
        out.append({"handedness": handed,
                    "openness": round(openness, 2)})
    return out


def camera_shake(video_path, sample_fps=10, win_s=2.0):
    """
    Detect shaky-cam / unstable framing via global motion variance.
    Returns [(t, shake_score)] where shake_score > 1.0 is notable.
    Uses phase correlation for global translation estimation.
    """
    cap = cv2.VideoCapture(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, int(round(src_fps / sample_fps)))
    translations, idx, prev = [], 0, None
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            gray = cv2.cvtColor(
                cv2.resize(frame, (160, 90)), cv2.COLOR_BGR2GRAY)
            if prev is not None:
                (dx, dy), _ = cv2.phaseCorrelate(
                    prev.astype(np.float32), gray.astype(np.float32))
                translations.append((idx / src_fps, float(dx), float(dy)))
            prev = gray
        idx += 1
    cap.release()
    # shake = high-freq variance of translation
    out = []
    winsz = max(2, int(win_s * sample_fps))
    for i in range(0, len(translations) - winsz, winsz // 2):
        chunk = translations[i:i + winsz]
        dxs = np.array([c[1] for c in chunk])
        dys = np.array([c[2] for c in chunk])
        shake = float(np.std(dxs) + np.std(dys))
        out.append((round(chunk[0][0], 1), round(shake, 3)))
    return out


if __name__ == "__main__":
    import sys, json
    video = sys.argv[1]
    if "--still" in sys.argv:
        print(json.dumps(still_regions(video), indent=1))
    elif "--flow" in sys.argv:
        print(json.dumps(optical_flow_series(video)[:20], indent=1))
    elif "--pose" in sys.argv:
        t = float(sys.argv[sys.argv.index("--pose") + 1])
        print(json.dumps(pose_at(video, t), indent=1))
    elif "--hands" in sys.argv:
        t = float(sys.argv[sys.argv.index("--hands") + 1])
        print(json.dumps(hand_tracking_at(video, t), indent=1))
    elif "--shake" in sys.argv:
        print(json.dumps(camera_shake(video), indent=1))
    else:
        print(json.dumps({
            "still_regions": still_regions(video),
            "camera_shake": camera_shake(video),
        }, indent=1))
