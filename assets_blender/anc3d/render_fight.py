# V17.96 male fight frames (owner's ref. youtube.com/shorts/R6KUQ73HhlI; pose approved as AFNICA_Anc95_fight_still.jpg):
# two adult males head-to-tail side by side, dorsals up, pectorals spread. Both fish in one frame, the pair's centre on the
# ground at (150, 84) of a 300x130 game px frame (2x). Fish 1 (in front) faces right, fish 2 (behind) faces left; at the end
# of the half circle the picture is the same with the two swapped, so every phase loops into the next. Played at 15 fps:
#   A settle 12 frames (0.8 s): dorsals rise, pectorals spread, the rear male starts to curl
#   B sweep  12 frames (0.8 s, cyclic): the rear male curls into a C and sweeps its tail at the other's head, the other flinches
#   C shove  15 frames (1.0 s): the rear male rears its front up and pushes forward in three small jerks
#   D circle 21 frames (1.4 s): the pair swings half a circle round its centre, head to tail
# Run: D:\Blender\blender.exe -b -P render_fight.py -- <A|B|C|D> <out_dir> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; PH, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 40
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 300, 130, 32.5; PIV = (150., 84.)
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=8, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
cam.data.shift_x = .5 - PIV[0] / FW; cam.data.shift_y = (.5 - (1 - PIV[1] / FH)) * FH / FW
L = B2.LEN['M']; HALF = L / 2; DY = 1.5; H0 = math.radians(14)
N = {'A': 12, 'B': 12, 'C': 15, 'D': 21}[PH]
def ss(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def place(name, mid, hd, rear=0., push=0., **kw):
    f = B2.build_fish('M', name, **kw)
    snout = (mid[0] + (HALF + push) * math.cos(hd), mid[1] + (HALF + push) * math.sin(hd))
    f.rotation_euler = (0, -rear, hd); f.location = (snout[0], snout[1], L * math.sin(rear) * .95)
for k in range(N):
    for o in [o for o in bpy.data.objects if o.name.startswith('male')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    u = k / N; al = 0.; b1 = 0.; b2 = .3; fold = 0.; spr = 1.35; rear = 0.; push = 0.; push1 = 0.; w2 = .03; ph = 0.
    if PH == 'A':
        e = ss(u / .9); fold = .3 * (1 - e); spr = 1. + .35 * e; b2 = .3 * e
    elif PH == 'B':
        ph = 2 * math.pi * u; c = (1 - math.cos(ph)) / 2
        b2 = .3 + .75 * c; b1 = -.14 * (1 - math.cos(ph - .9)) / 2; w2 = .03 + .03 * c
    elif PH == 'C':
        env = math.sin(math.pi * u); jerk = abs(math.sin(3 * math.pi * u))
        rear = math.radians(9) * env * (.55 + .45 * jerk); push = .3 * env * jerk; push1 = -.12 * env * jerk; b2 = .3 + .15 * env
    else:
        e = u * u * u * (u * (u * 6 - 15) + 10); al = math.pi * e
        b1 = b2 = .3 + .25 * math.sin(math.pi * u)
    ca, sa = math.cos(al), math.sin(al); r = DY * (1 - .62 * math.sin(math.pi * u)) if PH == 'D' else DY   # they close in while swinging
    m1 = (r * sa, -r * ca); m2 = (-r * sa, r * ca)              # mid-body points swing round the centre
    place('male1', m1, H0 + al, push=push1, fold=fold, spread=spr, sweep=.05, bend=b1, bend_from=1.0)
    place('male2', m2, H0 + math.pi + al, rear=rear, push=push, fold=fold, spread=spr, sweep=.05, bend=b2, bend_from=1.1, wave=w2, wave_ph=ph + 1.2)
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, 'P_%s%02d.png' % (PH, k)); bpy.ops.render.render(write_still=True)
    print('FRAME', PH, k, flush=True)
