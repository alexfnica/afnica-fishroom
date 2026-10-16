import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B
sc, cam = B.scene_setup(res=(1200, 680), ortho=9.23, pitch=8, target=(0, 0, .95), samples=8)
cave = B.build_cave(cam, sc, loc=(-1.2, .6, 0)); mouth, ax, floor = B.cave_axis(cave)
m = B.build_fish('M', 'male', fold=.35, spread=.55, sweep=.35); face = -ax; m.rotation_euler = (0, 0, math.atan2(face.y, face.x))
p = mouth + face * .42; m.location = (p.x, p.y, floor + .05); bpy.context.view_layer.update()
inv = cave.matrix_world.inverted(); c = B.CAVE
for o in m.children_recursive:
    if o.type != 'MESH': continue
    w = -9; at = None
    for v in o.data.vertices:
        q = inv @ (o.matrix_world @ v.co); rr = math.hypot(q.y, q.z)
        if -c['L']/2 <= q.x <= c['L']/2 and rr > c['r']:
            if rr - c['r'] > w: w = rr - c['r']; at = (round(q.x,2), round(q.y,2), round(q.z,2), 'local', tuple(round(t,2) for t in v.co))
    print(o.name, round(w,3), at)
