#!/usr/bin/env python3
"""Bake real head-turn / nod DEFORM keyforms into Ashes.inp — TURNFIX.

Root cause (verified in the shipped PR #34 Ashes.inp): ParamAngleX and
ParamAngleY carried NO "deform" bindings at all — only a head-group
node rotation (transform.r.y [-0.52,0,0.52] / transform.r.x
[-0.42,0,0.42]) plus physics-anchor slides. image2live2d's author.py
states why: "ParamAngle* mesh_offsets stay empty ... the nijilive
backend synthesises its own head turn". That synthesis is a uniform
cos-squash of the whole head group about its bbox pivot — features and
outline move identically, so no turn can ever read. The owner's words
on the resulting proof: "more like a standing cross armed idle sway
with a blink than a turn and nod".

This script patches the puppet JSON inside Ashes.inp:
  * REMOVES the transform.r.y / transform.r.x node bindings from
    ParamAngleX / ParamAngleY (the rigid squash path).
  * ADDS per-vertex "deform" bindings for every head part (and the
    neck follow-through) at the 3 existing axis points (-30, 0, +30),
    computed by turn_deform.field — dome-depth rotation about the
    neck pivot, features leading the outline.
  * KEEPS the physics-anchor bindings (hair physics still driven by
    the Angle params) and ParamAngleZ's roll (a legit in-plane tilt).
Texture section is carried over byte-for-byte; only the JSON length
header is updated. Vertex->pixel mapping was fit from the file itself
(px = 0.4*vx + bx, py = 0.864*vy + by, residual ~1e-12) and is
re-fit per node here, with slopes asserted.
"""
import json
import struct
import sys

import numpy as np

from turn_deform import field

SRC = sys.argv[1] if len(sys.argv) > 1 else "Ashes.inp"
DST = sys.argv[2] if len(sys.argv) > 2 else "Ashes_turnfix.inp"

data = open(SRC, "rb").read()
assert data[:8] == b"TRNSRTS\x00", data[:8]
jlen = struct.unpack(">I", data[8:12])[0]
pj = json.loads(data[12:12 + jlen])
tail = data[12 + jlen:]
assert tail[:8] == b"TEX_SECT", tail[:9]

# node map
nodes = {}
def walk(n):
    nodes[n["uuid"]] = n
    for c in n.get("children") or []:
        walk(c)
walk(pj["nodes"])

# ------------------------------------------------------------------
# FACE UNDERPLATE (owner's fill-behind-the-cutout rule): the shipped
# face plate has a notch under the braid roots (measured: in the box
# x210-260/y150-220 the face texture covers only 1201/3500 px and the
# hood back 9 px; at rest the braids cover it, in a turn it opens to
# background). Add a void-coloured underplate part behind the face
# plate, spanning both braid-root zones, deforming with the face.
# ------------------------------------------------------------------
UNDERPLATE_UUID = 90
if UNDERPLATE_UUID not in nodes:
    import io as _io
    import math as _math
    from PIL import Image as _Image
    # append a solid void-colour texture (face void median RGB 2,1,45)
    count = struct.unpack(">I", tail[8:12])[0]
    off = 12
    entries = []
    for _ in range(count):
        ln = struct.unpack(">I", tail[off:off + 4])[0]
        entries.append(tail[off:off + 5 + ln])
        off += 5 + ln
    rest = tail[off:]
    buf = _io.BytesIO()
    _Image.new("RGBA", (64, 64), (2, 1, 45, 255)).save(buf, "PNG")
    png = buf.getvalue()
    entries.append(struct.pack(">I", len(png)) + b"\x00" + png)
    tail = b"TEX_SECT" + struct.pack(">I", len(entries)) + b"".join(entries) + rest
    new_tex_index = len(entries) - 1
    # ellipse fan mesh in layer px, converted with the face fit below
    cx, cy, rx, ry, seg = 192.0, 196.0, 98.0, 58.0, 20
    ring = [(cx + rx * _math.cos(2 * _math.pi * i / seg),
             cy + ry * _math.sin(2 * _math.pi * i / seg)) for i in range(seg)]
    pts = [(cx, cy)] + ring
    # placeholder verts; real verts set after the face fit is known
    node = {
        "uuid": UNDERPLATE_UUID, "name": "03_face_underplate",
        "type": "Part", "enabled": True, "zsort": -2.5,
        "transform": {"trans": [0.0, 0.0, 0.0], "rot": [0.0, 0.0, 0.0],
                      "scale": [1.0, 1.0]},
        "lockToRoot": False, "pinToMesh": False,
        "mesh": {"verts": [], "uvs": [], "indices": [], "origin": [0.0, 0.0]},
        "textures": [new_tex_index, 4294967295, 4294967295],
        "blend_mode": "Normal", "tint": [1.0, 1.0, 1.0], "screenTint": [0.0, 0.0, 0.0],
        "emissionStrength": 1.0, "mask_threshold": 0.5, "opacity": 1.0,
        "_underplate_pts_px": pts,
    }
    head = nodes[20]
    pos = next(i for i, c in enumerate(head["children"]) if c["uuid"] == 5)
    head["children"].insert(pos, node)
    nodes[UNDERPLATE_UUID] = node
    print(f"underplate added: texture index {new_tex_index}, zsort -2.5")

HEAD_PARTS = [4, 5, 90, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # head node 20 children + underplate
NECK = 3

def node_px(n):
    """(px, py) arrays for a Part node's verts, fit from its own uvs."""
    m = n["mesh"]
    v = np.array(m["verts"], dtype=float).reshape(-1, 2)
    uv = np.array(m["uvs"], dtype=float).reshape(-1, 2)
    # texture size from the node's texture: all layer textures are 400x864
    px_t, py_t = uv[:, 0] * 400.0, uv[:, 1] * 864.0
    ax = np.polyfit(v[:, 0], px_t, 1)
    ay = np.polyfit(v[:, 1], py_t, 1)
    assert abs(ax[0] - 0.4) < 1e-6 and abs(ay[0] - 0.864) < 1e-6, (n["name"], ax, ay)
    assert np.abs(np.polyval(ax, v[:, 0]) - px_t).max() < 1e-6
    assert np.abs(np.polyval(ay, v[:, 1]) - py_t).max() < 1e-6
    return v, px_t, py_t, ax, ay

# ------------------------------------------------------------------
# SHELL MESH BRIDGES: at max nod, a hood flame tip at the top-right
# (rest zone x 222-262, y 20-62) disconnects — a pre-existing mesh
# coverage gap in hair_back/hair_front that the pitch opens. Bridge
# it with extra triangles in the parts' OWN meshes sampling their
# OWN texture (alpha-gated: invisible where the part is transparent,
# seamless where it is not). Runs before deform baking so the new
# verts get keyforms like every other vertex.
# ------------------------------------------------------------------
def _bridge(n, x0, x1, y0, y1, nx=4, ny=3):
    m = n["mesh"]
    v = np.array(m["verts"], dtype=float).reshape(-1, 2)
    uv = np.array(m["uvs"], dtype=float).reshape(-1, 2)
    px_t, py_t = uv[:, 0] * 400.0, uv[:, 1] * 864.0
    ax = np.polyfit(v[:, 0], px_t, 1)
    ay = np.polyfit(v[:, 1], py_t, 1)
    base = len(v)
    verts, uvs = list(m["verts"]), list(m["uvs"])
    for j in range(ny + 1):
        for i in range(nx + 1):
            pxx = x0 + (x1 - x0) * i / nx
            pyy = y0 + (y1 - y0) * j / ny
            verts += [(pxx - ax[1]) / ax[0], (pyy - ay[1]) / ay[0]]
            uvs += [pxx / 400.0, pyy / 864.0]
    idx = list(m["indices"])
    for j in range(ny):
        for i in range(nx):
            a = base + j * (nx + 1) + i
            b = a + 1
            c = a + nx + 1
            d = c + 1
            idx += [a, c, b, b, c, d]
    m["verts"] = [float(t) for t in verts]
    m["uvs"] = [float(t) for t in uvs]
    m["indices"] = idx
    print(f"bridge added to {n['name']}: +{(nx+1)*(ny+1)} verts")

_bridge(nodes[4], 222, 262, 20, 62)    # 02_hair_back
_bridge(nodes[12], 222, 262, 20, 62)   # 08_hair_front

# set the underplate's real verts/uvs from its px points via the face fit
if "_underplate_pts_px" in nodes.get(UNDERPLATE_UUID, {}):
    _face = nodes[5]
    _, _, _, _ax, _ay = node_px(_face)
    _pts = nodes[UNDERPLATE_UUID].pop("_underplate_pts_px")
    _seg = len(_pts) - 1
    _verts, _uvs, _idx = [], [], []
    for i, (pxx, pyy) in enumerate(_pts):
        _verts += [(pxx - _ax[1]) / _ax[0], (pyy - _ay[1]) / _ay[0]]
        if i == 0:
            _uvs += [0.5, 0.5]
        else:
            a = 2 * np.pi * (i - 1) / _seg
            _uvs += [0.5 + 0.44 * float(np.cos(a)), 0.5 + 0.44 * float(np.sin(a))]
    for i in range(1, _seg + 1):
        _idx += [0, i, i % _seg + 1]
    _m = nodes[UNDERPLATE_UUID]["mesh"]
    _m["verts"] = [float(v) for v in _verts]
    _m["uvs"] = [float(v) for v in _uvs]
    _m["indices"] = _idx
    # node_px() fits from uvs, which are nominal for the underplate:
    # wrap it so deform baking uses the face fit directly
    _orig_node_px = node_px
    def node_px(n, _orig=_orig_node_px, _ax=_ax, _ay=_ay):  # noqa: F811
        if n["uuid"] == UNDERPLATE_UUID:
            v = np.array(n["mesh"]["verts"], dtype=float).reshape(-1, 2)
            return v, np.polyval(_ax, v[:, 0]), np.polyval(_ay, v[:, 1]), _ax, _ay
        return _orig(n)

def deform_values(n, axis):
    """values[3][nverts][2] deform offsets (inp units) for axis 'x' or 'y'."""
    v, px, py, ax, ay = node_px(n)
    out = []
    for s in (-1.0, 0.0, 1.0):
        offs = []
        for x, y in zip(px, py):
            if axis == "x":
                dx, dy = field(n["name"], float(x), float(y), s, 0.0)
            else:  # AngleY: -30 (value min) = nod down in this rig's convention
                dx, dy = field(n["name"], float(x), float(y), 0.0, -s)
            offs.append([dx / ax[0], dy / ay[0]])
        out.append(offs)
    return out

def deform_values_torso(n):
    """AngleY follow-through for the torso top band: the collar trim
    islands at the neck (measured torso alpha islands y 91-146) are
    covered by the hood at rest but detach in a nod if the torso is
    rigid. Weight 1.0 at the collar -> 0 at y=340 (chest stays)."""
    import math as _m
    from turn_deform import PITCH_MAX, PIVOT_Y, R as _R
    v, px, py, ax, ay = node_px(n)
    out = []
    for s in (-1.0, 0.0, 1.0):
        nod = -s
        ph = nod * PITCH_MAX
        offs = []
        for x, y in zip(px, py):
            if y <= 150.0:
                w = 1.0
            elif y >= 340.0:
                w = 0.0
            else:
                t = (y - 150.0) / 190.0
                w = 1.0 - t * t * (3.0 - 2.0 * t)
            dy = ((y - PIVOT_Y) * (_m.cos(ph) - 1.0) + _R * _m.sin(ph)) * w
            offs.append([0.0, dy / ay[0]])
        out.append(offs)
    return out

report = {}
for p in pj["param"]:
    if p["name"] == "ParamAngleX":
        before = [(b["node"], b["param_name"]) for b in p["bindings"]]
        p["bindings"] = [b for b in p["bindings"]
                         if not (b["node"] == 20 and b["param_name"] == "transform.r.y")]
        for u in HEAD_PARTS + [NECK]:
            n = nodes[u]
            p["bindings"].append({
                "node": u, "param_name": "deform",
                "values": deform_values(n, "x"),
                "isSet": [[True], [True], [True]],
                "interpolate_mode": "Linear",
            })
        report["ParamAngleX"] = {"before": before,
                                 "after": [(b["node"], b["param_name"]) for b in p["bindings"]]}
    elif p["name"] == "ParamAngleY":
        before = [(b["node"], b["param_name"]) for b in p["bindings"]]
        p["bindings"] = [b for b in p["bindings"]
                         if not (b["node"] == 20 and b["param_name"] == "transform.r.x")]
        for u in HEAD_PARTS + [NECK]:
            n = nodes[u]
            p["bindings"].append({
                "node": u, "param_name": "deform",
                "values": deform_values(n, "y"),
                "isSet": [[True], [True], [True]],
                "interpolate_mode": "Linear",
            })
        p["bindings"].append({
            "node": 2, "param_name": "deform",
            "values": deform_values_torso(nodes[2]),
            "isSet": [[True], [True], [True]],
            "interpolate_mode": "Linear",
        })
        report["ParamAngleY"] = {"before": before,
                                 "after": [(b["node"], b["param_name"]) for b in p["bindings"]]}

new_json = json.dumps(pj, separators=(",", ":")).encode()
out = b"TRNSRTS\x00" + struct.pack(">I", len(new_json)) + new_json + tail
open(DST, "wb").write(out)
print("wrote", DST, len(out), "bytes (src", len(data), ")")
print(json.dumps(report, indent=1))
# displacement summary at extremes, in layer px, for the report
for u, label in ((15, "eye_l"), (17, "mouth/grill"), (5, "face_base"), (10, "braid_L")):
    n = nodes[u]
    v, px, py, ax, ay = node_px(n)
    for axis, s in (("yaw+30", 1.0),):
        ds = [field(n["name"], float(x), float(y), s, 0.0) for x, y in zip(px, py)]
        ds = np.array(ds)
        print(f"{label}: yaw max |dx| mean={np.abs(ds[:,0]).mean():.1f}px max={np.abs(ds[:,0]).max():.1f}px  centroid dx={ds[:,0].mean():+.1f}px")
    ds = np.array([field(n["name"], float(x), float(y), 0.0, 1.0) for x, y in zip(px, py)])
    print(f"{label}: nod max dy mean={ds[:,1].mean():+.1f}px max={ds[:,1].max():.1f}px")
