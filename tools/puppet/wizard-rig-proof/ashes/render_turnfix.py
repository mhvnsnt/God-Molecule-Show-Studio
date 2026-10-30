#!/usr/bin/env python3
"""Render poses FROM a patched Ashes .inp — TURNFIX proof renderer.

Parses the .inp puppet JSON + TEX_SECT textures, applies the deform
bindings for ParamAngleX / ParamAngleY (linear interp between the 3
axis keyforms, exactly as a runtime would), and rasterises each part
mesh with per-triangle affine warps in layer draw order. Other params
stay at rest (eyes open, mouth closed). This renders the rig FILE,
not a mockup: if the bindings are wrong, the proof shows it.
"""
import io
import json
import struct
import sys

import cv2
import numpy as np
from PIL import Image

W, H = 400, 864
BG = (30, 30, 36)

DRAW_ORDER = [  # rig_layers filename order (proven draw order)
    "00_torso", "01_neck", "02_hair_back", "03_face_underplate", "03_face_base", "04_arm_l_up",
    "04_arm_l_lo", "05_arm_r_up", "05_arm_r_lo", "06_hair_side", "07_hair_side", "08_hair_front",
    "09_accessory_l", "09_accessory_r", "10_eye_l", "11_eye_r", "12_mouth",
]
SKIP = {"13_eye_closed_l", "14_eye_closed_r"}  # opacity 0 at rest


def load_inp(path):
    data = open(path, "rb").read()
    assert data[:8] == b"TRNSRTS\x00"
    jlen = struct.unpack(">I", data[8:12])[0]
    pj = json.loads(data[12:12 + jlen])
    tail = data[12 + jlen:]
    assert tail[:8] == b"TEX_SECT"
    count = struct.unpack(">I", tail[8:12])[0]
    off = 12
    textures = []
    for _ in range(count):
        ln = struct.unpack(">I", tail[off:off + 4])[0]
        off += 4
        off += 1  # texture type byte (0 = PNG)
        textures.append(Image.open(io.BytesIO(tail[off:off + ln])).convert("RGBA"))
        off += ln
    nodes = {}
    def walk(n):
        nodes[n["uuid"]] = n
        for c in n.get("children") or []:
            walk(c)
    walk(pj["nodes"])
    params = {p["name"]: p for p in pj["param"]}
    return nodes, params, textures


def interp_offsets(param, value, node_uuid):
    """Per-vertex deform offsets (inp units) for `param` at `value`
    on one node, or None. Axis points are [0, .5, 1] over [min, max]."""
    for b in param["bindings"]:
        if b["node"] == node_uuid and b["param_name"] == "deform":
            lo, hi = param["min"][0], param["max"][0]
            t = (value - lo) / (hi - lo) if hi != lo else 0.5
            vals = b["values"]
            if t <= 0.5:
                a, bb, tt = vals[0], vals[1], t / 0.5
            else:
                a, bb, tt = vals[1], vals[2], (t - 0.5) / 0.5
            a = np.array(a, dtype=float)
            bb = np.array(bb, dtype=float)
            return a * (1 - tt) + bb * tt
    return None


def render(nodes, params, textures, angle_x=0.0, angle_y=0.0):
    canvas = np.zeros((H, W, 4), dtype=np.uint8)
    by_name = {n["name"]: n for n in nodes.values() if n.get("type") == "Part"}
    for name in DRAW_ORDER:
        n = by_name[name]
        m = n["mesh"]
        verts = np.array(m["verts"], dtype=float).reshape(-1, 2)
        uvs = np.array(m["uvs"], dtype=float).reshape(-1, 2)
        idx = np.array(m["indices"], dtype=np.int32).reshape(-1, 3)
        # fit pixel mapping from this node's own uvs (asserted in builder);
        # the underplate's uvs are nominal (solid texture) — use the face fit
        if name == "03_face_underplate":
            fm = by_name["03_face_base"]["mesh"]
            fv = np.array(fm["verts"], dtype=float).reshape(-1, 2)
            fuv = np.array(fm["uvs"], dtype=float).reshape(-1, 2)
            ax = np.polyfit(fv[:, 0], fuv[:, 0] * W, 1)
            ay = np.polyfit(fv[:, 1], fuv[:, 1] * H, 1)
            px_t, py_t = np.polyval(ax, verts[:, 0]), np.polyval(ay, verts[:, 1])
        else:
            px_t, py_t = uvs[:, 0] * W, uvs[:, 1] * H
            ax = np.polyfit(verts[:, 0], px_t, 1)
            ay = np.polyfit(verts[:, 1], py_t, 1)
        dst = np.column_stack([np.polyval(ax, verts[:, 0]),
                               np.polyval(ay, verts[:, 1])])
        for pid, val in (("ParamAngleX", angle_x), ("ParamAngleY", angle_y)):
            if val != 0.0:
                off = interp_offsets(params[pid], val, n["uuid"])
                if off is not None:
                    dst = dst + off * np.array([ax[0], ay[0]])
        tex_img = textures[n["textures"][0]]
        src = np.column_stack([uvs[:, 0] * tex_img.size[0], uvs[:, 1] * tex_img.size[1]])
        tex = np.array(tex_img)
        layer = np.zeros((H, W, 4), dtype=np.uint8)
        for tri in idx:
            s = src[list(tri)].astype(np.float32)
            d = dst[list(tri)].astype(np.float32)
            x0 = max(0, int(np.floor(d[:, 0].min())) - 1)
            x1 = min(W, int(np.ceil(d[:, 0].max())) + 1)
            y0 = max(0, int(np.floor(d[:, 1].min())) - 1)
            y1 = min(H, int(np.ceil(d[:, 1].max())) + 1)
            if x1 - x0 < 2 or y1 - y0 < 2:
                continue
            dl = d - np.array([x0, y0], dtype=np.float32)
            M = cv2.getAffineTransform(s, dl)
            warped = cv2.warpAffine(tex, M, (x1 - x0, y1 - y0),
                                    flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=(0, 0, 0, 0))
            mask = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
            cv2.fillConvexPoly(mask, dl.astype(np.int32), 255)
            # dilate mask edge 1px to close seams, like the repo preview
            mask = cv2.dilate(mask, np.ones((3, 3), np.uint8))
            warped[mask == 0] = 0
            roi = layer[y0:y1, x0:x1]
            a = (warped[:, :, 3:4].astype(np.float32) / 255.0)
            layer[y0:y1, x0:x1] = (warped[:, :, :].astype(np.float32) * a +
                                    roi.astype(np.float32) * (1 - a)).astype(np.uint8) \
                if False else cv2.convertScaleAbs(
                    warped.astype(np.float32) * a + roi.astype(np.float32) * (1 - a))
        # composite layer over canvas
        a = (layer[:, :, 3:4].astype(np.float32) / 255.0)
        ca = canvas[:, :, 3:4].astype(np.float32) / 255.0
        out_a = a + ca * (1 - a)
        rgb = (layer[:, :, :3].astype(np.float32) * a +
               canvas[:, :, :3].astype(np.float32) * ca * (1 - a)) / np.maximum(out_a, 1e-6)
        canvas = np.dstack([rgb, out_a * 255]).astype(np.uint8)
    out = Image.fromarray(canvas, "RGBA")
    bg = Image.new("RGBA", (W, H), BG + (255,))
    return Image.alpha_composite(bg, out).convert("RGB")


if __name__ == "__main__":
    inp = sys.argv[1]
    nodes, params, textures = load_inp(inp)
    poses = {
        "neutral": (0.0, 0.0),
        "left": (-30.0, 0.0),
        "right": (30.0, 0.0),
        "nod": (0.0, -30.0),
    }
    for name, (ax_, ay_) in poses.items():
        img = render(nodes, params, textures, ax_, ay_)
        img.save(f"pose_{name}.png")
        print("saved", name)
