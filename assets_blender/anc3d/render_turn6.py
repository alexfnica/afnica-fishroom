# V17.104 SNAP turn (owner: the V17.102/103 arc "turns like a shark - not realistic"; ref. the owner's own calico juvenile
# clip, 6.60-7.40 s, AFNICA_Anc103_calico_turn.jpg): a bristlenose stays flat on the bottom, its head / pectorals hold
# their spot like a pivot, the tail kicks round into a sharp C and the body follows and straightens - about 0.5 s, then
# it settles. No walking arc, no lift, no roll; the game camera stays side-on (3 deg).
# Geometry: the pivot P sits D_PIV body lengths ahead of the mid-body (pectoral base); the body rotates PI about it, so
# the mid-body ends 2*D_PIV BL further along - block90 carries the fish's x along with it (no jump at the hand-back).
# Timing e(u) = smoothstep(u^.75): quick flick, slow settle. C-bend follows the turn rate, peaking a little early.
# Same frame layout as render_turn4 (240x110 game px at 2x, mid-body ground point at (110, 64)); TURN_N+1 frames.
# Run: D:\Blender\blender.exe -b -P render_turn6.py -- <M|F|JO|JB> <out_dir> [samples]   (env TURN_K="0,8,16" = only these)
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; SEX, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 40
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 240, 110, 32.5; PIV = (110., 64.)
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=3, target=(0, 0, 0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
B2.HANG = True; B2.FLAT = True                               # V17.102b rules: flat photo colours, no baked shadow
for o in bpy.data.objects:
    if getattr(o, 'is_shadow_catcher', False): o.hide_render = True
cam.data.shift_x = .5 - PIV[0] / FW; cam.data.shift_y = (.5 - (1 - PIV[1] / FH)) * FH / FW
L = B2.LEN[SEX]; half = L / 2; N = int(os.environ.get('TURN_N', '30'))
D_PIV = float(os.environ.get('D_PIV', '.28')); d = D_PIV * L
SG = float(os.environ.get('TURN_SIDE', '1'))   # V17.104c: +1 = head turns AWAY from the viewer (the model's head-on face looked like a stretched mask), -1 = toward
KS = [int(v) for v in os.environ['TURN_K'].split(',')] if os.environ.get('TURN_K') else range(N + 1)
ss3 = lambda t: (lambda q: q * q * (3 - 2 * q))(min(1., max(0., t)))
E = lambda u: ss3(min(1., max(0., u)) ** .75)               # quick flick, slow settle (block90 uses the same curve)
dE = lambda u: (E(u + 1e-3) - E(u - 1e-3)) / 2e-3
DMAX = max(dE(i / 400.) for i in range(1, 400))
LIFT = None; SHY = None
for k in range(N + 1):
    if k not in KS and LIFT is not None: continue
    u = k / N; e = E(u); flare = math.sin(math.pi * u)
    th = SG * math.pi * e                                      # heading: right -> away from the viewer (SG +1) -> left
    bend = SG * 1.15 * dE(min(1., u + .06)) / DMAX * min(1., u / .08, (1 - u) / .08)   # C into the turn while it swings, straight at both ends
    mx, my = d - d * math.cos(th), -d * math.sin(th)           # mid-body = P - d*dir, P = (d, 0)
    for o in [o for o in bpy.data.objects if o.name.startswith('fish')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    f = B2.build_fish(SEX, 'fish', fold=0., spread=1. + .3 * flare, sweep=.05, bend=bend, bend_from=1.0,
                      wave=.05 * flare, wave_ph=-5 * math.pi * u)        # pectorals brace, a tail kick or two
    f.rotation_euler = (0, 0, th); f.location = (mx + half * math.cos(th), my + half * math.sin(th), 0)
    bpy.context.view_layer.update()
    if LIFT is None:                                         # measured once (frame 0 = the photo's pose), then kept: no lift
        mz = min((o.matrix_world @ v.co).z for o in bpy.data.objects if o.name.startswith('fish') and o.type == 'MESH' for v in o.data.vertices)
        LIFT = max(0., -mz); cam.data.shift_y += LIFT / cam.data.ortho_scale
    f.location.z = LIFT
    if SHY is None: SHY = cam.data.shift_y
    cam.data.shift_y = SHY + my * math.sin(math.radians(3)) / cam.data.ortho_scale   # sand line stays put
    bpy.context.view_layer.update()
    if k not in KS: continue
    sc.render.filepath = os.path.join(OUT, '%s_turn%02d.png' % (SEX, k)); bpy.ops.render.render(write_still=True)
    print('FRAME', k, round(math.degrees(th)), round(bend, 2), round(mx / L, 3), flush=True)
