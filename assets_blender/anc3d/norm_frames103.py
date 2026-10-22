# V17.103b (owner: "a dubious highlight shows when it turns - the fish must keep its shape, colour, contrast"): measured,
# the mid-turn 3D views came out milky - darks lifted (male p10 38 -> 50), spots duller (p98 187 -> 168), contrast sd
# 42 -> 33 - while norm_frames102 only kept the MEAN equal. Now every turn frame's fish luma distribution is mapped onto
# its frame 00 (= the photo, after lut_match_photo100): a monotone quantile map, applied as a per-pixel RGB gain so the
# hue stays. Run: python norm_frames103.py <dir>   (in place; after lut_match_photo100, instead of norm_frames102)
import sys, glob, os, numpy as np, pngio
D = sys.argv[1]; Q = np.linspace(0, 100, 51)
W = np.array([.299, .587, .114])
for t in ('M', 'F', 'JO', 'JB'):
    fs = sorted(glob.glob(os.path.join(D, '%s_turn*.png' % t)))
    if not fs: continue
    a0 = pngio.read(fs[0]); ref = np.percentile((a0[..., :3][a0[..., 3] > 200].astype(float) * W).sum(-1), Q)
    sds = []
    for f in fs:
        a = pngio.read(f); b = a.astype(np.float32); L = (b[..., :3] * W).sum(-1)
        src = np.percentile(L[a[..., 3] > 200], Q); src = np.maximum.accumulate(src + np.arange(len(Q)) * 1e-4)
        L2 = np.interp(L, src, ref); g = L2 / np.maximum(L, 1.)
        b[..., :3] = np.clip(b[..., :3] * g[..., None], 0, 255)
        pngio.write(f, b.round().astype(np.uint8))
        sds.append((L2[a[..., 3] > 200]).std())
    print(t, 'fish luma sd per frame min %.1f max %.1f (frame 00 %.1f)' % (min(sds), max(sds), sds[0]))
