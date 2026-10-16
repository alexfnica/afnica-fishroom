import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
B.CAVE['L'] = 4.46
sc, cam = B.scene_setup(res=(200, 100), ortho=10, pitch=3, target=(0, 0, 0), samples=4)
cave = B.build_cave(cam, sc, loc=(0, 0, 0)); mouth, ax, floor = B.cave_axis(cave)
m = B2.build_fish('M', 'male', fold=.15, spread=.08, sweep=.22); d = -50
snout = mouth - ax * (d / 32.5); dirv = -ax
m.rotation_euler = (0, 0, math.atan2(dirv.y, dirv.x)); m.location = (snout.x, snout.y, floor + .1); bpy.context.view_layer.update()
inv = cave.matrix_world.inverted(); c = B.CAVE
for o in m.children_recursive:
    if o.type != 'MESH': continue
    w = -9; at = None
    for v in o.data.vertices:
        q = inv @ (o.matrix_world @ v.co); rr = math.hypot(q.y, q.z)
        if -c['L'] / 2 - .02 <= q.x <= c['L'] / 2:
            outer = c['lip'] if q.x < -c['L'] / 2 + c['lipL'] + .04 else c['R']
            if c['r'] - .005 < rr < outer + .005:
                iv = min(rr - c['r'], outer - rr)
                if iv > w: w = iv; at = (round(q.x, 2), round(q.y, 2), round(q.z, 2), 'local', tuple(round(t, 2) for t in v.co))
    if w > 0: print('HIT', o.name, round(w, 4), at)
print('done')
