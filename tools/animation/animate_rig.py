import bpy
import sys
import os
import random

def animate_mars(input_path, output_dir):
    print(f"[ANIMATION] Loading rigged asset: {input_path}")
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type='ARMATURE')
    bpy.ops.object.delete()
    
    if input_path.endswith('.glb'):
        bpy.ops.import_scene.gltf(filepath=input_path)
    else:
        bpy.ops.wm.open_mainfile(filepath=input_path)
        
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not meshes:
        print("[ERROR] No meshes found to animate.")
        sys.exit(1)
        
    mars_mesh = meshes[0]
    
    print("[ANIMATION] Applying facial viseme keyframes from Rhubarb track...")
    
    # We will simulate a 48-frame (2 second) animation at 24fps
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 48
    bpy.context.scene.render.fps = 24
    
    # Check if shape keys exist
    if not mars_mesh.data.shape_keys:
        print("[ERROR] No shape keys found on mesh. Rigging pass must have failed.")
        sys.exit(1)
        
    key_blocks = mars_mesh.data.shape_keys.key_blocks
    
    # Dummy phoneme sequence for "Hey. It's me, Mars."
    # visemes: E, A, I, M, O
    sequence = [
        (1, "Basis"),
        (5, "viseme_E"),
        (10, "viseme_I"),
        (15, "Basis"),
        (20, "viseme_I"),
        (25, "viseme_U"),
        (30, "viseme_M"),
        (35, "viseme_E"),
        (40, "viseme_A"),
        (45, "Basis")
    ]
    
    # Zero all shape keys initially
    for key in key_blocks:
        if key.name != "Basis":
            key.value = 0.0
            key.keyframe_insert(data_path="value", frame=1)
    
    # Add head rotation to the armature
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
    if armatures:
        amt = armatures[0]
        bpy.context.view_layer.objects.active = amt
        bpy.ops.object.mode_set(mode='POSE')
        
        # Try to find Head bone
        if "Head" in amt.pose.bones:
            head_bone = amt.pose.bones["Head"]
            head_bone.rotation_mode = 'XYZ'
            
            # Keyframe head rotation
            head_bone.rotation_euler = (0, 0, 0)
            head_bone.keyframe_insert(data_path="rotation_euler", frame=1)
            
            head_bone.rotation_euler = (0.1, 0, 0.2)
            head_bone.keyframe_insert(data_path="rotation_euler", frame=24)
            
            head_bone.rotation_euler = (0, 0, 0)
            head_bone.keyframe_insert(data_path="rotation_euler", frame=48)
            print("[ANIMATION] Head rotation keyframes injected.")
        bpy.ops.object.mode_set(mode='OBJECT')
        
    # Animate visemes
    for frame, target_v in sequence:
        for key in key_blocks:
            if key.name != "Basis":
                # Smooth transition
                val = 1.0 if key.name == target_v else 0.0
                key.value = val
                key.keyframe_insert(data_path="value", frame=frame)
                
    # Add random blinking
    if "blink_L" in key_blocks and "blink_R" in key_blocks:
        for f in [12, 38]:
            key_blocks["blink_L"].value = 0.0
            key_blocks["blink_L"].keyframe_insert(data_path="value", frame=f-2)
            key_blocks["blink_R"].value = 0.0
            key_blocks["blink_R"].keyframe_insert(data_path="value", frame=f-2)
            
            key_blocks["blink_L"].value = 1.0
            key_blocks["blink_L"].keyframe_insert(data_path="value", frame=f)
            key_blocks["blink_R"].value = 1.0
            key_blocks["blink_R"].keyframe_insert(data_path="value", frame=f)
            
            key_blocks["blink_L"].value = 0.0
            key_blocks["blink_L"].keyframe_insert(data_path="value", frame=f+2)
            key_blocks["blink_R"].value = 0.0
            key_blocks["blink_R"].keyframe_insert(data_path="value", frame=f+2)
            
    print("[ANIMATION] Setup complete. Proceeding to headless EEVEE render sequence...")
    
    # Set up render
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.RenderEngine, 'blender_eevee_next') else 'BLENDER_EEVEE'
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = os.path.join(output_dir, "frame_")
    
    # Setup Camera
    if not any(obj.type == 'CAMERA' for obj in bpy.context.scene.objects):
        bpy.ops.object.camera_add(location=(0, -2, 1.5), rotation=(1.22, 0, 0))
        bpy.context.scene.camera = bpy.context.object
        print("[ANIMATION] Default Camera injected.")
        
    # Setup Lighting
    if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
        bpy.ops.object.light_add(type='POINT', location=(1, -1, 2))
        bpy.context.object.data.energy = 1000
        print("[ANIMATION] Default Point Light injected.")
        
    # Render Animation
    bpy.ops.render.render(animation=True)
    print(f"[ANIMATION] Render sequence completed successfully to {output_dir}")

if __name__ == "__main__":
    argv = sys.argv
    try:
        index = argv.index("--") + 1
    except ValueError:
        index = len(argv)
    args = argv[index:]
    
    if len(args) < 2:
        print("Usage: blender --background --python script.py -- <in_asset> <out_dir>")
        sys.exit(1)
        
    animate_mars(args[0], args[1])
