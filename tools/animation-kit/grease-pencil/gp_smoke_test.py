# Headless Grease Pencil smoke test: draw a starburst stroke, render PNG.
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.object.gpencil_add(type='STROKE')
gp = bpy.context.active_object
gpd = gp.data
layer = gpd.layers.new("FX")
frame = layer.frames.new(1)
import math
stroke = frame.strokes.new()
stroke.display_mode = '3DSPACE'
pts = []
n = 16
for i in range(n*2+1):
    a = math.pi*2*i/(n*2)
    r = 2.0 if i%2==0 else 0.8
    pts.append((r*math.cos(a), r*math.sin(a), 0))
stroke.points.add(len(pts))
for p, co in zip(stroke.points, pts):
    p.co = co
mat = bpy.data.materials.new("ink")
bpy.data.materials.create_gpencil_data(mat)
mat.grease_pencil.color = (0.0, 0.8, 0.2, 1.0)
mat.grease_pencil.show_stroke = True
mat.grease_pencil.show_fill = False
stroke.material_index = 0
gp.data.materials.append(mat)
scene = bpy.context.scene
scene.render.resolution_x, scene.render.resolution_y = 640, 360
scene.render.film_transparent = True
scene.render.filepath = "/home/hatch/workspace/video-fix-tools/grease-pencil/gp_test.png"
scene.render.image_settings.file_format = 'PNG'
bpy.ops.object.camera_add(location=(0,0,12))
cam = bpy.context.active_object
scene.camera = cam
bpy.ops.render.render(write_still=True)
print("GP_SMOKE_OK")
