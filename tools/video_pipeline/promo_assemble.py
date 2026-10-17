#!/usr/bin/env python3
"""promo_assemble.py — scripted 50-second promo assembler (MoviePy 2.x + ffmpeg).

One command:
    python3 promo_assemble.py shotlist.json -o promo.mp4

Shot-list schema (JSON):
{
  "size": [1920, 1080], "fps": 30,
  "crossfade": 0.6,
  "shots": [
     {"src": "clip.mp4", "start": 12.0, "dur": 8.0},        # video segment
     {"title": "CONCRETE DRAGON", "sub": "coming soon",       # title card
      "dur": 3.0, "bg": [10, 10, 14]}
  ],
  "captions": [
     {"t": 2.0, "dur": 3.0, "text": "The block is yours."}
  ],
  "audio": {
     "voiceover": "vo_track.wav",        # rendered by voiceover.py
     "music": "theme.wav", "music_gain": 0.25,
     "sfx": [{"file": "hit.wav", "t": 9.5, "gain": 0.8}]
  }
}

Text is rendered with PIL (no ImageMagick dependency).
License: tooling for money-machine-hq. Dependencies used: moviepy (MIT),
ffmpeg (LGPL/GPL per build), Pillow (HPND), numpy (BSD). Prototype freely;
audit before ship.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy import (VideoFileClip, ImageClip, CompositeVideoClip,
                     AudioFileClip, CompositeAudioClip, concatenate_videoclips)
from moviepy import vfx
from moviepy.audio import fx as afx


def _font(size):
    # DejaVu ships with most distros; fall back to PIL default
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def text_card(size, title, sub="", bg=(10, 10, 14), fg=(245, 245, 245),
              accent=(255, 200, 60)):
    w, h = size
    img = Image.new("RGB", (w, h), tuple(bg))
    d = ImageDraw.Draw(img)
    f_big, f_sub = _font(120), _font(52)
    # center title (may be multi-line)
    lines = title.split("\n")
    ys = h // 2 - (len(lines) * 130) // 2
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=f_big)
        tw = bb[2] - bb[0]
        d.text(((w - tw) / 2, ys), ln, font=f_big, fill=fg)
        ys += 130
    if sub:
        bb = d.textbbox((0, 0), sub, font=f_sub)
        d.text(((w - (bb[2] - bb[0])) / 2, ys + 40), sub, font=f_sub,
               fill=accent)
    return np.array(img)


def caption_clip(size, text, fontsize=56, pad=36):
    w, h = size
    f = _font(fontsize)
    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    bb = tmp.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 170))
    d = ImageDraw.Draw(img)
    d.text((pad - bb[0], pad - bb[1]), text, font=f, fill=(255, 255, 255, 255))
    arr = np.array(img)
    return ImageClip(arr).with_position(("center", h - th - 90))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shotlist")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    spec = json.load(open(a.shotlist))
    W, H = spec.get("size", [1920, 1080])
    fps = spec.get("fps", 30)
    xf = spec.get("crossfade", 0.6)

    clips = []
    for s in spec["shots"]:
        if "src" in s:
            c = VideoFileClip(s["src"]).subclipped(s.get("start", 0),
                                                   s.get("start", 0) + s["dur"])
            if (c.w, c.h) != (W, H):
                c = c.resized((W, H))
        else:
            arr = text_card((W, H), s.get("title", ""), s.get("sub", ""),
                            tuple(s.get("bg", [10, 10, 14])))
            c = ImageClip(arr, duration=s["dur"])
        clips.append(c)

    # crossfade chain: overlap neighbours by xf seconds
    xf_clips = []
    for i, c in enumerate(clips):
        if i > 0:
            c = c.with_effects([vfx.CrossFadeIn(xf)])
        xf_clips.append(c)
    video = concatenate_videoclips(xf_clips, padding=-xf, method="compose")

    # captions on top
    caps = []
    for cap in spec.get("captions", []):
        cc = caption_clip((W, H), cap["text"]).with_start(cap["t"]).with_duration(cap["dur"])
        caps.append(cc)
    if caps:
        video = CompositeVideoClip([video] + caps, size=(W, H))

    # audio mix
    tracks = []
    au = spec.get("audio", {})
    if au.get("voiceover"):
        tracks.append(AudioFileClip(au["voiceover"]))
    if au.get("music"):
        m = AudioFileClip(au["music"])
        m = m.with_effects([afx.MultiplyVolume(au.get("music_gain", 0.25))])
        if m.duration < video.duration:
            m = m.with_effects([afx.Loop(duration=video.duration)])
        else:
            m = m.subclipped(0, video.duration)
        tracks.append(m)
    for s in au.get("sfx", []):
        f = AudioFileClip(s["file"])
        f = f.with_effects([afx.MultiplyVolume(s.get("gain", 0.8))]).with_start(s["t"])
        tracks.append(f)
    if tracks:
        video = video.with_audio(CompositeAudioClip(tracks))

    video.write_videofile(a.out, fps=fps, codec="libx264",
                          audio_codec="aac", preset="medium")
    print(f"WROTE {a.out}  {video.duration:.1f}s @ {W}x{H}")


if __name__ == "__main__":
    main()
