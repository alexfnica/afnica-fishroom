# One fish, side view at game framing, 4x game px: current look vs proposed fix. Run: blender -b -P still_fix.py -- <M|F> <out.png> <fold> <pitch> <emit> <fin_reach> <sun>
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; SEX, OUT = a[0], os.path.abspath(a[1]); fold, pitch, emit, reach, sun = (float(v) for v in a[2:7])
B2.EMIT = emit; B2.FIN_REACH = reach
sc, cam = B.scene_setup(res=(640, 360), ortho=160 / 32.5, pitch=pitch, target=(0, 0, 0), samples=64)
cam.data.shift_x = .5 - 77.7 / 160; cam.data.shift_y = (.5 - (1 - 48.4 / 90)) * 90 / 160
bpy.data.objects['sun'].data.energy = sun
f = B2.build_fish(SEX, 'fish', fold=fold, spread=1., sweep=.05); L = B2.LEN[SEX]; f.location = (L / 2, 0, 0)
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
