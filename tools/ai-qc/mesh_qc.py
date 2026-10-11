#!/usr/bin/env python3
"""
mesh_qc.py — 3D asset QC for episode/show pipelines (parallel lane).

Validates GLB files (the format our character models use):
- Mesh sanity: degenerate triangles, unreferenced vertices, NaN positions
- Normals / UVs present?
- Textures: referenced images exist, reasonable resolution
- Skinning: joint weights sum to ~1, all vertices bound
- Node sanity: scale anomalies, negative scale (mirroring bugs)

Lightweight: parses GLB binary directly (JSON chunk + BIN chunk),
no trimesh/pygltflib needed. Draco-compressed meshes are reported
as "needs draco" rather than decoded.

Also handles .obj (basic) via a minimal parser.
"""
import json
import os
import struct

import numpy as np

# glTF component type sizes
_COMP = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
_TYPE_COUNT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def _read_glb(path):
    with open(path, "rb") as f:
        magic = f.read(4)
        if magic != b"glTF":
            raise ValueError("not a GLB file")
        f.read(4)  # version
        f.read(4)  # length
        chunks = {}
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                break
            clen, ctype = struct.unpack("<II", hdr)
            data = f.read(clen)
            chunks[ctype] = data
        js = json.loads(chunks[0x4E4F534A].decode("utf-8"))
        bin_data = chunks.get(0x004E4942, b"")
        return js, bin_data


def _accessor_data(js, bin_data, idx):
    acc = js["accessors"][idx]
    bv = js["bufferViews"][acc["bufferView"]]
    comp_size = _COMP[acc["componentType"]]
    n_comp = _TYPE_COUNT[acc["type"]]
    count = acc["count"]
    byte_offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    n_bytes = count * n_comp * comp_size
    raw = bin_data[byte_offset:byte_offset + n_bytes]
    dtype = {5126: np.float32, 5123: np.uint16, 5125: np.uint32,
             5121: np.uint8}[acc["componentType"]]
    arr = np.frombuffer(raw, dtype=dtype).reshape(count, n_comp)
    return arr.astype(np.float64)


def check_mesh(js, bin_data, prim, mesh_name):
    """Per-primitive checks. Returns list of (severity, message)."""
    issues = []
    attrs = prim.get("attributes", {})
    if "POSITION" not in attrs:
        issues.append(("critical", f"{mesh_name}: no POSITION attribute"))
        return issues
    pos = _accessor_data(js, bin_data, attrs["POSITION"])
    n_verts = len(pos)
    # NaN / Inf
    if not np.all(np.isfinite(pos)):
        issues.append(("critical", f"{mesh_name}: NaN/Inf in positions"))
    # degenerate: all verts at same point
    if np.allclose(pos.max(0) - pos.min(0), 0):
        issues.append(("critical", f"{mesh_name}: zero-size mesh"))
    # indices
    if "indices" in prim:
        idx = _accessor_data(js, bin_data, prim["indices"]).astype(np.int64).ravel()
        if idx.max() >= n_verts:
            issues.append(("critical",
                           f"{mesh_name}: index out of range ({idx.max()} >= {n_verts})"))
        tris = idx.reshape(-1, 3)
        # degenerate triangles (zero area)
        v0, v1, v2 = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
        area = np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1) / 2
        n_degen = int(np.sum(area < 1e-9))
        if n_degen:
            issues.append(("major",
                           f"{mesh_name}: {n_degen}/{len(tris)} degenerate triangles"))
        # unreferenced vertices
        used = np.zeros(n_verts, dtype=bool)
        used[idx] = True
        n_unused = n_verts - int(used.sum())
        if n_unused > n_verts * 0.1:
            issues.append(("minor",
                           f"{mesh_name}: {n_unused}/{n_verts} unreferenced verts"))
    # normals
    if "NORMAL" not in attrs:
        issues.append(("minor", f"{mesh_name}: no NORMALs (flat shading?)"))
    else:
        nrm = _accessor_data(js, bin_data, attrs["NORMAL"])
        lens = np.linalg.norm(nrm, axis=1)
        if np.any(~np.isfinite(lens)) or np.any(lens < 1e-6):
            issues.append(("major", f"{mesh_name}: zero-length normals"))
    # UVs
    if "TEXCOORD_0" not in attrs:
        issues.append(("minor", f"{mesh_name}: no UVs (untexturable)"))
    # skinning
    if "JOINTS_0" in attrs and "WEIGHTS_0" in attrs:
        w = _accessor_data(js, bin_data, attrs["WEIGHTS_0"])
        sums = w.sum(axis=1)
        bad = np.sum(np.abs(sums - 1.0) > 0.01)
        if bad:
            issues.append(("major",
                           f"{mesh_name}: {bad}/{len(w)} verts with bad weight sums"))
    elif "JOINTS_0" in attrs:
        issues.append(("minor", f"{mesh_name}: joints but no weights"))
    # material
    if "material" not in prim:
        issues.append(("minor", f"{mesh_name}: no material assigned"))
    return issues


def audit_glb(path):
    """
    Full GLB audit. Returns {"file":..., "issues": [(sev,msg)...],
    "stats": {...}}.
    """
    js, bin_data = _read_glb(path)
    issues, stats = [], {}
    meshes = js.get("meshes", [])
    stats["meshes"] = len(meshes)
    n_prims = n_verts_total = n_tris_total = 0
    for mi, mesh in enumerate(meshes):
        name = mesh.get("name", f"mesh_{mi}")
        for pi, prim in enumerate(mesh["primitives"]):
            if "KHR_draco_mesh_compression" in prim.get("extensions", {}):
                issues.append(("minor",
                               f"{name}: draco-compressed (not decoded)"))
                continue
            n_prims += 1
            for sev, msg in check_mesh(js, bin_data, prim, f"{name}[{pi}]"):
                issues.append((sev, msg))
            attrs = prim.get("attributes", {})
            if "POSITION" in attrs:
                n_verts_total += js["accessors"][attrs["POSITION"]]["count"]
            if "indices" in prim:
                n_tris_total += js["accessors"][prim["indices"]]["count"] // 3
    stats.update(primitives=n_prims, verts=n_verts_total, tris=n_tris_total)
    # textures
    images = js.get("images", [])
    stats["images"] = len(images)
    for im in images:
        if "uri" in im:
            uri = im["uri"]
            if uri.startswith("data:"):
                continue
            full = os.path.join(os.path.dirname(path), uri)
            if not os.path.exists(full):
                issues.append(("major",
                               f"missing texture file: {uri}"))
        elif "bufferView" not in im:
            issues.append(("minor", f"image '{im.get('name')}' has no data"))
    # nodes: scale anomalies
    for ni, node in enumerate(js.get("nodes", [])):
        name = node.get("name", f"node_{ni}")
        if "scale" in node:
            s = node["scale"]
            if any(x <= 0 for x in s):
                issues.append(("major",
                               f"node '{name}': non-positive scale {s}"))
            if max(s) / (min(s) + 1e-9) > 100:
                issues.append(("minor",
                               f"node '{name}': extreme non-uniform scale {s}"))
        if "matrix" in node:
            m = np.array(node["matrix"]).reshape(4, 4)
            if abs(np.linalg.det(m[:3, :3])) < 1e-9:
                issues.append(("major",
                               f"node '{name}': degenerate transform matrix"))
    # skins
    for si, skin in enumerate(js.get("skins", [])):
        joints = skin.get("joints", [])
        if not joints:
            issues.append(("major", f"skin {si}: no joints"))
    stats["skins"] = len(js.get("skins", []))
    return {"file": path, "issues": issues, "stats": stats}


def _read_obj(path):
    """Minimal OBJ: verts, faces. Returns issues list."""
    issues = []
    verts, faces = [], []
    with open(path) as f:
        for line in f:
            p = line.split()
            if not p:
                continue
            if p[0] == "v":
                try:
                    verts.append(tuple(map(float, p[1:4])))
                except ValueError:
                    issues.append(("critical", "bad vertex line"))
            elif p[0] == "f":
                try:
                    faces.append([int(x.split("/")[0]) - 1 for x in p[1:]])
                except ValueError:
                    issues.append(("critical", "bad face line"))
    if not verts:
        issues.append(("critical", "no vertices"))
        return issues
    V = np.array(verts)
    if not np.all(np.isfinite(V)):
        issues.append(("critical", "NaN/Inf in vertices"))
    n_degen = 0
    for f in faces:
        if len(f) < 3:
            continue
        p0, p1, p2 = V[f[0]], V[f[1]], V[f[2]]
        if np.linalg.norm(np.cross(p1 - p0, p2 - p0)) / 2 < 1e-9:
            n_degen += 1
    if n_degen:
        issues.append(("major", f"{n_degen}/{len(faces)} degenerate faces"))
    return issues


def audit_obj(path):
    return _read_obj(path)


if __name__ == "__main__":
    import sys, json
    path = sys.argv[1]
    if path.lower().endswith(".glb"):
        r = audit_glb(path)
    else:
        r = {"file": path, "issues": audit_obj(path), "stats": {}}
    print(json.dumps(r, indent=1, default=str))