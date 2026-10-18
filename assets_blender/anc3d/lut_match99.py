# V17.99: the fight frames were colour-matched after rendering with settings that were not recorded. Learn the mapping
# back per layer and channel as a 256-entry LUT from an old raw render and its matched copy (same render, so pixel for
# pixel), then apply it to new raw frames.
# Run: python lut_match99.py <old_raw_dir> <old_matched_dir> <new_raw_dir> <out_dir>
import sys, os, glob, numpy as np, pngio
RAW0, M0, RAW1, OUT = sys.argv[1:5]; os.makedirs(OUT, exist_ok=True)
for L in (1, 2):
    acc = np.zeros((3, 256)); cnt = np.zeros((3, 256)); err = []
    for f in sorted(glob.glob(os.path.join(RAW0, 'P%d_[ABC]*.png' % L))):
        g = os.path.join(M0, os.path.basename(f))
        if not os.path.exists(g): continue
        a, b = pngio.read(f), pngio.read(g)
        if a.shape != b.shape: continue
        m = (a[..., 3] > 230) & (b[..., 3] > 230)
        for c in range(3):
            np.add.at(acc[c], a[..., c][m], b[..., c][m].astype(float)); np.add.at(cnt[c], a[..., c][m], 1)
    lut = np.zeros((3, 256), np.uint8)
    for c in range(3):
        ok = cnt[c] > 0; xs = np.nonzero(ok)[0]; lut[c] = np.clip(np.interp(np.arange(256), xs, acc[c][ok] / cnt[c][ok]), 0, 255).round()
    f = sorted(glob.glob(os.path.join(RAW0, 'P%d_A*.png' % L)))[0]; a, b = pngio.read(f), pngio.read(os.path.join(M0, os.path.basename(f)))
    m = (a[..., 3] > 230) & (b[..., 3] > 230); pred = np.stack([lut[c][a[..., c]] for c in range(3)], -1)
    print('layer', L, 'LUT fit error on', os.path.basename(f), 'mean abs %.2f' % np.abs(pred[m].astype(int) - b[..., :3][m].astype(int)).mean())
    n = 0
    for f in sorted(glob.glob(os.path.join(RAW1, 'P%d_*.png' % L))):
        a = pngio.read(f); o = a.copy()
        for c in range(3): o[..., c] = lut[c][a[..., c]]
        pngio.write(os.path.join(OUT, os.path.basename(f)), o); n += 1
    print('layer', L, n, 'frames ->', OUT)
