#!/usr/bin/env python3
"""
Pose extraction for Wizard Gang EP02 repair pipeline.
Uses MediaPipe Tasks PoseLandmarker to extract skeletons from video frames,
outputs ControlNet-style pose maps (black bg, colored skeleton).

Usage:
    venv/bin/python extract_pose.py --input clip.mp4 --out-dir ./pose-out/

Outputs:
    pose-out/skeleton.mp4  - ControlNet-ready pose video (black bg, skeleton overlay)
    pose-out/poses.json    - Per-frame landmark data (normalized coords)
    pose-out/preview.png   - Side-by-side: original frame vs skeleton

First run downloads the pose_landmarker_heavy.task model (~150MB) from Google.
"""
import argparse
import json
import subprocess
import urllib.request
from pathlib import Path

import cv2
import numpy as np

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"

# MediaPipe pose connections (subset of the 33 landmarks, major bones)
POSE_CONNECTIONS = [
    # Torso
    (11, 12), (11, 23), (12, 24), (23, 24),
    # Arms L
    (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    # Arms R
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    # Legs L
    (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
    # Legs R
    (24, 26), (26, 28), (28, 30), (28, 32), (30, 32),
    # Head
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
]


def ensure_model(model_path):
    if not model_path.exists():
        print(f"Downloading pose model (~150MB)...")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, str(model_path))
        print(f"Model saved: {model_path}")


def draw_skeleton(landmarks, h, w):
    """Draw skeleton on black background, ControlNet pose-map style."""
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    vis = [getattr(lm, 'visibility', 1.0) for lm in landmarks]

    for a, b in POSE_CONNECTIONS:
        if a < len(pts) and b < len(pts) and vis[a] > 0.5 and vis[b] > 0.5:
            cv2.line(canvas, pts[a], pts[b], (255, 255, 255), 4)

    for idx, pt in enumerate(pts):
        if vis[idx] > 0.5:
            if idx < 11:
                color = (0, 255, 255)    # head - yellow
            elif idx in (13, 14, 15, 16, 17, 18, 19, 20, 21, 22):
                color = (0, 255, 0)      # arms/hands - green
            elif idx in (25, 26, 27, 28, 29, 30, 31, 32):
                color = (255, 0, 0)      # legs/feet - blue
            else:
                color = (0, 0, 255)      # torso - red
            cv2.circle(canvas, pt, 6, color, -1)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-frames", type=int, default=0)
    args = ap.parse_args()

    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    import mediapipe as mp
    MPImage = mp.Image
    MPImageFormat = mp.ImageFormat

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model_path = Path(__file__).parent / "models" / "pose_landmarker_heavy.task"
    ensure_model(model_path)

    base_opts = mp_python.BaseOptions(model_asset_path=str(model_path))
    options = mp_vision.PoseLandmarkerOptions(
        base_options=base_opts,
        running_mode=mp_vision.RunningMode.VIDEO,
        num_poses=5,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    landmarker = mp_vision.PoseLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(args.input)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Input: {args.input} ({W}x{H} @ {fps:.1f}fps, {total} frames)")

    pose_data = []
    skeleton_frames = []
    preview_saved = False
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if args.max_frames and frame_idx >= args.max_frames:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = MPImage(image_format=MPImageFormat.SRGB, data=rgb)
        ts_ms = int(frame_idx / fps * 1000)
        result = landmarker.detect_for_video(mp_image, ts_ms)

        if result.pose_landmarks:
            # Draw ALL detected people on the same canvas
            skeleton = np.zeros((H, W, 3), dtype=np.uint8)
            all_landmarks = []
            for person_lm in result.pose_landmarks:
                person_skel = draw_skeleton(person_lm, H, W)
                # Composite: take max to overlay multiple skeletons
                skeleton = np.maximum(skeleton, person_skel)
                all_landmarks.append([
                    {"x": round(p.x, 4), "y": round(p.y, 4), "z": round(p.z, 4)}
                    for p in person_lm
                ])
            pose_data.append({
                "frame": frame_idx,
                "num_poses": len(result.pose_landmarks),
                "people": all_landmarks,
            })
            if not preview_saved:
                preview = np.hstack([frame, skeleton])
                cv2.imwrite(str(out_dir / "preview.png"), preview)
                preview_saved = True
                print(f"Preview saved (frame {frame_idx})")
        else:
            skeleton = np.zeros((H, W, 3), dtype=np.uint8)
            pose_data.append({"frame": frame_idx, "num_poses": 0, "landmarks": None})

        skeleton_frames.append(skeleton)
        frame_idx += 1
        if frame_idx % 30 == 0:
            print(f"  {frame_idx}/{total}...")

    cap.release()
    landmarker.close()
    detected = sum(1 for p in pose_data if p.get("people"))
    print(f"Poses detected: {detected}/{frame_idx} frames")

    with open(out_dir / "poses.json", "w") as f:
        json.dump({"source": args.input, "fps": fps, "width": W,
                   "height": H, "frames": pose_data}, f)
    print(f"Pose JSON: {out_dir / 'poses.json'}")

    skel_path = out_dir / "skeleton.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(int(fps)), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(skel_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for sf in skeleton_frames:
        proc.stdin.write(cv2.cvtColor(sf, cv2.COLOR_BGR2RGB).tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"Skeleton video: {skel_path}")


if __name__ == "__main__":
    main()
