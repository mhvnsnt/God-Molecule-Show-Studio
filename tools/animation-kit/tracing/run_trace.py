#!/usr/bin/env python3
"""Raster-to-vector tracing wrapper (vtracer).
Usage: run_trace.py --input in.png --output out.svg [--mode color|binary] [--detail N]
Serves: clean mascot/character edges — trace cartoon frames or mattes to SVG
        for infinitely scalable, crisp-edged character art (merch, title cards).
"""
import argparse, sys, os, subprocess
VENVPY = "/home/hatch/workspace/video-fix-tools/venv/bin/python"
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--output", required=True)
    ap.add_argument("--mode", default="color", choices=["color", "binary"])
    ap.add_argument("--detail", type=int, default=8, help="path detail 1-10 (higher=more detail)")
    ap.add_argument("--no-filter-speckle", action="store_true", help="keep tiny speckles")
    a = ap.parse_args()
    code = (
        "import vtracer\n"
        f"vtracer.convert_image_to_svg_py({a.input!r}, {a.output!r},\n"
        f"    colormode={a.mode!r},\n"
        "    hierarchical='stacked',\n"
        f"    filter_speckle={4 if not a.no_filter_speckle else 0},\n"
        "    color_precision=6, layer_difference=16,\n"
        f"    path_precision={a.detail},\n"
        "    corner_threshold=60, length_threshold=4.0,\n"
        "    splice_threshold=45, mode='spline')\n"
        f"print('traced', {a.output!r})\n"
    )
    sys.exit(subprocess.run([VENVPY, "-c", code]).returncode)
if __name__ == "__main__": main()
