# Cloud version of cut_translucent.py (no Blender needed: numpy + Pillow).
# Cuts a translucent subject (glassy larva/fry, clear fins) out of a white background by difference matting: alpha comes
# from how far each pixel is from the paper colour, then the paper is un-mixed from the colour, so clear parts stay
# see-through. Crops to the subject, optionally flips it to face right, and scales to the given width.
# Run: python assets_blender/cut_translucent_np.py <in> <out.png> [width=300] [gain=3.2] [--flip]
import sys
import numpy as np
from PIL import Image

args = [a for a in sys.argv[1:] if not a.startswith('--')]
FLIP = '--flip' in sys.argv
SRC, OUT = args[0], args[1]
WIDTH = int(args[2]) if len(args) > 2 else 300
GAIN = float(args[3]) if len(args) > 3 else 3.2

rgb = np.asarray(Image.open(SRC).convert('RGB'), np.float32) / 255.0
# the paper is never perfectly white: estimate it from the border
b = 8
border = np.concatenate([rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3), rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])
bg = np.median(border, 0)
diff = np.max(np.abs(rgb - bg), -1)
alpha = np.clip((diff - .025) * GAIN, 0, 1)
alpha = np.where(alpha > .02, alpha, 0)
a3 = alpha[..., None]
col = np.clip((rgb - bg * (1 - a3)) / np.maximum(a3, 1e-3), 0, 1)
col = np.where(a3 > .97, rgb, col)
ys, xs = np.nonzero(alpha > .08)
if not len(ys):
    sys.exit('nothing found on the background')
y0, y1 = max(0, ys.min() - 4), ys.max() + 5
x0, x1 = max(0, xs.min() - 4), xs.max() + 5
out = np.concatenate([col, a3], -1)[y0:y1, x0:x1]
img = Image.fromarray((out * 255 + .5).astype(np.uint8), 'RGBA')
if FLIP:
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
h = max(1, round(img.height * WIDTH / img.width))
img = img.resize((WIDTH, h), Image.LANCZOS)
img.save(OUT)
print('CUT', OUT, WIDTH, h, 'paper', np.round(bg, 3))
