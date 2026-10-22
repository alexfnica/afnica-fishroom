# V17.104d (owner: "still some corruption / highlight / outline when it turns"): on screen the 3D turn frames had a
# ragged pale edge (semi-transparent edge pixels lighter than the fish) and the 2-5 px band inside the outline ran ~6 %
# lighter than the fish (black male 71 vs photo 67, female 65 vs 61, whole-fish means equal) - a pale contour.
# 1) defringe: every pixel with alpha < 250 takes the colour of the opaque fish next to it (alpha kept);
# 2) the band within BAND px of the outline is scaled (ramped to 0 at BAND) so its mean = R x the mean of the fish
#    deeper inside (the photo on screen: ~.96).
# Run: python edge104.py <frames_dir> [R] [BAND]   (in place)
import sys, os, glob, numpy as np, pngio
D = sys.argv[1]; R = float(sys.argv[2]) if len(sys.argv) > 2 else .96; BAND = int(sys.argv[3]) if len(sys.argv) > 3 else 6
W = np.array([.299, .587, .114])
def box(x):
    p = np.pad(x, ((1, 1), (1, 1)) + ((0, 0),) * (x.ndim - 2), mode='edge'); return sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
out = []
for f in sorted(glob.glob(os.path.join(D, '*_turn*.png'))):
    a = pngio.read(f); b = a.astype(np.float32); al = b[..., 3]; op = al >= 250
    col = b[..., :3] * op[..., None]; wt = op.astype(np.float32); known = op.copy()
    for _ in range(6):                                       # grow the opaque colours outward over the soft edge
        s, n = box(col), box(wt); new = (n > 0) & ~known
        col[new] = s[new] / n[new][:, None]; wt[new] = 1; known |= new
    edge = (al > 0) & (al < 250) & known; b[..., :3][edge] = col[edge]
    dist = np.zeros(al.shape, np.int32); m = al > 128      # distance (px) from the outline, up to BAND + 4
    cur = m.copy()
    for k in range(1, BAND + 5):
        cur = cur & np.roll(cur, 1, 0) & np.roll(cur, -1, 0) & np.roll(cur, 1, 1) & np.roll(cur, -1, 1); dist[cur] = k
    L = (b[..., :3] * W).sum(-1); band = m & (dist < BAND); inner = m & (dist >= BAND) & (dist < BAND + 4)
    if band.sum() > 50 and inner.sum() > 50:
        k = float(np.clip(1 - R * L[inner].mean() / max(L[band].mean(), 1), 0, .25))
        ramp = np.clip(1 - dist / BAND, 0, 1) * band; g = 1 - k * ramp / max(ramp[band].mean(), 1e-3) * (ramp > 0)
        b[..., :3] *= np.clip(g, .6, 1)[..., None]; out.append(k)
    pngio.write(f, np.clip(b, 0, 255).round().astype(np.uint8))
print('edge104: %d frames, band darkening %.3f..%.3f' % (len(out), min(out), max(out)))
