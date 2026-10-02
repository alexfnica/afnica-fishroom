# Paint an original newborn guppy fry sprite (side view, facing right), modelled on reference photos of real newborn
# guppies: a short glassy see-through body with the spine showing, a deep round head with a very large black eye ringed
# in gold, a warm golden belly (the last of the yolk), a small clear rounded tail fin and a faint fin fold.
# Run: D:\Blender\blender.exe -b -P paint_newborn.py -- <out.png> [supersample]
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
OUT = a[0]; K = int(a[1]) if len(a) > 1 else 3
UW, UH = 200, 70                                                 # work in 200x70 units, supersampled K times
W, H = UW * K, UH * K
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) / K
img = np.zeros((H, W, 4), np.float32)

def over(rgb, alpha):                                            # straight-alpha "over"
    A = img[..., 3]; a2 = np.clip(alpha, 0, 1); oa = a2 + A * (1 - a2)
    for c in range(3):
        img[..., c] = np.where(oa > 0, (rgb[c] * a2 + img[..., c] * A * (1 - a2)) / np.maximum(oa, 1e-6), 0)
    img[..., 3] = oa

def soft(e): return np.clip(e, 0, 1)

TB, SN, cy = 72.0, 168.0, 35.0                                   # tail base, snout, midline
u = np.clip((xx - TB) / (SN - TB), 0, 1)
half = 3.0 + 10.5 * np.clip(np.sin(np.pi * np.clip(.62 * u + .38 * u * u, 0, 1)), 0, 1) ** .6 * (.45 + .55 * u)   # deep round head
curve = 1.2 * np.sin(np.pi * u)
body = soft((half - np.abs(yy - cy + curve)) * 1.4) * ((xx >= TB - 2) & (xx <= SN + 4))
# small clear rounded tail fin
tx = (TB - xx) / 24; tr = np.sqrt(np.clip(tx, 0, 9)) * 11 + 3.2
tail = soft((tr - np.abs(yy - cy)) * 1.2) * soft((1 - tx) * 6) * (xx < TB + 1)
over((.8, .86, .88), tail * .28)
for k in range(5):
    ang = (k - 2) * .17
    ray = soft(1.2 - np.abs((yy - cy) - np.tan(ang) * (TB - xx)) * 1.6) * (xx < TB) * (xx > TB - 24) * tail
    over((.85, .9, .92), ray * .18)
# fin fold along the back and belly of the rear body
fold = soft((half + 3.0 - np.abs(yy - cy + curve)) * 1.2) * (1 - body) * (xx > TB + 2) * (xx < TB + 50)
over((.82, .88, .9), fold * .14)
# glassy body with a bright rim
rim = soft((1.8 - np.abs(np.abs(yy - cy + curve) - half + 1.4)) * 1.1) * body
over((.78, .84, .86), body * .34)
over((.95, .98, 1.0), rim * .3)
# spine and gut showing through
spine = soft(1.1 - np.abs(yy - (cy - curve + .6)) * 1.3) * (xx > TB + 2) * (xx < SN - 20) * body
over((.35, .33, .3), spine * .38)
gut = soft(1.0 - np.abs(yy - (cy - curve + 3.6)) * 1.2) * (xx > SN - 58) * (xx < SN - 28) * body
over((.6, .45, .3), gut * .3)
# golden belly and warm head
yolk = soft((9 - np.sqrt(((xx - (SN - 22)) / 1.6) ** 2 + ((yy - cy - 5) / 1.1) ** 2)) * .35) * body
over((.95, .7, .32), yolk * .45)
headt = soft((13 - np.sqrt(((xx - (SN - 12)) / 1.2) ** 2 + (yy - cy + .8) ** 2)) * .4) * body
over((.93, .78, .5), headt * .28)
# the big eye
ex, ey = SN - 12, cy - 2.6
d = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2)
over((.85, .62, .25), soft((7.4 - d) * 1.6) * .95)
over((.04, .04, .05), soft((6.0 - d) * 1.6))
over((1, 1, 1), soft((1.4 - np.sqrt((xx - ex + 2) ** 2 + (yy - ey + 2.1) ** 2)) * 1.6) * .85)
mouth = soft(.9 - np.abs(yy - (cy + 2.4)) * 1.5) * (xx > SN - 4) * (xx < SN + 3)
over((.5, .42, .35), mouth * .35)
out = img.reshape(UH, K, UW, K, 4).mean(axis=(1, 3))
ys, xs = np.nonzero(out[..., 3] > .03)
out = out[max(0, ys.min() - 1):ys.max() + 2, max(0, xs.min() - 1):xs.max() + 2]
r = bpy.data.images.new('nb', out.shape[1], out.shape[0], alpha=True)
r.pixels.foreach_set(np.ascontiguousarray(out[::-1], np.float32).reshape(-1)); r.filepath_raw = OUT; r.file_format = 'PNG'; r.save()
print('SAVED', OUT, out.shape[1], out.shape[0])
