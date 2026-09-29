# Cut a dark fish out of a light (white / grey gradient) background.
# Run: D:\Blender\blender.exe -b -P cutout.py -- <in.jpg> <out.png> [lighten] [blank x0 y0 x1 y1]...
# Background = light pixels connected to the image border (flood fill), so the fish's own highlights and the gold eye stay.
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = a[0], a[1]
LIGHTEN = float(a[2]) if len(a) > 2 else 0.0
img = bpy.data.images.load(SRC); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px)
S = px.reshape(H, W, 4)[::-1].copy()                      # top-down
rgb = S[..., :3]
# blank rectangles (UI overlays such as an "Edit" button) -> paint them as background
rest = a[3:]
for i in range(0, len(rest) - 3, 4):
    x0, y0, x1, y1 = map(int, rest[i:i + 4]); rgb[y0:y1, x0:x1] = 1.0
lum = rgb @ np.array([.299, .587, .114], np.float32)
light = lum > .42
bg = np.zeros_like(light)
bg[0, :] = light[0, :]; bg[-1, :] = light[-1, :]; bg[:, 0] = light[:, 0]; bg[:, -1] = light[:, -1]
for _ in range(4000):                                     # flood fill through light pixels
    n = bg.copy()
    n[1:, :] |= bg[:-1, :]; n[:-1, :] |= bg[1:, :]; n[:, 1:] |= bg[:, :-1]; n[:, :-1] |= bg[:, 1:]
    n &= light
    if (n == bg).all(): break
    bg = n
# soft alpha: inside the fish = 1; in the background region alpha follows darkness (fine fin rays stay see-through)
alpha = np.where(bg, np.clip((.78 - lum) / .36, 0, 1), 1.0).astype(np.float32)
# the grey gradient under the image is not white: estimate the local background brightness per row and use it
rowbg = np.array([np.percentile(lum[y][bg[y]], 60) if bg[y].any() else 1.0 for y in range(H)], np.float32)[:, None]
alpha = np.where(bg, np.clip((rowbg - .06 - lum) / (rowbg * .55), 0, 1), alpha)
# un-mix the background from semi-transparent edge pixels (colour decontamination)
bgc = np.repeat(rowbg[..., None], 3, -1) * np.ones_like(rgb)
a3 = np.maximum(alpha, 1e-3)[..., None]
col = np.clip((rgb - bgc * (1 - alpha[..., None])) / a3, 0, 1)
col = np.where(alpha[..., None] > .98, rgb, col)
if LIGHTEN:                                              # fry: born charcoal-grey, not jet black
    col = np.clip(col * (1 - LIGHTEN) + LIGHTEN * .38 + col * LIGHTEN * .8, 0, 1)
out = np.concatenate([col, alpha[..., None]], -1)
ys, xs = np.nonzero(alpha > .06)
y0, y1, x0, x1 = max(0, ys.min() - 3), min(H, ys.max() + 4), max(0, xs.min() - 3), min(W, xs.max() + 4)
out = out[y0:y1, x0:x1]
res = bpy.data.images.new('c', out.shape[1], out.shape[0], alpha=True)
res.pixels.foreach_set(np.ascontiguousarray(out[::-1], np.float32).reshape(-1))
res.filepath_raw = OUT; res.file_format = 'PNG'; res.save()
print('CUT', OUT, out.shape[1], out.shape[0])
