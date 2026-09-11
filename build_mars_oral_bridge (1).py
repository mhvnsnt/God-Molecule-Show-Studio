#!/usr/bin/env python3
"""Blender-side MARS oral repair.

Inputs:
  --donor-npz   output of build_gnm_oral_donor.py
  --mouth-frame measured Mars mouth frame JSON
  --output      repaired .blend

The source MARS mesh is duplicated; the canonical source object is never edited.
The GNM mouth_sock is used as the cavity cutter/liner. No sphere, cube, or
hand-built tooth row is used.

Placement law (fail-closed):
  All oral donor geometry must sit BEHIND the measured lip plane.
  A pink plank protruding past the lips is PROTRUSION_FAIL, not anatomy success.
  Solidify on the cutter is inward-only so the cavity wall does not expand through
  the aperture.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector, Matrix


DEFAULT_RECESS = 0.008
PROTRUSION_TOLERANCE = 1e-4


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--donor-npz", required=True)
    ap.add_argument("--mouth-frame", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--render-dir", default="")
    ap.add_argument("--recess", type=float, default=DEFAULT_RECESS,
                    help="Minimum distance oral donor front must sit behind lip plane")
    return ap.parse_args(argv)


def require_mesh():
    named = bpy.data.objects.get("MARS_CANONICAL")
    if named and named.type == "MESH":
        return named
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("MARS_ORAL_BRIDGE: FAIL — no mesh in source blend")
    return max(meshes, key=lambda o: len(o.data.vertices))


def collection(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(c)
    return c


def unlink_all(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)


def make_mesh(name, verts, faces, parent):
    me = bpy.data.meshes.new(name + "_MESH")
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    ob = bpy.data.objects.new(name, me)
    parent.objects.link(ob)
    return ob


def submesh(verts, faces, mask):
    face_mask = np.all(mask[np.asarray(faces, dtype=np.int32)], axis=1)
    selected = np.asarray(faces, dtype=np.int32)[face_mask]
    if len(selected) == 0:
        raise RuntimeError("MARS_ORAL_BRIDGE: empty anatomical submesh")
    used = np.unique(selected)
    remap = np.full(len(verts), -1, dtype=np.int32)
    remap[used] = np.arange(len(used), dtype=np.int32)
    return verts[used], remap[selected], used


def add_shape(ob, name, delta_by_vertex):
    if not ob.data.shape_keys:
        ob.shape_key_add(name="Basis")
    key = ob.shape_key_add(name=name)
    for i, delta in enumerate(delta_by_vertex):
        p = ob.data.vertices[i].co
        key.data[i].co = p + Vector(delta)
    return key


def world_vertices(ob):
    return np.asarray([ob.matrix_world @ v.co for v in ob.data.vertices], dtype=np.float64)


def find_front_surface(mars, center):
    pts = world_vertices(mars)
    dxy = np.linalg.norm(pts[:, :2] - np.asarray(center[:2]), axis=1)
    radius = max(float(np.ptp(pts[:, 0])) * 0.08, 1e-3)
    near = pts[dxy <= radius]
    if len(near) < 20:
        near = pts[np.argsort(dxy)[: min(200, len(pts))]]
    return float(np.percentile(near[:, 2], 95.0))


def lip_plane(frame, mars):
    center = np.asarray(frame["center"], dtype=np.float64)
    left = np.asarray(frame["left_corner"], dtype=np.float64)
    right = np.asarray(frame["right_corner"], dtype=np.float64)

    if "outward_normal" in frame:
        n = np.asarray(frame["outward_normal"], dtype=np.float64)
        n = n / max(np.linalg.norm(n), 1e-12)
        return center, n

    front_z = float(frame.get("front_surface_z", find_front_surface(mars, center)))
    point = np.array([center[0], center[1], front_z], dtype=np.float64)
    normal = np.array([0.0, 0.0, 1.0], dtype=np.float64)

    width_vec = right - left
    if np.linalg.norm(width_vec) > 1e-8:
        up = np.array([0.0, 1.0, 0.0], dtype=np.float64)
        n = np.cross(width_vec, up)
        if np.linalg.norm(n) > 1e-8:
            n = n / np.linalg.norm(n)
            if n[2] < 0:
                n = -n
            normal = n
            point = center.copy()
            point[2] = front_z

    return point, normal


def signed_distances(pts, plane_point, plane_normal):
    return (pts - plane_point) @ plane_normal


def protrusion_mm(ob, plane_point, plane_normal):
    pts = world_vertices(ob)
    if len(pts) == 0:
        return 0.0
    d = signed_distances(pts, plane_point, plane_normal)
    return float(np.max(d))


def recess_object_behind_plane(ob, plane_point, plane_normal, recess):
    pts = world_vertices(ob)
    d = signed_distances(pts, plane_point, plane_normal)
    front = float(np.percentile(d, 95.0))
    target_front = -abs(recess)
    if front <= target_front:
        return 0.0, front
    shift = Vector(((-plane_normal) * (front - target_front)).tolist())
    ob.matrix_world.translation += shift
    pts2 = world_vertices(ob)
    d2 = signed_distances(pts2, plane_point, plane_normal)
    return float(front - target_front), float(np.percentile(d2, 95.0))


def assert_no_protrusion(objects, plane_point, plane_normal, label="oral donor"):
    worst_name = None
    worst = -1e9
    report = {}
    for name, ob in objects.items():
        p = protrusion_mm(ob, plane_point, plane_normal)
        report[name] = p
        if p > worst:
            worst = p
            worst_name = name
    if worst > PROTRUSION_TOLERANCE:
        detail = ", ".join(f"{k}={v:.6f}" for k, v in report.items())
        raise RuntimeError(
            f"MARS_ORAL_BRIDGE: PROTRUSION_FAIL — {label} crosses lip plane "
            f"(worst={worst_name} protrusion={worst:.6f}; {detail}). "
            f"Pink plank / cavity-in-front-of-aperture is not anatomy success."
        )
    return report


def fit_transform(sock_verts, frame):
    center = np.asarray(frame["center"], dtype=np.float64)
    left = np.asarray(frame["left_corner"], dtype=np.float64)
    right = np.asarray(frame["right_corner"], dtype=np.float64)
    target_width = float(np.linalg.norm(left - right))
    if target_width <= 0:
        raise RuntimeError("MARS_ORAL_BRIDGE: invalid measured mouth width")

    lo = sock_verts.min(axis=0)
    hi = sock_verts.max(axis=0)
    donor_width = max(float(hi[0] - lo[0]), 1e-8)
    scale = target_width / donor_width

    roll = math.radians(float(frame.get("roll_degrees", 0.0)))
    rot = Matrix.Rotation(roll, 4, "Z")

    donor_center = (lo + hi) * 0.5
    scaled_center = Vector((donor_center * scale).tolist())
    trans = Vector(center.tolist()) - (rot @ scaled_center)
    mat = Matrix.Translation(trans) @ rot @ Matrix.Diagonal((scale, scale, scale, 1.0))
    return mat, scale


def solidify_cutter_inward(sock, thickness=0.012):
    bpy.context.view_layer.objects.active = sock
    sock.select_set(True)
    mod = sock.modifiers.new("ORAL_SOCK_SOLIDIFY", "SOLIDIFY")
    mod.thickness = thickness
    mod.offset = -1.0  # inward only — offset=0 produced the pink plank
    bpy.ops.object.modifier_apply(modifier=mod.name)
    sock.select_set(False)


def boolean_cavity(mars, cutter):
    bpy.context.view_layer.objects.active = mars
    mod = mars.modifiers.new("MARS_ORAL_CAVITY_BOOLEAN", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if len(mars.data.vertices) == 0:
        raise RuntimeError("MARS_ORAL_BRIDGE: boolean destroyed Mars mesh")


def main():
    a = args()
    donor_path = Path(a.donor_npz).resolve()
    frame_path = Path(a.mouth_frame).resolve()
    out = Path(a.output).resolve()
    if not donor_path.is_file() or not frame_path.is_file():
        raise SystemExit("MARS_ORAL_BRIDGE: FAIL — donor or measured mouth frame missing")

    donor = np.load(donor_path, allow_pickle=False)
    frame = json.loads(frame_path.read_text(encoding="utf-8"))
    for key in ("center", "left_corner", "right_corner"):
        if key not in frame:
            raise RuntimeError(f"MARS_ORAL_BRIDGE: measured mouth frame missing {key}")

    mars = require_mesh()
    original_count = len(mars.data.vertices)
    repaired = mars.copy()
    repaired.data = mars.data.copy()
    repaired.name = "MARS_ORAL_REPAIRED_SURFACE"
    repaired_coll = collection("MARS_ORAL_REPAIR")
    unlink_all(repaired)
    repaired_coll.objects.link(repaired)

    v = np.asarray(donor["vertices"], dtype=np.float64)
    f = np.asarray(donor["faces"], dtype=np.int32)
    jaw = np.asarray(donor["jaw_open_delta"], dtype=np.float64)

    masks = {
        "sock": np.asarray(donor["mouth_sock_mask"], dtype=bool),
        "upper": np.asarray(donor["upper_mask"], dtype=bool),
        "lower": np.asarray(donor["lower_mask"], dtype=bool),
        "teeth": np.asarray(donor["teeth_mask"], dtype=bool),
        "gums": np.asarray(donor["gums_mask"], dtype=bool),
        "tongue": np.asarray(donor["tongue_mask"], dtype=bool),
    }

    mat, scale = fit_transform(v[masks["sock"]], frame)
    plane_point, plane_normal = lip_plane(frame, repaired)
    recess = float(a.recess)

    objs = {}
    for tag in ("sock", "upper", "lower", "tongue"):
        sv, sf, used = submesh(v, f, masks[tag])
        ob = make_mesh("MARS_ORAL_" + tag.upper(), sv, sf, repaired_coll)
        ob.matrix_world = mat.copy()
        objs[tag] = (ob, used)

        local_jaw = jaw[used] * scale
        if tag in ("lower", "tongue"):
            add_shape(ob, "jaw_open", local_jaw)
        else:
            add_shape(ob, "jaw_open", np.zeros_like(local_jaw))

    oral_objects = {tag: objs[tag][0] for tag in objs}
    recess_report = {}
    for tag, ob in oral_objects.items():
        moved, front_after = recess_object_behind_plane(
            ob, plane_point, plane_normal, recess
        )
        recess_report[tag] = {"moved": moved, "front_signed": front_after}

    assert_no_protrusion(
        oral_objects, plane_point, plane_normal, label="oral donor pre-boolean"
    )

    sock = objs["sock"][0]

    cutter = sock.copy()
    cutter.data = sock.data.copy()
    cutter.name = "MARS_ORAL_CAVITY_CUTTER"
    repaired_coll.objects.link(cutter)
    cutter.matrix_world = sock.matrix_world.copy()
    cutter.scale = cutter.scale * 1.02
    cutter.matrix_world.translation += Vector(((-plane_normal) * (recess * 0.5)).tolist())
    solidify_cutter_inward(cutter, thickness=0.010)

    cutter_protrusion = protrusion_mm(cutter, plane_point, plane_normal)
    if cutter_protrusion > PROTRUSION_TOLERANCE:
        cutter.matrix_world.translation += Vector(
            ((-plane_normal) * (cutter_protrusion + recess * 0.25)).tolist()
        )
        cutter_protrusion = protrusion_mm(cutter, plane_point, plane_normal)
        if cutter_protrusion > PROTRUSION_TOLERANCE:
            raise RuntimeError(
                f"MARS_ORAL_BRIDGE: PROTRUSION_FAIL — cavity cutter still past lip plane "
                f"(protrusion={cutter_protrusion:.6f}). Inward solidify/recess insufficient."
            )

    boolean_cavity(repaired, cutter)
    bpy.data.objects.remove(cutter, do_unlink=True)

    protrusion_after = assert_no_protrusion(
        oral_objects, plane_point, plane_normal, label="oral donor post-boolean"
    )

    lower_delta = jaw[masks["lower"]]
    travel = float(np.linalg.norm(np.mean(lower_delta, axis=0)) * scale)
    if travel <= 1e-5:
        raise RuntimeError("MARS_ORAL_BRIDGE: GNM jaw-open donor has zero lower travel")

    pts = world_vertices(repaired)
    c = np.asarray(frame["center"], dtype=np.float64)
    width = float(np.linalg.norm(
        np.asarray(frame["left_corner"]) - np.asarray(frame["right_corner"])
    ))
    half_w = max(width * 0.5, 1e-6)
    height = max(width * 0.45, 1e-6)
    deltas_world = np.zeros_like(pts)

    for i, p in enumerate(pts):
        nx = (p[0] - c[0]) / half_w
        ny = (p[1] - c[1]) / height
        radial = nx * nx + ny * ny
        if ny < -0.02 and radial <= 1.25:
            w = max(0.0, 1.0 - radial / 1.25)
            w = w * w * (3.0 - 2.0 * w)
            deltas_world[i, 1] -= travel * w

    inv3 = repaired.matrix_world.to_3x3().inverted()
    local_delta = np.asarray([inv3 @ Vector(d) for d in deltas_world])
    add_shape(repaired, "jaw_open", local_delta)

    key = repaired.data.shape_keys.key_blocks["jaw_open"]
    for name, factor in (("AA", 1.0), ("OH", 0.78), ("EE", 0.28), ("MM", 0.0)):
        k = repaired.shape_key_add(name=name)
        for i, p in enumerate(key.data):
            base = repaired.data.vertices[i].co
            delta = Vector(p.co) - Vector(base)
            if name == "EE":
                w = max(0.0, 1.0 - abs((repaired.matrix_world @ base).x - c[0]) / half_w)
                k.data[i].co = Vector(base) + delta * factor + Vector((0.002 * w, 0, 0))
            elif name == "MM":
                k.data[i].co = Vector(base)
            else:
                k.data[i].co = Vector(base) + delta * factor

    repaired["mars_source_object"] = mars.name
    repaired["mars_source_vertex_count"] = original_count
    repaired["oral_donor"] = "Google GNM Head v3 / Apache-2.0"
    repaired["cavity_source"] = "GNM mouth_sock"
    repaired["sphere_cavity"] = False
    repaired["procedural_tooth_grid"] = False
    repaired["measured_mouth_frame"] = str(frame_path)
    repaired["jaw_open_source"] = "GNM canonical mouth-open expression"
    repaired["donor_scale"] = scale
    repaired["lower_dental_travel"] = travel
    repaired["lip_plane_point"] = plane_point.tolist()
    repaired["lip_plane_normal"] = plane_normal.tolist()
    repaired["oral_recess"] = recess
    repaired["protrusion_gate"] = "FAIL_CLOSED"
    repaired["protrusion_report"] = json.dumps(protrusion_after)
    repaired["recess_report"] = json.dumps(recess_report)

    mars.hide_render = True
    mars.hide_viewport = True
    repaired.hide_render = False
    repaired.hide_viewport = False

    if a.render_dir:
        render_dir = Path(a.render_dir).resolve()
        render_dir.mkdir(parents=True, exist_ok=True)
        bpy.context.scene.render.filepath = str(render_dir / "mars_oral_preview.png")
        bpy.context.scene.render.resolution_x = 854
        bpy.context.scene.render.resolution_y = 480
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.frame_set(1)
        bpy.ops.render.render(write_still=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    print("MARS_ORAL_BRIDGE: VERIFIED")
    print(f"SOURCE_VERTICES={original_count}")
    print(f"REPAIRED_VERTICES={len(repaired.data.vertices)}")
    print(f"LOWER_DENTAL_TRAVEL={travel:.6f}")
    print(f"ORAL_RECESS={recess:.6f}")
    print(f"PROTRUSION={json.dumps(protrusion_after)}")
    print("CAVITY=GNM_MOUTH_SOCK")
    print("SOLIDIFY=INWARD_ONLY")
    print("SPHERE_CAVITY=FALSE")
    print("PROTRUSION_GATE=PASS")
    print("MARS_IDENTITY_REPLACEMENT=FALSE")


if __name__ == "__main__":
    main()
