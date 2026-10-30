#!/usr/bin/env python3
"""Render the TURNFIX proof video from Ashes_turnfix3.inp.

Choreography per the owner's acceptance (holds are the point, so it
cannot read as a sway):
  neutral hold 0.5s -> turn LEFT hold -> neutral -> turn RIGHT hold ->
  neutral -> nod DOWN, hold -> up -> nod DOWN, hold -> neutral.
24 fps, poses change on 2s (every 2nd frame), eased with cosine.
Unique poses are rendered once (multiprocessing, 2 workers) and
repeated for holds.
"""
import math
import os
from multiprocessing import Pool

import render_turnfix as R

FPS = 24
DUR = 11.5
NFRAMES = int(FPS * DUR)

def track(keys):
    keys = sorted(keys)
    def at(t):
        if t <= keys[0][0]:
            return keys[0][1]
        if t >= keys[-1][0]:
            return keys[-1][1]
        for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0)
                e = 0.5 - 0.5 * math.cos(math.pi * u)
                return v0 + (v1 - v0) * e
        return keys[-1][1]
    return at

ax_track = track([(0, 0), (0.5, 0), (1.5, -30), (3.0, -30), (3.9, 0),
                  (4.4, 0), (5.4, 30), (6.9, 30), (7.8, 0), (11.5, 0)])
ay_track = track([(0, 0), (8.2, 0), (8.8, -30), (9.4, -30), (9.8, 0),
                  (10.2, -30), (10.9, -30), (11.5, 0)])

# unique poses on 2s: quantise time to even frames
pose_keys = {}
for f in range(NFRAMES):
    t = (f // 2 * 2) / FPS
    key = (round(ax_track(t), 2), round(ay_track(t), 2))
    pose_keys.setdefault(key, []).append(f)

print(f"{NFRAMES} frames, {len(pose_keys)} unique poses")

_N = {}
def init():
    global _N
    _N["nodes"], _N["params"], _N["textures"] = R.load_inp("Ashes.inp")

def job(key):
    ax, ay = key
    img = R.render(_N["nodes"], _N["params"], _N["textures"], ax, ay)
    path = f"vidframes/pose_{ax:+.2f}_{ay:+.2f}.png"
    img.save(path)
    return path

if __name__ == "__main__":
    os.makedirs("vidframes", exist_ok=True)
    keys = list(pose_keys.keys())
    with Pool(2, initializer=init) as pool:
        paths = pool.map(job, keys)
    lut = dict(zip(keys, paths))
    # assemble frame sequence
    import shutil
    os.makedirs("vidseq", exist_ok=True)
    for f in range(NFRAMES):
        t = (f // 2 * 2) / FPS
        key = (round(ax_track(t), 2), round(ay_track(t), 2))
        dst = f"vidseq/f_{f:04d}.png"
        if os.path.exists(dst):
            os.remove(dst)
        os.link(lut[key], dst)
    print("sequence assembled")
