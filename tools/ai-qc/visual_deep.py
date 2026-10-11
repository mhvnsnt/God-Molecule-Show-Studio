#!/usr/bin/env python3
"""
visual_deep.py — Deeper visual analysis for episode QC (horizontal scale).

- Frozen frames: consecutive near-identical frames (slideshow detection)
- Color grading: per-scene histogram stats, sudden grading shifts
- Glitch detection: blockiness, banding, compression artifacts
- Text overlay detection: regions likely containing rendered text
- Composition: face placement (rule of thirds), headroom, centering
- Filter signature: detect cartoon/bilateral "bullshit filter" regions

OpenCV + numpy only.
"""
import cv2
import numpy as np


def _frames(video_path, sample_fps=2, max_frames=3000, width=320):
    """Yield (t, frame_bgr) sampled from video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {video_path}")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, int(round(src_fps / sample_fps)))
    idx = 0
    while idx < max_frames * step:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            h, w = frame.shape[:2]
            scale = width / w
            small = cv2.resize(frame, (width, int(h * scale)))
            yield round(idx / src_fps, 2), small
        idx += 1
    cap.release()


def frozen_regions(video_path, sample_fps=5, diff_thresh=2.0, min_frozen_s=3.0):
    """
    Return [(t_start, t_end)] where frames are near-identical.
    Catches: slideshow segments, frozen renders, stuck frames.
    diff_thresh: mean abs pixel diff below this = frozen.
    """
    out, start, prev = [], None, None
    for t, frame in _frames(video_path, sample_fps=sample_fps, width=160):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            d = float(np.mean(np.abs(gray - prev)))
            if d < diff_thresh and start is None:
                start = t
            elif d >= diff_thresh and start is not None:
                if t - start >= min_frozen_s:
                    out.append((round(start, 1), round(t, 1)))
                start = None
        prev = gray
    if start is not None:
        # use last sampled t
        out.append((round(start, 1), round(t, 1)))
    return out


def color_profile(video_path, sample_fps=1):
    """
    Per-sample color stats: mean brightness, saturation, warmth, contrast.
    Returns [(t, brightness, saturation, warmth, contrast)].
    Sudden jumps = grading inconsistency or filter on/off.
    """
    out = []
    for t, frame in _frames(video_path, sample_fps=sample_fps):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        bgr = frame.astype(np.float32)
        brightness = float(hsv[:, :, 2].mean() / 255)
        saturation = float(hsv[:, :, 1].mean() / 255)
        # warmth: red-yellow vs blue (B channel vs R channel)
        warmth = float((bgr[:, :, 2].mean() - bgr[:, :, 0].mean()) / 255)
        contrast = float(hsv[:, :, 2].std() / 255)
        out.append((t, round(brightness, 3), round(saturation, 3),
                    round(warmth, 3), round(contrast, 3)))
    return out


def grading_shifts(video_path, sample_fps=1, jump_thresh=0.25):
    """
    Timestamps where color grading jumps suddenly (filter toggled,
    scene rendered differently). Returns [(t, metric, delta)].
    """
    prof = color_profile(video_path, sample_fps=sample_fps)
    out = []
    for i in range(1, len(prof)):
        t0, b0, s0, w0, c0 = prof[i - 1]
        t1, b1, s1, w1, c1 = prof[i]
        deltas = {"brightness": abs(b1 - b0), "saturation": abs(s1 - s0),
                  "warmth": abs(w1 - w0), "contrast": abs(c1 - c0)}
        for m, d in deltas.items():
            if d > jump_thresh:
                out.append((t1, m, round(d, 3)))
    return out


def blockiness_map(frame):
    """Estimate JPEG-style blockiness (8x8 grid edge energy). Higher = worse."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
    h, w = gray.shape
    # vertical block edges
    v_edges = np.abs(np.diff(gray[:, 7::8], axis=1)).mean()
    h_edges = np.abs(np.diff(gray[7::8, :], axis=0)).mean()
    # non-block edges for normalization
    v_all = np.abs(np.diff(gray, axis=1)).mean()
    h_all = np.abs(np.diff(gray, axis=0)).mean()
    return float(((v_edges + h_edges) / 2) / ((v_all + h_all) / 2 + 1e-6))


def glitch_scan(video_path, sample_fps=2, block_thresh=2.5):
    """
    Return [(t, blockiness)] where compression artifacts spike.
    Also flags near-black / near-white flash frames.
    """
    out = []
    for t, frame in _frames(video_path, sample_fps=sample_fps):
        b = blockiness_map(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean = float(gray.mean())
        flags = []
        if b > block_thresh:
            flags.append(f"blocky:{round(b, 2)}")
        if mean < 5:
            flags.append("near-black")
        if mean > 250:
            flags.append("near-white")
        if flags:
            out.append((t, flags))
    return out


def text_regions(frame):
    """
    Detect likely text overlay regions via MSER.
    Returns [x, y, w, h] boxes (in frame coords).
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mser = cv2.MSER_create(_delta=5, _max_variation=0.25)
    regions, _ = mser.detectRegions(gray)
    boxes = []
    h, w = gray.shape
    for r in regions:
        x, y, bw, bh = cv2.boundingRect(r)
        # text-like aspect + size filter
        if 10 < bw < w * 0.9 and 8 < bh < h * 0.3 and bw / max(bh, 1) > 1.5:
            boxes.append((x, y, bw, bh))
    # merge overlapping
    merged = []
    for b in boxes:
        placed = False
        for i, m in enumerate(merged):
            x0 = min(b[0], m[0]); y0 = min(b[1], m[1])
            x1 = max(b[0] + b[2], m[0] + m[2])
            y1 = max(b[1] + b[3], m[1] + m[3])
            if (x1 - x0) < (b[2] + m[2]) * 0.8 and (y1 - y0) < (b[3] + m[3]) * 1.5:
                merged[i] = (x0, y0, x1 - x0, y1 - y0)
                placed = True
                break
        if not placed:
            merged.append(b)
    return merged


def text_overlay_scan(video_path, sample_fps=0.5):
    """Return [(t, n_boxes)] where text overlays are detected."""
    out = []
    for t, frame in _frames(video_path, sample_fps=sample_fps, width=640):
        boxes = text_regions(frame)
        if boxes:
            out.append((t, len(boxes)))
    return out


def cartoon_filter_score(frame):
    """
    Signature of bilateral/cartoon "bullshit filter":
    - very low texture (high smoothing)
    - strong edges preserved (high edge density despite smoothing)
    - posterized color regions (few unique colors)
    Returns 0..1 (higher = more likely filtered).
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # texture: Laplacian variance (low = smoothed)
    tex = cv2.Laplacian(gray, cv2.CV_64F).var()
    # edges: Canny density
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(edges.mean() / 255)
    # posterization: unique colors in quantized image
    small = cv2.resize(frame, (80, 45))
    quant = (small // 64 * 64).reshape(-1, 3)
    uniq = len(np.unique(quant, axis=0))
    # cartoon filter: low texture + preserved edges + few colors
    s_tex = float(np.clip(1 - tex / 500, 0, 1))
    s_edge = float(np.clip(edge_density * 8, 0, 1))
    s_post = float(np.clip(1 - uniq / 2000, 0, 1))
    return round(0.4 * s_tex + 0.3 * s_edge + 0.3 * s_post, 3)


def filter_scan(video_path, sample_fps=1, thresh=0.6):
    """
    Return [(t_start, t_end)] where cartoon-filter signature is strong.
    Use to verify the bullshit filter is GONE from the episode.
    """
    out, start = [], None
    for t, frame in _frames(video_path, sample_fps=sample_fps):
        s = cartoon_filter_score(frame)
        if s >= thresh and start is None:
            start = t
        elif s < thresh and start is not None:
            out.append((round(start, 1), round(t, 1), "cartoon-filter?"))
            start = None
    if start is not None:
        out.append((round(start, 1), round(t, 1), "cartoon-filter?"))
    return out


def composition_at(video_path, t_seconds):
    """
    Composition check at a timestamp using face detection.
    Returns {faces, rule_of_thirds_ok, headroom_ok, centered}.
    """
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import video_qc
    import mediapipe as mp
    from mediapipe.tasks.python import vision as mp_vision
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t_seconds * fps))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return {"error": "no frame"}
    h, w = frame.shape[:2]
    lm = video_qc._landmarker(running_mode=mp_vision.RunningMode.IMAGE)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                      data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    res = lm.detect(mp_img)
    lm.close()
    if not res.face_landmarks:
        return {"faces": 0}
    # use nose tip (idx 1) as face center
    nose = res.face_landmarks[0][1]
    cx, cy = nose.x, nose.y  # normalized 0..1
    # rule of thirds: near 1/3 or 2/3 lines
    thirds_x = min(abs(cx - 1/3), abs(cx - 2/3), abs(cx - 0.5))
    thirds_ok = thirds_x < 0.12 or abs(cx - 0.5) < 0.08
    headroom_ok = 0.05 < cy < 0.45
    return {"faces": len(res.face_landmarks),
            "face_center": (round(cx, 2), round(cy, 2)),
            "rule_of_thirds_ok": bool(thirds_ok),
            "headroom_ok": bool(headroom_ok)}


if __name__ == "__main__":
    import sys, json
    video = sys.argv[1]
    if "--frozen" in sys.argv:
        print(json.dumps(frozen_regions(video), indent=1))
    elif "--grading" in sys.argv:
        print(json.dumps(grading_shifts(video), indent=1))
    elif "--glitch" in sys.argv:
        print(json.dumps(glitch_scan(video), indent=1))
    elif "--text" in sys.argv:
        print(json.dumps(text_overlay_scan(video), indent=1))
    elif "--filter" in sys.argv:
        print(json.dumps(filter_scan(video), indent=1))
    elif "--comp" in sys.argv:
        t = float(sys.argv[sys.argv.index("--comp") + 1])
        print(json.dumps(composition_at(video, t), indent=1))
    else:
        print(json.dumps({
            "frozen_regions": frozen_regions(video),
            "grading_shifts": grading_shifts(video),
            "filter_regions": filter_scan(video),
        }, indent=1))
