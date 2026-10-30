#!/usr/bin/env python3
"""Bake real head-turn / nod DEFORM keyforms into Ashes.inp — TURNFIX v2.

Same patch shape as v1 (see RIG_TURNFIX_2026-10-29.md for the root
cause: PR #34's ParamAngleX/Y carried NO deform bindings, only a
head-group rotation + the preview's uniform cos-squash). v2 keeps the
deform approach and the nod, and replaces the deformation FIELD with
turn_deform.field — the v4 GLOBAL field: displacement is a function
of canvas position only (cosine dome in x, height weights in y),
identical for every part, because the part separation smeared the
braids/chain across five layers whose copies must move together or
the stack shreds (see turn_deform.py's header and the v2 section of
RIG_TURNFIX_2026-10-29.md). The underplate is a face-silhouette
plate (one filled fan per face-texture alpha component, eroded 2px,
zsort -1.5 behind the hood back) instead of v1's 20-gon ellipse,
whose exposed slab read as a black rectangle at max turn.

  * REMOVES the transform.r.y / transform.r.x node bindings from
    ParamAngleX / ParamAngleY (the rigid squash path).
  * ADDS per-vertex "deform" bindings for EVERY part at the 3
    existing axis points (-30, 0, +30) — torso and arms included,
    because their textures carry braid/chain fragments.
  * KEEPS the physics-anchor bindings and ParamAngleZ's roll.
Texture section gains ONE appended entry (the underplate's solid
texture); all existing entries are carried over byte-for-byte.
Vertex->pixel mapping is re-fit per node here, with slopes asserted.
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
    # Face-SILHOUETTE plate (v2): filled external contour of the face
    # texture's alpha, dilated 9px. v1's ellipse (rx98 vs face
    # half-width 81) exposed a flat slab beside the face at max turn
    # whose polygon chords read as a black rectangle. The silhouette
    # plate can only ever expose a thin curved shadow ring, and its
    # filled interior covers the braid-root notch zone by construction.
    import cv2 as _cv2
    _face_tex_idx = nodes[5]["textures"][0]
    _fe = entries[_face_tex_idx]
    _flen = struct.unpack(">I", _fe[:4])[0]
    _fimg = _Image.open(_io.BytesIO(_fe[5:5 + _flen])).convert("RGBA")
    _alpha = np.array(_fimg)[:, :, 3]
    _mask = (_alpha > 10).astype(np.uint8) * 255
    # the face texture is FOUR alpha components (main plate + right
    # cheek/ear pieces + left ear tip) — fill EVERY external contour
    # and union them; v2's largest-contour-only plate silently
    # dropped the face's right side (plate stopped at x255 of 274)
    _cnts, _ = _cv2.findContours(_mask, _cv2.RETR_EXTERNAL, _cv2.CHAIN_APPROX_SIMPLE)
    # ONE FAN PER COMPONENT: dilating the union failed to bridge the
    # components (plate stopped at x254 of 277), so each component
    # gets its own filled fan, dilated 2px to cover its AA edge.
    # Disjoint fans in one mesh are fine — the plate sits BEHIND
    # hair_back (zsort -1.5), so the fans are invisible at rest and
    # only fill the braid-root notch + turn leaks in a pose.
    fans = []
    for _c in _cnts:
        if _cv2.contourArea(_c) < 40:
            continue
        _one = np.zeros_like(_mask)
        _cv2.drawContours(_one, [_c], -1, 255, -1)
        # ERODE 2px: the plate must stay strictly inside the face's
        # opaque core. A dilated plate reaches behind the face's
        # anti-aliased edge pixels and changes their blend at rest
        # (161 changed px measured); eroded, the rest backdrop stays
        # hair_back exactly as PR #34, and the plate still fills the
        # interior notch (its job) in a pose.
        _one = _cv2.erode(_one, _cv2.getStructuringElement(_cv2.MORPH_ELLIPSE, (5, 5)))
        _cc, _ = _cv2.findContours(_one, _cv2.RETR_EXTERNAL, _cv2.CHAIN_APPROX_SIMPLE)
        _oc = max(_cc, key=_cv2.contourArea)
        _ap = _cv2.approxPolyDP(_oc, 2.0, True).reshape(-1, 2)
        _Mm = _cv2.moments(_oc)
        _cx, _cy = _Mm["m10"] / _Mm["m00"], _Mm["m01"] / _Mm["m00"]
        fans.append(((float(_cx), float(_cy)),
                     [(float(a), float(b)) for a, b in _ap]))
    pts = fans   # consumed by the fan-builder below as a fan list
    print(f"underplate silhouette: {len(fans)} fans, "
          f"{sum(len(r) for _, r in fans)} ring pts")
    # placeholder verts; real verts set after the face fit is known
    node = {
        "uuid": UNDERPLATE_UUID, "name": "03_face_underplate",
        "type": "Part", "enabled": True, "zsort": -1.5,
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
    print(f"underplate added: texture index {new_tex_index}, zsort -1.5 (behind hair_back)")

ALL_PARTS = [2, 3, 4, 5, 90, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # every Part node: the v4 field is global (position-based), so torso/arms/accessory must carry it too or their painted fragments separate from the head parts

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

# v2: rim-band subdivision — an IDENTICAL grid (same verts, same
# triangulation) added to BOTH shell parts over the whole hood-rim
# region, so their piecewise-linear surfaces track each other under
# the field and the dark interior dashes along the flame edges close.
# (Supersedes v1's small 222-262/20-62 bridges; this region contains
# that zone.)
_bridge(nodes[4], 100, 280, 15, 260, nx=9, ny=12)    # 02_hair_back
_bridge(nodes[12], 100, 280, 15, 260, nx=9, ny=12)   # 08_hair_front

# set the underplate's real verts/uvs from its px points via the face fit
if "_underplate_pts_px" in nodes.get(UNDERPLATE_UUID, {}):
    _face = nodes[5]
    _, _, _, _ax, _ay = node_px(_face)
    _fans = nodes[UNDERPLATE_UUID].pop("_underplate_pts_px")
    _verts, _uvs, _idx = [], [], []
    for _cen, _ring in _fans:
        _base = len(_verts) // 2
        _verts += [(_cen[0] - _ax[1]) / _ax[0], (_cen[1] - _ay[1]) / _ay[0]]
        _uvs += [0.5, 0.5]
        for (pxx, pyy) in _ring:
            _verts += [(pxx - _ax[1]) / _ax[0], (pyy - _ay[1]) / _ay[0]]
            _ang = np.arctan2(pyy - _cen[1], pxx - _cen[0])
            _uvs += [0.5 + 0.44 * float(np.cos(_ang)), 0.5 + 0.44 * float(np.sin(_ang))]
        _seg = len(_ring)
        for i in range(1, _seg + 1):
            _idx += [_base, _base + i, _base + i % _seg + 1]
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

report = {}
for p in pj["param"]:
    if p["name"] == "ParamAngleX":
        before = [(b["node"], b["param_name"]) for b in p["bindings"]]
        p["bindings"] = [b for b in p["bindings"]
                         if not (b["node"] == 20 and b["param_name"] == "transform.r.y")]
        for u in ALL_PARTS:
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
        for u in ALL_PARTS:
            n = nodes[u]
            p["bindings"].append({
                "node": u, "param_name": "deform",
                "values": deform_values(n, "y"),
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
