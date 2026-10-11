#!/usr/bin/env python3
"""
ocr.py — Text detection and OCR in video frames.

- Frame text extraction via tesseract (system binary, no pip needed)
- Subtitle region scan: finds burned-in captions / lower-thirds
- Watermark/logo heuristic: persistent small text in corners across time
- Uses visual_deep.text_regions for candidate boxes, then OCRs them

tesseract must be installed (it is: /usr/bin/tesseract).
"""
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import visual_deep


def ocr_image(img_bgr, psm=6):
    """Run tesseract on a BGR image. Returns (text, confidence)."""
    # upscale small regions, grayscale, threshold
    h, w = img_bgr.shape[:2]
    scale = max(1, 300 // max(h, 1))
    big = cv2.resize(img_bgr, (w * scale, h * scale),
                     interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    tmp = "/tmp/aiqc_ocr.png"
    cv2.imwrite(tmp, th)
    try:
        r = subprocess.run(
            ["tesseract", tmp, "stdout", "--psm", str(psm), "-c",
             "tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz0123456789.,!?'-#: ",
             "2>/dev/null"],
            capture_output=True, text=True, timeout=15)
        text = r.stdout.strip()
        # confidence from tsv output
        r2 = subprocess.run(
            ["tesseract", tmp, "stdout", "--psm", str(psm),
             "tsv", "2>/dev/null"],
            capture_output=True, text=True, timeout=15)
        confs = []
        for line in r2.stdout.splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) > 10 and parts[10].strip().lstrip("-").isdigit():
                confs.append(float(parts[10]))
        conf = float(np.mean(confs)) if confs else 0.0
        return text, round(conf, 1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "", 0.0


def frame_text(video_path, t_seconds, min_conf=30):
    """
    OCR all text-like regions in a frame.
    Returns [{"box": (x,y,w,h), "text": "...", "conf": x}].
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t_seconds * fps))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return []
    out = []
    for (x, y, w, h) in visual_deep.text_regions(frame):
        pad = 4
        crop = frame[max(0, y-pad):y+h+pad, max(0, x-pad):x+w+pad]
        if crop.size == 0:
            continue
        text, conf = ocr_image(crop)
        if text and conf >= min_conf and len(text.strip()) >= 2:
            out.append({"box": (x, y, w, h), "text": text, "conf": conf})
    return out


def subtitle_scan(video_path, sample_fps=0.5, min_conf=40):
    """
    Scan for burned-in subtitles/captions (typically bottom third).
    Returns [(t, text)].
    """
    out = []
    cap = cv2.VideoCapture(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, int(round(src_fps / sample_fps)))
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            t = round(idx / src_fps, 1)
            h, w = frame.shape[:2]
            # bottom third only (subtitle zone)
            zone = frame[int(h * 0.65):, :]
            for (x, y, bw, bh) in visual_deep.text_regions(zone):
                crop = zone[max(0, y-4):y+bh+4, max(0, x-4):x+bw+4]
                if crop.size == 0:
                    continue
                text, conf = ocr_image(crop, psm=7)
                if text and conf >= min_conf and len(text.strip()) >= 3:
                    out.append((t, text.strip()))
        idx += 1
    cap.release()
    # dedupe consecutive duplicates
    dedup = []
    for t, txt in out:
        if not dedup or dedup[-1][1] != txt:
            dedup.append((t, txt))
    return dedup


def watermark_scan(video_path, sample_fps=0.25, corner_frac=0.2):
    """
    Heuristic watermark/logo detection: text-like regions that persist
    in frame corners across many samples.
    Returns [{"corner": "tl|tr|bl|br", "hits": n, "sample_text": "..."}].
    """
    from collections import Counter
    cap = cv2.VideoCapture(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, int(round(src_fps / sample_fps)))
    idx, corner_hits = 0, Counter()
    corner_text = {}
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            h, w = frame.shape[:2]
            cw, ch = int(w * corner_frac), int(h * corner_frac)
            corners = {"tl": frame[0:ch, 0:cw],
                       "tr": frame[0:ch, w-cw:w],
                       "bl": frame[h-ch:h, 0:cw],
                       "br": frame[h-ch:h, w-cw:w]}
            for name, c in corners.items():
                for (x, y, bw, bh) in visual_deep.text_regions(c):
                    crop = c[max(0, y-2):y+bh+2, max(0, x-2):x+bw+2]
                    if crop.size == 0:
                        continue
                    text, conf = ocr_image(crop, psm=8)
                    if text and conf >= 50:
                        corner_hits[name] += 1
                        corner_text[name] = text.strip()
        idx += 1
    cap.release()
    total = idx // step
    return [{"corner": k, "hits": v,
             "persistence": round(v / max(total, 1), 2),
             "sample_text": corner_text.get(k, "")}
            for k, v in corner_hits.most_common()
            if v / max(total, 1) > 0.3]


if __name__ == "__main__":
    import json
    video = sys.argv[1]
    if "--frame" in sys.argv:
        t = float(sys.argv[sys.argv.index("--frame") + 1])
        print(json.dumps(frame_text(video, t), indent=1))
    elif "--subs" in sys.argv:
        print(json.dumps(subtitle_scan(video), indent=1))
    elif "--watermark" in sys.argv:
        print(json.dumps(watermark_scan(video), indent=1))
    else:
        print(json.dumps({
            "subtitles": subtitle_scan(video),
            "watermarks": watermark_scan(video),
        }, indent=1))
