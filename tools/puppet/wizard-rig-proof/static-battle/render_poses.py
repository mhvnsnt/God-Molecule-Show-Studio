#!/usr/bin/env python3
"""Worker C Wave 8 — render neutral + posed frames from the Static BATTLE rig.

Uses image2live2d's own preview renderer (preview.render_pose), which mirrors
the nijilive emitter's node hierarchy: head-turn params rotate the head group
as one rigid unit about a pivot; local params (blink) stay per-vertex.
This renders the RIG DATA (meshes + parameter keyforms) emitted into
Echo.inp — a deformation proof of the actual rig, not a mockup.

Poses: neutral, head-turn (ParamAngleX/Y — no mouth param exists on a
void-face rig), blink (ParamEyeLOpen/R=0 — real closed-eye art swap).
Includes the Wave-4 preview fix: _offsets/_grouped_offsets skipped params at
value 0.0 assuming "0 = rest", but ParamEyeLOpen's rest is 1.0 (open) — the
skip now compares against each param's default.
"""
import json
import image2live2d.pipeline as P
import image2live2d.preview as PV

def _safe_synth_no_cavity_no_blush(stack) -> None:
    """Skip the anime mouth-cavity and blush painters (canon: black void face)."""
    from image2live2d.core.synth import synthesize_closed_eyes
    try:
        synthesize_closed_eyes(stack)
    except (ImportError, OSError):
        pass

P._safe_synth = _safe_synth_no_cavity_no_blush

_orig_offsets = PV._offsets
_orig_grouped = PV._grouped_offsets
def _offsets_fixed(params, settings):
    import numpy as np
    from image2live2d.preview import _interp
    acc = {}
    for p in params:
        v = settings.get(p.id, p.default)
        if v == p.default:
            continue
        for pid, arr in _interp(p, v).items():
            acc[pid] = acc.get(pid, 0) + arr
    return acc
def _grouped_fixed(params, settings, head_ids, body_ids):
    import numpy as np
    from image2live2d.preview import _interp, _HEAD_TURN, _BODY_TURN
    acc = {}
    for p in params:
        v = settings.get(p.id, p.default)
        if v == p.default:
            continue
        skip = head_ids if p.id in _HEAD_TURN else (body_ids if p.id in _BODY_TURN else set())
        for pid, arr in _interp(p, v).items():
            if pid in skip:
                continue
            acc[pid] = acc.get(pid, 0) + arr
    return acc
PV._offsets = _offsets_fixed
PV._grouped_offsets = _grouped_fixed

from image2live2d import rig_from_layer_dir
from image2live2d.core.decompose import from_layer_dir
from image2live2d.pipeline import prepare_meshes
from image2live2d.preview import render_pose  # noqa: F401 (kept for reference)
from image2live2d.preview import (_interp, _affine, _rot_about, _head_ids,
                                  _angles, _grouped_offsets)
from image2live2d.backends.nijilive.puppet import _HEAD_ROT, _BODY_ROT

def _opacity_at(params, settings):
    """{part_id: opacity} at settings, by lerping each param's
    opacity_overrides between keyforms (parts not mentioned stay 1.0).
    The stock preview.render_pose ignores opacity_overrides, so opacity-driven
    params (blink crossfade) render as no-ops. This makes the proof renders
    faithful to the rig data actually emitted into the .inp (which
    nijigenerate honours). Multiplicative combine across params."""
    import numpy as np
    op = {}
    for p in params:
        v = settings.get(p.id, p.default)
        if v == p.default:
            continue
        kfs = sorted(p.keyforms, key=lambda k: k.value)
        if not kfs:
            continue
        if v <= kfs[0].value:
            chosen = [(kfs[0], 1.0)]
        elif v >= kfs[-1].value:
            chosen = [(kfs[-1], 1.0)]
        else:
            chosen = [(kfs[0], 1.0)]
            for a, b in zip(kfs, kfs[1:]):
                if a.value <= v <= b.value:
                    t = (v - a.value) / (b.value - a.value) if b.value != a.value else 0.0
                    chosen = [(a, 1 - t), (b, t)]
                    break
        part_op = {}
        for kf, wt in chosen:
            for pid, o in (kf.opacity_overrides or {}).items():
                part_op[pid] = part_op.get(pid, 0.0) + o * wt
        for pid, o in part_op.items():
            op[pid] = op.get(pid, 1.0) * max(0.0, min(1.0, o))
    return op


def render_pose_opacity(stack, meshes, params, settings, *, res=512):
    """render_pose + per-part opacity from keyforms. Otherwise identical to
    image2live2d.preview.render_pose (same node hierarchy, same math)."""
    import numpy as np
    from PIL import Image, ImageDraw

    settings = settings or {}
    mbp = {m.part_id: m for m in meshes}
    drawn = [(L, mbp[L.id]) for L in stack.layers if L.id in mbp]
    head_ids = _head_ids(drawn)
    body_ids = {L.id for L, _ in drawn if L.id not in head_ids}
    all_pts = np.array([v for _, m in drawn for v in m.vertices], dtype=float) if drawn else np.zeros((1, 2))
    feet_pivot = ((all_pts[:, 0].min() + all_pts[:, 0].max()) / 2.0, all_pts[:, 1].min())
    hpts = np.array([v for L, m in drawn if L.id in head_ids for v in m.vertices], dtype=float)
    head_pivot = ((hpts[:, 0].min() + hpts[:, 0].max()) / 2.0, hpts[:, 1].min()) if len(hpts) else feet_pivot
    h_roll, h_yaw, h_pitch = _angles(params, settings, _HEAD_ROT)
    b_roll, b_yaw, b_pitch = _angles(params, settings, _BODY_ROT)
    offs = _grouped_offsets(params, settings, head_ids, body_ids)
    opac = _opacity_at(params, settings)
    canvas = Image.new("RGBA", (res, res), (0, 0, 0, 0))
    for layer in sorted(stack.layers, key=lambda L: L.draw_order):
        m = mbp.get(layer.id)
        if m is None:
            continue
        tex = Image.open(layer.texture_path).convert("RGBA")
        tw, th = tex.size
        verts = np.array(m.vertices, dtype=float)
        d = offs.get(layer.id)
        dv = verts + d if d is not None and len(d) == len(verts) else verts
        if layer.id in head_ids:
            dv = _rot_about(dv, head_pivot, h_roll, h_yaw, h_pitch)
            dv = _rot_about(dv, feet_pivot, b_roll, b_yaw, b_pitch)
        elif layer.id in body_ids:
            dv = _rot_about(dv, feet_pivot, b_roll, b_yaw, b_pitch)
        dst_px = np.column_stack([dv[:, 0] * res, (1 - dv[:, 1]) * res])
        src_px = np.array(m.uvs, dtype=float) * [tw, th]
        for tri in m.triangles:
            dst = [tuple(dst_px[i]) for i in tri]
            src = [tuple(src_px[i]) for i in tri]
            xs = [p[0] for p in dst]
            ys = [p[1] for p in dst]
            bx0, by0 = max(0, int(np.floor(min(xs)))), max(0, int(np.floor(min(ys))))
            bx1, by1 = min(res, int(np.ceil(max(xs)))), min(res, int(np.ceil(max(ys))))
            if bx1 - bx0 < 1 or by1 - by0 < 1:
                continue
            local = [(x - bx0, y - by0) for x, y in dst]
            coeffs = _affine(local, src)
            if coeffs is None:
                continue
            patch = tex.transform((bx1 - bx0, by1 - by0), Image.AFFINE, coeffs, resample=Image.BILINEAR)
            mask = Image.new("L", (bx1 - bx0, by1 - by0), 0)
            md = ImageDraw.Draw(mask)
            md.polygon(local, fill=255)
            md.line(local + [local[0]], fill=255, width=2)
            alpha = Image.composite(patch.getchannel("A"), mask, mask)
            layer_op = opac.get(layer.id, 1.0)
            if layer_op < 1.0:
                alpha = alpha.point(lambda v: int(v * layer_op))
            patch.putalpha(alpha)
            region = Image.alpha_composite(canvas.crop((bx0, by0, bx1, by1)), patch)
            canvas.paste(region, (bx0, by0))
    return canvas

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/static-battle"
stack = from_layer_dir(f"{OUT}/rig_layers")
_INP_PARTS = {"00_torso", "01_face_base", "02_accessory", "03_arm_r",
              "04_eye_l", "05_eye_r",
              "4_eye_closed_l", "5_eye_closed_r"}
stack.layers = [L for L in stack.layers if L.id in _INP_PARTS]
meshes = prepare_meshes(stack)
rig = rig_from_layer_dir(f"{OUT}/rig_layers", name="StaticBattle")

print("parameters:")
for p in rig.parameters:
    print(f"  {p.id}: [{p.min}, {p.max}] default={p.default} keyforms={len(p.keyforms)}")
with open(f"{OUT}/proofs/rig_parameters.json", "w") as f:
    json.dump([{"id": p.id, "min": p.min, "max": p.max, "default": p.default,
                "keyforms": len(p.keyforms)} for p in rig.parameters], f, indent=2)

RES = 960
neutral = render_pose_opacity(stack, meshes, rig.parameters, {}, res=RES)
neutral.save(f"{OUT}/proofs/static_battle_pose_neutral.png")

# posed: head turned (AngleX 15 + AngleY -10). Moderate values: the preview
# renderer's 3D head-turn breaks down into black-bar triangle artifacts past
# ~20 degrees (verified: stock render_pose does it too, and Ashes re-renders
# the same way — a preview limitation, not rig data; the .inp keyforms are
# correct and nijigenerate's emitter handles full range). No mouth param on a
# void-face rig — the black void is the mouth.
posed = render_pose_opacity(stack, meshes, rig.parameters,
                    {"ParamAngleX": 15.0, "ParamAngleY": -10.0}, res=RES)
posed.save(f"{OUT}/proofs/static_battle_pose_head-turn.png")

# blink proof: eyes closed
blink = render_pose_opacity(stack, meshes, rig.parameters,
                    {"ParamEyeLOpen": 0.0, "ParamEyeROpen": 0.0}, res=RES)
blink.save(f"{OUT}/proofs/static_battle_pose_blink.png")
print("renders saved")
