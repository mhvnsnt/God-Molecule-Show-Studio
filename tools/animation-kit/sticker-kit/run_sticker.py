#!/usr/bin/env python3
"""Sticker / clean-cut toolkit (PIL, purpose-built).
Subcommands:
  cleanup    -- alpha edge cleanup: threshold weak alpha, smooth jagged edges
  sticker    -- white-border sticker: dilate alpha, white outline + optional drop shadow
  refine     -- alpha matting refinement: erode/dilate + feather for cleaner composites
  cutout     -- all-in-one: cleanup -> sticker (merch-ready cutout)

Usage: run_sticker.py sticker --input cut.png --output sticker.png [--border 24] [--shadow]
       run_sticker.py cleanup --input cut.png --output clean.png [--threshold 24] [--smooth 2]
       run_sticker.py refine --input cut.png --output refined.png [--erode 1] [--feather 2]
Serves: merch-ready mascot cutouts, clean character edges for cards/composites.
"""
import argparse, sys
from PIL import Image, ImageFilter, ImageOps

def load_rgba(p):
    im = Image.open(p)
    return im.convert("RGBA") if im.mode != "RGBA" else im

def cleanup(im, threshold=24, smooth=2):
    r, g, b, a = im.split()
    a = a.point(lambda v: 0 if v < threshold else 255)
    if smooth > 0:
        a = a.filter(ImageFilter.GaussianBlur(smooth))
        a = a.point(lambda v: 0 if v < 128 else 255)
    im.putalpha(a)
    return im

def refine(im, erode=1, feather=2):
    from PIL import ImageChops
    r, g, b, a = im.split()
    if erode > 0:
        a = a.filter(ImageFilter.MinFilter(erode * 2 + 1))
    if feather > 0:
        a = a.filter(ImageFilter.GaussianBlur(feather))
    im.putalpha(a)
    return im

def sticker(im, border=24, border_color=(255, 255, 255, 255), shadow=False,
            shadow_blur=18, shadow_offset=(0, 10)):
    r, g, b, a = im.split()
    grown = a.filter(ImageFilter.MaxFilter(border * 2 + 1))
    grown = grown.filter(ImageFilter.GaussianBlur(border / 6))
    grown = grown.point(lambda v: 255 if v > 40 else 0)
    base = Image.new("RGBA", im.size, (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        shp = Image.new("RGBA", im.size, (0, 0, 0, 160))
        sh.paste(shp, shadow_offset, grown)
        sh = sh.filter(ImageFilter.GaussianBlur(shadow_blur))
        base = Image.alpha_composite(base, sh)
    outline = Image.new("RGBA", im.size, border_color)
    base.paste(outline, (0, 0), grown)
    base = Image.alpha_composite(base, im)
    return base

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("cleanup", "sticker", "refine", "cutout"):
        s = sub.add_parser(name)
        s.add_argument("--input", required=True); s.add_argument("--output", required=True)
    sub.choices["cleanup"].add_argument("--threshold", type=int, default=24)
    sub.choices["cleanup"].add_argument("--smooth", type=int, default=2)
    sub.choices["sticker"].add_argument("--border", type=int, default=24)
    sub.choices["sticker"].add_argument("--shadow", action="store_true")
    sub.choices["refine"].add_argument("--erode", type=int, default=1)
    sub.choices["refine"].add_argument("--feather", type=int, default=2)
    sub.choices["cutout"].add_argument("--border", type=int, default=24)
    sub.choices["cutout"].add_argument("--shadow", action="store_true")
    a = ap.parse_args()
    im = load_rgba(a.input)
    if a.cmd == "cleanup":
        im = cleanup(im, a.threshold, a.smooth)
    elif a.cmd == "sticker":
        im = sticker(im, a.border, shadow=a.shadow)
    elif a.cmd == "refine":
        im = refine(im, a.erode, a.feather)
    elif a.cmd == "cutout":
        im = sticker(cleanup(im), a.border, shadow=a.shadow)
    im.save(a.output)
    print(f"{a.cmd}: wrote {a.output} {im.size}")

if __name__ == "__main__":
    main()
