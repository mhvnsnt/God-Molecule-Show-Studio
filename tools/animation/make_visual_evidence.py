#!/usr/bin/env python3
"""Create a human-reviewable evidence packet from real render frames.

This tool never labels the render as visually correct. It only packages the
actual pixels plus deterministic metadata so a human can inspect them.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames_dir", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--columns", type=int, default=4)
    ap.add_argument("--thumb-width", type=int, default=320)
    args = ap.parse_args()

    frames = sorted(p for p in args.frames_dir.glob("*.png") if p.is_file())
    if not frames:
        raise SystemExit("NO_RENDER_FRAMES: nothing to inspect")

    args.out.mkdir(parents=True, exist_ok=True)
    evidence_dir = args.out / "frames"
    evidence_dir.mkdir(exist_ok=True)

    entries = []
    thumbs = []
    for i, src in enumerate(frames, 1):
        dst = evidence_dir / f"frame-{i:04d}.png"
        dst.write_bytes(src.read_bytes())
        with Image.open(src) as im:
            im = im.convert("RGB")
            im.thumbnail((args.thumb_width, args.thumb_width))
            canvas = Image.new("RGB", (args.thumb_width, args.thumb_width + 28), "black")
            x = (canvas.width - im.width) // 2
            y = (args.thumb_width - im.height) // 2
            canvas.paste(im, (x, y))
            ImageDraw.Draw(canvas).text((8, args.thumb_width + 6), f"frame {i}", fill="white")
            thumbs.append(canvas)
            entries.append({
                "frame": i,
                "source": str(src),
                "evidence": str(dst.relative_to(args.out)),
                "sha256": sha256(src),
                "width": im.width,
                "height": im.height,
            })

    rows = (len(thumbs) + args.columns - 1) // args.columns
    sheet = Image.new("RGB", (args.columns * args.thumb_width, rows * (args.thumb_width + 28)), "black")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % args.columns) * args.thumb_width, (i // args.columns) * (args.thumb_width + 28)))
    sheet.save(args.out / "CONTACT-SHEET.png")

    manifest = {
        "schemaVersion": 1,
        "visualInspection": "HUMAN_REVIEW_REQUIRED",
        "verdict": None,
        "frames": entries,
        "contactSheet": "CONTACT-SHEET.png",
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
