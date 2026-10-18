# V17.99: colour-match new raw turn frames like the old ones (per fish type and channel, a 256-entry LUT learnt from the
# old raw turn frames and their matched copies). Run: python lut_match_turn99.py <old_raw> <old_matched> <new_raw> <out>
import sys, os, glob, numpy as np, pngio
RAW0, M0, RAW1, OUT = sys.argv[1:5]; os.makedirs(OUT, exist_ok=True)
for S in ('M', 'F', 'JO', 'JB'):
    acc = np.zeros((3, 256)); cnt = np.zeros((3, 256))
    for f in sorted(glob.glob(os.path.join(RAW0, S + '_turn*.png'))):
        g = os.path.join(M0, os.path.basename(f)); a, b = pngio.read(f), pngio.read(g)
        m = (a[..., 3] > 230) & (b[..., 3] > 230)
        for c in range(3): np.add.at(acc[c], a[..., c][m], b[..., c][m].astype(float)); np.add.at(cnt[c], a[..., c][m], 1)
    lut = np.zeros((3, 256), np.uint8)
    for c in range(3):
        ok = cnt[c] > 0; xs = np.nonzero(ok)[0]; lut[c] = np.clip(np.interp(np.arange(256), xs, acc[c][ok] / cnt[c][ok]), 0, 255).round()
    f = os.path.join(RAW0, S + '_turn12.png'); a, b = pngio.read(f), pngio.read(os.path.join(M0, S + '_turn12.png')); m = (a[..., 3] > 230) & (b[..., 3] > 230)
    pred = np.stack([lut[c][a[..., c]] for c in range(3)], -1); print(S, 'fit error turn12 mean abs %.2f' % np.abs(pred[m].astype(int) - b[..., :3][m].astype(int)).mean())
    n = 0
    for f in sorted(glob.glob(os.path.join(RAW1, S + '_turn*.png'))):
        a = pngio.read(f); o = a.copy()
        for c in range(3): o[..., c] = lut[c][a[..., c]]
        pngio.write(os.path.join(OUT, os.path.basename(f)), o); n += 1
    print(S, n, 'frames')
