#!/usr/bin/env python3
"""
EbSynth video style-transfer wrapper for Wizard Gang EP02 repair pipeline.

Takes an input video + a hand-painted (or cartoon-filtered) keyframe,
propagates the keyframe style across the whole video using EbSynth's
patch-based texture synthesis, and reassembles the output video.

Usage:
    python run_ebsynth.py --input input.mp4 --keyframe styled.png \
        --keyframe-index 0 --output output.mp4 [--fps 10] [--scale 640:360]

    python run_ebsynth.py --input clip.mp4 --keyframe key.png --output fixed.mp4

How it works:
  1. Extract frames from input video (ffmpeg)
  2. For each frame: run `ebsynth -style <keyframe> -guide <src_keyframe> <target> -output <out>`
     (the guide pair tells EbSynth how pixels moved between keyframe and target)
  3. Reassemble output frames into video (ffmpeg)

For long clips, add multiple keyframes with --keyframes key1.png@0,key2.png@150
to anchor different sections (reduces drift).

Requires:
  - ebsynth binary at ~/workspace/video-fix-tools/ebsynth/ebsynth
    (built from public-domain jamriska/ebsynth; see README.md)
  - ffmpeg on PATH
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EBSYNTH_BIN = Path.home() / "workspace/video-fix-tools/ebsynth/ebsynth"
if not EBSYNTH_BIN.exists():
    # fallback: binary inside src/bin
    alt = Path.home() / "workspace/video-fix-tools/ebsynth/src/bin/ebsynth"
    if alt.exists():
        EBSYNTH_BIN = alt


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def main():
    ap = argparse.ArgumentParser(description="EbSynth video style propagation wrapper")
    ap.add_argument("--input", required=True, help="Input video path")
    ap.add_argument("--keyframe", required=True,
                    help="Styled keyframe image (same content as source frame at keyframe-index, painted in target style)")
    ap.add_argument("--keyframe-index", type=int, default=0,
                    help="0-based index of the source frame the keyframe was painted from")
    ap.add_argument("--output", required=True, help="Output video path")
    ap.add_argument("--fps", type=int, default=10,
                    help="Working fps for EbSynth (lower = faster; final video keeps input fps via re-encode)")
    ap.add_argument("--scale", default="640:360",
                    help="Working resolution W:H (lower = faster)")
    ap.add_argument("--keyframes", default="",
                    help="Extra keyframes as path@index,path@index (e.g. k2.png@150). Anchors later sections.")
    ap.add_argument("--ebsynth-args", default="",
                    help="Extra args passed to ebsynth binary (e.g. '-patchsize 7')")
    ap.add_argument("--keep-frames", action="store_true",
                    help="Keep extracted/styled frames in output dir alongside video")
    args = ap.parse_args()

    if not EBSYNTH_BIN.exists():
        sys.exit(f"ERROR: ebsynth binary not found at {EBSYNTH_BIN}")

    workdir = Path(tempfile.mkdtemp(prefix="ebsynth-"))
    frames_dir = workdir / "frames"
    out_dir = workdir / "styled"
    frames_dir.mkdir()
    out_dir.mkdir()
    print(f"Working in {workdir}")

    # 1. Extract frames
    print("Extracting frames...")
    run(["ffmpeg", "-y", "-v", "error", "-i", args.input,
         "-vf", f"fps={args.fps},scale={args.scale}",
         str(frames_dir / "frame-%04d.png")])
    frames = sorted(frames_dir.glob("frame-*.png"))
    n = len(frames)
    print(f"Extracted {n} frames")

    # 2. Build keyframe list: [(index, styled_path, source_frame_path)]
    keyframes = [(args.keyframe_index, Path(args.keyframe),
                  frames[args.keyframe_index])]
    for spec in args.keyframes.split(","):
        if not spec.strip():
            continue
        path, idx = spec.rsplit("@", 1)
        idx = int(idx)
        keyframes.append((idx, Path(path), frames[idx]))
    keyframes.sort()
    print(f"Using {len(keyframes)} keyframe(s): {[k[0] for k in keyframes]}")

    # 3. Propagate: each target frame uses the nearest keyframe as style source
    extra = args.ebsynth_args.split() if args.ebsynth_args else []
    for i, tgt in enumerate(frames):
        # nearest keyframe
        kf_idx, kf_styled, kf_source = min(keyframes, key=lambda k: abs(k[0] - i))
        out_path = out_dir / f"styled-{i:04d}.png"
        cmd = [str(EBSYNTH_BIN),
               "-style", str(kf_styled),
               "-guide", str(kf_source), str(tgt),
               "-output", str(out_path)] + extra
        subprocess.run(cmd, check=True, capture_output=True)
        if (i + 1) % 10 == 0 or i == n - 1:
            print(f"  styled {i + 1}/{n} frames (keyframe @{kf_idx})")

    # 4. Reassemble
    print("Reassembling video...")
    run(["ffmpeg", "-y", "-v", "error",
         "-framerate", str(args.fps),
         "-i", str(out_dir / "styled-%04d.png"),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
         "-preset", "medium", args.output])
    print(f"Done: {args.output}")

    if args.keep_frames:
        keep = Path(args.output).parent / (Path(args.output).stem + "-frames")
        shutil.copytree(out_dir, keep)
        print(f"Frames kept at {keep}")
    else:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
