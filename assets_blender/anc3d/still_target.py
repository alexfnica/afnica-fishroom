# Step-2 target still: the 3D cave (owner's terracotta photo on a 3D tube), the male guarding head-out lying on the cave
# floor, the female resting on the sand turned toward us; transparent PNG with contact shadows, to lay over the game sand.
# Run: D:\Blender\blender.exe -b -P still_target.py -- <out.png> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; OUT = os.path.abspath(a[0]); SAMP = int(a[1]) if len(a) > 1 else 64
sc, cam = B.scene_setup(res=(1200, 680), ortho=9.23, pitch=8, target=(0, 0, 2.0), samples=SAMP)
cave = B.build_cave(cam, sc, loc=(-1.2, .6, 0))
mouth, ax, floor = B.cave_axis(cave)
# male: inside, facing out, snout 0.42 past the mouth, belly on the curved floor; fins tucked until nothing touches the clay
for spread, sweep in ((.5, .35), (.45, .45), (.4, .5), (.35, .55)):
    m = B.build_fish('M', 'male', fold=.35, spread=spread, sweep=sweep)
    face = -ax; m.rotation_euler = (0, 0, math.atan2(face.y, face.x))
    p = mouth + face * .6; m.location = (p.x, p.y, floor + .05)
    bpy.context.view_layer.update(); cl = B.clearance(B.fish_points(m), cave)
    print('male spread', spread, 'sweep', sweep, 'worst intrusion into the clay %.3f' % cl)
    if cl <= 0 or spread == .35: break
    for o in [m] + list(m.children_recursive): bpy.data.objects.remove(o, do_unlink=True)
# female: on the sand, front right, turned 30 deg toward us, dorsal folded, fins flat
f = B.build_fish('F', 'female', fold=.7, spread=1.0, sweep=.15)
f.rotation_euler = (0, math.radians(2), math.radians(210)); f.location = (1.6, -1.3, 0)
bpy.context.view_layer.update(); print('female intrusion into the clay %.3f' % B.clearance(B.fish_points(f), cave))
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True); print('SAVED', OUT)
