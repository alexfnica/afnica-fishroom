# Mirror an image left-right (so the fish faces right like every game sprite).
# Run: D:\Blender\blender.exe -b -P flip_h.py -- <in> <out.png>
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(a[0]); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px)
px = px.reshape(H, W, 4)[:, ::-1].copy()
o = bpy.data.images.new('f', W, H, alpha=True); o.pixels.foreach_set(px.reshape(-1))
o.filepath_raw = a[1]; o.file_format = 'PNG'; o.save(); print('FLIP', a[1])
