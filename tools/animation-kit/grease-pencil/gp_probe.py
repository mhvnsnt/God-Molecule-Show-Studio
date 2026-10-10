import bpy
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
bpy.ops.object.gpencil_add(type='STROKE')
gp = bpy.context.active_object
print("GP type:", type(gp.data).__name__)
mat = bpy.data.materials.new("ink")
bpy.data.materials.create_gpencil_data(mat)
g = mat.grease_pencil
print("has color attr:", hasattr(g, 'color'))
g.color = (0.0, 0.8, 0.2, 1.0)
print("color now:", tuple(g.color))
print("show_stroke:", g.show_stroke)
# try v3 layers API
d = gp.data
print("layers:", [l.name for l in d.layers])
