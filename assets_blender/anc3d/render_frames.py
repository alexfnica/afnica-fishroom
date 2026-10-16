# V17.90 sprite frames of one 3D bristlenose for the game (2x game px, transparent, contact shadow baked in).
# Frame = 160x90 game px; the fish's mid-body ground point sits at (77.7, 48.4) of that frame, which is where the old
# sprite's (60, 38.4) lands when the 160x90 canvas sits at (-20, -10) inside the 120x70 fish box.
# Run: D:\Blender\blender.exe -b -P render_frames.py -- <M|F> <out_dir> [samples]
import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anc_build as B, anc_build2 as B2
a = sys.argv[sys.argv.index('--') + 1:]; SEX, OUT = a[0], os.path.abspath(a[1]); SAMP = int(a[2]) if len(a) > 2 else 48
os.makedirs(OUT, exist_ok=True)
FW, FH, PX = 160, 90, 32.5; PIV = (77.7, 48.4)
sc, cam = B.scene_setup(res=(FW * 2, FH * 2), ortho=FW / PX, pitch=3, target=(0, 0, 0), samples=SAMP)   # nearly level, like the photos
B2.EMIT = .75; bpy.data.objects['sun'].data.energy = 1.4   # the photo's own colours, a little shading on top
cam.data.shift_x = .5 - PIV[0] / FW                       # the world origin lands on the pivot pixel
cam.data.shift_y = (.5 - (1 - PIV[1] / FH)) * FH / FW
ground = bpy.data.objects['ground']
L = B2.LEN[SEX]
FR = []
for d in range(15, 91, 15): FR.append(('yaw', d, dict(fold=0., spread=1., sweep=.05), dict(yaw=-d)))   # yaw00/crawl/rasp/swim come from the photos (photo_frames.py)
for i in range(3): FR.append(('glass', i, dict(fold=1., spread=1.1, sweep=.08, bend=(-.16, 0, .16)[i], bend_from=1.6, paired='top'), dict(yaw=0, glass=True)))   # fins flat on the glass
if os.environ.get('ONLY'): FR = [f for f in FR if f[0] == os.environ['ONLY']]
meta = []
for kind, idx, fp, pose in FR:
    for o in [o for o in bpy.data.objects if o.name.startswith('fish')]: bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for dd in [dd for dd in coll if dd.users == 0]: coll.remove(dd)
    f = B2.build_fish(SEX, 'fish', **fp)
    yaw = math.radians(pose.get('yaw', 0))
    # root = snout; put the mid-body ground point on the world origin, then turn about it
    from mathutils import Vector, Matrix
    half = L / 2
    if pose.get('glass'):
        ground.hide_render = True
        f.rotation_euler = (math.radians(-90), 0, 0); f.location = (half, 0, 0)
    else:
        ground.hide_render = False
        pit = math.radians(pose.get('pitch', 0))
        f.rotation_euler = (0, pit, yaw); f.location = (half * math.cos(yaw) + pose.get('dx', 0), half * math.sin(yaw), pose.get('lift', 0) + half * math.sin(pit) * 0)
    bpy.context.view_layer.update()
    name = '%s_%s%02d.png' % (SEX, kind, idx); sc.render.filepath = os.path.join(OUT, name); bpy.ops.render.render(write_still=True)
    meta.append(dict(file=name, kind=kind, i=idx, yaw=pose.get('yaw', 0)))
    print('FRAME', name, flush=True)
json.dump(dict(sex=SEX, w=FW * 2, h=FH * 2, piv=PIV, frames=meta), open(os.path.join(OUT, '%s_frames.json' % SEX), 'w'), indent=1)
