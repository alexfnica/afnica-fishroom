# V17.94 turn (owner: "everything" about the old turn was unnatural): the fish WALKS a U-turn - it curves away into the tank
# along a semicircle (radius 1.2 units ~ 39 px) and comes back facing the other way, its body bent along the arc; the
# heading follows the path, smooth start and stop, fastest in the middle. Depth hardly moves it on screen (camera pitch 3).
# 25 frames u = 0..1 for a turn from facing right to facing left (the other way = mirror). Frame 240x110 game px at 2x,
# mid-body ground point at the START at (110, 64) -> (220, 128) px. Run:
#   D:\Blender\blender.exe -b -P render_turn2.py -- <M|F|JO|JB> <out_dir> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; SEX, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 40
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 240, 110, 32.5; PIV = (110., 64.); R = 1.2
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=3, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
cam.data.shift_x = .5 - PIV[0] / FW; cam.data.shift_y = (.5 - (1 - PIV[1] / FH)) * FH / FW
L = B2.LEN[SEX]; N = 24
for k in range(N + 1):
    u = k / N; th = math.pi * (u - math.sin(2 * math.pi * u) / (2 * math.pi))   # heading 0 -> pi, smooth ends, fastest mid
    cx, cy = 0., R * (1 - math.cos(th))                                          # the forward part of the walk is added by the game (it fits the free space ahead)
    bend = min(.85, L / R * .32) * math.sin(math.pi * u)                         # body bent along the arc (tail toward the inside)
    for o in [o for o in bpy.data.objects if o.name.startswith('fish')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    flare = math.sin(math.pi * u)
    f = B2.build_fish(SEX, 'fish', fold=0., spread=1. + .2 * flare, sweep=.05, bend=bend, bend_from=1.0,
                      wave=.03 * flare, wave_ph=-2 * math.pi * 2 * u)            # walking: a small crawl wave
    half = L / 2
    f.rotation_euler = (0, 0, th); f.location = (cx + half * math.cos(th), cy + half * math.sin(th), 0)
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, '%s_turn%02d.png' % (SEX, k)); bpy.ops.render.render(write_still=True)
    print('FRAME', k, flush=True)
