# Cut a translucent subject (glassy fry, clear fins) out of a pure white background by difference matting:
# alpha comes from how far each pixel is from white, then the white is un-mixed from the colour. Clear parts stay
# see-through instead of being thrown away. Crops to the subject and scales to the given width.
# Run: D:\Blender\blender.exe -b -P cut_translucent.py -- <in> <out.png> [width] [gain]
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = a[0], a[1]; WIDTH = int(a[2]) if len(a) > 2 else 300; GAIN = float(a[3]) if len(a) > 3 else 3.2
img = bpy.data.images.load(SRC); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); S = px.reshape(H, W, 4)[::-1].copy()
rgb = S[..., :3]
# the paper is not perfectly white: estimate it from the border
border = np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)])
bg = np.median(border, 0)
diff = np.max(np.abs(rgb - bg), -1)
alpha = np.clip((diff - .025) * GAIN, 0, 1)
alpha = np.where(alpha > .02, alpha, 0)
col = np.clip((rgb - bg * (1 - alpha[..., None])) / np.maximum(alpha[..., None], 1e-3), 0, 1)
col = np.where(alpha[..., None] > .97, rgb, col)
out = np.concatenate([col, alpha[..., None]], -1).astype(np.float32)
ys, xs = np.nonzero(alpha > .08)
out = out[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
h, w = out.shape[:2]; nh = max(1, round(h * WIDTH / w))
r = bpy.data.images.new('c', w, h, alpha=True); r.pixels.foreach_set(np.ascontiguousarray(out[::-1]).reshape(-1)); r.scale(WIDTH, nh)
r.filepath_raw = OUT; r.file_format = 'PNG'; r.save(); print('CUT', OUT, WIDTH, nh, 'bg', bg)
