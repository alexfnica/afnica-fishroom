# V17.101 fight stills (owner's ref. youtube.com/watch?v=FbPG89ootMs, "Ancistrus males fighting over dominance"):
#   H = the shoving hold (clip 25.4 s): both males face the SAME way, side by side, flanks pressed, heads level (cheek to
#       cheek), dorsals up, pectorals spread and overlapping; the far male rides a little up on the near one's shoulder.
#   W = the whirl burst (clip 82.2 s): heads still together, tails thrown apart into a V, both bodies curled, tails whipping.
# Same framing as still_fight.py (4x game size). Run:
#   D:\Blender\blender.exe -b -P still_fight101.py -- <H|W> <out.png> [samples]
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; PO, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 64
sc, cam = B.scene_setup(res=(1200, 680), ortho=9.23, pitch=8, target=(0, 0, 2.0), samples=SAMP)
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4
D = math.radians
def put(name, snout, hd, rear=0., lift=0., **kw):
    f = B2.build_fish('M', name, fold=0., spread=1.35, sweep=.05, **kw)   # origin = snout
    f.rotation_euler = (0, -rear, hd); f.location = (snout[0], snout[1], lift); return f
# Seen from the side (game camera, pitch 8) two parallel males hide each other, so the pair is turned a little toward
# us (PHI) and the far male rides up on the near one's shoulder, as in the clip at 41-59 s; heads stay together.
def pair(phi, th, g, far_rear, far_lift, b, bf, w=0.):
    n = (-math.sin(phi), math.cos(phi)); C = (1.9, 0.)
    put('male1', (C[0] - n[0] * g / 2, C[1] - n[1] * g / 2), phi + th, bend=-b, bend_from=bf, wave=w, wave_ph=0.)
    put('male2', (C[0] + n[0] * g / 2, C[1] + n[1] * g / 2), phi - th, rear=far_rear, lift=far_lift, bend=b, bend_from=bf, wave=w, wave_ph=2.2)
if PO == 'H': pair(D(-18), D(6), .85, D(10), .32, .08, 1.0)
else: pair(D(-18), D(12), .8, D(13), .3, -.8, .9, .05)
bpy.context.view_layer.update()
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True); print('SAVED', OUT)
