import bpy, numpy as np
img = bpy.data.images.load('D:/Retirement/assets_blender/logo/afnica_fishroom_src.webp'); W, H = img.size
px = np.empty(W*H*4, np.float32); img.pixels.foreach_get(px); S = px.reshape(H, W, 4)[::-1]
lum = S[..., :3].mean(-1); ink = lum < .5
print('SIZE', W, H, 'bg', np.median(lum[:10]), 'alphaMin', S[...,3].min())
rows = ink.any(1); bands = []; y = 0
while y < H:
    if rows[y]:
        y0 = y
        while y < H and rows[y]: y += 1
        xs = np.nonzero(ink[y0:y].any(0))[0]; bands.append((y0, y-1, xs.min(), xs.max()))
    else: y += 1
for b in bands: print('BAND rows %d-%d cols %d-%d' % b)
# circle ring: bounding box of the first band
