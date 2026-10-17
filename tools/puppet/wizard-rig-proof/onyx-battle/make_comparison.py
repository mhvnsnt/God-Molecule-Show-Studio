#!/usr/bin/env python3
"""Worker C Wave 9 — Onyx Negra BATTLE comparison render: canon source crop
vs the rig's neutral pose, side by side."""
from PIL import Image
import os

OUT = "/home/hatch/workspace/god-molecule-studio/tools/puppet/wizard-rig-proof/onyx-battle"
src = Image.open(os.path.join(OUT, "onyx_battle_crop_source.png")).convert("RGB")
rig = Image.open(os.path.join(OUT, "proofs/onyx_battle_pose_neutral.png")).convert("RGBA")

H = 900
src_r = src.resize((int(src.width * H / src.height), H))
# rig render on checkerboard-ish neutral gray to show transparency honestly
bg = Image.new("RGB", rig.size, (40, 40, 48))
bg.paste(rig, mask=rig.split()[3])
rig_r = bg.resize((int(bg.width * H / bg.height), H))

comp = Image.new("RGB", (src_r.width + rig_r.width + 20, H), (20, 20, 24))
comp.paste(src_r, (0, 0))
comp.paste(rig_r, (src_r.width + 20, 0))
comp.save(os.path.join(OUT, "proofs/onyx_battle_comparison.png"))
print("comparison saved", comp.size)
