# Small fixes on the owner's specimen photos before they are used as textures:
#  - full-grown male top view: the two nostrils were drawn like a second pair of eyes -> blend them into the skin and
#    leave a small dark nostril slit.
# Run: python prep_photos.py   (writes ../incoming/anc_mfull_top_fix.png)
import os, numpy as np, pngio
HERE = os.path.dirname(os.path.abspath(__file__)); INC = os.path.join(HERE, '..', 'incoming')
a = pngio.read(os.path.join(INC, 'anc_mfull_top_cut.png')).astype(np.float32)
H, W = a.shape[:2]; Y, X = np.mgrid[0:H, 0:W]
for cx, cy in ((1030, 268), (1030, 340)):                     # nostril centres (cut image px)
    d = np.hypot(X - cx, Y - cy)
    w = np.clip((26 - d) / 9, 0, 1)[..., None]                  # 1 inside r 17, fading to 0 at r 26
    src = np.roll(a[..., :3], 75, axis=1)                        # spotted skin 75 px further back on the head
    a[..., :3] = a[..., :3] * (1 - w) + src * w
    slit = np.clip(1 - np.hypot((X - cx) / 7, (Y - cy) / 3.2), 0, 1)[..., None] ** .7
    a[..., :3] = a[..., :3] * (1 - .75 * slit) + np.array([25, 22, 15]) * .75 * slit
pngio.write(os.path.join(INC, 'anc_mfull_top_fix.png'), np.clip(a, 0, 255))
print('ok')

# V17.91 juveniles: the same nostril fix on both juvenile top views (smaller fish: radius x0.75, clone 55 px back)
for name, pts in (('anc_juv_olive_top', ((746, 198), (746, 257))), ('anc_juv_black_top', ((745, 198), (745, 256)))):
    a = pngio.read(os.path.join(INC, name + '_cut.png')).astype(np.float32); H, W = a.shape[:2]; Y, X = np.mgrid[0:H, 0:W]
    for cx, cy in pts:
        d = np.hypot(X - cx, Y - cy); w = np.clip((19 - d) / 7, 0, 1)[..., None]
        a[..., :3] = a[..., :3] * (1 - w) + np.roll(a[..., :3], 55, axis=1) * w
        slit = np.clip(1 - np.hypot((X - cx) / 5.5, (Y - cy) / 2.5), 0, 1)[..., None] ** .7
        a[..., :3] = a[..., :3] * (1 - .7 * slit) + np.array([20, 18, 12]) * .7 * slit
    pngio.write(os.path.join(INC, name + '_fix.png'), np.clip(a, 0, 255)); print('ok', name)
