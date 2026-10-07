#!/usr/bin/env python3
"""Worker C Wave 4 — render neutral + posed frames from the Ashes rig.

Uses image2live2d's own preview renderer (preview.render_pose), which mirrors
the nijilive emitter's node hierarchy: head-turn params rotate the head group
as one rigid unit about a pivot; local params (blink/mouth) stay per-vertex.
This renders the RIG DATA (meshes + parameter keyforms) that was emitted into
ashes.inp — a deformation proof of the actual rig, not a mockup.
"""
import json
import image2live2d.pipeline as P
import image2live2d.preview as PV

def _safe_synth_no_cavity(stack) -> None:
    """Skip the anime mouth-cavity painter (canon: the grill IS the mouth)."""
    from image2live2d.core.synth import synthesize_closed_eyes
    try:
        synthesize_closed_eyes(stack)
    except (ImportError, OSError):
        pass

P._safe_synth = _safe_synth_no_cavity

# The preview's _offsets/_grouped_offsets skip params at value 0.0 assuming
# "0 = rest", but ParamEyeLOpen's rest is 1.0 (open) — so a blink (0.0) was
# silently skipped. Patch the skip to compare against each param's default.
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
from image2live2d.preview import render_pose

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/ashes"
stack = from_layer_dir(f"{OUT}/rig_layers")
meshes = prepare_meshes(stack)
rig = rig_from_layer_dir(f"{OUT}/rig_layers", name="Ashes")

print("parameters:")
for p in rig.parameters:
    print(f"  {p.id}: [{p.min}, {p.max}] default={p.default} keyforms={len(p.keyforms)}")
with open(f"{OUT}/proofs/rig_parameters.json", "w") as f:
    json.dump([{"id": p.id, "min": p.min, "max": p.max, "default": p.default,
                "keyforms": len(p.keyforms)} for p in rig.parameters], f, indent=2)

RES = 864
neutral = render_pose(stack, meshes, rig.parameters, {}, res=RES)
neutral.save(f"{OUT}/proofs/ashes_pose_neutral.png")

# posed: head turned to max (AngleX 30 + AngleY -15) + grill mouth fully open
posed = render_pose(stack, meshes, rig.parameters,
                    {"ParamAngleX": 30.0, "ParamAngleY": -15.0,
                     "ParamMouthOpenY": 1.0}, res=RES)
posed.save(f"{OUT}/proofs/ashes_pose_head-turn_mouth-open.png")

# blink proof: eyes closed
blink = render_pose(stack, meshes, rig.parameters,
                    {"ParamEyeLOpen": 0.0, "ParamEyeROpen": 0.0}, res=RES)
blink.save(f"{OUT}/proofs/ashes_pose_blink.png")
print("renders saved")
