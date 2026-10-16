# Match the 3D renders to the owner's photos: per fish, per-channel gain + gamma so the side-on 3D frame (turn00) has the
# same mean colour and brightness spread as the photo frame (yaw00). Applied in place to the given 3D frames.
# Run: python colour_match.py <photo_frame.png> <ref_3d_frame.png> <frame.png> [...]
import sys, numpy as np, pngio
ph, rf = pngio.read(sys.argv[1]).astype(float), pngio.read(sys.argv[2]).astype(float)
def stats(a):
    m = a[..., 3] > 230; px = a[..., :3][m] / 255.; return px.mean(0), px.std(0)
mp, sp = stats(ph); mr, sr = stats(rf)
# y = ((x - mr) * k + mp), k = sp/sr per channel, clipped to a sane range
k = np.clip(sp / np.maximum(sr, 1e-3), .7, 1.6)
print('photo mean', mp.round(3), 'render mean', mr.round(3), 'gain', k.round(2))
for f in sys.argv[3:]:
    a = pngio.read(f).astype(float); rgb = a[..., :3] / 255.; al = a[..., 3:4] / 255.
    body = np.clip((a[..., 3:4] - 60) / 120, 0, 1)                    # leave the soft baked shadow alone
    out = np.clip((rgb - mr) * k + mp, 0, 1)
    a[..., :3] = (rgb * (1 - body) + out * body) * 255
    pngio.write(f, np.clip(a, 0, 255))
print('matched', len(sys.argv) - 3)
