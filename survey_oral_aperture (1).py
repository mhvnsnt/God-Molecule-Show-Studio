#!/usr/bin/env python3
"""Aperture survey that does not lie about protruding cavity material.

Rays hitting cavity in front of the lip plane are PROTRUSION_FAIL, not missing teeth.

blender -b repaired.blend --python tools/character/survey_oral_aperture.py -- \\
  --mouth-frame mouth-frame.json --output survey.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--mouth-frame", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--rays", type=int, default=64)
    return ap.parse_args(argv)


def world_bvh(ob):
    deps = bpy.context.evaluated_depsgraph_get()
    eval_ob = ob.evaluated_get(deps)
    mesh = eval_ob.to_mesh()
    try:
        mesh.transform(eval_ob.matrix_world)
        return BVHTree.FromPolygons(
            [v.co.copy() for v in mesh.vertices],
            [p.vertices for p in mesh.polygons],
        )
    finally:
        eval_ob.to_mesh_clear()


def classify(name: str) -> str:
    n = name.upper()
    if "TOOTH" in n or "TEETH" in n:
        return "teeth"
    if "GUM" in n:
        return "gums"
    if "TONGUE" in n:
        return "tongue"
    if "SOCK" in n or "CAVITY" in n or "ORAL_UPPER" in n or "ORAL_LOWER" in n:
        return "cavity"
    if "MARS" in n or "REPAIRED" in n or "CANONICAL" in n:
        return "shell"
    return "other"


def main():
    a = parse_args()
    frame = json.loads(Path(a.mouth_frame).read_text(encoding="utf-8"))
    center = Vector(frame["center"])
    left = Vector(frame["left_corner"])
    right = Vector(frame["right_corner"])
    front_z = float(frame.get("front_surface_z", center.z))
    plane_point = Vector((center.x, center.y, front_z))
    plane_normal = Vector(frame.get("outward_normal", (0.0, 0.0, 1.0))).normalized()

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.hide_render]
    trees = []
    protrusion = {}
    for ob in meshes:
        max_d = -1e9
        for v in ob.data.vertices:
            w = ob.matrix_world @ v.co
            d = (w - plane_point).dot(plane_normal)
            if d > max_d:
                max_d = d
        protrusion[ob.name] = float(max_d)
        trees.append((ob.name, classify(ob.name), world_bvh(ob), float(max_d)))

    width = (right - left).length
    hits = {"teeth": 0, "gums": 0, "tongue": 0, "cavity": 0, "shell": 0, "other": 0, "none": 0}
    protrusion_hits = 0
    cleared = 0
    n = max(4, int(a.rays ** 0.5))
    for i in range(n):
        for j in range(n):
            u = (i + 0.5) / n - 0.5
            v = (j + 0.5) / n - 0.5
            origin = plane_point + (right - left) * u + Vector((0, width * 0.35, 0)) * v
            origin = origin + plane_normal * 0.02
            direction = -plane_normal
            best = None
            best_dist = 1e9
            best_class = None
            best_protrusion = None
            for name, cls, tree, protr in trees:
                loc, _normal, _idx, dist = tree.ray_cast(origin, direction, 0.25)
                if loc is not None and dist < best_dist:
                    best_dist = dist
                    best = loc
                    best_class = cls
                    best_protrusion = protr
            if best is None:
                hits["none"] += 1
                continue
            signed = (best - plane_point).dot(plane_normal)
            if signed > 1e-4 or (best_protrusion is not None and best_protrusion > 1e-4 and best_class == "cavity"):
                protrusion_hits += 1
                hits["cavity"] += 1
                continue
            cleared += 1
            hits[best_class or "other"] += 1

    total = n * n
    behind_denom = max(cleared, 1)
    report = {
        "schema": "god-molecule.oral-aperture-survey.v2",
        "rays": total,
        "cleared_aperture_rays": cleared,
        "protrusion_intercept_rays": protrusion_hits,
        "hit_counts": hits,
        "fractions_of_all_rays": {k: hits[k] / total for k in hits},
        "fractions_behind_lip_plane": {
            k: (hits[k] / behind_denom if k in ("teeth", "gums", "tongue", "cavity", "shell", "other") else None)
            for k in hits
        },
        "object_protrusion": protrusion,
        "protrusion_gate": "FAIL" if any(p > 1e-4 for p in protrusion.values()) else "PASS",
        "note": "Use fractions_behind_lip_plane for anatomy. All-ray fractions include protrusion intercepts.",
    }
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["protrusion_gate"] == "FAIL":
        raise SystemExit("ORAL_SURVEY: PROTRUSION_FAIL")
    print("ORAL_SURVEY: OK")


if __name__ == "__main__":
    main()
