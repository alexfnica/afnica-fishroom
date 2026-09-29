# Lyretail black molly models from the in-game female photo (keeps the photographic texture).
# Run: D:\Blender\blender.exe -b -P molly_models.py -- <src_female.png> <out.png> <sex M|F> <lyre> [scale_ref]
#   lyre : lobe growth (0.5 = streamers ~50% longer than the fan at the very edge)
# Coordinates below are in the 337x155 adult female photo (fish faces right).
import bpy, sys, numpy as np

a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT, SEX, LYRE = a[0], a[1], a[2].upper(), float(a[3])
NOTCH = float(a[4]) if len(a) > 4 else .32          # how deep the crescent is cut into the middle of the tail

img = bpy.data.images.load(SRC); W0, H0 = img.size
px = np.empty(W0 * H0 * 4, dtype=np.float32); img.pixels.foreach_get(px)
S0 = px.reshape(H0, W0, 4)[::-1].copy()
k = W0 / 337.0                                            # works for scaled copies of the same photo

PT = int(26 * k); PB = int(14 * k)                        # room above (taller male dorsal, upper streamer) and below
PL = int(90 * k * max(.3, LYRE))                          # room on the left for the streamers
H, W = H0 + PT + PB, W0 + PL
S = np.zeros((H, W, 4), np.float32); S[PT:PT + H0, PL:PL + W0] = S0
def X(x): return x * k + PL                               # female-photo coords -> padded canvas
def Y(y): return y * k + PT

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def sample(src, xs, ys):
    h, w = src.shape[:2]
    xs = np.clip(xs, 0, w - 1.001); ys = np.clip(ys, 0, h - 1.001)
    x0 = np.floor(xs).astype(int); y0 = np.floor(ys).astype(int); fx = (xs - x0)[..., None]; fy = (ys - y0)[..., None]
    def pm(c): return np.concatenate([c[..., :3] * c[..., 3:4], c[..., 3:4]], -1)
    r = pm(src[y0, x0]) * (1 - fx) * (1 - fy) + pm(src[y0, x0 + 1]) * fx * (1 - fy) + pm(src[y0 + 1, x0]) * (1 - fx) * fy + pm(src[y0 + 1, x0 + 1]) * fx * fy
    al = r[..., 3:4]; rgb = np.where(al > 1e-5, r[..., :3] / np.maximum(al, 1e-5), 0)
    return np.concatenate([rgb, al], -1)
def sm(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def over(dst, src):                                       # src over dst (straight alpha)
    a1 = src[..., 3:4]; a0 = dst[..., 3:4]; ao = a1 + a0 * (1 - a1)
    rgb = np.where(ao > 1e-5, (src[..., :3] * a1 + dst[..., :3] * a0 * (1 - a1)) / np.maximum(ao, 1e-5), 0)
    return np.concatenate([rgb, ao], -1)

if SEX == 'M':
    base = S.copy()
    # ---- 1. dorsal: males carry a taller, more pointed dorsal (still a normal molly dorsal, no long filament) ----
    ytop = lambda x: Y(62 - (x - X(140)) / k * .2)        # back line under the dorsal (canvas coords in, canvas out)
    xa, xb2 = X(118), X(210)
    inD = (xx > xa) & (xx < xb2) & (yy < ytop(xx) + 1)
    h = np.clip((ytop(xx) - yy) / (48 * k), 0, 1.6)       # height above the back, 0..1 over the fin
    grow = 1.42                                           # video: males carry a clearly larger, sail-like dorsal
    ys = ytop(xx) - (ytop(xx) - yy) / grow
    xs = xx - (xx - xa) * .12 * h                          # rear rays swept back further -> pointed rear tip
    d = sample(base, xs, ys)
    wD = sm((xx - xa) / (6 * k)) * sm((xb2 - xx) / (6 * k))
    S = np.where((inD)[..., None], d * np.stack([np.ones_like(wD)] * 3 + [wD], -1) + base * (1 - wD)[..., None] * 0, S)
    S[..., 3] = np.where(inD, np.maximum(d[..., 3] * wD, base[..., 3] * (1 - wD)), S[..., 3])
    # ---- 2. gonopodium: the anal fin of a male is a slim pointed rod angled back along the belly ----
    ybot = lambda x: Y(100 + (x - X(140)) / k * .06)      # belly line over the anal fin
    erase = (xx > X(118)) & (xx < X(196)) & (yy > ybot(xx) + 1.2 * k)
    wx = sm((xx - X(118)) / (5 * k)) * sm((X(196) - xx) / (8 * k))           # fade the cut out at both ends: no step in the belly
    S[..., 3] = np.where(erase, S[..., 3] * (1 - wx * sm((yy - ybot(xx) - 2.2 * k) / (2.5 * k))), S[..., 3])
    B = np.array([X(186), Y(103.5)]); T = np.array([X(128), Y(121)])  # base (just behind the pelvic fins) -> tip
    ax = T - B; Lg = np.hypot(*ax); ux, uy = ax / Lg; nx, ny = -uy, ux
    s = ((xx - B[0]) * ux + (yy - B[1]) * uy) / Lg
    t = (xx - B[0]) * nx + (yy - B[1]) * ny
    wid = (3.4 * (1 - np.clip(s, 0, 1)) ** .6 + .45) * k
    tt = t / np.maximum(wid, 1e-3)
    inG = (s > -.04) & (s < 1.02) & (np.abs(tt) < 1.25)
    # texture: fin rays of the (original) anal fin, squeezed into the rod
    sx = (185 - np.clip(s, 0, 1) * 48) * k; sy = (112 + tt * 7) * k
    g = sample(S0, sx, sy)
    g[..., :3] = np.minimum(g[..., :3] * 1.0 + .008, 1)
    g[..., 3] = np.clip(1.25 - np.abs(tt), 0, 1) * sm((1.02 - s) / .06) * sm((s + .04) / .08) * .96
    g[..., 3] *= inG
    S = over(S, g)

# ---- 2b. molly build: a deep, stocky body with a high back and a thick caudal peduncle (the source photo is too
#          slim, it read as a guppy). Stretch vertically about the body's centre line, most at mid-body. -----------
DEEP = float(a[5]) if len(a) > 5 else .30
src = S.copy()
xf = (xx - PL) / k                                        # back to female-photo x
cyl = Y(83.5 - (np.clip(xf, 105, 330) - 105) / 225 * 11)  # centre line rises slightly toward the head
bodyU = np.clip((xf - 105) / 225, 0, 1)
f = 1 + DEEP * np.clip(np.sin(np.pi * bodyU), 0, 1) ** 1.1 + .15 * np.exp(-((xf - 112) / 22) ** 2)   # mid-body hump + thick peduncle
f = np.where(xf < 105, 1 + (f - 1) * sm((xf - 70) / 35), f)
f = 1 + (f - 1) * sm((292 - xf) / 40)                        # the head (eye at x~290) keeps its shape                         # fade out into the tail
S = sample(src, xx, cyl + (yy - cyl) / f)

# ---- 3. lyretail caudal (moderate) ---------------------------------------------------------------------------
xb, cy, half = X(105), Y(83.5), 53.5 * k                  # peduncle, centre line, fin half height
L = X(105) - X(12)
src = S.copy()
d_o = xb - xx
blend = sm(d_o / (L * .18))
v = (yy - cy) / half
up = np.clip(-v, 0, None); dn = np.clip(v, 0, None)
grow = LYRE * (np.clip((up - .3) / .72, 0, 1) ** 1.8 + np.clip((dn - .3) / .72, 0, 1) ** 1.8)
m = 1 + (grow - NOTCH * np.exp(-(v / .45) ** 2)) * blend
d_s = d_o / np.maximum(m, .2)
flare = 1 + .12 * np.clip(d_o / L, 0, 1.6) * np.clip(np.abs(v), 0, 1) * blend
ov = np.clip((d_o - L) / max(1, L * max(LYRE, .01)), 0, 1)
bow = half * .06 * np.sin(np.pi * ov) * np.sign(v) * (np.abs(v) > .5)
tail = sample(src, xb - d_s, cy + (yy - cy - bow) / flare)
S = np.where((xx < xb)[..., None], tail, S)

# ---- 4. colour: velvet jet black with a faint cool sheen, gold-ringed eye kept -------------------------------
rgb = S[..., :3]; lum = rgb @ np.array([.299, .587, .114], np.float32); sat = rgb.max(-1) - rgb.min(-1)
eye = (sat > .18) & (rgb[..., 0] > rgb[..., 2])
gg = np.clip(lum, 0, 1) ** 1.35 * .78
S[..., :3] = np.where(eye[..., None], rgb, np.stack([gg * 1.04, gg * .96, gg * .94], -1))   # warm brown-black like the reference photo

# ---- 5. crop to content (+2px) ---------------------------------------------------------------------------------
al = S[..., 3] > .02; ys_, xs_ = np.nonzero(al)
y0, y1, x0 = max(0, ys_.min() - 2), min(H, ys_.max() + 3), max(0, xs_.min() - 2)
S = S[y0:y1, x0:]
print('RESULT', SEX, 'size', S.shape[1], S.shape[0], 'left_pad_added', W - x0 - W0, 'top', PT - y0, 'bottom', (y1 - (PT + H0)))
res = bpy.data.images.new('m', S.shape[1], S.shape[0], alpha=True)
res.pixels.foreach_set(np.ascontiguousarray(S[::-1], dtype=np.float32).reshape(-1)); res.filepath_raw = OUT; res.file_format = 'PNG'; res.save()
