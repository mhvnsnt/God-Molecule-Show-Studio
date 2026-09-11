import sys
import struct
import json

def parse_glb(filepath):
    with open(filepath, 'rb') as f:
        magic = f.read(4)
        if magic != b'glTF':
            return {"error": "Not a valid GLB file (missing glTF magic)"}
            
        version, = struct.unpack('<I', f.read(4))
        length, = struct.unpack('<I', f.read(4))
        
        chunk0_len, = struct.unpack('<I', f.read(4))
        chunk0_type = f.read(4)
        
        if chunk0_type != b'JSON':
            return {"error": "First chunk is not JSON"}
            
        json_data = f.read(chunk0_len).decode('utf-8')
        gltf = json.loads(json_data)
        
        stats = {
            "meshes": len(gltf.get('meshes', [])),
            "materials": len(gltf.get('materials', [])),
            "textures": len(gltf.get('textures', [])),
            "images": len(gltf.get('images', [])),
            "skins": len(gltf.get('skins', [])),
            "cameras": len(gltf.get('cameras', [])),
            "animations": len(gltf.get('animations', [])),
            "nodes": len(gltf.get('nodes', [])),
        }
        
        # Check for morph targets (blendshapes)
        has_blendshapes = False
        for mesh in gltf.get('meshes', []):
            if 'weights' in mesh or any('targets' in p for p in mesh.get('primitives', [])):
                has_blendshapes = True
                
        stats['has_blendshapes'] = has_blendshapes
        
        # Check for lights
        stats['lights'] = 0
        if 'extensions' in gltf and 'KHR_lights_punctual' in gltf['extensions']:
            stats['lights'] = len(gltf['extensions']['KHR_lights_punctual'].get('lights', []))
            
        return stats

if __name__ == '__main__':
    print(json.dumps(parse_glb(sys.argv[1])))
