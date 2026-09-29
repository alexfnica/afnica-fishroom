# Make a newborn-fry look from a juvenile cut-out: colour drained to translucent silver-grey, slightly see-through.
# Run: D:\Blender\blender.exe -b -P fry_from.py -- <in.png> <out.png>
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(a[0]); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); S = px.reshape(H, W, 4)
lum = S[..., :3] @ np.array([.299, .587, .114], np.float32)
g = .42 + .5 * lum                                   # lift the darks: fry have no tuxedo black yet
S[..., 0] = g * .96; S[..., 1] = g * .98; S[..., 2] = g * 1.02
S[..., 3] *= .86
res = bpy.data.images.new('f', W, H, alpha=True); res.pixels.foreach_set(S.reshape(-1))
res.filepath_raw = a[1]; res.file_format = 'PNG'; res.save(); print('FRY', W, H)
