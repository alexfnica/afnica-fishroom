# V17.92 cave entry, smooth: the male is rendered WITHOUT the tube, split in two layers by the mouth plane:
#   _out = the part of him in front of the mouth (never hidden by the clay: the camera is on the mouth side),
#   _in  = the part inside the tube (the game shows it only through the mouth ellipse).
# The game draws: tube (C_tube00) -> _in clipped to the mouth opening -> _out, at the exact sub-pixel position, so he
# moves smoothly and still never overlaps the clay. Path: side-on on the sand at d=-60, lining up with the tube axis by
# d=-10, rising over the lip onto the curved floor, body undulating with progress (wriggle tied to distance).
# Frame contract = render_cave.py (340x110 game px at 2x, mouth at 173.8, 72). d = snout distance past the mouth (in);
# for 'o' (facing out) d = snout distance outside the mouth. Run:
#   D:\Blender\blender.exe -b -P render_cave2.py -- <out_dir> <i|o|f> [samples]
import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
a = sys.argv[sys.argv.index('--') + 1:]; OUT = os.path.abspath(a[0]); KIND = a[1]; SAMP = int(a[2]) if len(a) > 2 else 40
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 340, 110, 32.5; MOUTH_PX = (173.8, 72.0)
B.CAVE['L'] = 4.46
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=3, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
cave = B.build_cave(cam, sc, loc=(0, 0, 0)); mouth, ax, floor = B.cave_axis(cave)
bpy.context.view_layer.update()
v = world_to_camera_view(sc, cam, mouth)
cam.data.shift_x = (v.x - MOUTH_PX[0] / FW); cam.data.shift_y = (v.y - (1 - MOUTH_PX[1] / FH)) * FH / FW
cave.hide_render = True                                   # the tube is drawn by the game (C_tube00)
ground = bpy.data.objects['ground']
sm = lambda q: (lambda t: t * t * (3 - 2 * t))(min(1., max(0., q)))
X = Vector((1, 0, 0)); FL = floor + .1                    # belly height on the tube floor

def split_materials(side):
    """side 'out': only what is in front of the mouth plane; 'in': only what is behind it"""
    for m in bpy.data.materials:
        if not m.use_nodes or m.name.startswith(('clay', 'Material')): continue
        nt = m.node_tree; outn = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if not outn or not outn.inputs['Surface'].links: continue
        src = outn.inputs['Surface'].links[0].from_socket
        if src.node.name == 'split92': src = src.node.inputs[1].links[0].from_socket
        geo = nt.nodes.new('ShaderNodeNewGeometry')
        sub = nt.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = mouth
        dot = nt.nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; dot.inputs[1].default_value = ax
        cmp = nt.nodes.new('ShaderNodeMath'); cmp.operation = 'GREATER_THAN' if side == 'out' else 'LESS_THAN'; cmp.inputs[1].default_value = 0.
        tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.name = 'split92'
        nt.links.new(geo.outputs['Position'], sub.inputs[0]); nt.links.new(sub.outputs['Vector'], dot.inputs[0])
        nt.links.new(dot.outputs['Value'], cmp.inputs[0]); nt.links.new(cmp.outputs['Value'], mx.inputs['Fac'])
        nt.links.new(src, mx.inputs[1]); nt.links.new(tr.outputs['BSDF'], mx.inputs[2]); nt.links.new(mx.outputs['Shader'], outn.inputs['Surface'])

LF = B2.LEN['M']; EDGE = mouth.z - math.sqrt(B.CAVE['r'] ** 2 - .45 ** 2) + .015   # the lip edge under the belly corners (flat belly, round tube)
def climb(dd_in, outgoing=False):
    """snout height and pitch (rad, + = nose down) for a straight body resting on the lip edge: dd_in = how far the snout
    is past the mouth plane (units, in); the tail stays on the sand until it is near the edge, then the fish levels on the floor"""
    if not outgoing:
        if dd_in <= -.35: return 0., 0.
        if dd_in <= 0: zs = EDGE * sm((dd_in + .35) / .35); return zs, -math.atan(zs / LF)
        run = LF - dd_in                                 # body length still outside the mouth
        if run <= 0: return FL, 0.
        sl = EDGE / max(run, .8); zs = EDGE + sl * dd_in; w = sm((1. - run) / .8) if run < 1. else 0.
        return zs * (1 - w) + FL * w, -math.atan(sl) * (1 - w)
    out = -dd_in                                         # snout outside the mouth (units)
    if out <= LF * .45: return FL, 0.                  # head pokes out level
    if out >= LF: return 0., 0.
    sl = EDGE / out; zs = EDGE - sl * out               # the snout touches down on the sand, body over the edge
    w = sm((out - LF * .45) / .5); return FL * (1 - w) + max(0., zs) * w, math.atan(sl) * w

def pose(kind, d, fanph=None):
    """snout position, heading (unit, world), snout z, pitch, bend"""
    if kind == 'i':
        w = sm((d + 60) / 50.); dirv = (X * (1 - w) + ax * w).normalized()
        t = (d / PX) / dirv.x; snout = mouth + dirv * t
        z, pit = climb(d / PX)
        bend = (.06 + .14 * sm((d + 10) / 30.)) * math.sin(2 * math.pi * d / 32.)
        return snout, dirv, z, pit, bend
    if kind == 'o':
        w = sm((d - 60) / 50.); dirv = (-ax * (1 - w) - X * w).normalized()
        t = (d / PX) / -dirv.x; snout = mouth + dirv * t
        z, pit = climb(-d / PX, True)
        bend = (.06 + .14 * (1 - sm((d - 40) / 40.))) * math.sin(2 * math.pi * d / 32.)
        return snout, dirv, z, pit, bend
    snout = mouth + ax * (74 / PX)
    return snout, ax, FL, 0., .42 * math.sin(2 * math.pi * fanph / 24)   # 24 frames per beat (smooth)

FR = []
if KIND == 'i': FR = [('i', d) for d in range(-64, 145, 4)]
elif KIND == 'o': FR = [('o', d) for d in range(-52, 125, 4)]
else: FR = [('f', k) for k in range(24)]
if os.environ.get('CHUNK'):
    k_, n_ = map(int, os.environ['CHUNK'].split('/')); FR = FR[k_::n_]
LOG = []
for kind, d in FR:
    for o in [o for o in bpy.data.objects if o.name.startswith('male')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0 and not dd.name.startswith('clay')]: coll.remove(dd)
    snout, dirv, z, pit, bend = pose(kind, d if kind != 'f' else 0, d if kind == 'f' else None)
    inside = (kind == 'i' and d > -10) or (kind == 'o' and d < 60) or kind == 'f'
    tries = ((1., .05), (.6, .3), (.45, .45), (.32, .55), (.2, .65), (.1, .72)) if inside else ((1., .05),)
    for spread, sweep in tries:
        m = B2.build_fish('M', 'male', fold=.15, spread=spread, sweep=sweep, bend=bend, bend_from=1.7 if kind == 'f' else 1.0)
        m.rotation_euler = (0, pit, math.atan2(dirv.y, dirv.x)); m.location = (snout.x, snout.y, z)
        bpy.context.view_layer.update(); cl = B.clearance(B.fish_points(m), cave)
        if cl <= 0: break
        for o in [m] + list(m.children_recursive): bpy.data.objects.remove(o, do_unlink=True)
    else:
        m = B2.build_fish('M', 'male', fold=.15, spread=.1, sweep=.72, bend=bend, bend_from=1.0)
        m.rotation_euler = (0, pit, math.atan2(dirv.y, dirv.x)); m.location = (snout.x, snout.y, z); bpy.context.view_layer.update()
        cl = B.clearance(B.fish_points(m), cave)
    name = 'C2_%s%s' % (kind, ('%+04d' % d) if kind != 'f' else '%02d' % d)
    for side in ('out', 'in'):
        split_materials(side); ground.hide_render = side == 'in'            # inside: no ground shadow (dark tube floor)
        sc.render.filepath = os.path.join(OUT, '%s_%s.png' % (name, side)); bpy.ops.render.render(write_still=True)
    LOG.append(dict(name=name, clay=round(cl, 4)))
    print('FRAME', name, 'clay', cl, flush=True)
json.dump(LOG, open(os.path.join(OUT, 'log_%s_%s.json' % (KIND, os.environ.get('CHUNK', 'all').replace('/', 'of'))), 'w'))
