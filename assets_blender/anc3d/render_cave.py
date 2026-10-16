# V17.90 cave frames: the terracotta tube (owner's photo on the 3D tube) with the male INSIDE it, rendered together so the
# clay hides exactly what it should (owner: no cut-off, no overlap between the fish and the cave).
# Frame = 340x110 game px drawn at (cave.left-160, cave.top-30); the mouth centre lands on (173.8, 72) = the game's (L+13.8, T+42).
# Sets: tube (empty), in<d> (facing in, snout d px past the mouth), fan<i> (tail out, fanning), out<d> (facing out, snout d px
# outside the mouth; negative = still inside). Every frame is checked: no fish point inside the clay.
# Run: D:\Blender\blender.exe -b -P render_cave.py -- <out_dir> [samples] [only_prefix]
import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
a = sys.argv[sys.argv.index('--') + 1:]; OUT = os.path.abspath(a[0]); SAMP = int(a[1]) if len(a) > 1 else 48; ONLY = a[2] if len(a) > 2 else ''
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 340, 110, 32.5; MOUTH_PX = (173.8, 72.0)
B.CAVE['L'] = 4.46                                        # the game's tube: 158.6 x 64.9 px -> lip radius 1, length 4.46
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=3, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
cave = B.build_cave(cam, sc, loc=(0, 0, 0)); mouth, ax, floor = B.cave_axis(cave)
bpy.context.view_layer.update()
v = world_to_camera_view(sc, cam, mouth)                  # put the mouth centre on its pixel
cam.data.shift_x = (v.x - MOUTH_PX[0] / FW); cam.data.shift_y = (v.y - (1 - MOUTH_PX[1] / FH)) * FH / FW
FR = [('tube', 0, None)]
for d in range(-20, 141, 10):
    FR.append(('in', d, dict(face=1, d=d)))
    for v, bb in (('a', .2), ('b', -.2)): FR.append(('in', d, dict(face=1, d=d, wig=bb, v=v)))   # V17.91: wriggling in, body bent left / right
for i in range(12): FR.append(('fan', i, dict(face=1, d=74, fan=i)))
for d in range(-50, 121, 10):
    FR.append(('out', d, dict(face=-1, d=d)))
    for v, bb in (('a', .2), ('b', -.2)): FR.append(('out', d, dict(face=-1, d=d, wig=bb, v=v)))
meta = []
for kind, idx, P in FR:
    name = 'C_%s%s' % (kind, ('%+04d' % idx) if kind in ('in', 'out') else '%02d' % idx) + (P.get('v', '') if P else '')
    if ONLY and not name.startswith(ONLY): continue
    for o in [o for o in bpy.data.objects if o.name.startswith('male')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    cl = None
    if P:
        out_amt = max(0, (P['d'] - 60) / 60) if P['face'] < 0 else max(0, (-P['d'] + 10) / 30)   # fins open as he comes out
        for spread, sweep in ((.45 + .55 * min(1, out_amt), .45 - .3 * min(1, out_amt)), (.45, .45), (.38, .55), (.32, .6), (.26, .65), (.16, .7), (.08, .75)):
            fp = dict(fold=.15, spread=spread, sweep=sweep * .3)
            if 'fan' in P: fp.update(bend=.42 * math.sin(2 * math.pi * P['fan'] / 12), bend_from=1.7)
            if 'wig' in P: fp.update(bend=P['wig'], bend_from=.9)
            m = B2.build_fish('M', 'male', **fp)
            dirv = ax if P['face'] > 0 else -ax
            snout = mouth + ax * (P['d'] / PX) if P['face'] > 0 else mouth - ax * (P['d'] / PX)
            m.rotation_euler = (0, 0, math.atan2(dirv.y, dirv.x)); m.location = (snout.x, snout.y, floor + .1)
            bpy.context.view_layer.update(); cl = B.clearance(B.fish_points(m), cave)
            if cl <= 0: break
            for o in [m] + list(m.children_recursive): bpy.data.objects.remove(o, do_unlink=True)
            m = None
        if m is None:   # last resort: keep the tightest tuck even if a fin tip grazes (reported)
            m = B2.build_fish('M', 'male', fold=.15, spread=.08, sweep=.22, **({'bend': .42 * math.sin(2 * math.pi * P['fan'] / 12), 'bend_from': 1.7} if 'fan' in P else {'bend': P['wig'], 'bend_from': .9} if 'wig' in P else {}))
            m.rotation_euler = (0, 0, math.atan2(dirv.y, dirv.x)); m.location = (snout.x, snout.y, floor + .1); bpy.context.view_layer.update()
            cl = B.clearance(B.fish_points(m), cave)
    sc.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True)
    meta.append(dict(name=name, kind=kind, i=idx, clay=None if cl is None else round(cl, 4)))
    print('FRAME', name, 'clay', cl, flush=True)
json.dump(dict(w=FW * 2, h=FH * 2, mouth=MOUTH_PX, frames=meta), open(os.path.join(OUT, 'cave_frames%s.json' % ('_' + ONLY if ONLY else '')), 'w'), indent=1)
