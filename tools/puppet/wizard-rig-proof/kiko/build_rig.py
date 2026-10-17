#!/usr/bin/env python3
"""Worker C Wave 5 — build the Kiko nijilive rig WITHOUT the anime painters.

image2live2d's _safe_synth would paint an anime mouth cavity, blush, and
closed eyes. On Kiko that is a canon violation: the face is a BLACK VOID —
the void already reads as the mouth interior (no mouth layer exists, so the
cavity painter is a no-op by construction), and blush would paint pink blocks
on the void. We keep ONLY closed-eye synthesis (no blink (no eye layers; see below)
glints), skipping cavity+blush via a targeted monkeypatch of _safe_synth.
Same policy as the Wave-4 Ashes rig (whose docstring wrongly said blush was
kept — the code skipped it; this docstring corrects the record).
Everything else in the pipeline runs unmodified.
"""
import image2live2d.pipeline as P

def _safe_synth_no_cavity_no_blush(stack) -> None:
    from image2live2d.core.synth import synthesize_closed_eyes
    try:
        synthesize_closed_eyes(stack)   # a glint with no closed pose can only squash
    except (ImportError, OSError):
        pass

P._safe_synth = _safe_synth_no_cavity_no_blush

from image2live2d import convert_layers

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/kiko"
result = convert_layers(f"{OUT}/rig_layers", OUT, name="Kiko")
print("wrote", result.inp_path)
print("parts:", len(result.rig.parts), "params:", len(result.rig.parameters))
print("qa passed:", result.qa.passed, "| reasons:", result.qa.reasons)

# NOTE: Kiko has NO eye layers and NO blink param. The owner-approved
# robed card shows a pure black void (max V=80; verified on the original
# webp). The "sparkly white glints" from the brief live on the GROUP-ART
# Kiko, a different source. Painting glints in would invent canon detail.
