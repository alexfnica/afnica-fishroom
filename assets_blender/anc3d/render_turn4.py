# V17.102 ARC turn (owner: "it must turn naturally, like a normal ancistrus"; ref. B7RksQ1xU18 25.0-27.75 s: the fish
# walks forward round a curve while it turns, head first, body bent, tail swinging wide - it does not spin on one spot and
# never shows a flat head-on face). Replaces the V17.95 pivot (render_turn3.py).
# The mid-body ground point walks a half ellipse: forward RX, round toward the viewer (depth RZ), back to (almost) the start
# facing the other way - so the game hands back to the photo in place (end depth 2*RZ ~ 2 px on screen at pitch 3).
# Heading = the path's tangent (always head first). The front follows the path ahead of the mid-body, the rear the path
# behind it: the body bends into the curve like the real fish (tail swings wide), strongest mid-turn.
# Owner: "don't lift the specimen during the animation": the fin lift (V17.100 HANG) is measured once on frame 0 and kept
# for every frame - the belly stays on the same sand line the whole turn, no bob.
# Same frame / atlas layout as render_turn3: 49 frames, 240x110 game px at 2x, mid-body ground point at (110, 64).
# Run: D:\Blender\blender.exe -b -P render_turn4.py -- <M|F|JO|JB> <out_dir> [samples]   (env TURN_K="0,12,24" = only these)
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; SEX, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 40
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 240, 110, 32.5; PIV = (110., 64.)
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=3, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
B2.HANG = True
# V17.102b (owner: "it hovers and it highlights / changes colour during the turn"): measured in the game - the baked
# shadow reached ~5 px below the fish (the photo's own shadow ends right under it) and the lit 3D was 3-7 % brighter than
# the photo, varying as it turned. Now: flat skin (the photo's colours as pure emission, no lighting) and no baked shadow -
# the game keeps the fish's own shadow under it for the whole turn (block90 moves it along the arc).
B2.FLAT = True
for o in bpy.data.objects:
    if getattr(o, 'is_shadow_catcher', False): o.hide_render = True
cam.data.shift_x = .5 - PIV[0] / FW; cam.data.shift_y = (.5 - (1 - PIV[1] / FH)) * FH / FW
L = B2.LEN[SEX]; half = L / 2; N = int(os.environ.get('TURN_N', '60'))   # V17.102c: 61 frames (one per game frame of the 2 s turn, no blending in the game)
RX, RZ = .30 * L, .15 * L                                    # forward reach / depth of the half ellipse
KS = [int(v) for v in os.environ['TURN_K'].split(',')] if os.environ.get('TURN_K') else range(N + 1)
ss5 = lambda q: (lambda t: t * t * t * (t * (t * 6 - 15) + 10))(min(1., max(0., q)))
def path(p):                                                 # p 0..1 along the turn -> (x, y, heading)
    f = math.pi * min(1., max(0., p))
    return RX * math.sin(f), -RZ * (1 - math.cos(f)), math.atan2(-RZ * math.sin(f), RX * math.cos(f))
LIFT = None; SHY = None
for k in range(N + 1):
    if k not in KS and LIFT is not None: continue
    u = k / N; e = ss5(u); flare = math.sin(math.pi * u)
    x, y, th = path(e)
    if abs(e - 1) < 1e-9: th = -math.pi
    LEAD = .16                                               # how far ahead / behind along the path the front / rear look
    hf = path(min(1., e + LEAD))[2] if e < 1 else -math.pi; hr = path(max(0., e - LEAD))[2]
    d = lambda a_, b_: (a_ - b_ + math.pi) % (2 * math.pi) - math.pi
    env = ss5(min(u, 1 - u) / .3)                            # straight at both ends (= the photo), full C from 30 % to 70 %
    bend = max(-1.05, min(1.05, 1.8 * d(hf, hr))) * env      # C into the curve, tail swinging wide (negative = turning toward the viewer here)
    for o in [o for o in bpy.data.objects if o.name.startswith('fish')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    f = B2.build_fish(SEX, 'fish', fold=0., spread=1. + .3 * flare, sweep=.05, bend=bend, bend_from=1.0,
                      wave=.03 * flare, wave_ph=-4 * math.pi * u)       # walking: pectorals as props, tail strokes
    f.rotation_euler = (0, 0, th); f.location = (x + half * math.cos(th), y + half * math.sin(th), 0)
    bpy.context.view_layer.update()
    if LIFT is None:                                         # measured once (frame 0 = the photo's pose), then kept
        mz = min((o.matrix_world @ v.co).z for o in bpy.data.objects if o.name.startswith('fish') and o.type == 'MESH' for v in o.data.vertices)
        LIFT = max(0., -mz); cam.data.shift_y += LIFT / cam.data.ortho_scale
    f.location.z = LIFT
    if k == 0 or SHY is None: SHY = cam.data.shift_y
    cam.data.shift_y = SHY + y * math.sin(math.radians(3)) / cam.data.ortho_scale   # the fish walks ~2*RZ nearer; the view follows its depth so its sand line stays put on screen (the fish itself stays on the floor)
    bpy.context.view_layer.update()
    if k not in KS: continue
    sc.render.filepath = os.path.join(OUT, '%s_turn%02d.png' % (SEX, k)); bpy.ops.render.render(write_still=True)
    print('FRAME', k, round(math.degrees(th)), round(bend, 2), flush=True)
