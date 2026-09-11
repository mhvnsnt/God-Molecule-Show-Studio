import sys
import trimesh

def generate_proxy(input_path, output_path):
    print(f"[PROXY] Loading canonical asset: {input_path}")
    mesh = trimesh.load(input_path, process=False)
    
    if isinstance(mesh, trimesh.Scene):
        if len(mesh.geometry) == 0:
            print("[ERROR] Empty scene")
            sys.exit(1)
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    
    extents = mesh.extents
    max_dim = max(extents)
    pitch = max_dim / 30.0
    
    print(f"[PROXY] Voxelizing with pitch {pitch:.4f}...")
    voxel = mesh.voxelized(pitch=pitch)
    proxy_mesh = voxel.marching_cubes
    
    proxy_mesh.export(output_path)
    print(f"[PROXY] Saved proxy to {output_path}")

if __name__ == '__main__':
    generate_proxy(sys.argv[1], sys.argv[2])
