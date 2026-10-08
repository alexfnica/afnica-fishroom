# Put a cut-out sprite in the middle of a larger transparent canvas (the fish then shows smaller in the game, which
# fits sprites to a fixed box). Run: D:\Blender\blender.exe -b -P pad_sprite.py -- <in.png> <out.png> <factor>
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(a[0]); W, H = img.size; K = float(a[2])
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); S = px.reshape(H, W, 4)
NW, NH = round(W * K), round(H * K); O = np.zeros((NH, NW, 4), np.float32)
x0, y0 = (NW - W) // 2, (NH - H) // 2; O[y0:y0 + H, x0:x0 + W] = S
out = bpy.data.images.new('p', NW, NH, alpha=True); out.pixels.foreach_set(O.reshape(-1))
out.filepath_raw = a[1]; out.file_format = 'PNG'; out.save(); print('PAD', a[1], NW, NH)
