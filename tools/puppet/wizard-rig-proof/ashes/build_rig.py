#!/usr/bin/env python3
"""Worker C Wave 4 — build the Ashes nijilive rig WITHOUT the anime mouth cavity.

image2live2d's synthesize_mouth_cavity paints an anime-style mouth interior
sized from the mouth bbox. On Ashes that is a canon violation: the mouth IS
the diamond-grill grin, and the black face void behind it already reads as
the mouth interior. The pipeline's own docstring tolerates no cavity ("the
mouth simply stays shut"). We keep closed-eye synthesis (real blink) and
blush, and skip only the cavity painter via a targeted monkeypatch of
_safe_synth. Everything else in the pipeline runs unmodified.
"""
import image2live2d.pipeline as P

def _safe_synth_no_cavity(stack) -> None:
    from image2live2d.core.synth import synthesize_closed_eyes
    try:
        synthesize_closed_eyes(stack)   # an eye with no closed pose can only squash
    except (ImportError, OSError):
        pass

P._safe_synth = _safe_synth_no_cavity

from image2live2d import convert_layers

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/ashes"
result = convert_layers(f"{OUT}/rig_layers", OUT, name="Ashes")
print("wrote", result.inp_path)
print("parts:", len(result.rig.parts), "params:", len(result.rig.parameters))
print("qa passed:", result.qa.passed, "| reasons:", result.qa.reasons)
