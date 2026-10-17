#!/usr/bin/env python3
"""AnimeGANv2 inference (face_paint_512_v2) — anime stylization tier above whitebox.
Usage:
  run_animegan2.py --input in.jpg --output out.png [--weights face_paint_512_v2.pt]
  run_animegan2.py --input frames_in/ --output frames_out/   (folder mode)
Input is resized to 512 (model native), output resized back to input size.
"""
import argparse, os, sys
import numpy as np
import torch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_animegan2 import Generator

HERE = os.path.dirname(os.path.abspath(__file__))


def stylize(pil_img, net, device):
    w, h = pil_img.size
    img = pil_img.convert("RGB").resize((512, 512), Image.BILINEAR)
    x = (np.asarray(img).astype(np.float32) / 127.5 - 1.0)
    x = torch.from_numpy(x).permute(2, 0, 1).unsqueeze(0).to(device)
    with torch.no_grad():
        y = net(x)[0].clamp(-1, 1).cpu()
    out = ((y.permute(1, 2, 0).numpy() + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out).resize((w, h), Image.BILINEAR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--weights", default=os.path.join(HERE, "weights", "face_paint_512_v2.pt"))
    a = ap.parse_args()
    device = "cpu"
    net = Generator().to(device).eval()
    sd = torch.load(a.weights, map_location=device, weights_only=True)
    missing = net.load_state_dict(sd, strict=True)
    print("weights loaded:", a.weights, "| missing:", len(missing.missing_keys),
          "| unexpected:", len(missing.unexpected_keys))

    if os.path.isdir(a.input):
        os.makedirs(a.output, exist_ok=True)
        files = sorted(f for f in os.listdir(a.input)
                       if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
        for f in files:
            out = stylize(Image.open(os.path.join(a.input, f)), net, device)
            out.save(os.path.join(a.output, os.path.splitext(f)[0] + ".png"))
            print("styled", f)
    else:
        out = stylize(Image.open(a.input), net, device)
        out.save(a.output)
        print("wrote", a.output, out.size)


if __name__ == "__main__":
    main()
