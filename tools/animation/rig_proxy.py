import bpy
import sys
import os
import mathutils


RHUBARB_CONTROLS = [
    "viseme_A", "viseme_B", "viseme_C", "viseme_D",
    "viseme_E", "viseme_F", "viseme_G", "viseme_H", "viseme_X",
    "blink_L", "blink_R", "brows_up", "brows_down",
]


def auto_rig(input_path, output_path):
    print(f"[RIGGING] Initializing Auto-Rig for {input_path}")

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type='ARMATURE')
    bpy.ops.object.delete()

    bpy.ops.import_scene.gltf(filepath=input_path)
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not meshes:
        raise RuntimeError("No meshes found for rigging.")

    mars_mesh = meshes[0]
    bpy.ops.object.select_all(action='DESELECT')
    mars_mesh.select_set(True)
    bpy.context.view_layer.objects.active = mars_mesh

    print("[RIGGING] Establishing complete Rhubarb facial control set...")
    if not mars_mesh.data.shape_keys:
        mars_mesh.shape_key_add(name="Basis")
    existing = {k.name for k in mars_mesh.data.shape_keys.key_blocks}
    for name in RHUBARB_CONTROLS:
        if name not in existing:
            mars_mesh.shape_key_add(name=name)

    bbox = [mars_mesh.matrix_world @ mathutils.Vector(corner) for corner in mars_mesh.bound_box]
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)
    height = max_z - min_z

    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, min_z))
    armature = bpy.context.active_object
    armature.name = "Mars_Rig"
    amt = armature.data

    bone_base = amt.edit_bones[0]
    bone_base.name = "Spine"
    bone_base.head = (0, 0, min_z + height * 0.2)
    bone_base.tail = (0, 0, min_z + height * 0.6)

    bone_neck = amt.edit_bones.new("Neck")
    bone_neck.head = bone_base.tail
    bone_neck.tail = (0, 0, min_z + height * 0.8)
    bone_neck.parent = bone_base

    bone_head = amt.edit_bones.new("Head")
    bone_head.head = bone_neck.tail
    bone_head.tail = (0, 0, max_z)
    bone_head.parent = bone_neck

    bone_jaw = amt.edit_bones.new("Jaw")
    bone_jaw.head = (0, 0.1, min_z + height * 0.75)
    bone_jaw.tail = (0, 0.2, min_z + height * 0.7)
    bone_jaw.parent = bone_head

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    mars_mesh.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    if output_path.endswith('.blend'):
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
    else:
        bpy.ops.object.select_all(action='DESELECT')
        mars_mesh.select_set(True)
        armature.select_set(True)
        bpy.ops.export_scene.gltf(filepath=output_path, use_selection=True, export_animations=False)

    print("[RIGGING] Complete Rhubarb control set exported.")


if __name__ == "__main__":
    argv = sys.argv
    try:
        index = argv.index("--") + 1
    except ValueError:
        index = len(argv)
    args = argv[index:]
    if len(args) < 2:
        print("Usage: blender --background --python script.py -- <in> <out>")
        sys.exit(2)
    try:
        auto_rig(args[0], args[1])
    except Exception as exc:
        print(f"[BLOCKED] {exc}")
        sys.exit(1)
