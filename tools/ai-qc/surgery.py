#!/usr/bin/env python3
"""
surgery.py — The HANDS. Precise frame-level test edits.

All operations work on COPIES in experiments/. NEVER touches production.
Purpose: verify a fix works on a test clip before the owner approves it.

Every function takes src (production file, read-only) and writes to
experiments/<label>/test-<op>.mp4. Returns the output path.

Usage:
    surgery.py replace-audio src.mp4 121 132 new_line.mp3 --label cipher-c4
    surgery.py mute src.mp4 81 92 --label l3-cleanup
    surgery.py swap-video src.mp4 52 60 fixed_clip.mp4 --label s10-fix
    surgery.py gain src.mp4 200 210 -6 --label quiet-sfx
"""
import os
import subprocess
import sys

EXP_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "experiments")


def _exp_dir(label):
    d = os.path.join(EXP_BASE, label)
    os.makedirs(d, exist_ok=True)
    return d


def _run(cmd):
    subprocess.run(cmd, check=True)


def replace_audio(src, t0, t1, new_audio, label, out_name=None):
    """Mute t0-t1, place new_audio at t0. For dialogue fixes."""
    d = _exp_dir(label)
    out = os.path.join(d, out_name or "test-replace-audio.mp4")
    ms = int(t0 * 1000)
    filt = (f"[0:a]volume='if(between(t,{t0},{t1}),0,1)':eval=frame[muted];"
            f"[1:a]adelay={ms}|{ms},apad[na];"
            f"[muted][na]amix=inputs=2:duration=first:normalize=0[aout]")
    _run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", new_audio,
          "-filter_complex", filt, "-map", "0:v", "-map", "[aout]",
          "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
    return out


def mute(src, t0, t1, label, out_name=None):
    """Silence a range. For removing doubles/overlaps."""
    d = _exp_dir(label)
    out = os.path.join(d, out_name or "test-mute.mp4")
    filt = (f"[0:a]volume='if(between(t,{t0},{t1}),0,1)':eval=frame[aout]")
    _run(["ffmpeg", "-y", "-v", "error", "-i", src,
          "-af", filt, "-map", "0:v", "-map", "[aout]",
          "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
    return out


def gain(src, t0, t1, db, label, out_name=None):
    """Apply gain (dB) to a range. For volume fixes."""
    d = _exp_dir(label)
    out = os.path.join(d, out_name or "test-gain.mp4")
    filt = (f"[0:a]volume='if(between(t,{t0},{t1}),{db}dB,0dB)':eval=frame[aout]")
    _run(["ffmpeg", "-y", "-v", "error", "-i", src,
          "-af", filt, "-map", "0:v", "-map", "[aout]",
          "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
    return out


def swap_video(src, t0, t1, new_video, label, out_name=None):
    """
    Replace video t0-t1 with new_video (keeps original audio).
    For visual fixes. new_video is trimmed/scaled to fit.
    """
    d = _exp_dir(label)
    out = os.path.join(d, out_name or "test-swap-video.mp4")
    dur = t1 - t0
    # split src into 3 parts, middle gets new video + src audio
    p1 = os.path.join(d, "_p1.mp4")
    p3 = os.path.join(d, "_p3.mp4")
    mid = os.path.join(d, "_mid.mp4")
    _run(["ffmpeg", "-y", "-v", "error", "-i", src,
          "-t", str(t0), "-c", "copy", p1])
    _run(["ffmpeg", "-y", "-v", "error", "-ss", str(t1), "-i", src,
          "-c", "copy", p3])
    # new video trimmed to dur, with src's audio for that window
    _run(["ffmpeg", "-y", "-v", "error",
          "-i", new_video, "-ss", str(t0), "-t", str(dur), "-i", src,
          "-filter_complex",
          f"[0:v]trim=duration={dur},setpts=PTS-STARTPTS,"
          f"scale=1280:720:force_original_aspect_ratio=decrease,"
          f"pad=1280:720:(ow-iw)/2:(oh-ih)/2[v];"
          f"[1:a]atrim=start={t0}:duration={dur},asetpts=PTS-STARTPTS[a]",
          "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20",
          "-c:a", "aac", mid])
    # concat
    lst = os.path.join(d, "_list.txt")
    with open(lst, "w") as f:
        f.write(f"file '{p1}'\nfile '{mid}'\nfile '{p3}'\n")
    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
          "-i", lst, "-c", "copy", out])
    for p in (p1, p3, mid, lst):
        if os.path.exists(p):
            os.remove(p)
    return out


def clip(src, t0, t1, label, out_name=None):
    """Extract a test clip t0-t1 for review."""
    d = _exp_dir(label)
    out = os.path.join(d, out_name or f"test-clip-{t0}-{t1}.mp4")
    _run(["ffmpeg", "-y", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0),
          "-i", src, "-c:v", "libx264", "-crf", "20", "-c:a", "aac", out])
    return out


if __name__ == "__main__":
    # CLI: surgery.py <op> <src> <args...> --label <label>
    args = sys.argv[1:]
    label = "misc"
    if "--label" in args:
        li = args.index("--label")
        label = args[li + 1]
        args = args[:li]
    op, src = args[0], args[1]
    if op == "replace-audio":
        t0, t1, na = float(args[2]), float(args[3]), args[4]
        print(replace_audio(src, t0, t1, na, label))
    elif op == "mute":
        t0, t1 = float(args[2]), float(args[3])
        print(mute(src, t0, t1, label))
    elif op == "gain":
        t0, t1, db = float(args[2]), float(args[3]), args[4]
        print(gain(src, t0, t1, db, label))
    elif op == "swap-video":
        t0, t1, nv = float(args[2]), float(args[3]), args[4]
        print(swap_video(src, t0, t1, nv, label))
    elif op == "clip":
        t0, t1 = float(args[2]), float(args[3])
        print(clip(src, t0, t1, label))
    else:
        print(__doc__)
