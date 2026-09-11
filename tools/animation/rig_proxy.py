import bpy
import sys
import os

def auto_rig(input_path, output_path):
    print(f"[RIGGING] Initializing Auto-Rig for {input_path}")
    
    # Clear scene
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type='ARMATURE')
    bpy.ops.object.delete()
    
    # Import mesh
    bpy.ops.import_scene.gltf(filepath=input_path)
    
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not meshes:
        print("[ERROR] No meshes found for rigging.")
        sys.exit(1)
        
    mars_mesh = meshes[0]
    
    # Deselect all, set active to mesh
    bpy.ops.object.select_all(action='DESELECT')
    mars_mesh.select_set(True)
    bpy.context.view_layer.objects.active = mars_mesh
    
    # Create Shape Keys (Facial Controls)
    print("[RIGGING] Establishing Facial Controls (Shape Keys/Blendshapes)...")
    if not mars_mesh.data.shape_keys:
        mars_mesh.shape_key_add(name="Basis")
        
    visemes = ["viseme_A", "viseme_E", "viseme_I", "viseme_O", "viseme_U", "viseme_M", "blink_L", "blink_R", "brows_up", "brows_down"]
    for v in visemes:
        mars_mesh.shape_key_add(name=v)
        
    # Calculate bounding box to place bones
    bbox = [mars_mesh.matrix_world @ mathutils.Vector(corner) for corner in mars_mesh.bound_box]
    min_z = min([v.z for v in bbox])
    max_z = max([v.z for v in bbox])
    height = max_z - min_z
    
    # Create Armature
    print("[RIGGING] Constructing Armature...")
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, min_z))
    armature = bpy.context.active_object
    armature.name = "Mars_Rig"
    
    # Edit bones
    amt = armature.data
    bone_base = amt.edit_bones[0]
    bone_base.name = "Spine"
    bone_base.head = (0, 0, min_z + (height * 0.2))
    bone_base.tail = (0, 0, min_z + (height * 0.6))
    
    bone_neck = amt.edit_bones.new("Neck")
    bone_neck.head = bone_base.tail
    bone_neck.tail = (0, 0, min_z + (height * 0.8))
    bone_neck.parent = bone_base
    
    bone_head = amt.edit_bones.new("Head")
    bone_head.head = bone_neck.tail
    bone_head.tail = (0, 0, max_z)
    bone_head.parent = bone_neck
    
    # Jaw bone for speech fallback
    bone_jaw = amt.edit_bones.new("Jaw")
    bone_jaw.head = (0, 0.1, min_z + (height * 0.75))
    bone_jaw.tail = (0, 0.2, min_z + (height * 0.7))
    bone_jaw.parent = bone_head
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Parent Mesh to Armature with Automatic Weights
    print("[RIGGING] Binding geometry to armature (Automatic Weights)...")
    bpy.ops.object.select_all(action='DESELECT')
    mars_mesh.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    
    # Export
    print(f"[RIGGING] Exporting rigged asset to {output_path}")
    if output_path.endswith('.blend'):
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
    else:
        # Select both to export
        bpy.ops.object.select_all(action='DESELECT')
        mars_mesh.select_set(True)
        armature.select_set(True)
        bpy.ops.export_scene.gltf(filepath=output_path, use_selection=True, export_animations=False)
        
    print("[RIGGING] Pass completed successfully.")

if __name__ == "__main__":
    import mathutils
    argv = sys.argv
    try:
        index = argv.index("--") + 1
    except ValueError:
        index = len(argv)
    args = argv[index:]
    
    if len(args) < 2:
        print("Usage: blender --background --python script.py -- <in> <out>")
        sys.exit(1)
        
    auto_rig(args[0], args[1])
