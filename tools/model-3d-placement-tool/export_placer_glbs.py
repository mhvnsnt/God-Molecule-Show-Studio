"""Export body + part GLBs for the Model 3D Placement Tool.

Split-exports the current Blender scene into two GLBs:
  - <out>_body.glb : every mesh EXCEPT the part (transforms baked, static)
  - <out>_part.glb : the part object alone, origin kept at its attachment
    point, transforms NOT baked (so the viewer reads its start position)

CONFIG section below: point it at your files, name your part object,
optionally downscale textures for phone-friendly files.

Run headless:
  env -u PYTHONPATH <blender> -b --python export_placer_glbs.py
"""
import bpy, os

# ---------------- CONFIG ----------------
FBX_PATH   = os.path.expanduser("~/workspace/game-reverse-engineering/tekken7/king/5PMH7G85GYN7P71W3BD1V0249.fbx")
MODEL_SCALE = 100.0          # multiply imported object scales by this
PART_NAME   = "PanteraTail"  # object name of the part (must exist in scene)
OUT_DIR     = "/tmp"
OUT_BASENAME = "model"       # produces <OUT_BASENAME>_body.glb + _part.glb
TEX_MAX     = 512            # downscale textures larger than this (0 = skip)
# ----------------------------------------

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_PATH)
for o in bpy.context.scene.objects:
    o.scale = tuple(s * MODEL_SCALE for s in o.scale)
bpy.context.view_layer.update()

# NOTE: build your part mesh here (or import it) and name it PART_NAME,
# with its origin at the attachment point. Example (tail from a curve):
#   bpy.ops.curve.primitive_bezier_curve_add(location=tail_base)
#   ... shape it ...
#   bpy.ops.object.convert(target='MESH')
#   bpy.context.active_object.name = PART_NAME

if TEX_MAX:
    for img in bpy.data.images:
        if img.size[0] > TEX_MAX:
            img.scale(img.size[0] // 2, img.size[1] // 2)

bpy.ops.object.select_all(action='DESELECT')
part = bpy.data.objects.get(PART_NAME)
assert part is not None, f"part object '{PART_NAME}' not found in scene"
part.select_set(True)
bpy.context.view_layer.objects.active = part
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT_DIR, f"{OUT_BASENAME}_part.glb"),
    use_selection=True, export_apply=False,
    export_materials='EXPORT', export_image_format='AUTO')

bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type == 'MESH' and o.name != PART_NAME:
        o.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT_DIR, f"{OUT_BASENAME}_body.glb"),
    use_selection=True, export_apply=True,
    export_materials='EXPORT', export_image_format='AUTO')

print("EXPORT DONE:",
      os.path.join(OUT_DIR, f"{OUT_BASENAME}_body.glb"),
      os.path.join(OUT_DIR, f"{OUT_BASENAME}_part.glb"))
