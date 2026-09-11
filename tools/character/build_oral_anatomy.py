"""Measured oral-placement gate and derived anatomy repair for God Molecule.

Canonical MARS is never modified. All oral objects are derived assets.
Usage:
 blender --background --python build_oral_anatomy.py -- INPUT.blend OUTPUT.blend [mouth_frame.json]
"""
import bpy, sys, os, json
from mathutils import Vector

DEFAULT_PLANE_Y = -0.21
DEFAULT_RECESS = 0.006
DONOR_NAMES = ("sock","upper","lower","tongue","tooth","teeth","gum","gums")

def load_frame(path):
    data={"plane_y":DEFAULT_PLANE_Y,"normal":[0,1,0],"recess":DEFAULT_RECESS}
    if path and os.path.isfile(path):
        with open(path,encoding="utf-8") as f: data.update(json.load(f))
    n=Vector(data.get("normal",[0,1,0]))
    if n.length == 0: raise RuntimeError("MOUTH_FRAME_INVALID: zero plane normal")
    n.normalize()
    return Vector(data.get("origin",[0,float(data["plane_y"]),0])), n, float(data.get("recess",DEFAULT_RECESS))

def is_oral(o):
    s=(o.name+" "+o.data.name+" "+" ".join(m.name for m in o.data.materials if m)).lower()
    return o.get("god_molecule_generated_oral") or any(k in s for k in DONOR_NAMES)

def front_distance(obj, origin, normal):
    pts=[obj.matrix_world @ v.co for v in obj.data.vertices]
    return max(((p-origin).dot(normal) for p in pts), default=-1e9)

def identify():
    rows=[]
    for o in bpy.context.scene.objects:
        if o.type=="MESH" and is_oral(o):
            rows.append((o.name, o.data.name, [m.name for m in o.data.materials if m], o.users_collection[0].name if o.users_collection else "<none>"))
    return rows

def report_protrusion(origin, normal):
    rows=[]
    worst=None
    for o in bpy.context.scene.objects:
        if o.type=="MESH" and is_oral(o):
            d=front_distance(o,origin,normal)
            rows.append({"name":o.name,"material":[m.name for m in o.data.materials if m],
                         "collection":o.users_collection[0].name if o.users_collection else "<none>",
                         "front_signed_distance":d})
            if worst is None or d>worst[1]: worst=(o,d)
    return rows,worst

def recess_object(obj, origin, normal, target):
    inv=obj.matrix_world.inverted()
    moved=0
    for v in obj.data.vertices:
        p=obj.matrix_world @ v.co
        d=(p-origin).dot(normal)
        if d > target:
            p -= normal*(d-target)
            v.co=inv @ p
            moved += 1
    return moved

def ensure_material(name, color, roughness):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1); m.roughness=roughness
    return m

def rebuild_oral():
    # Remove only previously generated anatomy. The canonical mesh is untouched.
    for o in list(bpy.context.scene.objects):
        if o.get("god_molecule_generated_oral"):
            bpy.data.objects.remove(o,do_unlink=True)
    cavity=ensure_material("OralCavity",(0.012,0.002,0.003),.78)
    tooth=ensure_material("Teeth",(0.82,0.76,0.60),.34)
    gum=ensure_material("Gums",(0.24,0.018,0.025),.52)
    tongue_mat=ensure_material("Tongue",(0.42,0.045,0.065),.48)
    # All centers are behind the lip plane. These are shallow anatomical volumes,
    # not a sphere intersecting the face.
    def uv(name,loc,scale,mat):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc)
        o=bpy.context.object; o.name=name; o.scale=scale
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(mat); o["god_molecule_generated_oral"]=True
        return o
    uv("Oral_Sock",(0,-0.275,0.241),(0.15,0.055,0.082),cavity)
    uv("Upper_Gum",(0,-0.255,0.276),(0.125,0.018,0.012),gum)
    uv("Lower_Gum",(0,-0.255,0.206),(0.125,0.018,0.012),gum)
    uv("Tongue",(0,-0.255,0.222),(0.095,0.035,0.025),tongue_mat)
    for row,z,y in (("Upper",0.274,-0.255),("Lower",0.208,-0.250)):
        for i in range(10):
            x=(i-4.5)*0.019
            bpy.ops.mesh.primitive_cube_add(location=(x,y,z))
            o=bpy.context.object; o.name=f"{row}_Tooth_{i+1:02d}"; o.scale=(.012,.012,.020)
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
            o.data.materials.append(tooth); o["god_molecule_generated_oral"]=True

def validate_after(origin,normal):
    rows,worst=report_protrusion(origin,normal)
    protrusion=max(0.0,(worst[1] if worst else -1e9))*1000.0
    if worst and worst[1] > 0:
        raise RuntimeError(f"ORAL_PLACEMENT_FAIL: {worst[0].name} protrudes {protrusion:.3f} mm")
    return rows,protrusion

def main(inp,out,frame):
    bpy.ops.wm.open_mainfile(filepath=inp)
    origin,normal,recess=load_frame(frame)
    print("[ORAL] OBJECT IDENTIFICATION")
    for row in identify(): print("[ORAL]",row)
    rows,worst=report_protrusion(origin,normal)
    if worst: print(f"[ORAL] PRE_REPAIR worst={worst[0].name} signed_distance={worst[1]:.6f} protrusion_mm={max(0,worst[1])*1000:.3f}")
    # Recess every existing oral donor, including the old slab/sock.
    target=-recess
    for o in bpy.context.scene.objects:
        if o.type=="MESH" and is_oral(o):
            recess_object(o,origin,normal,target)
    # Remove/rebuild generated anatomy so it is guaranteed to obey the plane.
    rebuild_oral()
    for o in bpy.context.scene.objects:
        if o.type=="MESH" and is_oral(o):
            recess_object(o,origin,normal,target)
    rows,protrusion=validate_after(origin,normal)
    print(f"[ORAL] POST_REPAIR protrusion_mm={protrusion:.3f}")
    print("[ORAL] GATE: PASS placement only (creative anatomy still HUMAN_REVIEW_REQUIRED)")
    bpy.ops.wm.save_as_mainfile(filepath=out)

if __name__=="__main__":
    a=sys.argv
    try:i=a.index("--")+1
    except ValueError:i=len(a)
    if len(a)-i<2: raise SystemExit("usage: ... INPUT.blend OUTPUT.blend [mouth_frame.json]")
    main(a[i],a[i+1],a[i+2] if len(a)-i>2 else None)
