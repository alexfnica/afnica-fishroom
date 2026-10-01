# Real 3D render of a fish sprite whose rear half is curled toward the camera.
# The sprite is a subdivided plane (head half straight, tail half bent along a constant-curvature arc that swings out of the
# picture plane toward the viewer), textured with the sprite and rendered by Blender with a perspective camera.
# Run: D:\Blender\blender.exe -b -P bend_render.py -- <in.png> <out_prefix> <hinge 0..1> <deg1> <deg2> ...   (sprite faces right)
import bpy, bmesh, sys, math
a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT, HINGE = a[0], a[1], float(a[2]); ANGLES = [float(v) for v in a[3:]]
bpy.ops.wm.read_factory_settings(use_empty=True)
img = bpy.data.images.load(SRC); W, H = img.size; img.pack()
UNIT = 1.0 / W                                        # 1 blender unit = whole sprite width
PW, PH = 1.0, H / W
xh = HINGE * PW                                       # hinge position along the width (0 = tail tip, 1 = nose)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = W * 2, H * 2
sc.render.resolution_percentage = 100
try: sc.eevee.taa_render_samples = 96
except Exception: pass
sc.view_settings.view_transform = 'Standard'

# material: emission of the sprite colours, alpha from the sprite
mat = bpy.data.materials.new('fish'); mat.use_nodes = True
nt = mat.node_tree; nt.nodes.clear()
tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.extension = 'EXTEND'; tex.interpolation = 'Cubic'
em = nt.nodes.new('ShaderNodeEmission'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(tex.outputs['Color'], em.inputs['Color']); nt.links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
nt.links.new(tr.outputs['BSDF'], mix.inputs[1]); nt.links.new(em.outputs['Emission'], mix.inputs[2]); nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
try: mat.surface_render_method = 'DITHERED'
except Exception: pass
mat.use_backface_culling = False

for n, deg in enumerate(ANGLES, 1):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
    th = math.radians(deg); k = th / xh               # curvature of the tail arc (angle reached at the very tip)
    NX, NZ = 360, 120
    bm = bmesh.new(); uv = bm.loops.layers.uv.new('uv')
    verts = {}
    for j in range(NZ + 1):
        for i in range(NX + 1):
            u, v = i / NX, j / NZ
            x = u * PW; z = (v - .5) * PH
            s = xh - x
            if s > 0 and k > 1e-6:                    # tail side: follow the arc, toward the camera (-Y)
                phi = k * s
                X = xh - math.sin(phi) / k; Y = -(1 - math.cos(phi)) / k
            else:
                X, Y = x, 0.0
            verts[(i, j)] = bm.verts.new((X - PW / 2, Y, z))
    for j in range(NZ):
        for i in range(NX):
            f = bm.faces.new((verts[(i, j)], verts[(i + 1, j)], verts[(i + 1, j + 1)], verts[(i, j + 1)]))
            for lp, (iu, jv) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uv].uv = (iu / NX, jv / NZ)
    me = bpy.data.meshes.new('m'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('fish', me); me.materials.append(mat); sc.collection.objects.link(ob)
    # camera: looks along +Y; sized so the straight sprite exactly fills the frame at the hinge-plane distance
    D = 0.75 * PW
    cam = bpy.data.cameras.new('c'); cam.sensor_width = 36; cam.lens = 36 * D / PW; cam.sensor_fit = 'HORIZONTAL'
    co = bpy.data.objects.new('cam', cam); co.location = (0, -D, 0); co.rotation_euler = (math.pi / 2, 0, 0)
    sc.collection.objects.link(co); sc.camera = co
    sc.render.filepath = '%s_%d.png' % (OUT, n)
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    bpy.ops.render.render(write_still=True)
    r = bpy.data.images.load(sc.render.filepath); r.scale(W, H); r.filepath_raw = sc.render.filepath; r.file_format = 'PNG'; r.save()
    print('RENDER', n, deg)
