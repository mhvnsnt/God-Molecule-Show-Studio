#!/usr/bin/env python3
"""Seamless loop toolkit (PIL + ffmpeg, purpose-built).
Subcommands:
  bob        -- from ONE hold frame: sinusoidal vertical bob + subtle scale
                "breathe" -> N-frame seamless loop (mascot idles, card holds)
  pingpong   -- from frames dir or clip: forward+reverse -> seamless loop
  crossfade  -- from clip: crossfade tail into head over K frames -> seamless loop

Usage: run_loop.py bob --input hold.png --output bob.mp4 [--frames 48] [--fps 24]
                        [--bob-px 10] [--breathe 0.02]
       run_loop.py pingpong --input clip.mp4 --output loop.mp4 [--fps 24]
       run_loop.py crossfade --input clip.mp4 --output loop.mp4 [--blend 12] [--fps 24]
Serves: animation holds for the commercial/EP01 — mascot idles, end-card holds.
"""
import argparse, sys, os, subprocess, math, glob
from PIL import Image

def bob(input_path, output, frames=48, fps=24, bob_px=10, breathe=0.02):
    base = Image.open(input_path).convert("RGBA")
    w, h = base.size
    tmpd = "/tmp/loopkit_bob"
    os.makedirs(tmpd, exist_ok=True)
    for i in range(frames):
        t = 2 * math.pi * i / frames
        dy = int(round(bob_px * math.sin(t)))
        sc = 1.0 + breathe * math.sin(t + math.pi / 2)
        nw, nh = int(w * sc), int(h * sc)
        fr = base.resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.alpha_composite(fr, ((w - nw) // 2, (h - nh) // 2 + dy))
        canvas.save(os.path.join(tmpd, f"f{i:04d}.png"))
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps),
                        "-i", os.path.join(tmpd, "f%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", output])
    # seamless check: first vs last frame identical phase (sin(0)==sin(2pi))
    print(f"bob: wrote {output} ({frames}f @ {fps}fps, bob={bob_px}px, breathe={breathe})")
    return r.returncode

def extract_frames(src, tmpd, fps=None):
    os.makedirs(tmpd, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src]
    if fps: cmd += ["-vf", f"fps={fps}"]
    cmd += [os.path.join(tmpd, "f%04d.png")]
    subprocess.run(cmd, check=True)
    return sorted(glob.glob(os.path.join(tmpd, "f*.png")))

def frames_to_mp4(tmpd, output, fps):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps),
                        "-i", os.path.join(tmpd, "f%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", output])
    return r.returncode

def pingpong(src, output, fps=24):
    tmpd = "/tmp/loopkit_pp"
    files = extract_frames(src, tmpd)
    n = len(files)
    seq = files + files[-2::-1]  # forward then reverse (no duplicate endpoints)
    outd = "/tmp/loopkit_pp_out"
    os.makedirs(outd, exist_ok=True)
    for i, f in enumerate(seq):
        Image.open(f).save(os.path.join(outd, f"f{i:04d}.png"))
    rc = frames_to_mp4(outd, output, fps)
    print(f"pingpong: {n}f -> {len(seq)}f loop -> {output}")
    return rc

def crossfade(src, output, fps=24, blend=12):
    tmpd = "/tmp/loopkit_cf"
    files = extract_frames(src, tmpd, fps=fps)
    n = len(files)
    if blend >= n // 2: blend = max(2, n // 4)
    head = [Image.open(f).convert("RGBA") for f in files[:blend]]
    tail = [Image.open(f).convert("RGBA") for f in files[-blend:]]
    body = [Image.open(f).convert("RGBA") for f in files[blend:-blend]]
    outd = "/tmp/loopkit_cf_out"
    os.makedirs(outd, exist_ok=True)
    seq = []
    seq += body
    for i in range(blend):
        a = i / blend
        seq.append(Image.blend(tail[i], head[i], a))
    for i, fr in enumerate(seq):
        fr.save(os.path.join(outd, f"f{i:04d}.png"))
    rc = frames_to_mp4(outd, output, fps)
    print(f"crossfade: {n}f, blend={blend} -> {len(seq)}f seamless loop -> {output}")
    return rc

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bob")
    b.add_argument("--input", required=True); b.add_argument("--output", required=True)
    b.add_argument("--frames", type=int, default=48); b.add_argument("--fps", type=int, default=24)
    b.add_argument("--bob-px", type=int, default=10); b.add_argument("--breathe", type=float, default=0.02)
    p = sub.add_parser("pingpong")
    p.add_argument("--input", required=True); p.add_argument("--output", required=True)
    p.add_argument("--fps", type=int, default=24)
    c = sub.add_parser("crossfade")
    c.add_argument("--input", required=True); c.add_argument("--output", required=True)
    c.add_argument("--fps", type=int, default=24); c.add_argument("--blend", type=int, default=12)
    a = ap.parse_args()
    if a.cmd == "bob":
        sys.exit(bob(a.input, a.output, a.frames, a.fps, a.bob_px, a.breathe))
    elif a.cmd == "pingpong":
        sys.exit(pingpong(a.input, a.output, a.fps))
    elif a.cmd == "crossfade":
        sys.exit(crossfade(a.input, a.output, a.fps, a.blend))

if __name__ == "__main__":
    main()
