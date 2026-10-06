# Cut a DARK fish (black molly) out of a white background. The subject is near black, so a pixel's alpha is how dark it
# is between the paper and the fish's own dark tone (a luminance key); partly covered pixels (smoky fins, the edge of the
# body) get a dark smoky colour instead of being un-mixed into pale fringes. Crops and scales to the given width.
# Run: D:\Blender\blender.exe -b -P cut_dark.py -- <in> <out.png> [width] [fish_lum]
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = a[0], a[1]; WIDTH = int(a[2]) if len(a) > 2 else 300; FL = float(a[3]) if len(a) > 3 else .07
img = bpy.data.images.load(SRC); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); S = px.reshape(H, W, 4)[::-1].copy()
rgb = S[..., :3]; lum = rgb @ np.array([.299, .587, .114], np.float32)
border = np.concatenate([lum[:8].ravel(), lum[-8:].ravel(), lum[:, :8].ravel(), lum[:, -8:].ravel()]); bg = float(np.median(border))
alpha = np.clip((bg - .02 - lum) / max(.05, bg - .02 - FL), 0, 1)
alpha = np.where(alpha > .03, alpha, 0)
smoke = np.array([.075, .078, .085], np.float32)                          # the tone of a black molly's fins
unmix = np.clip((rgb - bg * (1 - alpha[..., None])) / np.maximum(alpha[..., None], 1e-3), 0, 1)
k = np.clip((alpha - .55) / .4, 0, 1)[..., None]                           # solid body keeps its real pixels, the rest turns smoky
col = np.minimum(unmix, .6) * k + (smoke * .7 + np.minimum(unmix, .35) * .3) * (1 - k)
col = np.where(alpha[..., None] > .95, rgb, col)
out = np.concatenate([col, alpha[..., None]], -1).astype(np.float32)
ys, xs = np.nonzero(alpha > .08)
out = out[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
h, w = out.shape[:2]; nh = max(1, round(h * WIDTH / w))
r = bpy.data.images.new('c', w, h, alpha=True); r.pixels.foreach_set(np.ascontiguousarray(out[::-1]).reshape(-1)); r.scale(WIDTH, nh)
r.filepath_raw = OUT; r.file_format = 'PNG'; r.save(); print('CUT', OUT, WIDTH, nh, 'bg', round(bg, 3))
