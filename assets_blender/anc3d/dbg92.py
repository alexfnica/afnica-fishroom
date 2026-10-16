import bpy, sys, os, math
sys.argv = [sys.argv[0], '--', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', '_dbg'), 'i', '4']
os.environ['CHUNK'] = '23/53'
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render_cave2.py')).read().split('LOG = []')[0])
kind, d = 'i', 28
snout, dirv, z, pit, bend = pose(kind, d)
for spread, sweep in ((1., .05), (.6, .3), (.45, .45), (.32, .55), (.2, .65), (.1, .72)):
    m = B2.build_fish('M', 'male', fold=.15, spread=spread, sweep=sweep, bend=bend, bend_from=1.0)
    m.rotation_euler = (0, pit, math.atan2(dirv.y, dirv.x)); m.location = (snout.x, snout.y, z); bpy.context.view_layer.update()
    inv = cave.matrix_world.inverted(); c = B.CAVE; worst = {}
    for o in m.children_recursive:
        if o.type != 'MESH': continue
        for v in o.data.vertices:
            q = inv @ (o.matrix_world @ v.co); rr = math.hypot(q.y, q.z)
            if -c['L'] / 2 - .02 <= q.x <= c['L'] / 2:
                outer = c['lip'] if q.x < -c['L'] / 2 + c['lipL'] + .04 else c['R']
                if c['r'] - .005 < rr < outer + .005:
                    iv = min(rr - c['r'], outer - rr)
                    if iv > worst.get(o.name, (0,))[0]: worst[o.name] = (round(iv, 3), round(q.x, 2), round(q.y, 2), round(q.z, 2))
    print('spread', spread, worst)
    for o in [m] + list(m.children_recursive): bpy.data.objects.remove(o, do_unlink=True)
print('z', z, 'pit', math.degrees(pit))
