import bpy, math
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
mat = bpy.data.materials.new("ink")
bpy.data.materials.create_gpencil_data(mat)
mat.grease_pencil.color = (0.0, 0.8, 0.2, 1.0)
mat.grease_pencil.show_stroke = True
bpy.ops.object.gpencil_add(type='STROKE')
gp = bpy.context.active_object
gp.data.materials.append(mat)
layer = gp.data.layers.new("FX")
frame = layer.frames.new(1)
stroke = frame.strokes.new()
stroke.material_index = 0
stroke.line_width = 12
n=16; pts=[]
for i in range(n*2+1):
    a=math.pi*2*i/(n*2); r=2.0 if i%2==0 else 0.8
    pts.append((r*math.cos(a), r*math.sin(a), 0))
stroke.points.add(len(pts))
for p,co in zip(stroke.points, pts): p.co=co
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(0,0,12)); sc.camera=bpy.context.active_object
sc.render.resolution_x, sc.render.resolution_y = 640,360
sc.render.film_transparent=False
sc.world.color=(1,1,1)
sc.render.filepath="/home/hatch/workspace/video-fix-tools/grease-pencil/gp_test2.png"
bpy.ops.render.render(write_still=True)
print("GP_SMOKE2_OK")
