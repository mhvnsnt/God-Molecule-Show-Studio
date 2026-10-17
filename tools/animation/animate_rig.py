import bpy
import sys
import os
import json
import math


RHUBARB_TO_VISEME = {
    "A": "viseme_A", "B": "viseme_B", "C": "viseme_C", "D": "viseme_D",
    "E": "viseme_E", "F": "viseme_F", "G": "viseme_G", "H": "viseme_H",
    "X": "viseme_X",
}


def load_rhubarb(path):
    if not path or not os.path.isfile(path):
        raise RuntimeError("REAL_AUDIO_REQUIRED: Rhubarb JSON was not supplied")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cues = data.get("mouthCues", [])
    if not cues:
        raise RuntimeError("REAL_AUDIO_REQUIRED: Rhubarb JSON contains no mouthCues")
    return cues


def key_real_lipsync(mesh, cues, fps):
    keys = mesh.data.shape_keys.key_blocks
    available = set(keys.keys())
    missing = sorted({RHUBARB_TO_VISEME.get(c.get("value", "X"), "viseme_X")
                      for c in cues} - available)
    if missing:
        raise RuntimeError("LIPSYNC_CONTROLS_MISSING: " + ", ".join(missing))

    # Clear all non-basis controls at the start.
    for key in keys:
        if key.name != "Basis":
            key.value = 0.0
            key.keyframe_insert(data_path="value", frame=1)

    for cue in cues:
        value = RHUBARB_TO_VISEME.get(cue.get("value", "X"))
        if not value:
            continue
        start = max(1, round(float(cue["start"]) * fps) + 1)
        end = max(start, round(float(cue["end"]) * fps) + 1)
        for key in keys:
            if key.name != "Basis":
                key.value = 1.0 if key.name == value else 0.0
                key.keyframe_insert(data_path="value", frame=start)
                key.keyframe_insert(data_path="value", frame=end)

    return len(cues)


def animate_mars(input_path, output_dir, rhubarb_path):
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
        raise RuntimeError("No meshes found to animate.")

    mars_mesh = meshes[0]
    cues = load_rhubarb(rhubarb_path)

    fps = 24
    duration = max(float(c["end"]) for c in cues)
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = max(2, round(duration * fps) + 1)
    bpy.context.scene.render.fps = fps

    if not mars_mesh.data.shape_keys:
        raise RuntimeError("LIPSYNC_CONTROLS_MISSING: mesh has no shape keys")

    # These are real Rhubarb controls. No invented transcript or cadence.
    count = key_real_lipsync(mars_mesh, cues, fps)
    print(f"[FACE] REAL_AUDIO: {count} Rhubarb mouth cues applied")

    # Bounded jaw motion is driven by the actual Rhubarb cue timing.
    # Visemes remain the primary facial control; this adds measured hinge motion.
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
    if armatures and "Jaw" in armatures[0].pose.bones:
        jaw = armatures[0].pose.bones["Jaw"]
        jaw.rotation_mode = 'XYZ'
        openness = {"A":1.0,"B":0.72,"C":0.55,"D":0.68,"E":0.45,"F":0.30,
                    "G":0.50,"H":0.40,"X":0.05}
        for cue in cues:
            amount = openness.get(cue.get("value","X"), 0.05)
            start = max(1, round(float(cue["start"]) * fps) + 1)
            end = max(start, round(float(cue["end"]) * fps) + 1)
            jaw.rotation_euler[0] = math.radians(-11.0 * amount)
            jaw.keyframe_insert(data_path="rotation_euler", frame=start)
            jaw.keyframe_insert(data_path="rotation_euler", frame=end)
        print("[FACE] REAL_AUDIO: bounded jaw motion keyed from Rhubarb cues")

    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
    if armatures and "Head" in armatures[0].pose.bones:
        bpy.context.view_layer.objects.active = armatures[0]
        bpy.ops.object.mode_set(mode='POSE')
        head_bone = armatures[0].pose.bones["Head"]
        head_bone.rotation_mode = 'XYZ'
        head_bone.rotation_euler = (0, 0, 0)
        head_bone.keyframe_insert(data_path="rotation_euler", frame=1)
        bpy.ops.object.mode_set(mode='OBJECT')

    os.makedirs(output_dir, exist_ok=True)
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = os.path.join(output_dir, "frame_")

    if not any(obj.type == 'CAMERA' for obj in bpy.context.scene.objects):
        bpy.ops.object.camera_add(location=(0, -2, 1.5), rotation=(1.22, 0, 0))
        bpy.context.scene.camera = bpy.context.object

    if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
        bpy.ops.object.light_add(type='POINT', location=(1, -1, 2))
        bpy.context.object.data.energy = 1000

    bpy.ops.render.render(animation=True)
    print(f"[ANIMATION] REAL_RENDER completed: {output_dir}")


if __name__ == "__main__":
    argv = sys.argv
    try:
        index = argv.index("--") + 1
    except ValueError:
        index = len(argv)
    args = argv[index:]
    if len(args) < 3:
        print("Usage: blender --background --python animate_rig.py -- <asset> <out_dir> <rhubarb.json>")
        sys.exit(2)
    try:
        animate_mars(args[0], args[1], args[2])
    except Exception as exc:
        print(f"[BLOCKED] {exc}")
        sys.exit(1)
