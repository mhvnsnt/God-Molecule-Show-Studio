import sys
import json
import os
import hashlib
import struct

def parse_glb_json(filepath):
    try:
        with open(filepath, 'rb') as f:
            magic = f.read(4)
            if magic != b'glTF':
                return None
            version, = struct.unpack('<I', f.read(4))
            length, = struct.unpack('<I', f.read(4))
            chunk0_len, = struct.unpack('<I', f.read(4))
            chunk0_type = f.read(4)
            if chunk0_type != b'JSON':
                return None
            json_data = f.read(chunk0_len).decode('utf-8')
            return json.loads(json_data)
    except Exception:
        return None

def inspect_obj(filepath):
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    stats = {
        "vertices": 0,
        "faces": 0,
        "materials": [],
        "topologyStatus": "UNKNOWN",
        "skeletonStatus": "BLOCKED (No Armature Found)",
        "blendshapes": "BLOCKED (No Morph Targets Found)",
        "bounds": [],
        "extents": [],
        "components": 1,
        "has_uv": False,
        "format": "UNKNOWN",
        "meshes": 0,
        "textures": 0,
        "cameras": 0,
        "lights": 0
    }

    if filepath.lower().endswith('.glb'):
        stats["format"] = "GLB (glTF Binary)"
        gltf = parse_glb_json(filepath)
        if gltf:
            stats["meshes"] = len(gltf.get('meshes', []))
            stats["materials"] = [m.get('name', 'unnamed') for m in gltf.get('materials', [])]
            stats["textures"] = len(gltf.get('textures', []))
            stats["cameras"] = len(gltf.get('cameras', []))
            
            if 'extensions' in gltf and 'KHR_lights_punctual' in gltf['extensions']:
                stats['lights'] = len(gltf['extensions']['KHR_lights_punctual'].get('lights', []))
                
            skins = gltf.get('skins', [])
            if len(skins) > 0:
                stats["skeletonStatus"] = f"VERIFIED ({len(skins)} skins detected)"
                
            has_blendshapes = False
            for mesh in gltf.get('meshes', []):
                if 'weights' in mesh or any('targets' in p for p in mesh.get('primitives', [])):
                    has_blendshapes = True
            
            if has_blendshapes:
                stats["blendshapes"] = "VERIFIED (Morph targets found)"

    try:
        import trimesh
        mesh = trimesh.load(filepath, process=False)
        
        if isinstance(mesh, trimesh.Scene):
             stats["vertices"] = sum(len(g.vertices) for g in mesh.geometry.values() if hasattr(g, 'vertices'))
             stats["faces"] = sum(len(g.faces) for g in mesh.geometry.values() if hasattr(g, 'faces'))
             stats["topologyStatus"] = "PASS (Watertight)" if all(g.is_watertight for g in mesh.geometry.values() if hasattr(g, 'is_watertight')) else "PASS (Non-manifold)"
             stats["bounds"] = mesh.bounds.tolist() if mesh.bounds is not None else []
             stats["extents"] = mesh.extents.tolist() if mesh.extents is not None else []
             stats["components"] = len(mesh.geometry.values())
             stats["has_uv"] = any(hasattr(g.visual, 'uv') and g.visual.uv is not None and len(g.visual.uv) > 0 for g in mesh.geometry.values() if hasattr(g, 'visual'))
             if stats["format"] == "UNKNOWN":
                 stats["meshes"] = len(mesh.geometry.values())
        else:
             stats["vertices"] = len(mesh.vertices)
             stats["faces"] = len(mesh.faces)
             stats["topologyStatus"] = "PASS (Watertight)" if mesh.is_watertight else "PASS (Non-manifold)"
             stats["bounds"] = mesh.bounds.tolist() if mesh.bounds is not None else []
             stats["extents"] = mesh.extents.tolist() if mesh.extents is not None else []
             stats["components"] = trimesh.graph.connected_components(mesh.edges).shape[0] if hasattr(mesh, 'edges') else 1
             stats["has_uv"] = hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None and len(mesh.visual.uv) > 0
             if stats["format"] == "UNKNOWN":
                 stats["meshes"] = 1

    except Exception as e:
        stats["error"] = f"Trimesh inspection failed: {e}"

    return stats

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)
        
    filepath = sys.argv[1]
    result = inspect_obj(filepath)
    print(json.dumps(result))
