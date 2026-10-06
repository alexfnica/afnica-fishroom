import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(a[0]); W, H = img.size
px = np.empty(W*H*4, np.float32); img.pixels.foreach_get(px); S = px.reshape(H, W, 4)
S[..., 3] = np.clip(S[..., 3] * 1.9 + (S[..., 3] > .05) * .12, 0, 1)
res = bpy.data.images.new('f', W, H, alpha=True); res.pixels.foreach_set(S.reshape(-1)); res.filepath_raw = a[1]; res.file_format = 'PNG'; res.save(); print('OPAQ', W, H)