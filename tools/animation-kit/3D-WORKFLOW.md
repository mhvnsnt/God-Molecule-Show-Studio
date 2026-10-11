# 3D WORKFLOW — recommended stack for our character work

## The stack

```
 concept art (Krita / ComfyUI notebook / TripoSR)
        │
        ▼
 Blender 4.0.2  (~/workspace/tools/blender/ — already ours)
   ├── Rigify ............ humanoid rigs built in Blender
   ├── Mixamo ............ auto-rigger + REAL mocap clips (see law below)
   ├── ArmorPaint ........ texture painting on the model
   └── Material Maker .... procedural PBR materials
        │
        ▼
 render / export (GLB for web+engines, FBX for Unity/Unreal)
```

## The law that governs all of it: NO FAKE ANIMATION

Real animation clips first — Mixamo (free, Adobe) auto-rigs a character
and gives you a huge library of real motion-capture clips. Procedural is
allowed ONLY when done well (Human Fall Flat is the bar). What is NEVER
allowed: snapping/teleporting bodies between poses with no move happening.
Every grapple shows GRAB → LIFT → LOCKUP → THROW. If a move can't get a
real clip AND can't be done well procedurally, flag it — don't ship the snap.
(Global: every game, every repo.)

## Where each piece lives

| Piece | Location / source |
|---|---|
| Blender 4.0.2 | `~/workspace/tools/blender/` (local install) |
| Mixamo | mixamo.com (free Adobe account) — rigger + clip library |
| Rigify | ships inside Blender (enable in Preferences → Add-ons) |
| ArmorPaint / Material Maker | Tier B catalog — install on his machine |
| `mesh3d/convert.py` | this kit — GLB/OBJ/STL/PLY conversion + stats |
| TripoSR notebook | Tier C — image → 3D on his free Colab GPU |
| Photogrammetry | Meshroom/COLMAP (Tier B) — phone photos → 3D sets |

## Character pipeline (the actual order of operations)

1. **Design** — concept art in Krita, or generate with the ComfyUI notebook.
2. **Model** — build in Blender, or TripoSR from concept art for props.
3. **Rig** — Rigify for full control, or Mixamo auto-rig for speed.
4. **Animate** — Mixamo mocap clips retargeted (REAL clips, per the law).
   Hand-key only what the library can't give you.
5. **Texture** — ArmorPaint for painted detail, Material Maker for surfaces.
6. **Verify** — feet above ground, facing matches movement, no clipping
   (the deliverable verification law applies to 3D too).
7. **Export** — GLB for web viewers, FBX for Unity/Unreal.

## Diagnose before repair

No rig/mesh repair runs without the diagnostic first
(`tools/rig-repair/diagnose_rig.py` pattern): rest-pose angles, skeleton
sanity, weight-bleed detection, severed-mesh check. The repair plan must
address what the diagnosis finds.
