import bpy, math
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
bpy.ops.object.gpencil_add(type='STROKE')
gp = bpy.context.active_object
print("mats on new GP:", [m.name for m in gp.data.materials])
# recolor the DEFAULT material instead of making a new one
mat = gp.data.materials[0]
mat.grease_pencil.color = (0.0, 0.9, 0.2, 1.0)
layer = gp.data.layers.new("FX")
frame = layer.frames.new(1)
stroke = frame.strokes.new()
stroke.material_index = 0
stroke.line_width = 25
n=12; pts=[]
for i in range(n*2+1):
    a=math.pi*2*i/(n*2); r=2.2 if i%2==0 else 0.9
    pts.append((r*math.cos(a), r*math.sin(a), 0))
stroke.points.add(len(pts))
for p,co in zip(stroke.points, pts): p.co=co
print("stroke mat idx:", stroke.material_index, "npoints:", len(stroke.points))
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(0,0,12)); sc.camera=bpy.context.active_object
sc.render.resolution_x, sc.render.resolution_y = 640,360
sc.render.film_transparent=True
sc.render.filepath="/home/hatch/workspace/video-fix-tools/grease-pencil/gp_test3.png"
bpy.ops.render.render(write_still=True)
print("GP_SMOKE3_OK")
