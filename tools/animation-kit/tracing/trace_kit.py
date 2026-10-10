#!/usr/bin/env python3
"""trace-kit — mascot-grade vectorization pipeline (the power drill over raw vtracer).
Chain: input -> (optional rembg matte) -> alpha cleanup -> color posterize
       -> vtracer with mascot-tuned params -> SVG.
Posterizing first collapses painterly gradients into flat cartoon regions, which
is what makes character traces come out clean instead of thousands of speck paths.
Usage:
  trace_kit.py --input mascot.png --output mascot.svg [--preset mascot|logo|scene]
  presets: mascot = posterize 12 colors, detail 8 (character art)
           logo    = posterize 6 colors, detail 10 (crisp marks)
           scene   = posterize 24 colors, detail 6 (backgrounds)
"""
import argparse, os, subprocess, sys
import numpy as np
from PIL import Image

VENVPY = "/home/hatch/workspace/video-fix-tools/venv/bin/python"
PRESETS = {
    "mascot": dict(colors=12, detail=8, corner=60, speckle=4),
    "logo": dict(colors=6, detail=10, corner=30, speckle=2),
    "scene": dict(colors=24, detail=6, corner=60, speckle=8),
}


def posterize(img, colors):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    px = a.reshape(-1, 3)
    # fast k-means-ish: median-cut via PIL
    q = img.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    return q.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--preset", default="mascot", choices=list(PRESETS))
    a = ap.parse_args()
    p = PRESETS[a.preset]

    img = Image.open(a.input)
    alpha = img.getchannel("A") if img.mode == "RGBA" else None
    flat = posterize(img, p["colors"])
    if alpha is not None:
        flat.putalpha(alpha)
    tmp = "/tmp/trace-kit-posterized.png"
    flat.save(tmp)

    code = (
        "import vtracer\n"
        f"vtracer.convert_image_to_svg_py({tmp!r}, {a.output!r},\n"
        "    colormode='color', hierarchical='stacked',\n"
        f"    filter_speckle={p['speckle']}, color_precision=6, layer_difference=16,\n"
        f"    path_precision={p['detail']}, corner_threshold={p['corner']},\n"
        "    length_threshold=4.0, splice_threshold=45, mode='spline')\n"
        f"print('traced', {a.output!r})\n"
    )
    r = subprocess.run([VENVPY, "-c", code])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
