#!/usr/bin/env python3
"""Real-ESRGAN upscaling (anime_6B default) — restoration tier for frames/keyframes.
Cleans up and 4x-upscales cartoon frames before stylization, or restores
soft phone footage. CPU-tiled to stay in memory.
Usage:
  run_upscale.py --input in.png --output out.png [--tile 256] [--scale-out 2]
  --scale-out 2 downsamples the 4x result to 2x (sharper than native 2x).
"""
import argparse, os, sys
import numpy as np
import torch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rrdbnet import load_rrdbnet

HERE = os.path.dirname(os.path.abspath(__file__))


def upscale_tiled(img, net, device, tile=256):
    w, h = img.size
    x = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    x = torch.from_numpy(x).permute(2, 0, 1).unsqueeze(0).to(device)
    _, _, th, tw = x.shape
    pad_h = (tile - th % tile) % tile
    pad_w = (tile - tw % tile) % tile
    import torch.nn.functional as F
    x = F.pad(x, (0, pad_w, 0, pad_h), mode="reflect")
    out = torch.zeros(1, 3, (th + pad_h) * 4, (tw + pad_w) * 4)
    with torch.no_grad():
        for i in range(0, th + pad_h, tile):
            for j in range(0, tw + pad_w, tile):
                t = x[:, :, i:i + tile, j:j + tile]
                out[:, :, i * 4:(i + tile) * 4, j * 4:(j + tile) * 4] = net(t).cpu()
    out = out[:, :, :th * 4, :tw * 4][0].clamp(0, 1)
    arr = (out.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    return Image.fromarray(arr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--weights", default=os.path.join(HERE, "weights", "RealESRGAN_x4plus_anime_6B.pth"))
    ap.add_argument("--num-block", type=int, default=6)
    ap.add_argument("--tile", type=int, default=256)
    ap.add_argument("--scale-out", type=float, default=4.0,
                    help="final scale vs input (4=native, 2=downsampled sharper)")
    a = ap.parse_args()
    device = "cpu"
    net = load_rrdbnet(a.weights, num_block=a.num_block, device=device)
    print("Real-ESRGAN loaded:", a.weights)
    img = Image.open(a.input)
    out = upscale_tiled(img, net, device, tile=a.tile)
    if abs(a.scale_out - 4.0) > 1e-6:
        nw, nh = int(img.size[0] * a.scale_out), int(img.size[1] * a.scale_out)
        out = out.resize((nw, nh), Image.LANCZOS)
    out.save(a.output)
    print("wrote", a.output, out.size)


if __name__ == "__main__":
    main()
