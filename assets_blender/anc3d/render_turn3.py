# V17.95 PIVOT turn (owner's reference B7RksQ1xU18 0:25.4-0:27.8, a common bristlenose on gravel): the fish turns almost
# on the spot - belly on the ground, pectorals spread wide as props, dorsal up, a gentle body curve, head swinging away into
# the tank while the tail sweeps round toward the viewer; slow and even (~2 s in the game). Replaces the V17.94 walking
# U-turn (render_turn2.py: a 39 px walk out and back = 6.2 px/frame on screen). The mid-body ground point only drifts a
# little into depth (radius R), so the game adds no walk of its own.
# 25 frames u = 0..1 for a turn from facing right to facing left (the other way = mirror). Frame 240x110 game px at 2x,
# mid-body ground point at (110, 64) -> (220, 128) px (same as V17.94, same atlas cells). Run:
#   D:\Blender\blender.exe -b -P render_turn3.py -- <M|F|JO|JB> <out_dir> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; SEX, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 40
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 240, 110, 32.5; PIV = (110., 64.); R = .12          # R: small drift into the tank (~4 px), no walk
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=3, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
B2.HANG = True   # V17.100 (owner: "the fins vanish for a moment when they turn"): fins + chin bristles hang like in the photo
SHY0 = None
cam.data.shift_x = .5 - PIV[0] / FW; cam.data.shift_y = (.5 - (1 - PIV[1] / FH)) * FH / FW
L = B2.LEN[SEX]; N = int(os.environ.get('TURN_N', '48'))   # V17.100: 49 frames (was 25: neighbours ~14 deg apart at peak yaw, blended into a pale mid-turn halo)
for k in range(N + 1):
    u = k / N; ss5 = lambda q: (lambda t: t * t * t * (t * (t * 6 - 15) + 10))(min(1., max(0., q)))   # smootherstep
    # V17.99 (owner: "it turns rigid and straight, as one flat piece; a real fish bends into a C, head leading"): the head
    # leads and the tail follows LAG later (0.24 s of the 2 s turn); the rigid front (head shield) carries the heading, the
    # rear body bends by the difference between head and tail heading (C into the turn, peak ~35 deg), straight at both ends.
    LAG = .12
    eh, et = ss5(u / (1 - LAG)), ss5((u - LAG) / (1 - LAG))
    th = -math.pi * eh                                                            # head heading (head swings toward the viewer, V17.98)
    cx, cy = 0., R * math.sin(th)                                                 # back to the same spot at the end
    flare = math.sin(math.pi * u)
    bend = -min(.62, .78 * math.pi * (eh - et))                                   # rear body lags the head: C into the turn
    for o in [o for o in bpy.data.objects if o.name.startswith('fish')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    f = B2.build_fish(SEX, 'fish', fold=0., spread=1. + .35 * flare, sweep=.05, bend=bend, bend_from=1.0,
                      wave=.015 * flare, wave_ph=-2 * math.pi * u)                 # pectorals as props, hardly any body wave
    half = L / 2
    f.rotation_euler = (0, 0, th); f.location = (cx + half * math.cos(th), cy + half * math.sin(th), 0)
    bpy.context.view_layer.update()
    # V17.100: the photo's fins hang below its belly (= ground) line; the shadow-catcher floor at z 0 hid them, so the fish is
    # lifted until the lowest fin tip touches the floor and the camera moves up the same amount (body stays where the photo has it)
    mz = min((o.matrix_world @ v.co).z for o in bpy.data.objects if o.name.startswith('fish') and o.type == 'MESH' for v in o.data.vertices)
    lift = max(0., -mz); f.location.z = lift; bpy.context.view_layer.update()
    if SHY0 is None: SHY0 = cam.data.shift_y
    cam.data.shift_y = SHY0 + lift / cam.data.ortho_scale
    print('LIFT', k, round(lift, 3), flush=True)
    sc.render.filepath = os.path.join(OUT, '%s_turn%02d.png' % (SEX, k)); bpy.ops.render.render(write_still=True)
    print('FRAME', k, flush=True)
