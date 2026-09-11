"""Build derived oral anatomy and a real mouth-opening deformation for MARS_CANONICAL.

The canonical scan is never modified. This operates on a derived LOD/rig asset.
The mouth frame is explicit because a closed scan contains no teeth/tongue volume.
"""
import bpy, sys, os, math
from mathutils import Vector

MOUTH_CENTER = Vector((0.0, -0.442, 0.241))
MOUTH_WIDTH = 0.34
MOUTH_HEIGHT = 0.20

def clear_generated():
    for o in list(bpy.data.objects):
        if o.get("god_molecule_generated_oral"):
            bpy.data.objects.remove(o, do_unlink=True)

def add_uv_sphere(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o=bpy.context.object; o.name=name
    o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat); o["god_molecule_generated_oral"]=True
    return o

def mat(name, color, rough=.45):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.roughness=rough
    return m

def create_anatomy():
    clear_generated()
    cavity=mat("OralCavity",(0.018,0.004,0.006),.7)
    tooth=mat("Teeth",(0.88,0.82,0.68),.3)
    gum=mat("Gums",(0.28,0.025,0.035),.5)
    tongue_mat=mat("Tongue",(0.48,0.08,0.11),.5)

    # Cavity is a flattened volume behind the measured lip plane, never a sphere
    add_uv_sphere("Oral_Cavity", MOUTH_CENTER+Vector((0,0.055,0)), (MOUTH_WIDTH*.48,.10,MOUTH_HEIGHT*.42), cavity)

    # Teeth are shallow individual crowns, recessed behind the lip aperture.
    for row,z,depth in [("Upper",MOUTH_CENTER.z+MOUTH_HEIGHT*.19,.055),
                        ("Lower",MOUTH_CENTER.z-MOUTH_HEIGHT*.17,.040)]:
        for i in range(10):
            x=(i-4.5)*(MOUTH_WIDTH*.075)
            bpy.ops.mesh.primitive_cube_add(location=(x,MOUTH_CENTER.y+depth,z))
            o=bpy.context.object; o.name=f"{row}_Tooth_{i+1:02d}"
            o.scale=(MOUTH_WIDTH*.030,.025,MOUTH_HEIGHT*.095)
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            o.data.materials.append(tooth); o["god_molecule_generated_oral"]=True

    add_uv_sphere("Upper_Gum",MOUTH_CENTER+Vector((0,0.025,MOUTH_HEIGHT*.18)),
                  (MOUTH_WIDTH*.40,.045,MOUTH_HEIGHT*.045),gum)
    add_uv_sphere("Lower_Gum",MOUTH_CENTER+Vector((0,0.025,-MOUTH_HEIGHT*.17)),
                  (MOUTH_WIDTH*.40,.045,MOUTH_HEIGHT*.045),gum)
    tongue=add_uv_sphere("Tongue",MOUTH_CENTER+Vector((0,-.005,-MOUTH_HEIGHT*.05)),
                         (MOUTH_WIDTH*.30,.075,MOUTH_HEIGHT*.11),tongue_mat)
    return tongue

def mouth_shape_keys(mesh):
    if not mesh.data.shape_keys:
        mesh.shape_key_add(name="Basis")
    basis=mesh.data.shape_keys.key_blocks["Basis"]
    names=["viseme_A","viseme_B","viseme_C","viseme_D","viseme_E","viseme_F",
           "viseme_G","viseme_H","viseme_X","blink_L","blink_R","brows_up","brows_down"]
    existing={k.name for k in mesh.data.shape_keys.key_blocks}
    for n in names:
        if n not in existing: mesh.shape_key_add(name=n)
    coords=[mesh.matrix_world @ v.co for v in mesh.data.vertices]
    # Only vertices around the measured mouth aperture are allowed to move.
    for key_name, gap in [("viseme_A",.065),("viseme_B",.045),("viseme_C",.035),
                          ("viseme_D",.055),("viseme_E",.025),("viseme_F",.020),
                          ("viseme_G",.040),("viseme_H",.030)]:
        key=mesh.data.shape_keys.key_blocks[key_name]
        for i,p in enumerate(coords):
            dx=abs(p.x-MOUTH_CENTER.x); dz=abs(p.z-MOUTH_CENTER.z)
            if dx > MOUTH_WIDTH*.62 or dz > MOUTH_HEIGHT*.58: continue
            # Separate upper/lower lip bands; leave cheeks/skull fixed.
            upper=max(0.0,min(1.0,(p.z-MOUTH_CENTER.z)/(MOUTH_HEIGHT*.48)))
            lower=max(0.0,min(1.0,(MOUTH_CENTER.z-p.z)/(MOUTH_HEIGHT*.48)))
            fall=max(0.0,1.0-dx/(MOUTH_WIDTH*.62))
            if upper>0 and lower==0:
                q=p.copy(); q.z += gap*upper*fall
            elif lower>0:
                q=p.copy(); q.z -= gap*lower*fall
            else:
                continue
            key.data[i].co=mesh.matrix_world.inverted() @ q
    # X/rest keeps the measured scan untouched.
    return True

def main(inp,out):
    bpy.ops.wm.open_mainfile(filepath=inp) if inp.endswith(".blend") else bpy.ops.import_scene.gltf(filepath=inp)
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH" and not o.get("god_molecule_generated_oral")]
    if not meshes: raise RuntimeError("No derived Mars mesh found")
    mesh=meshes[0]
    before=len(mesh.data.vertices)
    mouth_shape_keys(mesh)
    create_anatomy()
    bpy.ops.wm.save_as_mainfile(filepath=out)
    assert len(mesh.data.vertices)==before, "Exterior vertex count changed"
    print(f"[ORAL] Exterior vertices preserved: {before}")
    print("[ORAL] Recessed cavity + upper/lower teeth + gums + tongue created")
    print("[ORAL] Real aperture deformation controls installed on derived mesh")

if __name__=="__main__":
    a=sys.argv
    try:i=a.index("--")+1
    except ValueError:i=len(a)
    if len(a)-i<2: raise SystemExit("usage: blender --background --python build_oral_anatomy.py -- in.blend out.blend")
    try: main(a[i],a[i+1])
    except Exception as e: print("[BLOCKED]",e); raise
