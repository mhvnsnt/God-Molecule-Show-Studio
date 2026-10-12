#!/usr/bin/env python3
"""Remove viggle.ai watermark via template matching + OpenCV inpainting.

Usage:
    python3 remove_watermark.py input.mp4 output_clean.mp4

Detects the viggle.ai watermark per-frame (it shifts position) via template
matching, then inpaints the region with OpenCV Telea. Output is H.264 yuv420p.
Requires: opencv-python, numpy, ffmpeg on PATH.


Two known watermark positions (it shifts):
- bottom-left area (~x=45-185, y=365-405)
- bottom-right area (~x=1085-1240, y=495-540)
Uses normalized cross-correlation template matching per frame, inpaints matches.
"""
import cv2
import numpy as np
import sys
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TMPL_LEFT = cv2.imread(os.path.join(SCRIPT_DIR, 'wm_template_left.png'), cv2.IMREAD_GRAYSCALE)
TMPL_RIGHT = cv2.imread(os.path.join(SCRIPT_DIR, 'wm_template_right.png'), cv2.IMREAD_GRAYSCALE)
THRESH = 0.65  # match confidence threshold

def find_watermark(frame_gray):
    """Return list of (x, y, w, h) boxes where watermark was found."""
    boxes = []
    for tmpl in (TMPL_LEFT, TMPL_RIGHT):
        th, tw = tmpl.shape
        res = cv2.matchTemplate(frame_gray, tmpl, cv2.TM_CCOEFF_NORMED)
        # Find all locations above threshold (non-max suppression via dilation)
        loc = np.where(res >= THRESH)
        pts = list(zip(loc[1], loc[0]))
        # Simple NMS: keep points that are far apart
        kept = []
        for x, y in sorted(pts, key=lambda p: res[p[1], p[0]], reverse=True):
            if all(abs(x - kx) > tw//2 or abs(y - ky) > th//2 for kx, ky in kept):
                kept.append((x, y))
                if len(kept) >= 3:
                    break
        for x, y in kept:
            boxes.append((x, y, tw, th))
    return boxes

def clean_chunk(src, dst):
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    tmp = dst + '.tmp.mp4'
    out = cv2.VideoWriter(tmp, fourcc, fps, (W, H))

    found_total = 0
    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes = find_watermark(gray)
        if boxes:
            found_total += 1
            mask = np.zeros((H, W), dtype=np.uint8)
            for x, y, bw, bh in boxes:
                pad = 4
                x1 = max(0, x - pad); y1 = max(0, y - pad)
                x2 = min(W, x + bw + pad); y2 = min(H, y + bh + pad)
                mask[y1:y2, x1:x2] = 255
            frame = cv2.inpaint(frame, mask, 4, cv2.INPAINT_TELEA)
        out.write(frame)
        i += 1
        if i % 240 == 0:
            print(f"  frame {i}/{nframes} watermark_found={found_total}", flush=True)

    cap.release()
    out.release()
    print(f"Done: {i} frames, watermark inpainted in {found_total}")
    r = subprocess.run(['ffmpeg', '-y', '-i', tmp, '-c:v', 'libx264', '-preset', 'fast',
                        '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                        '-an', dst], capture_output=True, text=True)
    if r.returncode != 0:
        print("ffmpeg failed:", r.stderr[-500:])
        return False
    os.remove(tmp)
    return True

if __name__ == '__main__':
    ok = clean_chunk(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
