#!/usr/bin/env python3
"""Worker C Wave 9 — build the Sombra Negra BATTLE nijilive rig WITHOUT the
anime painters.

image2live2d's _safe_synth would paint an anime mouth cavity, blush, and
closed eyes. On Sombra Negra that is a canon violation: the face is a BLACK
VOID — the void already reads as the mouth interior (no mouth layer exists,
so the cavity painter is a no-op by construction), and blush would paint
blocks on the void. We keep ONLY closed-eye synthesis (real blink for the
white glints), skipping cavity+blush via a targeted monkeypatch of
_safe_synth. Same policy as the Wave-4 Ashes rig and all battle rigs since.
Everything else in the pipeline runs unmodified.

Assembly: parts/ -> rig_layers/{order}_{role}.png; the pipeline's
See-through auto-split turns the combined 04_eyes layer into eye_l/eye_r.
"""
import image2live2d.pipeline as P
import shutil
import os

def _safe_synth_no_cavity_no_blush(stack) -> None:
    from image2live2d.core.synth import synthesize_closed_eyes
    try:
        synthesize_closed_eyes(stack)
    except (ImportError, OSError):
        pass

P._safe_synth = _safe_synth_no_cavity_no_blush

from image2live2d import convert_layers

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/sombra-battle"
RL = os.path.join(OUT, "rig_layers")
os.makedirs(RL, exist_ok=True)
parts = os.path.join(OUT, "parts")
for src, dst in [("01_robe.png", "00_torso.png"),
                 ("02_head.png", "01_face_base.png"),
                 ("03_accessory.png", "02_accessory.png")]:
    shutil.copy(os.path.join(parts, src), os.path.join(RL, dst))
# eye split L/R at the face midline (x=186) done before this script;
# see build log. rig_layers/04_eye_l.png, 05_eye_r.png are full-canvas
# masked halves (Wave-8 lesson: never crop eyes).
print("assembled", sorted(os.listdir(RL)))

result = convert_layers(RL, OUT, name="SombraBattle")
print("wrote", result.inp_path)
print("parts:", len(result.rig.parts), "params:", len(result.rig.parameters))
print("qa passed:", result.qa.passed, "| reasons:", result.qa.reasons)
