# V17.92 natural U-turn frames: the head swings toward the viewer first, the body curls into a C and the tail follows
# (instead of a rigid turntable spin). 13 frames u = 0..1 for one turn from facing right to facing left (head toward the
# viewer); the opposite turn is the mirror image. Same frame contract as render_frames.py (2x of 160x90, mid-body ground
# point at 155.4, 96.8), contact shadow baked. Frame u=0 is also the side-on 3D reference for the colour match.
# Run: D:\Blender\blender.exe -b -P render_turn.py -- <M|F|JO|JB> <out_dir> [samples]
import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; SEX, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 48
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 160, 90, 32.5; PIV = (77.7, 48.4)
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=3, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
cam.data.shift_x = .5 - PIV[0] / FW; cam.data.shift_y = (.5 - (1 - PIV[1] / FH)) * FH / FW
L = B2.LEN[SEX]; N = 24
for k in range(N + 1):
    u = k / N; e = .5 - .5 * math.cos(math.pi * u)                     # eased progress
    yaw = -(180 * e + 28 * math.sin(math.pi * u))                       # the head leads ...
    bend = -.85 * math.sin(math.pi * u)                                 # ... the tail lags: body curled into a C
    for o in [o for o in bpy.data.objects if o.name.startswith('fish')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    flare = math.sin(math.pi * u)                                     # pectorals planted wide while pivoting (ref. 10:05)
    f = B2.build_fish(SEX, 'fish', fold=0., spread=1. + .35 * flare, sweep=.05 - .05 * flare, bend=bend, bend_from=1.0)
    y = math.radians(yaw); half = L / 2
    lx, ly = .18 * math.sin(math.pi * u), -.45 * math.sin(math.pi * u)  # a small loop toward the viewer, back at the end
    f.rotation_euler = (0, 0, y); f.location = (half * math.cos(y) + lx, half * math.sin(y) + ly, 0)
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, '%s_turn%02d.png' % (SEX, k)); bpy.ops.render.render(write_still=True)
    print('FRAME', k, flush=True)
