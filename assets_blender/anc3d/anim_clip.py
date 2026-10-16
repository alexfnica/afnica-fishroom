# First 3D bristlenose clip: male guarding with the head IN and the tail OUT of the cave, fanning sideways (eggs at the back);
# female on the sand: rests, turns head first through a real 3D turn, crawls slowly, then rasps with the head pressed down.
# Transparent PNG frames + log.json (positions, clay clearance). Run (frames f0..f1-1):
#   D:\Blender\blender.exe -b -P anim_clip.py -- <out_dir> <f0> <f1> [samples]
import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; OUT = os.path.abspath(a[0]); F0, F1 = int(a[1]), int(a[2]); SAMP = int(a[3]) if len(a) > 3 else 20
os.makedirs(OUT, exist_ok=True); FPS = 24; BL = 3.4
sc, cam = B.scene_setup(res=(910, 516), ortho=14.0, pitch=8, target=(0, 0, 3.37), samples=SAMP)   # 2x game px (455 x 258)
cave = B.build_cave(cam, sc, loc=(-2.6, .6, 0)); mouth, ax, floor = B.cave_axis(cave)
# the clutch at the back of the cave: a clump of orange eggs on the floor
egg = B.mat_plain('eggs', (.95, .55, .12), .3, .25)
import random; R = random.Random(5)
for i in range(46):
    u = R.uniform(1.25, 2.05); ang = R.uniform(-.9, .9); rr = .78 - .075
    lp = Vector((u, rr * math.sin(ang) * .9, -rr * math.cos(ang) * .92 + R.uniform(0, .16)))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.07, segments=10, ring_count=6, location=cave.matrix_world @ lp)
    bpy.context.object.data.materials.append(egg); bpy.context.object.data.polygons.foreach_set('use_smooth', [True] * len(bpy.context.object.data.polygons))

def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)

def female_pose(t):
    """snout position, yaw (rad), body bend, crawl wave, fin sweep, pitch, dorsal fold.
    Turns head first through a real 3D turn (head toward us at the middle), pivoting on the pectorals 0.55 behind the snout."""
    yaw0, yaw1 = math.radians(15), math.radians(-165); PIV = .55
    P0 = Vector((3.4, -1.05, 0))
    if t < 1.5: yaw = yaw0; P = P0; bend = 0; wave = 0; sw = .12; pit = 0; fold = .7
    elif t < 4.1:
        u = (t - 1.5) / 2.6; yaw = yaw0 + (yaw1 - yaw0) * ease(u); P = P0
        bend = -.4 * math.sin(math.pi * u); wave = 0; sw = .12 + .1 * math.sin(math.pi * u); pit = 0; fold = .55
    else:
        yaw = yaw1; d = Vector((math.cos(yaw), math.sin(yaw), 0))
        P = P0 + d * (.9 * ease((min(t, 7.6) - 4.1) / 3.5))             # slow crawl, smooth start and stop
        moving = t < 7.6; bend = 0; wave = .025 * moving; sw = .12 + (.1 * math.sin(2 * math.pi * 1.6 * t) if moving else 0)
        pit = math.radians(5) * ease((t - 7.6) / .6) if not moving else 0; fold = .55 if moving else .8
        if not moving:                                                # rasping: tiny forward shuffles
            k = (t - 7.6) / .7; P = P + d * (.018 * (math.floor(k) + ease(k - math.floor(k))))
    d = Vector((math.cos(yaw), math.sin(yaw), 0)); snout = P + d * PIV
    return snout, yaw, bend, wave, sw, pit, fold

LOG = []
for fr in range(F0, F1):
    t = fr / FPS
    for o in [o for o in bpy.data.objects if o.name.startswith(('male', 'female'))]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for d in [d for d in coll if d.users == 0]: coll.remove(d)
    # male: head in toward the eggs, tail out of the mouth, fanning (continuous, strength drifting, ~2.2 Hz)
    A = .42 + .1 * math.sin(2 * math.pi * t / 3.7)
    bend = A * math.sin(2 * math.pi * 2.2 * t)
    m = B.build_fish('M', 'male', fold=.3, spread=.45, sweep=.45, bend=bend, bend_from=1.7)
    m.rotation_euler = (0, 0, math.atan2(ax.y, ax.x)); p = mouth + ax * 2.25; m.location = (p.x, p.y, floor + .05)
    sn, yaw, fb, wv, sw, pit, fold = female_pose(t)
    f = B.build_fish('F', 'female', fold=fold, spread=1.0, sweep=sw, bend=fb, bend_from=1.0, wave=wv, wave_ph=-2 * math.pi * 1.6 * t)
    f.rotation_euler = (0, pit, yaw); f.location = sn
    bpy.context.view_layer.update()
    cl = B.clearance(B.fish_points(m), cave); clf = B.clearance(B.fish_points(f), cave)
    fmin = min(p.z for p in B.fish_points(f))
    LOG.append(dict(fr=fr, male_clay=round(cl, 4), female_clay=round(clf, 4), female_snout=[round(sn.x, 4), round(sn.y, 4)], yaw=round(yaw, 4),
                    female_minz=round(fmin, 4), bend=round(bend, 3)))
    sc.render.filepath = os.path.join(OUT, '%05d.png' % fr); bpy.ops.render.render(write_still=True)
    print('FRAME', fr, 'clay', round(cl, 3), flush=True)
json.dump(LOG, open(os.path.join(OUT, 'log_%05d.json' % F0), 'w'))
