#!/usr/bin/env python3
"""Build the Ashes nijilive rig WITHOUT the anime mouth cavity.

image2live2d's synthesize_mouth_cavity paints an anime-style mouth interior
sized from the mouth bbox. On Ashes that is a canon violation: the mouth IS
the diamond-grill grin, and the black face void behind it already reads as
the mouth interior. The pipeline's own docstring tolerates no cavity ("the
mouth simply stays shut"). We keep closed-eye synthesis (real blink) and
blush, and skip only the cavity painter via a targeted monkeypatch of
_safe_synth. Everything else in the pipeline runs unmodified.

Paths are relative to this script's folder (the Wave-4 version hardcoded a
stale absolute workspace path). Layer input: rig_layers/ in this folder —
after the 2026-10-29 part-separation repair that is the v2 stack
(19 parts; see RIG_REPAIR_BRAIDFIX_2026-10-29.md). Do NOT drop a
mouth_cavity layer into rig_layers/: build artifacts must not be committed
as parts (the stray 9_mouth_cavity.png removed by the repair loaded as a
phantom part and painted over the grill).
"""
import os

import image2live2d.pipeline as P


def _safe_synth_no_cavity(stack) -> None:
    from image2live2d.core.synth import synthesize_closed_eyes
    try:
        synthesize_closed_eyes(stack)   # an eye with no closed pose can only squash
    except (ImportError, OSError):
        pass


P._safe_synth = _safe_synth_no_cavity

# Mesh density: the default 14x14 grid leaves coverage holes in thin parts
# (measured on the repaired stack: a 130 px hole in the grill's left half,
# visible as a black notch at rest). At 28x28 the measured holes are:
# mouth 0, face 0, neck 0, braids 10/3 px. See the repair doc.
_orig_build_meshes = P.mesh.build_meshes
P.mesh.build_meshes = lambda stack: _orig_build_meshes(stack, grid=28)

from image2live2d import convert_layers

OUT = os.path.dirname(os.path.abspath(__file__))
result = convert_layers(os.path.join(OUT, "rig_layers"), OUT, name="Ashes")
print("wrote", result.inp_path)
print("parts:", len(result.rig.parts), "params:", len(result.rig.parameters))
print("qa passed:", result.qa.passed, "| reasons:", result.qa.reasons)
