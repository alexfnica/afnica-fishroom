# Phase 3 target still (owner's ref. youtube.com/shorts/R6KUQ73HhlI 8.2-9.0 s): two adult males head-to-tail side by side,
# dorsals fully up, pectorals spread wide as props, the rear one curled into a C sweeping its tail at the other's head.
# Same framing as still_target.py (4x game size, lay over the game sand with compose_still.py). Run:
#   D:\Blender\blender.exe -b -P still_fight.py -- <out.png> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; OUT = os.path.abspath(a[0]); SAMP = int(a[1]) if len(a) > 1 else 64
sc, cam = B.scene_setup(res=(1200, 680), ortho=9.23, pitch=8, target=(0, 0, 2.0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
# front male: faces right, nearly straight, a slight brace of the tail away from the rival
m1 = B2.build_fish('M', 'male1', fold=0., spread=1.35, sweep=.05, bend=-.12, bend_from=1.0)
m1.rotation_euler = (0, 0, math.radians(14)); m1.location = (1.55, -1.2, 0)
# rear male: faces left, snout beside the front male's tail root, body bent into a C, tail swept toward the front male's head
m2 = B2.build_fish('M', 'male2', fold=0., spread=1.35, sweep=.05, bend=1.05, bend_from=1.1, wave=.04, wave_ph=1.2)
m2.rotation_euler = (0, 0, math.radians(180 + 18)); m2.location = (-1.5, 1.0, 0)
bpy.context.view_layer.update()
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True); print('SAVED', OUT)
