# Stylised Pixar-leaning character built from primitives (no external model). Run:
#   D:/Blender/blender.exe -b -P make_char.py -- <json file>   (json: {"out": "...png", "skin": "#e0ac86", ...})
# Options: skin, hair, hairStyle(short|curly|long|bun|bald), eyes, top, topStyle(tee|hoodie), pants, shorts(bool), shoes, yaw, samples, w, h
import bpy, bmesh, math, sys, json, random
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
O = dict(out='D:/ClaudeWork/char.png', skin='#e0ac86', hair='#4a2a18', hairStyle='short', eyes='#5a3a22', top='#e8b83a', topStyle='hoodie',
         pants='#26272c', shorts=False, shoes='#e9ecef', yaw=18, samples=48, w=700, h=1100)
if argv: O.update(json.load(open(argv[0])))
random.seed(5)

def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    return (f(c[0]), f(c[1]), f(c[2]), 1)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = O['samples']; sc.cycles.use_denoising = True
try: sc.cycles.device = 'CPU'
except Exception: pass
sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = O['w'], O['h']; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'

def mat(name, col, rough=.5, sss=0, sss_col=None, spec=.5, sheen=0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = srgb(col) if isinstance(col, str) else col
    b.inputs['Roughness'].default_value = rough
    for k, v in (('Subsurface Weight', sss), ('Subsurface Scale', .05), ('Specular IOR Level', spec), ('Sheen Weight', sheen)):
        try: b.inputs[k].default_value = v
        except Exception: pass
    if sss and sss_col is not None:
        try: b.inputs['Subsurface Radius'].default_value = sss_col
        except Exception: pass
    return m

root = bpy.data.objects.new('char', None); sc.collection.objects.link(root)
DZ = -.17; HS = 1.32; PIV = Vector((0, 0, 1.56)); HEADP = []; HEADMODE = [False]
upper = bpy.data.objects.new('upper', None); sc.collection.objects.link(upper); upper.parent = root; upper.location = (0, 0, DZ)
def ell(name, loc, sc3, m, rot=(0, 0, 0), seg=40, par=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = sc3; o.rotation_euler = rot
    bpy.ops.object.shade_smooth(); o.data.materials.append(m); o.parent = par or upper
    if HEADMODE[0]: HEADP.append(o)
    return o
def limb(name, p0, p1, r0, r1, m, par=None):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; mid = (p0 + p1) / 2
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r0, radius2=r1, depth=d.length, location=mid)
    o = bpy.context.active_object; o.name = name
    o.rotation_euler = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()
    bpy.ops.object.shade_smooth(); o.data.materials.append(m); o.parent = par or upper
    s = o.modifiers.new('sub', 'SUBSURF'); s.levels = 1
    return o

SK = mat('skin', O['skin'], .45, .35, (1.0, .35, .25), .45)
HR = mat('hair', O['hair'], .38, 0, None, .6, .4)
TOP = mat('top', O['top'], .85, 0, None, .1, .5)
PANTS = mat('pants', O['pants'], .8, 0, None, .1, .3)
SHOE = mat('shoe', O['shoes'], .45, 0, None, .5)
SOLE = mat('sole', '#d9dde1', .6)
WHITE = mat('white', '#f7f7f4', .25, 0, None, .6)
IRIS = mat('iris', O['eyes'], .25, 0, None, .8)
DARK = mat('dark', '#0b0b10', .15, 0, None, 1)
LIP = mat('lip', '#a8504f', .4, .2, (1, .3, .3))
BLUSH = mat('blush', '#e98d7e', .5, .3, (1, .3, .3))
GLOW = bpy.data.materials.new('glow'); GLOW.use_nodes = True
gn = GLOW.node_tree.nodes; gn.clear(); em = gn.new('ShaderNodeEmission'); out = gn.new('ShaderNodeOutputMaterial'); em.inputs['Strength'].default_value = 6
GLOW.node_tree.links.new(em.outputs[0], out.inputs[0])

# ---- legs and shoes
for s in (-1, 1):
    x = s * .088
    if O['shorts']:
        limb('thigh', (x, 0, .84), (x, -.01, .54), .09, .068, PANTS, root)
        limb('calf', (x, -.01, .56), (x, -.02, .1), .058, .05, SK, root)
    else:
        limb('leg', (x, 0, .86), (x, -.01, .09), .094, .062, PANTS, root)
    ell('shoe', (x * 1.05, -.04, .06), (.075, .14, .065), SHOE, par=root)
    ell('sole', (x * 1.05, -.04, .02), (.078, .145, .024), SOLE, par=root)
# ---- torso and neck
ell('hips', (0, 0, .97), (.18, .115, .14), PANTS)
ell('torso', (0, 0, 1.17), (.19, .115, .27), TOP)
ell('chest', (0, -.004, 1.29), (.2, .12, .15), TOP)
limb('neck', (0, 0, 1.43), (0, 0, 1.54), .052, .05, SK)
if O['topStyle'] == 'hoodie':
    ell('hood', (0, .07, 1.45), (.14, .09, .075), TOP)
    ell('pocket', (0, -.1, 1.02), (.1, .03, .05), TOP)
# ---- arms (long sleeves) and hands
for s in (-1, 1):
    sh = (s * .205, 0, 1.38); el = (s * .255, -.01, 1.14); wr = (s * .245, -.05, .94)
    ell('shoulder', sh, (.075, .075, .075), TOP)
    limb('uarm', sh, el, .068, .06, TOP); ell('elbow', el, (.06, .06, .06), TOP)
    limb('farm', el, wr, .06, .052, TOP)
    ell('cuff', wr, (.058, .058, .035), TOP, rot=(.3, 0, 0))
    ell('hand', (s * .245, -.062, .87), (.045, .036, .065), SK, rot=(.2, 0, 0))
    ell('thumb', (s * .205, -.078, .885), (.016, .016, .035), SK)
# ---- head
HEADMODE[0] = True
ell('head', (0, 0, 1.66), (.125, .135, .15), SK, seg=64)
ell('chin', (0, -.025, 1.57), (.088, .092, .075), SK, seg=48)
for s in (-1, 1): ell('ear', (s * .127, .005, 1.655), (.02, .03, .045), SK, rot=(0, 0, s * .2))
ell('nose', (0, -.134, 1.642), (.026, .03, .028), SK)
for s in (-1, 1):
    ex = s * .052
    ell('eyeW', (ex, -.112, 1.685), (.037, .028, .046), WHITE)
    ell('iris', (ex - s * .002, -.134, 1.684), (.025, .012, .03), IRIS)
    ell('pupil', (ex - s * .002, -.1405, 1.685), (.0135, .007, .0165), DARK)
    ell('hl1', (ex + .008, -.1465, 1.696), (.007, .004, .007), GLOW)
    ell('hl2', (ex - .007, -.144, 1.673), (.0035, .003, .0035), GLOW)
    ell('lid', (ex, -.11, 1.718), (.04, .028, .016), SK, rot=(.15, 0, -s * .08))
    ell('brow', (ex, -.124, 1.752), (.036, .012, .0085), HR, rot=(.1, 0, s * .22))
    ell('cheek', (s * .082, -.108, 1.612), (.034, .02, .026), BLUSH)
# smile: a short beveled curve
cv = bpy.data.curves.new('smile', 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = .0042 * HS; cv.bevel_resolution = 3
sp = cv.splines.new('POLY'); pts = []
for i in range(15):
    a = -1 + 2 * i / 14
    q = Vector((a * .05, -.126 - .006 * (1 - a * a), 1.592 + .016 * a * a)); q = (q - PIV) * HS + PIV; pts.append(tuple(q))
sp.points.add(len(pts) - 1)
for p, c in zip(sp.points, pts): p.co = (c[0], c[1], c[2], 1)
mo = bpy.data.objects.new('smile', cv); sc.collection.objects.link(mo); mo.data.materials.append(LIP); mo.parent = upper
# ---- hair
def hair_cap(zmin=1.715):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=28, radius=1)
    for v in bm.verts:
        v.co.x *= .138; v.co.y *= .148; v.co.z *= .16; v.co.y += .012; v.co.z += 1.675
    kill = [v for v in bm.verts if not ((v.co.z > zmin and v.co.y > -.09) or (v.co.y > .02 and v.co.z > 1.55))]
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    me = bpy.data.meshes.new('cap'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('cap', me); sc.collection.objects.link(o); o.parent = upper; me.materials.append(HR); HEADP.append(o)
    for p in me.polygons: p.use_smooth = True
    so = o.modifiers.new('sol', 'SOLIDIFY'); so.thickness = .012
hs = O['hairStyle']
if hs != 'bald': hair_cap()
def fringe(n, spread, z0):
    for i in range(n):
        a = math.radians(-spread + i * 2 * spread / (n - 1)); ell('fringe', (math.sin(a) * .098, -.116 + abs(a) * .03, z0 - abs(a) * .03), (.05, .03, .037), HR, rot=(.3, 0, -a * .5))
if hs == 'short':
    fringe(9, 70, 1.757); ell('quiff', (-.03, -.07, 1.82), (.085, .07, .05), HR, rot=(0, .15, .25))
elif hs == 'curly':
    for i in range(80):
        th = random.uniform(0, math.tau); ph = random.uniform(.15, 1.5)
        x = math.sin(ph) * math.cos(th); y = math.sin(ph) * math.sin(th); z = math.cos(ph)
        if y < -.35 and z < .8: continue
        ell('curl', (x * .15, y * .16 + .01, 1.67 + z * .175), (.052, .052, .052), HR, seg=16)
elif hs == 'long':
    ell('back', (0, .085, 1.5), (.15, .08, .26), HR)
    for s in (-1, 1): ell('side', (s * .13, .0, 1.56), (.035, .06, .13), HR)
    fringe(7, 60, 1.76)
elif hs == 'bun':
    ell('bun', (0, .06, 1.86), (.07, .07, .065), HR); fringe(7, 60, 1.76)
HEADMODE[0] = False
for o in HEADP:
    o.location = (Vector(o.location) - PIV) * HS + PIV; o.scale = (o.scale[0] * HS, o.scale[1] * HS, o.scale[2] * HS)
root.rotation_euler = (0, 0, math.radians(O['yaw']))
# ---- light and camera
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (.55, .62, .68, 1); bg.inputs['Strength'].default_value = .45
def area(name, loc, energy, size, col=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.size = size; l.color = col
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 1.0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
area('key', (-1.6, -2.2, 2.6), 160, 1.8, (1, .96, .9)); area('fill', (2.0, -2.0, 1.4), 45, 2.4, (.85, .93, 1)); area('rim', (.6, 2.2, 2.4), 110, 1.4)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.0; cam.location = (0, -7.5, .93); cam.rotation_euler = (math.pi / 2, 0, 0)
sc.render.filepath = O['out']; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
bpy.ops.render.render(write_still=True)
print('RENDERED', O['out'])
