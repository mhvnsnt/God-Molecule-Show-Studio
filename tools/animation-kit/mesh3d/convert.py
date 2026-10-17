#!/usr/bin/env python3
"""convert.py — 3D model format conversion + inspection via trimesh.
GLB <-> OBJ <-> STL <-> PLY, plus a quick stats report.

Usage: convert.py --input model.glb --output model.obj [--info]
"""
import argparse
import json
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--info", action="store_true",
                    help="also write <output>.info.json with mesh stats")
    a = ap.parse_args()
    import trimesh
    scene = trimesh.load(a.input, force="scene")
    if isinstance(scene, trimesh.Scene):
        geoms = list(scene.geometry.values())
        mesh = trimesh.util.concatenate(geoms) if geoms else None
    else:
        mesh = scene
    if mesh is None:
        raise SystemExit("no geometry found in " + a.input)
    mesh.export(a.output)
    info = {
        "input": a.input, "output": a.output,
        "vertices": int(len(mesh.vertices)), "faces": int(len(mesh.faces)),
        "bounds": mesh.bounds.tolist(),
        "watertight": bool(mesh.is_watertight),
        "volume": float(mesh.volume) if mesh.is_watertight else None,
    }
    print(json.dumps({k: v for k, v in info.items() if k != "bounds"},
                     indent=1))
    if a.info:
        jp = a.output + ".info.json"
        json.dump(info, open(jp, "w"), indent=1)
        print("info ->", jp)


if __name__ == "__main__":
    main()
