# Model 3D Placement Tool Artifact Blender Prisma 3D Replacer

A real 3D viewport for placing a part (tail, accessory, armor piece, anything)
onto a character model. Orbit like Blender, grab the move gizmo on the part,
drag it through actual 3D space, fine-tune with sliders, hit Save and send the
numbers back — they go straight into the rig.

## Use

1. Export two GLBs from Blender (see `export_placer_glbs.py`):
   - `body.glb` — the character, everything except the part (baked transforms).
   - `part.glb` — the part alone, with its origin at the attachment point.
2. Commit both GLBs to the repo.
3. Open `model-3d-placement-tool.html` in a browser (or the chat widget) with params:
   - `?body=<URL-to-body.glb>&part=<URL-to-part.glb>&name=<part-name>`
   - Defaults to the Pantera body/tail if no params given.
   - GitHub raw URLs work: `https://raw.githubusercontent.com/<user>/<repo>/main/<path>/<file>.glb`
4. Drag to orbit, pinch to zoom, two fingers to pan. Grab the arrow gizmo to
   move the part. Sliders give fine X/Y/Z control plus scale.
5. Hit **Save** — it copies `X=___ Y=___ Z=___ Scale=___`, the part's offset
   from its starting position in model units. Send those numbers back and the
   rig gets updated to match.

## Notes

- The part GLB's origin should sit at the attachment point so it scales and
  rotates around the right spot.
- Body and part must come from the same scene/scale so the offsets map 1:1.
- Needs internet for the Three.js CDN. Models load from whatever URLs you pass.
