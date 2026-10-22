# V17.104b (owner: "there's still a highlight when it turns"): measured ON SCREEN (D:\ClaudeWork\scratch104\probe_hl.py,
# per-frame PNG minus an empty background), the turn frames' brightest specks ran far above the photo's (fish luma p99
# 192-200 vs 148-162; mean and p90 equal) for all four adult colours - the photo the game shows is softer than the sheet
# cell the frames were matched to. Fix: a luma quantile map from the on-screen 3D pixels to the on-screen photo pixels
# (pooled over one turn: <probe_dir>: the last 4 shots are the photo, the rest the 3D), applied to every turn frame of
# the given types as a per-pixel RGB gain (hue kept).
# Run: python screen_match104.py <frames_dir> <probe_dir> <types, e.g. M,JO>
import sys, os, glob, numpy as np, pngio
D, P, TY = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
W = np.array([.299, .587, .114]); Q = np.linspace(0, 100, 101)
C = pngio.read(os.path.join(P, 'C.png')).astype(float)
fs = sorted(f for f in glob.glob(os.path.join(P, '[0-9]*.png')))
def pix(fl):
    out = []
    for f in fl:
        a = pngio.read(f).astype(float); m = np.abs(a[..., :3] - C[..., :3]).sum(-1) > 60; out.append((a[..., :3][m] * W).sum(-1))
    return np.concatenate(out)
s3, sp = np.percentile(pix(fs[:-4]), Q), np.percentile(pix(fs[-4:]), Q)
s3 = np.maximum.accumulate(s3 + np.arange(len(Q)) * 1e-4)
print('3D  p50 %.0f p90 %.0f p99 %.0f -> photo p50 %.0f p90 %.0f p99 %.0f' % (s3[50], s3[90], s3[99], sp[50], sp[90], sp[99]))
for t in TY:
    for f in sorted(glob.glob(os.path.join(D, '%s_turn*.png' % t))):
        a = pngio.read(f); b = a.astype(np.float32); L = (b[..., :3] * W).sum(-1)
        g = np.interp(L, s3, sp) / np.maximum(L, 1.); b[..., :3] = np.clip(b[..., :3] * g[..., None], 0, 255)
        pngio.write(f, b.round().astype(np.uint8))
    print(t, 'done')
