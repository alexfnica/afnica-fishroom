# Paint the bottom rows of an image white (removes UI lines left at the bottom of a screen capture).
# Run: D:\Blender\blender.exe -b -P blank_bottom.py -- <in> <out.png> [rows]
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(a[0]); W, H = img.size; R = int(a[2]) if len(a) > 2 else 14
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); P = px.reshape(H, W, 4)
P[:R, :, :3] = 1.0; P[:R, :, 3] = 1.0          # Blender rows start at the bottom
out = bpy.data.images.new('b', W, H, alpha=True); out.pixels.foreach_set(P.reshape(-1))
out.filepath_raw = a[1]; out.file_format = 'PNG'; out.save(); print('BLANK', a[1])
