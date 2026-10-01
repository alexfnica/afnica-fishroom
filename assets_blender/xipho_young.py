# Swordtail juvenile and newborn fry derived from the adult female photo (same fish, same light), so they read as real.
# Juvenile: slimmer, slightly bigger eye, no gravid spot, a touch lighter.
# Fry: short body with a big head and eye (the tail half compressed), small translucent fins, pale orange, a bit see-through.
# Run: D:\Blender\blender.exe -b -P xipho_young.py -- <adult_f.png> <out_juvenile.png> <out_fry.png>
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(a[0]); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px)
S = px.reshape(H, W, 4)[::-1].copy()                                 # top-down
EYE = (345.0, 75.0); SPOT = (215.0, 115.0)

def sample(src, X, Y):                                               # bilinear, transparent outside
    h, w = src.shape[:2]
    x0 = np.floor(X).astype(int); y0 = np.floor(Y).astype(int); fx = X - x0; fy = Y - y0
    out = np.zeros(X.shape + (4,), np.float32)
    for dy in (0, 1):
        for dx in (0, 1):
            xi = x0 + dx; yi = y0 + dy; ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
            wgt = (fx if dx else 1 - fx) * (fy if dy else 1 - fy)
            v = np.zeros(X.shape + (4,), np.float32); v[ok] = src[yi[ok], xi[ok]]
            out += v * wgt[..., None]
    return out

def premul(s): s = s.copy(); s[..., :3] *= s[..., 3:4]; return s
def unpremul(s): s = s.copy(); s[..., :3] /= np.maximum(s[..., 3:4], 1e-4); return np.clip(s, 0, 1)

def no_spot(s):                                                      # paint the gravid spot over with the surrounding colour
    yy, xx = np.mgrid[0:H, 0:W]; d = np.hypot(xx - SPOT[0], yy - SPOT[1])
    ring = (d > 11) & (d < 16) & (s[..., 3] > .9); c = s[ring, :3].mean(0)
    k = np.clip((13 - d) / 4, 0, 1)[..., None]
    s[..., :3] = s[..., :3] * (1 - k) + c * k
    return s

def warp(s, eye_gain, eye_r, slim, tail_k, ox):
    """inverse map: output pixel -> source pixel. slim<1 thins the body vertically about the midline,
    tail_k<1 compresses everything behind ox horizontally (shorter body, bigger head share), eye_gain>1 magnifies the eye."""
    P = premul(s); h, w = P.shape[:2]
    newW = int(round(ox + (w - ox) * 1.0)) if tail_k >= 1 else int(round(ox * tail_k + (w - ox)))
    yy, xx = np.mgrid[0:h, 0:newW].astype(np.float32)
    cut = ox * tail_k
    X = np.where(xx < cut, xx / tail_k, xx - cut + ox)               # undo the tail compression
    cy = h * .5; Y = cy + (yy - cy) / slim
    ex = EYE[0] - ox + cut if EYE[0] > ox else EYE[0] * tail_k; ey = EYE[1]
    ey2 = cy + (ey - cy) * slim                                      # where the eye lands after slimming
    dx = xx - ex; dy = yy - ey2; r = np.hypot(dx, dy)
    g = np.where(r < eye_r, 1 / eye_gain + (1 - 1 / eye_gain) * (r / eye_r) ** 2, 1.0)   # smooth fisheye
    X = np.where(r < eye_r, EYE[0] + dx * g, X); Y = np.where(r < eye_r, EYE[1] + dy * g / slim, Y)
    return unpremul(sample(P, X, Y))

def crop(s):
    ys, xs = np.nonzero(s[..., 3] > .05)
    return s[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]

def save(s, path):
    s = crop(s); r = bpy.data.images.new('o', s.shape[1], s.shape[0], alpha=True)
    r.pixels.foreach_set(np.ascontiguousarray(s[::-1], np.float32).reshape(-1)); r.filepath_raw = path; r.file_format = 'PNG'; r.save()
    print('SAVED', path, s.shape[1], s.shape[0])

base = no_spot(S.copy())

# juvenile
J = warp(base, 1.28, 20, .9, 1.0, 0)
J[..., :3] = np.clip(J[..., :3] * 1.04 + .015, 0, 1)
save(J, a[1])

# newborn fry
Fr = warp(base, 1.5, 24, .78, 1.0, 0)                               # same long body as the adult, slimmer, bigger eye
lum = Fr[..., :3] @ np.array([.299, .587, .114], np.float32)
pale = np.stack([1.0 * np.ones_like(lum), .58 + .25 * lum, .40 + .25 * lum], -1)
Fr[..., :3] = Fr[..., :3] * .68 + pale * .32                           # pale orange, the red still shows through
fin = Fr[..., 3] < .97                                               # soft edges = fin rays: make them see-through
Fr[..., 3] = np.where(fin, Fr[..., 3] * .8, Fr[..., 3])
save(Fr, a[2])
