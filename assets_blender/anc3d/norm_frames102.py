# V17.102b (owner: "it must not change colour during the turn"): every turn frame of a fish type gets the same mean fish
# brightness as its frame 00 (= the photo, after lut_match_photo100): mid-turn views show more of the lighter head/top
# texture, which read as a highlight. Run: python norm_frames102.py <dir>   (in place)
import sys, glob, os, numpy as np, pngio
D = sys.argv[1]
for t in ('M', 'F', 'JO', 'JB'):
    fs = sorted(glob.glob(os.path.join(D, '%s_turn*.png' % t)))
    lum = lambda a: ((a[..., :3][a[..., 3] > 200].astype(float)) * [.299, .587, .114]).sum(-1).mean()
    ref = lum(pngio.read(fs[0])); out = []
    for f in fs:
        a = pngio.read(f); k = ref / lum(a); b = a.astype(np.float32); b[..., :3] = np.clip(b[..., :3] * k, 0, 255)
        pngio.write(f, b.round().astype(np.uint8)); out.append(round(k, 3))
    print(t, 'gain per frame min %.3f max %.3f' % (min(out), max(out)))
