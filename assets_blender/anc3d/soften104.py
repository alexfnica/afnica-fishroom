# V17.104c (owner: "still a little highlight"): the on-screen turn looked paler / sparkly next to the photo although the
# colour totals matched: the 3D frames carried ~40 % more FINE detail (screen luma minus a 3x3 mean: 11.7-12.6 vs photo
# 8.3-9.3) while the mid-scale pattern matched (11.6-12.4 vs 10.9-12.5) - the fine white speckle read as a sheen. Here the
# finest detail of every turn frame is cut by ALPHA (alpha-weighted 3x3 mean inside the fish, so the outline stays clean).
# Run: python soften104.py <frames_dir> [alpha]   (in place)
import sys, os, glob, numpy as np, pngio
D = sys.argv[1]; AL = float(sys.argv[2]) if len(sys.argv) > 2 else .45
def box(x):
    p = np.pad(x, ((1, 1), (1, 1)) + ((0, 0),) * (x.ndim - 2), mode='edge'); return sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.
for f in sorted(glob.glob(os.path.join(D, '*_turn*.png'))):
    a = pngio.read(f); b = a.astype(np.float32); w = b[..., 3:4] / 255.
    bl = box(b[..., :3] * w) / np.maximum(box(w), 1e-3)
    b[..., :3] = np.where(w > .02, b[..., :3] - AL * (b[..., :3] - bl), b[..., :3])
    pngio.write(f, np.clip(b, 0, 255).round().astype(np.uint8))
print('softened', len(glob.glob(os.path.join(D, '*_turn*.png'))), 'frames, alpha', AL)
