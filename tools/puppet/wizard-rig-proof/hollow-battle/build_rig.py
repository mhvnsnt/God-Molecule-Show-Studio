#!/usr/bin/env python3
"""Worker C Wave 10 — build the HOLLOW BATTLE nijilive rig WITHOUT the anime
painters.

image2live2d's _safe_synth would paint an anime mouth cavity, blush, and
closed eyes. On Hollow that is a canon violation: the face is a BLACK VOID —
the void already reads as the mouth interior (no mouth layer exists, so the
cavity painter is a no-op by construction), and blush would paint blocks
on the void. We keep ONLY closed-eye synthesis (real blink for the white
glints), skipping cavity+blush via a targeted monkeypatch of _safe_synth.
Same policy as the Wave-4 Ashes rig and all battle rigs since.
Everything else in the pipeline runs unmodified.

Assembly: parts/ -> rig_layers/{order}_{role}.png. The eye L/R split is done
manually at the face midline (x=462) as full-canvas masked halves (Wave-8
lesson: never crop eyes) — the pipeline has no combined-eyes role.
"""
import image2live2d.pipeline as P
import shutil
import os
import json
import numpy as np
from PIL import Image

def _safe_synth_no_cavity_no_blush(stack) -> None:
    from image2live2d.core.synth import synthesize_closed_eyes
    try:
        synthesize_closed_eyes(stack)
    except (ImportError, OSError):
        pass

P._safe_synth = _safe_synth_no_cavity_no_blush

from image2live2d import convert_layers

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/hollow-battle"
RL = os.path.join(OUT, "rig_layers")
os.makedirs(RL, exist_ok=True)
parts = os.path.join(OUT, "parts")
for src, dst in [("01_robe.png", "00_torso.png"),
                 ("02_head.png", "01_face_base.png")]:
    shutil.copy(os.path.join(parts, src), os.path.join(RL, dst))

# eye split L/R at the face midline (x=462, measured from parts/_eye_split.json)
with open(os.path.join(parts, "_eye_split.json")) as f:
    split_x = json.load(f)["split_x"]
eyes = Image.open(os.path.join(parts, "03_eyes.png")).convert("RGBA")
ea = np.array(eyes)
W = ea.shape[1]
left = ea.copy(); left[:, split_x:, 3] = 0
right = ea.copy(); right[:, :split_x, 3] = 0
Image.fromarray(left).save(os.path.join(RL, "02_eye_l.png"))
Image.fromarray(right).save(os.path.join(RL, "03_eye_r.png"))
print("eye split at x=%d; L px=%d R px=%d" % (split_x, (left[:, :, 3] > 0).sum(), (right[:, :, 3] > 0).sum()))

# blush trap check (Wave-9 hygiene): never ship a stray blush layer
blush = [f for f in os.listdir(RL) if "blush" in f.lower()]
assert not blush, f"blush contamination: {blush}"
print("assembled", sorted(os.listdir(RL)))

result = convert_layers(RL, OUT, name="HollowBattle")
print("wrote", result.inp_path)
print("parts:", len(result.rig.parts), "params:", len(result.rig.parameters))
print("qa passed:", result.qa.passed, "| reasons:", result.qa.reasons)
