#!/usr/bin/env python3
"""
features.py — Shared per-frame / per-window feature extraction for sensorium.

Visual features (OpenCV + numpy, no torch):
  sharpness, contrast, colorfulness, brightness, saturation,
  edge_density, flatness (2D-cartoon proxy), palette_size,
  gradient_smoothness (3D-render proxy), texture_energy,
  symmetry, thirds_balance, noise_est, blockiness

Audio features (librosa, no torch):
  rms, spectral_centroid, spectral_rolloff, zcr, mfcc13 means,
  spectral_contrast mean, energy_vad_ratio

All functions are pure numpy/OpenCV. Runs on CPU in seconds.
Part of sensorium (~/workspace/tools/brain/sensorium/).
Reuses the ai-qc venv: ~/workspace/tools/ai-qc/venv/bin/python
"""
import cv2
import numpy as np


# ---------------------------------------------------------------- visual ---

def visual_features_bgr(frame_bgr):
    """
    Compute the visual feature dict for one BGR frame (any size; internally
    downscaled to width 360 for speed). All values are floats.
    """
    h, w = frame_bgr.shape[:2]
    scale = 360.0 / max(1, w)
    small = cv2.resize(frame_bgr, (max(1, int(w * scale)),
                                   max(1, int(h * scale))),
                       interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)
    lab = cv2.cvtColor(small, cv2.COLOR_BGR2LAB).astype(np.float32)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV).astype(np.float32)
    L = lab[:, :, 0]          # 0..100
    S = hsv[:, :, 1]          # 0..255

    # sharpness: variance of Laplacian
    sharpness = float(cv2.Laplacian(gray, cv2.CV_32F).var())
    # contrast: RMS contrast of L
    contrast = float(gray.std())
    # brightness
    brightness = float(L.mean())
    # saturation
    saturation = float(S.mean())

    # colorfulness (Hasler & Susstrunk)
    b, g, r = (small[:, :, i].astype(np.float32) for i in range(3))
    rg = r - g
    yb = 0.5 * (r + g) - b
    colorfulness = float(np.sqrt(rg.std() ** 2 + yb.std() ** 2)
                         + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))

    # edge density (Canny)
    edges = cv2.Canny((gray).astype(np.uint8), 80, 160)
    edge_density = float((edges > 0).mean())

    # flatness: fraction of pixels in locally-flat regions
    # (2D cartoon = large flat color fields; 3D render = gradients everywhere)
    local_var = cv2.blur(gray ** 2, (9, 9)) - cv2.blur(gray, (9, 9)) ** 2
    flatness = float((local_var < 25.0).mean())

    # palette size: dominant quantized colors (5-bit per channel)
    q = (small // 8).reshape(-1, 3)
    # use a strided sample for speed
    qs = q[::37]
    palette_size = float(len(np.unique(qs.reshape(-1, 3), axis=0)))

    # gradient smoothness: mean gradient magnitude OUTSIDE strong edges
    # (3D subsurface scattering / soft GI = smooth gradients in non-edge areas)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    gmag = np.sqrt(gx ** 2 + gy ** 2)
    nonedge = gmag < 12.0
    gradient_smoothness = float(gmag[nonedge].mean()) if nonedge.any() else 0.0

    # texture energy: high-frequency energy (pores, fabric weave, film grain)
    blur = cv2.GaussianBlur(gray, (0, 0), 2.0)
    texture_energy = float(np.abs(gray - blur).mean())

    # symmetry: horizontal flip correlation
    fh, fw = gray.shape
    left = gray[:, :fw // 2]
    right = np.fliplr(gray[:, fw - fw // 2:])
    mw = min(left.shape[1], right.shape[1])
    lz, rz = left[:, :mw].ravel(), right[:, :mw].ravel()
    if lz.std() > 1e-6 and rz.std() > 1e-6:
        symmetry = float(np.corrcoef(lz, rz)[0, 1])
    else:
        symmetry = 0.0

    # thirds balance: distance of edge-mass centroid from nearest third-point
    ys, xs = np.nonzero(edges)
    if len(xs):
        cx, cy = xs.mean() / fw, ys.mean() / fh
        thirds = np.array([1 / 3, 2 / 3])
        thirds_balance = float(min(
            np.hypot(cx - tx, cy - ty)
            for tx in thirds for ty in thirds))
    else:
        thirds_balance = 0.5

    # noise estimate: median abs deviation of Laplacian high-pass
    lap = cv2.Laplacian(gray, cv2.CV_32F)
    noise_est = float(np.median(np.abs(lap)) / 0.6745)

    # blockiness: mean abs diff across 8x8 block boundaries (compression tell)
    bh, bw = (gray.shape[0] // 8) * 8, (gray.shape[1] // 8) * 8
    g8 = gray[:bh, :bw]
    vdiff = np.abs(np.diff(g8[7::8, :], axis=0)).mean()
    hdiff = np.abs(np.diff(g8[:, 7::8], axis=1)).mean()
    inner_v = np.abs(np.diff(g8, axis=0)).mean()
    inner_h = np.abs(np.diff(g8, axis=1)).mean()
    blockiness = float(max(0.0, (vdiff - inner_v) + (hdiff - inner_h)))

    return {
        "sharpness": sharpness,
        "contrast": contrast,
        "brightness": brightness,
        "saturation": saturation,
        "colorfulness": colorfulness,
        "edge_density": edge_density,
        "flatness": flatness,
        "palette_size": palette_size,
        "gradient_smoothness": gradient_smoothness,
        "texture_energy": texture_energy,
        "symmetry": symmetry,
        "thirds_balance": thirds_balance,
        "noise_est": noise_est,
        "blockiness": blockiness,
    }


VISUAL_KEYS = ["sharpness", "contrast", "brightness", "saturation",
               "colorfulness", "edge_density", "flatness", "palette_size",
               "gradient_smoothness", "texture_energy", "symmetry",
               "thirds_balance", "noise_est", "blockiness"]


def visual_vector(frame_bgr):
    d = visual_features_bgr(frame_bgr)
    return np.array([d[k] for k in VISUAL_KEYS], dtype=np.float64)


# ----------------------------------------------------------------- audio ---

def audio_features_window(y, sr=16000):
    """
    Feature dict for one mono audio window (numpy array). librosa only.
    """
    import librosa
    y = np.asarray(y, dtype=np.float32)
    if y.size < sr // 4:
        y = np.pad(y, (0, max(0, sr // 4 - y.size)))
    rms = float(np.sqrt(np.mean(y ** 2)) + 1e-9)
    zcr = float(np.mean(np.abs(np.diff(np.sign(y)))) / 2.0)
    spec = np.abs(np.fft.rfft(y * np.hanning(len(y)))) + 1e-9
    freqs = np.fft.rfftfreq(len(y), 1.0 / sr)
    centroid = float(np.sum(freqs * spec) / np.sum(spec))
    cumsum = np.cumsum(spec)
    rolloff = float(freqs[np.searchsorted(cumsum, 0.85 * cumsum[-1])])
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = mfcc.mean(axis=1)
    s_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    contrast_mean = float(s_contrast.mean())
    # pitch via yin (faster than pyin)
    try:
        f0 = librosa.yin(y, fmin=50, fmax=600, sr=sr)
        f0v = f0[(f0 > 55) & (f0 < 590)]
        pitch_med = float(np.median(f0v)) if len(f0v) else 0.0
        pitch_std = float(f0v.std()) if len(f0v) else 0.0
    except Exception:
        pitch_med, pitch_std = 0.0, 0.0
    d = {
        "rms": rms,
        "log_rms": float(np.log10(rms + 1e-9)),
        "zcr": zcr,
        "centroid": centroid,
        "rolloff": rolloff,
        "contrast_mean": contrast_mean,
        "pitch_med": pitch_med,
        "pitch_std": pitch_std,
    }
    for i, v in enumerate(mfcc_mean):
        d[f"mfcc{i:02d}"] = float(v)
    return d


AUDIO_KEYS = (["rms", "log_rms", "zcr", "centroid", "rolloff",
               "contrast_mean", "pitch_med", "pitch_std"]
              + [f"mfcc{i:02d}" for i in range(13)])


def audio_vector(y, sr=16000):
    d = audio_features_window(y, sr=sr)
    return np.array([d[k] for k in AUDIO_KEYS], dtype=np.float64)


# --------------------------------------------------------------- sampling ---

def sample_video_frames(video_path, sample_fps=2.0, width=480, t0=0.0,
                        t1=None):
    """
    Yield (t_seconds, frame_bgr) sampled at sample_fps between t0 and t1.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {video_path}")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(src_fps, 1e-6)
    t1 = duration if t1 is None else min(t1, duration)
    step = max(1, int(round(src_fps / sample_fps)))
    start_idx = int(t0 * src_fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_idx)
    idx = start_idx
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t = idx / src_fps
        if t > t1:
            break
        if (idx - start_idx) % step == 0:
            h, w = frame.shape[:2]
            s = width / w
            yield round(t, 2), cv2.resize(frame, (width, int(h * s)),
                                         interpolation=cv2.INTER_AREA)
        idx += 1
    cap.release()


def extract_audio_mono(video_path, sr=16000):
    """Extract mono audio from video to a temp wav; return (y, sr, path).
    Raises RuntimeError with a clear message if the file has no audio
    stream (several EP02 cuts are video-only by design)."""
    import subprocess
    import tempfile
    import os
    # fail fast with a clear message on video-only files
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=codec_type", "-of", "csv=p=0",
         video_path], capture_output=True, text=True)
    if "audio" not in probe.stdout:
        raise RuntimeError(f"{video_path} has no audio stream "
                           f"(video-only cut)")
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video_path,
                    "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", path],
                   check=True)
    from scipy.io import wavfile
    _sr, data = wavfile.read(path)
    y = data.astype(np.float32) / 32768.0
    return y, _sr, path
