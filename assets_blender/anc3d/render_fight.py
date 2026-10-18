# V17.96 male fight frames (owner's ref. youtube.com/shorts/R6KUQ73HhlI; pose approved as AFNICA_Anc95_fight_still.jpg):
# two adult males head-to-tail side by side, dorsals up, pectorals spread. Both fish in one frame, the pair's centre on the
# ground at (150, 84) of a 300x130 game px frame (2x). Fish 1 (in front) faces right, fish 2 (behind) faces left; at the end
# of the half circle the picture is the same with the two swapped, so every phase loops into the next. Played at 15 fps:
#   A settle 12 frames (0.8 s): dorsals rise, pectorals spread, the rear male starts to curl
#   B sweep  12 frames (0.8 s, cyclic): the rear male curls into a C and sweeps its tail at the other's head, the other flinches
#   C shove  15 frames (1.0 s): the rear male rears its front up and pushes forward in three small jerks
#   D strikes 21 frames (1.4 s), V17.98 (owner: they do not circle, they hit each other with their spines): the rear male
#     jerks his head sideways into the other's flank (fast in, slow out), then the front male strikes back; no circling
# V17.97: optional 4th arg = layer 1|2: only that fish is rendered (the other is a holdout that casts no shadow), so
# each male can be drawn in his own colour; files P1_* / P2_*.
# Run: D:\Blender\blender.exe -b -P render_fight.py -- <A|B|C|D> <out_dir> [samples] [layer]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; PH, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 40; LAYER = int(a[3]) if len(a) > 3 else 0
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
    if LAYER and name != 'male%d' % LAYER:
        for o in [f] + list(f.children_recursive): o.is_holdout = True; o.visible_shadow = False
for k in range(N):
    for o in [o for o in bpy.data.objects if o.name.startswith('male')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    u = k / N; al = 0.; b1 = 0.; b2 = .3; fold = 0.; spr = 1.35; rear = 0.; push = 0.; push1 = 0.; w2 = .03; ph = 0.
    # V17.99 (owner: "they spin against each other, it does not look natural"): a lateral display as in Ancistrus -
    # side by side, head to tail, both tails beating (~2.5 Hz at 15 fps), short shoves along the body, quick sideways head
    # strikes into the flank. Heads yaw at most 8 deg (was 22), the rear male's curl stays mild (bend <= .34, was 1.05).
    # Every phase starts and ends at b2 .12 / b1 -.056, so the phases loop into each other (A -> B.. -> C -> D -> B..).
    B2E, B1E = .12, -.056
    if PH == 'A':
        e = ss(u / .9); fold = .3 * (1 - e); spr = 1. + .35 * e; b2 = B2E * e; b1 = B1E * e
    elif PH == 'B':
        ph = 4 * math.pi * u
        b2 = B2E + .22 * math.sin(ph); b1 = .1 * math.sin(ph + math.pi + .6); w2 = .03
        b1 += B1E - .1 * math.sin(math.pi + .6)
    elif PH == 'C':
        env = math.sin(math.pi * u); jerk = abs(math.sin(3 * math.pi * u))
        rear = math.radians(4) * env * (.55 + .45 * jerk); push = .25 * env * jerk; push1 = -.08 * env * jerk; b2 = B2E + .06 * env; b1 = B1E
    s1 = s2 = 0.
    if PH == 'D':
        hit = lambda v: (v / .25 if v < .25 else max(0., 1 - (v - .25) / .75)) if 0 <= v < 1 else 0.   # fast in, slow out
        s2 = hit(u * 2); s1 = hit(u * 2 - 1); s2 = s2 * s2 * (3 - 2 * s2); s1 = s1 * s1 * (3 - 2 * s1)
        b2 = B2E - .12 * s2 + .05 * s1; b1 = B1E - .1 * s1 + .03 * s2
    r = DY * (1 - .38 * max(s1, s2))                             # the striker closes the gap
    m1 = (-.12 * s2, -r + .18 * s1 - .12 * s2); m2 = (.12 * s1, r - .18 * s2 + .12 * s1)   # striker pushes in, the other is knocked back
    place('male1', m1, H0 + math.radians(8) * s1 - math.radians(3) * s2, push=push1, fold=fold, spread=spr, sweep=.05, bend=b1, bend_from=1.0)
    place('male2', m2, H0 + math.pi + math.radians(8) * s2 - math.radians(3) * s1, rear=rear, push=push, fold=fold, spread=spr, sweep=.05, bend=b2, bend_from=1.1, wave=w2, wave_ph=ph + 1.2)
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, ('P%d_%s%02d.png' % (LAYER, PH, k) if LAYER else 'P_%s%02d.png' % (PH, k))); bpy.ops.render.render(write_still=True)
    print('FRAME', PH, k, flush=True)
