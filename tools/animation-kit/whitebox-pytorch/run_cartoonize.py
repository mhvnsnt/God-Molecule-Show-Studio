#!/usr/bin/env python3
"""White-box cartoonization wrapper (PyTorch port, sceneryonly weights).
Usage: run_cartoonize.py --input in.jpg --output out.png [--batch 4]
       run_cartoonize.py --input frames_dir --output out_dir   (folder mode)
Serves: cartoon stylization of rotoscoped backgrounds, style-matching hand-drawn
        frames to a unified cartoon look. CPU-friendly (~30s/frame at 1080p).
"""
import argparse, subprocess, sys, os, glob, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
VENV = "/home/hatch/workspace/video-fix-tools/venv/bin/python"
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="image file, video file, or frames folder")
    ap.add_argument("--output", required=True, help="output png (image/video) or folder (folder mode)")
    ap.add_argument("--batch", type=int, default=4)
    a = ap.parse_args()
    tmp = "/tmp/wb_wrap"
    os.makedirs(tmp, exist_ok=True)
    # upstream inference.py writes <src>_infered.png next to source for single files;
    # for folders it honors --dest_folder. Normalize: use folder mode always.
    if os.path.isdir(a.input):
        src, outdir, single = a.input, a.output, False
    else:
        src = os.path.join(tmp, "in"); shutil.rmtree(src, ignore_errors=True); os.makedirs(src)
        shutil.copy(a.input, os.path.join(src, "frame" + os.path.splitext(a.input)[1]))
        outdir, single = os.path.join(tmp, "out"), True
    os.makedirs(outdir, exist_ok=True)
    cmd = [VENV, os.path.join(HERE, "inference.py"), "-s", src,
           "-w", os.path.join(HERE, "weights/sceneryonly.pth.tar"),
           "--dest_folder", outdir, "--batch_size", str(a.batch)]
    print("CARTOONIZE:", " ".join(cmd)); sys.stdout.flush()
    r = subprocess.run(cmd, cwd=HERE)
    if r.returncode != 0: sys.exit(r.returncode)
    outs = sorted(glob.glob(os.path.join(outdir, "*_infered.*")))
    if not outs: print("no outputs produced"); sys.exit(1)
    if single:
        ext = ".png"
        shutil.move(outs[0], a.output if a.output.endswith(ext) else a.output + ext)
        print("wrote", a.output)
    else:
        print(f"wrote {len(outs)} frames to {outdir}")
if __name__ == "__main__": main()
