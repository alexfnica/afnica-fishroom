# V17.101 male fight frames (owner's ref. youtube.com/watch?v=FbPG89ootMs "Ancistrus males fighting over dominance";
# poses approved as AFNICA_Anc101_fight_stills.jpg, made with still_fight101.py). Two adult males HEAD TO HEAD: both face
# the same way (right as rendered), side by side, flanks pressed, heads level, dorsals up, pectorals spread. Seen from
# the side two parallel fish hide each other, so the pair turns 18 deg toward us and the far male rides up on the near
# one's shoulder (clip 41-59 s). Both fish in one 300x130 game px frame (2x); the mid-body ground point of both males
# (they stand at the same x) at (150, 84). Phases (15 fps unless the game plays them slower):
#   S settle 12 frames: from the two side-on photos (pair straight, flat, dorsals half down) into the hold pose.
#     The game plays S backwards at the end (back to the photos), so there is no separate end phase.
#   H hold 16 frames, cyclic (the game plays it at ~8 fps = 2 s per push): the long shoving hold - the far male presses
#     his head in and forward, the near one braces, tails sway slowly, the pair drifts a little round (clip 25-27 s).
#   W whirl 15 frames (1 s): heads stay together, the tails are thrown apart and whip twice (clip 81.2-82.2 s), back to
#     the hold pose. Frame 0 of H, the last frame of S and the first/last frames of W are the same hold pose.
# V17.101b (owner: "they overlap before the fight and stay on one spot"): S is no longer used; new phases, none with x
#   baked in - the game slides the layers along the sand (smooth per game frame):
#   A approach 15 (played over 2 s): from the two side-on photos, the far male (the intruder) comes in (the game slides his
#     layer from 0.9 BL behind), the pair turns toward us, he rides up on the shoulder once alongside.
#   Q pivot 10 (played forward then back, 6 fps): the pair turns 30 deg more toward us and back.
#   Y / Z break-away 15 (10 fps): Y = near male leaves, Z = far male leaves; both straighten and settle flat side-on, the
#     leaver beats his tail (the game slides him 0.75 BL forward).
# Optional 4th arg = layer 1|2: only that fish is rendered (the other is a holdout that casts no shadow), so each male is
# recoloured on his own; files P1_* (near male) / P2_* (far male).
# Run: D:\Blender\blender.exe -b -P render_fight.py -- <A|H|W|Q|Y|Z> <out_dir> [samples] [layer] [solo]   (A, Y, Z with solo)
# Old head-to-tail version (V17.96-V17.99): out/render_fight_v99_backup.py
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; PH, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 40; LAYER = int(a[3]) if len(a) > 3 else 0; SOLO = len(a) > 4 and a[4] == 'solo'
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 300, 130, 32.5; PIV = (150., 84.)
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=8, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
B2.FLAT = True   # V17.102: flat skin = the photo's colours, no light, no highlight, no colour change as the pair turns
B2.ROUGH, B2.SHINE = .85, .06   # V17.101c (owner: "a highlight appears on the body"): matte like the photos
cam.data.shift_x = .5 - PIV[0] / FW; cam.data.shift_y = (.5 - (1 - PIV[1] / FH)) * FH / FW
L = B2.LEN['M']; HALF = L / 2; D = math.radians
N = {'A': 15, 'H': 16, 'W': 15, 'Q': 10, 'K': 18, 'Y': 15, 'Z': 15}[PH]
def ss(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def lerp(p, q, e): return {k: p[k] + (q[k] - p[k]) * e for k in p}
# hold pose = the approved still H; START = the two photos (straight, flat, side-on, dorsals half down)
BASE = dict(phi=D(-30), th=D(6), g=.95, rear=0., lift=0.,   # V17.102 (owner: "no hovering"): both on the sand, the pair turned 30 deg toward us so both show
            nb=-.08, fb=.08, bf=1.0, fold=0., spr=1.35, w=0., ph=0.)
START = dict(BASE, phi=0., th=0., rear=0., lift=0., nb=0., fb=0., fold=0., spr=1.)   # V17.101c: dorsal up as in the photo (fold .3 made it 6-10 px lower = a jump at the hand-over)
def place(name, snout, hd, rear, lift, **kw):
    f = B2.build_fish('M', name, sweep=.05, **kw)   # origin = snout, faces +X
    f.rotation_euler = (0, -rear, hd); f.location = (snout[0], snout[1], lift)
    if LAYER and name != 'male%d' % LAYER:
        for o in [f] + list(f.children_recursive):
            if SOLO: o.hide_render = True   # V17.101b: the game slides this layer, so it must be the whole fish (the game draws far first, near on top)
            else: o.is_holdout = True; o.visible_shadow = False
def turn_mid(snout, hd, d):                     # turn a fish by d about its mid-body (the head swings, not the tail)
    m = (snout[0] - HALF * math.cos(hd), snout[1] - HALF * math.sin(hd)); h2 = hd + d
    return (m[0] + HALF * math.cos(h2), m[1] + HALF * math.sin(h2)), h2
def pair(P, far_rear=0., far_head=0., near_head=0., w1=None, w2=None, P1=None, ny=0., fy=0., nr=0., push1=0., push2=0.):
    """male1 = near (the rival in the game), male2 = far (the intruder, rides up on the near one's shoulder).
    P1: optional separate pose dict for the near male (break-away phases)."""
    phi = P['phi']; n = (-math.sin(phi), math.cos(phi))
    # the snouts sit HALF ahead of the common mid-body point (the game anchor), turned with the pair
    C = (HALF * math.cos(phi), HALF * math.sin(phi)); g = P['g']; Q = P1 or P
    s1, h1 = turn_mid((C[0] - n[0] * g / 2 + push1 * math.cos(phi), C[1] - n[1] * g / 2 + push1 * math.sin(phi)), phi + Q['th'] + near_head, ny)   # ny > 0: head toward the far male
    s2, h2 = turn_mid((C[0] + n[0] * g / 2 + push2 * math.cos(phi), C[1] + n[1] * g / 2 + push2 * math.sin(phi)), phi - P['th'] - far_head, -fy)   # fy > 0: head toward the near male
    place('male1', s1, h1, nr, L * math.sin(nr) * .95, bend=Q['nb'], wave_ph=Q['ph'],
          fold=Q['fold'], spread=Q['spr'], bend_from=Q['bf'], wave=Q['w'] if w1 is None else w1)
    place('male2', s2, h2, P['rear'] + far_rear, P['lift'], bend=P['fb'], wave_ph=P['ph'] + 2.2,
          fold=P['fold'], spread=P['spr'], bend_from=P['bf'], wave=P['w'] if w2 is None else w2)
for k in range(N):
    for o in [o for o in bpy.data.objects if o.name.startswith('male')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    u = k / (N - 1)
    if PH == 'A':
        # V17.101b approach (played over 2 s): the game slides the far male's layer in from 0.9 BL behind (no x baked here);
        # the pair turns toward us, dorsals rise; he rides up on the near one's shoulder only once he is alongside (u > .6)
        e = ss(u); up = ss((u - .6) / .4); sw = 1 - ss((u - .5) / .5)          # swimming tail wave while he comes in
        P = lerp(START, BASE, e); P['ph'] = 6 * math.pi * u
        pair(P, w1=0., w2=.04 * sw)
    elif PH == 'H':
        u = k / N; p = (1 - math.cos(2 * math.pi * u)) / 2; s = math.sin(2 * math.pi * u)   # p: 0 -> 1 -> 0 push, s: sway
        P = dict(BASE, g=BASE['g'] - .07 * p, phi=BASE['phi'] + D(2) * s, nb=BASE['nb'] - .05 * s, fb=BASE['fb'] - .04 * s, w=.012 * p, ph=2 * math.pi * u)
        pair(P, far_head=D(3) * p, near_head=D(2) * p)   # V17.102: no rearing on the push
    elif PH == 'W':
        env = math.sin(math.pi * u); wh = .3 * env * math.sin(4 * math.pi * u)   # two whips in 1 s
        P = dict(BASE, phi=BASE['phi'] - D(6) * env, th=BASE['th'] + D(6) * env, g=BASE['g'] - .05 * env,
                 nb=BASE['nb'] + .88 * env + wh, fb=BASE['fb'] - .88 * env - wh, bf=1. - .1 * env, w=.05 * env, ph=4 * math.pi * u)
        pair(P)
    elif PH == 'K':
        # V17.101c head strikes (owner: "they fight with the head, the horns, not only the tails"): the far male swings his
        # head and bristly snout sideways into the near one's head (fast in, slow out), the near one's head is knocked
        # away; then the near one strikes back. Both lift the front a little as they hit. Starts and ends on BASE.
        hit = lambda v: (v / .22 if v < .22 else max(0., 1 - (v - .22) / .78)) if 0 <= v < 1 else 0.
        a2 = ss(hit(u * 2)); a1 = ss(hit(u * 2 - 1)); env = math.sin(math.pi * u)
        P = dict(BASE, phi=BASE['phi'] - D(6) * env, g=BASE['g'] - .1 * max(a1, a2), w=.02 * env, ph=4 * math.pi * u)
        pair(P, ny=D(16) * a1 - D(7) * a2, fy=D(16) * a2 - D(7) * a1, push1=.1 * a1, push2=.1 * a2)   # V17.102: sideways head swings on the sand, no rearing
    elif PH == 'Q':
        # V17.101b slow pivot (clip: the pair turns round over the fight): the pair turns 30 deg more toward us, played
        # forward then backward by the game; the far male presses a little higher
        e = ss(u); P = dict(BASE, phi=BASE['phi'] - D(30) * e)
        pair(P)
    else:
        # V17.101b break-away: Y = the near male leaves, Z = the far male leaves; the game slides the leaver's layer
        # forward (no x baked). Both straighten and settle flat side-on (START), the leaver beats his tail.
        e = ss(u); sw = math.sin(math.pi * min(1, u * 1.3)); P = lerp(BASE, START, e); P['ph'] = 7 * math.pi * u
        P['fold'] = BASE['fold'] + (START['fold'] - BASE['fold']) * e
        if PH == 'Y': pair(P, w1=.05 * sw, w2=0.)
        else: pair(P, w1=0., w2=.05 * sw)
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, ('P%d_%s%02d.png' % (LAYER, PH, k) if LAYER else 'P_%s%02d.png' % (PH, k))); bpy.ops.render.render(write_still=True)
