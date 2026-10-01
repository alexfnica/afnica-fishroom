# Bend the rear half of a side-view fish sprite toward the camera (a real 3D curl seen in perspective).
# The head half stays straight and in place; the tail follows a constant-curvature arc that swings out of the picture
# plane toward the viewer, so it is foreshortened along the body and enlarged by perspective.
# Run: D:\Blender\blender.exe -b -P bend_toward_camera.py -- <in.png> <out_prefix> <hinge 0..1> <deg1> <deg2> ...
# Sprite must face right (tail on the left). Output: <out_prefix>_<n>.png, same size as the input.
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT, HINGE = a[0], a[1], float(a[2]); ANGLES = [float(v) for v in a[3:]]
img = bpy.data.images.load(SRC); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px)
S = px.reshape(H, W, 4)[::-1].copy()                          # top-down RGBA
S[..., :3] *= S[..., 3:4]                                    # premultiply so splatting blends cleanly
SS = 4                                                       # supersample the splat, then average down
xh = HINGE * W; cx = W / 2.0; cy = H / 2.0; D = 0.75 * W      # camera distance (perspective strength)
ys, xs = np.mgrid[0:H * SS, 0:W * SS].astype(np.float32) / SS + .5 / SS
sub = S[np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)]
for n, deg in enumerate(ANGLES, 1):
    th = np.radians(deg); Ls = xh                            # tail length (hinge to tip)
    s = np.clip(xh - xs, 0, None)                            # distance behind the hinge along the body
    k = th / Ls                                              # curvature: yaw grows linearly with s
    phi = k * s
    X = np.where(phi > 1e-6, np.sin(phi) / max(k, 1e-9), s)  # arc length integral of cos
    Z = np.where(phi > 1e-6, (1 - np.cos(phi)) / max(k, 1e-9), 0.0)   # integral of sin: toward the camera
    X = np.where(s > 0, X, 0); Z = np.where(s > 0, Z, 0)
    px3 = np.where(s > 0, xh - X, xs); pz = Z
    sc = D / (D - pz)                                        # closer to the camera = larger
    sx = cx + (px3 - cx) * sc; sy = cy + (ys - cy) * sc
    shade = np.where(s > 0, 1 - .22 * (1 - np.cos(phi)), 1.0)  # the curling tail turns away from the light a little
    out = np.zeros((H, W, 4), np.float32); wgt = np.zeros((H, W), np.float32)
    ix = np.clip(sx.round().astype(int), 0, W - 1); iy = np.clip(sy.round().astype(int), 0, H - 1)
    inside = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    # nearer points (larger Z) are drawn last: sort by depth so the tail overlaps the body
    order = np.argsort(pz[inside].ravel(), kind='stable')
    fi = np.nonzero(inside.ravel())[0][order]
    src = sub.reshape(-1, 4)[fi].copy(); src[:, :3] *= shade.ravel()[fi][:, None]
    flat = out.reshape(-1, 4); dst = (iy.ravel()[fi] * W + ix.ravel()[fi])
    # simple "over" splat in depth order (later = nearer wins where it is opaque)
    for c in range(4):
        pass
    acc = np.zeros((H * W, 4), np.float32); cnt = np.zeros(H * W, np.float32)
    np.add.at(acc, dst, src); np.add.at(cnt, dst, 1.0)
    m = cnt > 0
    flat[m] = acc[m] / cnt[m][:, None]                       # average of the supersamples that land in each pixel
    cover = np.clip(cnt / (SS * SS * 0.55), 0, 1)            # pixels hit by fewer samples are partly empty
    flat[:, 3] = np.where(m, flat[:, 3] * cover, 0)
    # fill 1px cracks: where alpha is low but neighbours are opaque, borrow the neighbour colour
    A = out[..., 3]
    for _ in range(2):
        nb = np.maximum.reduce([np.roll(A, 1, 0), np.roll(A, -1, 0), np.roll(A, 1, 1), np.roll(A, -1, 1)])
        hole = (A < .35) & (nb > .8)
        for ch in range(3):
            c3 = out[..., ch]
            n3 = (np.roll(c3, 1, 0) + np.roll(c3, -1, 0) + np.roll(c3, 1, 1) + np.roll(c3, -1, 1)) / 4
            c3[hole] = n3[hole]
        A[hole] = .85
    rgb = out[..., :3] / np.maximum(out[..., 3:4], 1e-3)     # un-premultiply
    res = np.concatenate([np.clip(rgb, 0, 1), out[..., 3:4]], -1)
    r = bpy.data.images.new('b%d' % n, W, H, alpha=True)
    r.pixels.foreach_set(np.ascontiguousarray(res[::-1], np.float32).reshape(-1))
    r.filepath_raw = '%s_%d.png' % (OUT, n); r.file_format = 'PNG'; r.save(); print('BEND', n, deg)
