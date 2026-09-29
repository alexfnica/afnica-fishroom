# Turn the in-game black molly photos into LYRETAIL black mollies, keeping the photographic texture.
# Run: D:\Blender\blender.exe -b -P lyretail_warp.py -- <src.png> <out.png> <ktop> <kbot> <notch> [grade]
#  ktop/kbot : how much the upper/lower caudal lobe grows (1.0 = +100% length at the very edge)
#  notch     : centre rays shortened by this fraction (the concave "lyre" between the lobes)
#  grade     : 1 = regrade the body to a velvet jet black (default 1)
# The fish faces right. Caudal fin = everything left of the caudal peduncle (narrowest point of the body).
import bpy, sys, numpy as np

a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = a[0], a[1]
KT, KB, NOTCH = float(a[2]), float(a[3]), float(a[4])
GRADE = int(a[5]) if len(a) > 5 else 1

img = bpy.data.images.load(SRC)
W, H = img.size
px = np.empty(W * H * 4, dtype=np.float32); img.pixels.foreach_get(px)
S = px.reshape(H, W, 4)[::-1].copy()                     # top-down rows
A = S[:, :, 3]

# ---- find the body centre line and the caudal peduncle ----------------------------------------------------
def run_around(col, y0):
    """contiguous opaque run in column col that contains row y0 (or the nearest opaque row)"""
    c = A[:, col] > .35
    if not c.any(): return None
    if not c[y0]:
        ys = np.nonzero(c)[0]; y0 = ys[np.argmin(abs(ys - y0))]
    t = y0
    while t > 0 and c[t - 1]: t -= 1
    b = y0
    while b < H - 1 and c[b + 1]: b += 1
    return t, b

# centre row: middle of the body near the head
col = int(W * .80); ys = np.nonzero(A[:, col] > .5)[0]      # head region: no dorsal fin above it
cy = int((ys.min() + ys.max()) / 2)
hs = {}
for x in range(int(W * .18), int(W * .55)):
    r = run_around(x, cy)
    if r: hs[x] = r[1] - r[0]
xb = min(hs, key=lambda k: hs[k])                         # peduncle = narrowest body column
tb = run_around(xb, cy); cy = (tb[0] + tb[1]) / 2
# caudal extent: leftmost opaque column of the fin (run touching the centre line)
x0 = xb
for x in range(xb, -1, -1):
    r = run_around(x, int(cy))
    if r is None: break
    x0 = x
L = xb - x0
half = max(4, max((lambda r: max(cy - r[0], r[1] - cy))(run_around(x, int(cy))) for x in range(x0, x0 + max(1, L // 3))))
if len(a) > 8:                                            # manual override: peduncle x, centre row, fin half-height
    xb, cy, half = int(a[6]), float(a[7]), float(a[8])
    x0 = xb
    for x in range(xb, -1, -1):
        if not (A[:, x] > .35).any(): break
        x0 = x
    L = xb - x0
print('W,H', W, H, 'peduncle x', xb, 'cy', cy, 'tail len', L, 'half', half)

# ---- inverse warp -------------------------------------------------------------------------------------------
PAD = int(L * max(KT, KB) * .95) + 4                     # new canvas room on the left for the longer lobes
OW = W + PAD
out = np.zeros((H, OW, 4), dtype=np.float32)
out[:, PAD:, :] = S                                       # body and everything right of the peduncle unchanged

def sample(xs, ys):
    xs = np.clip(xs, 0, W - 1.001); ys = np.clip(ys, 0, H - 1.001)
    x0i = np.floor(xs).astype(int); y0i = np.floor(ys).astype(int)
    fx = (xs - x0i)[..., None]; fy = (ys - y0i)[..., None]
    c00 = S[y0i, x0i]; c10 = S[y0i, x0i + 1]; c01 = S[y0i + 1, x0i]; c11 = S[y0i + 1, x0i + 1]
    # premultiplied bilinear so transparent edges do not darken/lighten
    def pm(c): return np.concatenate([c[..., :3] * c[..., 3:4], c[..., 3:4]], -1)
    r = (pm(c00) * (1 - fx) * (1 - fy) + pm(c10) * fx * (1 - fy) + pm(c01) * (1 - fx) * fy + pm(c11) * fx * fy)
    a_ = r[..., 3:4]; rgb = np.where(a_ > 1e-5, r[..., :3] / np.maximum(a_, 1e-5), 0)
    return np.concatenate([rgb, a_], -1)

yy, xx = np.mgrid[0:H, 0:(xb + PAD)].astype(np.float32)
d_o = (xb + PAD) - xx                                     # distance behind the peduncle, output space
blend_in = np.clip(d_o / max(3, L * .18), 0, 1)           # no warp right at the peduncle, full warp further back
v = (yy - cy) / half                                      # -1 (top edge of fin) .. +1 (bottom edge)
up = np.clip(-v, 0, None); dn = np.clip(v, 0, None)
# lobe growth concentrated on the outermost rays -> long pointed tips; centre shortened -> the lyre notch
# (real lyretails: only the outermost rays run on into thin streamers, the rest of the fan keeps its length)
grow = KT * np.power(np.clip((up - .5) / .55, 0, 1), 3.2) + KB * np.power(np.clip((dn - .5) / .55, 0, 1), 3.2)
m = 1 + (grow - NOTCH * np.exp(-(v / .38) ** 2)) * blend_in
d_s = d_o / np.maximum(m, .2)
# the lobes also flare outward a little as they grow, then run nearly parallel
flare = 1 + .20 * np.clip(d_o / max(1, L), 0, 1.6) * np.clip(np.abs(v), 0, 1) * blend_in
# lyre curve: beyond the fan's own length the streamers bow outward, then turn back in at the tips
over = np.clip((d_o - L) / max(1, L * max(KT, KB, .01)), 0, 1)
bow = half * .22 * np.sin(np.pi * over) * np.sign(v) * (np.abs(v) > .5)
xs = xb - d_s; ys = cy + (yy - cy - bow) / flare
tail = sample(xs, ys)
tail[..., 3] *= (xs >= -.5)                               # beyond the source image: nothing
region = out[:, :xb + PAD]
out[:, :xb + PAD] = np.where((xx >= PAD + xb - 0)[..., None], region, tail)

# ---- colour grade: velvet jet black with a faint blue sheen, keep the gold eye ------------------------------
if GRADE:
    rgb = out[..., :3]; lum = rgb @ np.array([.299, .587, .114], dtype=np.float32)
    sat = rgb.max(-1) - rgb.min(-1)
    eye = (sat > .18) & (rgb[..., 0] > rgb[..., 2])      # warm, saturated = the iris
    g = np.power(np.clip(lum, 0, 1), 1.35) * .78          # deeper blacks, softer scale highlights
    tint = np.stack([g * .86, g * .92, g * 1.12], -1)     # cool blue-black sheen instead of violet
    out[..., :3] = np.where(eye[..., None], rgb, tint)

# ---- save -----------------------------------------------------------------------------------------------------
res = bpy.data.images.new('lyre', OW, H, alpha=True)
res.pixels.foreach_set(out[::-1].reshape(-1))
res.filepath_raw = OUT; res.file_format = 'PNG'; res.save()
print('SAVED', OUT, OW, H)
