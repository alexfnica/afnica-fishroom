# Enlarge the caudal fin of a cut-out fish sprite (facing right): everything behind the caudal peduncle is scaled up by
# K about the peduncle's middle, on a canvas widened to the left; the body is untouched. A narrow blend at the peduncle
# hides the seam. Run: D:\Blender\blender.exe -b -P grow_tail.py -- <in.png> <out.png> <K>
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(a[0]); W, H = img.size; K = float(a[2])
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); S = px.reshape(H, W, 4)[::-1].copy()   # top row first
A = S[..., 3] > .24
cols = np.where(A.any(0))[0]; x0, x1 = cols.min(), cols.max(); L = x1 - x0
top = np.array([np.argmax(A[:, x]) if A[:, x].any() else -1 for x in range(W)])
bot = np.array([H - 1 - np.argmax(A[::-1, x]) if A[:, x].any() else -1 for x in range(W)])
rng = [x for x in range(int(x1 - .85 * L), int(x1 - .5 * L)) if top[x] >= 0]
xp = min(rng, key=lambda x: bot[x] - top[x]); yp = (top[xp] + bot[xp]) / 2
pad = int((xp - x0) * (K - 1)) + 4; vpad = int(H * (K - 1) * .5) + 2
NW, NH = W + pad, H + 2 * vpad
O = np.zeros((NH, NW, 4), np.float32)
O[vpad:vpad + H, pad:pad + W] = S                                   # the original, shifted right/down
cx, cy = xp + pad, yp + vpad                                        # peduncle middle in the new canvas
ys, xs = np.mgrid[0:NH, 0:NW]
sx = (xs - cx) / K + xp; sy = (ys - cy) / K + yp                    # sample position in the original
ix = np.clip(np.round(sx).astype(int), 0, W - 1); iy = np.clip(np.round(sy).astype(int), 0, H - 1)
T = S[iy, ix]; valid = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H) & (sx <= xp)
w = np.clip((cx - xs) / 6.0, 0, 1)[..., None] * valid[..., None]    # 0 at the peduncle -> 1 six px behind it
behind = xs <= cx
O = np.where(behind[..., None], O * (1 - w) + T * w, O)

out = bpy.data.images.new('t', NW, NH, alpha=True); out.pixels.foreach_set(np.ascontiguousarray(O[::-1].astype(np.float32)).reshape(-1))
out.filepath_raw = a[1]; out.file_format = 'PNG'; out.save(); print('TAIL', a[1], NW, NH, 'peduncle', xp, int(yp))
