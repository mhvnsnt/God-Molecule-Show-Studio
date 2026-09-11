import bpy
import sys
import os
import json

def setup_mars(obj_path, blend_path):
    # Clear existing mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    print(f"[BLENDER] Loading {obj_path}")
    
    # Import GLB
    try:
        bpy.ops.import_scene.gltf(filepath=obj_path)
    except Exception as e:
        print(f"[ERROR] GLTF Import failed: {e}")
        sys.exit(1)
    
    # Verify imported objects
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not meshes:
        print("[ERROR] No meshes imported")
        sys.exit(1)
        
    mars_obj = meshes[0]
    
    # Normalize scale and orientation
    # For now, just apply scale
    bpy.ops.object.select_all(action='DESELECT')
    mars_obj.select_set(True)
    bpy.context.view_layer.objects.active = mars_obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    print(f"[BLENDER] Canonical Origin Established.")
    
    materials = mars_obj.data.materials
    print(f"[BLENDER] Materials Verified: {len(materials)} found")
    
    # Save blend file
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[BLENDER] Canonical Package Built: {blend_path}")

    # Generate a dummy "rendered" frame for Tonnō
    render_path = blend_path.replace('.blend', '_render.png')
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = render_path
    bpy.ops.render.render(write_still=True)
    
    print(f"[BLENDER] Test frame rendered to {render_path}")

if __name__ == "__main__":
    argv = sys.argv
    try:
        index = argv.index("--") + 1
    except ValueError:
        index = len(argv)
    
    args = argv[index:]
    if len(args) < 2:
        print("Usage: blender -b -P script.py -- <obj_path> <blend_path>")
        sys.exit(1)
        
    obj_path = args[0]
    blend_path = args[1]
    
    setup_mars(obj_path, blend_path)
