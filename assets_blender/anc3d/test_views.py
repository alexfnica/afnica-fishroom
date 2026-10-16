# Model check: one fish from several yaw angles on a transparent background.
# Run: D:\Blender\blender.exe -b -P test_views.py -- <M|F> <out_prefix> [fold spread sweep]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, anc_build as B; importlib.reload(B)
a = sys.argv[sys.argv.index('--') + 1:]
sex, out = a[0], a[1]; fold, spread, sweep = (float(v) for v in (a[2:5] if len(a) >= 5 else (0, 1, 0)))
sc, cam = B.scene_setup(res=(900, 500), ortho=4.6, pitch=12, target=(0, 0, .35), samples=32)
root = B.build_fish(sex, 'f', fold=fold, spread=spread, sweep=sweep)
for deg in (0, 35, 90, 150):
    root.rotation_euler = (0, 0, math.radians(-deg)); root.location = (1.75 * math.cos(math.radians(deg)), -1.75 * math.sin(math.radians(-deg)) * 0, 0)
    root.location = (1.75 * math.cos(math.radians(-deg)), 1.75 * math.sin(math.radians(-deg)), 0)
    sc.render.filepath = '%s_%03d.png' % (out, deg); bpy.ops.render.render(write_still=True)
