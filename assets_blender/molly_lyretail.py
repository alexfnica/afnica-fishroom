# Black molly (lyretail) - procedural model + transparent side-view render.
# Run:  D:\Blender\blender.exe -b -P molly_lyretail.py -- <sex M|F> <out.png> [samples]
# Fish faces +X (head to the right), +Z up, camera looks along +Y at the fish's left flank.
import bpy, bmesh, math, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SEX = (argv[0] if len(argv) > 0 else 'M').upper()
OUT = argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(__file__), 'molly_%s.png' % SEX)
SAMPLES = int(argv[2]) if len(argv) > 2 else 64

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- materials
def principled(mat):
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return nt, bsdf

def setin(node, name, value):
    try:
        node.inputs[name].default_value = value
    except KeyError:
        pass

def mat_body():
    m = bpy.data.materials.new('molly_body'); m.use_nodes = True
    nt, b = principled(m)
    setin(b, 'Base Color', (0.006, 0.006, 0.010, 1))
    setin(b, 'Roughness', 0.38)
    setin(b, 'Specular IOR Level', 0.6)
    setin(b, 'Sheen Weight', 0.5); setin(b, 'Sheen Tint', (0.25, 0.3, 0.7, 1))
    setin(b, 'Coat Weight', 0.35); setin(b, 'Coat Roughness', 0.25)
    # scale pattern -> bump
    tc = nt.nodes.new('ShaderNodeTexCoord')
    vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 95
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.22
    nt.links.new(tc.outputs['Object'], vor.inputs['Vector'])
    nt.links.new(vor.outputs['Distance'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    # faint blue-violet sheen toward the back / top, browner belly
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Normal'], sep.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = (0.010, 0.008, 0.008, 1)
    ramp.color_ramp.elements[1].position = 0.95; ramp.color_ramp.elements[1].color = (0.020, 0.024, 0.055, 1)
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    return m

def mat_fin():
    m = bpy.data.materials.new('molly_fin'); m.use_nodes = True
    nt, b = principled(m)
    setin(b, 'Base Color', (0.012, 0.012, 0.018, 1))
    setin(b, 'Roughness', 0.5)
    setin(b, 'Specular IOR Level', 0.4)
    setin(b, 'Sheen Weight', 0.35); setin(b, 'Sheen Tint', (0.3, 0.3, 0.6, 1))
    setin(b, 'Transmission Weight', 0.0)
    return m

def mat_eye_iris():
    m = bpy.data.materials.new('molly_iris'); m.use_nodes = True
    nt, b = principled(m)
    setin(b, 'Base Color', (0.62, 0.42, 0.10, 1)); setin(b, 'Roughness', 0.18)
    setin(b, 'Metallic', 0.55)
    return m

def mat_pupil():
    m = bpy.data.materials.new('molly_pupil'); m.use_nodes = True
    nt, b = principled(m)
    setin(b, 'Base Color', (0.0, 0.0, 0.0, 1)); setin(b, 'Roughness', 0.05)
    setin(b, 'Coat Weight', 1.0); setin(b, 'Coat Roughness', 0.02)
    return m

MB, MF, MI, MP = mat_body(), mat_fin(), mat_eye_iris(), mat_pupil()

# ---------------------------------------------------------------- helpers
def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def new_obj(name, bm, mat, subsurf=0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    me.materials.append(mat)
    for p in me.polygons: p.use_smooth = True
    if subsurf:
        md = ob.modifiers.new('sub', 'SUBSURF'); md.levels = subsurf; md.render_levels = subsurf
    return ob

# ---------------------------------------------------------------- body (loft)
X0, X1 = 0.20, 1.0            # tail-base .. snout
N, M = 70, 32
def prof(x):
    t = (x - X0) / (X1 - X0)
    if t < 0.62:
        h = 0.082 + (0.315 - 0.082) * math.sin(math.pi / 2 * (t / 0.62)) ** 1.25
    else:
        h = 0.315 * math.cos(math.pi / 2 * ((t - 0.62) / 0.38)) ** 0.62
    w = h * (0.50 if t < 0.5 else 0.58)
    zc = -0.018 * math.sin(math.pi * t) - (0.028 if t > 0.82 else 0) * smooth((t - 0.82) / 0.18)
    return max(h, 0.006), max(w, 0.004), zc

bm = bmesh.new()
rings = []
for i in range(N + 1):
    u = i / N
    x = X0 + (X1 - X0) * (1 - (1 - u) ** 1.0)
    # denser stations near the snout and the peduncle
    x = X0 + (X1 - X0) * (0.5 - 0.5 * math.cos(math.pi * u))
    h, w, zc = prof(x)
    ring = []
    for j in range(M):
        th = 2 * math.pi * j / M
        s = math.sin(th)
        zz = zc + (h / 2) * s * (0.90 if s > 0 else 1.10)
        yy = (w / 2) * math.cos(th)
        ring.append(bm.verts.new((x, yy, zz)))
    rings.append(ring)
for i in range(N):
    for j in range(M):
        bm.faces.new((rings[i][j], rings[i][(j + 1) % M], rings[i + 1][(j + 1) % M], rings[i + 1][j]))
bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
body = new_obj('body', bm, MB, subsurf=1)

# ---------------------------------------------------------------- fins
def fin(name, outline, apex, rays, amp=0.0035, thick=0.0035, cuts=5, ray_phase=0.0, y0=0.0):
    """Flat fin from a (x,z) outline, corrugated along rays radiating from apex, then given thickness."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y0, z)) for x, z in outline]
    f = bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=[f])
    for _ in range(cuts):
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
    ax, az = apex
    for v in bm.verts:
        a = math.atan2(v.co.z - az, v.co.x - ax)
        r = math.hypot(v.co.z - az, v.co.x - ax)
        v.co.y = y0 + amp * math.sin(a * rays + ray_phase) * smooth(r * 6)
    ob = new_obj(name, bm, MF)
    sd = ob.modifiers.new('solid', 'SOLIDIFY'); sd.thickness = thick; sd.offset = 0
    return ob

def curve_pts(pts, per=10):
    """Catmull-Rom through pts, returns a denser polyline."""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            def cr(a, b, c, d):
                return 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
            out.append((cr(p0[0], p1[0], p2[0], p3[0]), cr(p0[1], p1[1], p2[1], p3[1])))
    out.append(pts[-1]); return out

# caudal: LYRETAIL - two long pointed lobes with a deep notch between them
cx, cz = 0.245, 0.0
top = [(0.245, 0.040), (0.15, 0.10), (0.02, 0.19), (-0.13, 0.27), (-0.235, 0.335)]
notch = [(-0.16, 0.20), (-0.085, 0.10), (-0.045, 0.03), (-0.035, 0.0)]
upper = curve_pts(top, 8) + curve_pts([(-0.235, 0.335)] + [(-0.20, 0.27), (-0.15, 0.20)] + notch, 8)
lower = [(x, -z) for (x, z) in reversed(upper)]
# mirror with a slightly longer lower lobe, like a real lyretail
lower = [(x - (0.02 if z < -0.25 else 0), z * 1.03) for (x, z) in lower]
outline = upper + lower
caudal = fin('caudal', outline, (cx, cz), rays=46, amp=0.0042, thick=0.004, cuts=4, y0=0.0)

# dorsal: tall, swept back (male taller)
dh = 0.30 if SEX == 'M' else 0.20
dor_pts = [(0.62, 0.150), (0.60, 0.20 + (dh - 0.2) * 0.4), (0.55, 0.15 + dh * 0.85), (0.47, 0.15 + dh), (0.395, 0.15 + dh * 0.78), (0.335, 0.150)]
dorsal_outline = curve_pts(dor_pts, 8) + [(0.335, 0.142), (0.62, 0.142)]
dorsal = fin('dorsal', dorsal_outline, (0.48, 0.13), rays=38, amp=0.003, thick=0.0032, cuts=4, y0=0.0)

# anal fin: pointed gonopodium (male) or a fan (female)
if SEX == 'M':
    an = [(0.49, -0.135), (0.44, -0.20), (0.36, -0.265), (0.318, -0.245), (0.335, -0.12)]
    anal = fin('anal', curve_pts(an, 6), (0.44, -0.13), rays=22, amp=0.0018, thick=0.003, cuts=3)
else:
    an = [(0.52, -0.14), (0.47, -0.20), (0.40, -0.255), (0.33, -0.235), (0.31, -0.12)]
    anal = fin('anal', curve_pts(an, 6), (0.42, -0.13), rays=30, amp=0.0026, thick=0.003, cuts=4)
# pelvic fins
pel = [(0.66, -0.11), (0.62, -0.20), (0.565, -0.245), (0.535, -0.175), (0.58, -0.10)]
pelvic = fin('pelvic', curve_pts(pel, 6), (0.60, -0.10), rays=16, amp=0.0016, thick=0.003, cuts=3, y0=-0.05)
# pectoral (near flank), slightly out from the body
pec = [(0.745, -0.035), (0.68, 0.03), (0.60, -0.02), (0.625, -0.095), (0.70, -0.105)]
pectoral = fin('pectoral', curve_pts(pec, 6), (0.745, -0.05), rays=18, amp=0.0016, thick=0.003, cuts=3, y0=-0.085)

# ---------------------------------------------------------------- head details: eye, gill crease, mouth
def uvsphere(name, r, loc, mat, sx=1, sy=1, sz=1):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=20, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz)) + Vector(loc)
    return new_obj(name, bm, mat, subsurf=0)

ex, ez, ey = 0.905, 0.045, -0.058
iris = uvsphere('iris', 0.030, (ex, ey, ez), MI, 1, 0.55, 1)
pupil = uvsphere('pupil', 0.019, (ex + 0.004, ey - 0.006, ez), MP, 1, 0.5, 1)
# eye socket rim (slightly raised dark ring)
rim = uvsphere('eyerim', 0.037, (ex, ey + 0.004, ez), MB, 1, 0.5, 1)
# gill cover: a shallow darker crescent standing proud of the flank
bm = bmesh.new()
pts = []
for k in range(0, 21):
    a = math.radians(-70 + 140 * k / 20)
    pts.append((0.775 - 0.06 * math.cos(a) * 0.55, -0.056, 0.02 + 0.20 * math.sin(a)))
for i in range(len(pts) - 1):
    a, b = pts[i], pts[i + 1]
    v = [bm.verts.new((a[0], a[1], a[2])), bm.verts.new((b[0], b[1], b[2])),
         bm.verts.new((b[0] - 0.02, b[1] + 0.01, b[2])), bm.verts.new((a[0] - 0.02, a[1] + 0.01, a[2]))]
    bm.faces.new(v)
gill = new_obj('gill', bm, MB, subsurf=0)
sd = gill.modifiers.new('solid', 'SOLIDIFY'); sd.thickness = 0.008

# ---------------------------------------------------------------- lighting + camera + render
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.35, 0.45, 0.60, 1); bg.inputs['Strength'].default_value = 0.9

def area(name, loc, energy, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = color
    ob = bpy.data.objects.new(name, ld); scene.collection.objects.link(ob); ob.location = loc
    d = (Vector((0.4, 0, 0)) - Vector(loc)); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
area('key', (0.6, -2.4, 2.2), 340, 2.2, (1.0, 0.97, 0.92))
area('fill', (-1.4, -2.6, 0.2), 120, 3.0, (0.75, 0.85, 1.0))
area('rim', (0.4, 1.6, 2.4), 260, 1.4, (0.8, 0.9, 1.0))

cam = bpy.data.cameras.new('cam'); cam.type = 'ORTHO'; cam.ortho_scale = 1.62
co = bpy.data.objects.new('cam', cam); scene.collection.objects.link(co)
co.location = (0.375, -4.0, 0.0); co.rotation_euler = (math.radians(90), 0, 0); scene.camera = co

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'; scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.resolution_x, scene.render.resolution_y = 1620, 800
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print('RENDERED', OUT)
