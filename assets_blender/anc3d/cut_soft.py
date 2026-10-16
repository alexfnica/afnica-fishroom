# Soft cut for translucent fish (fry): the grey card is modelled as a smooth colour gradient fitted to the image border,
# alpha = how far each pixel is from that background (glassy fins become partly transparent, as they are), and the colour
# is un-mixed from the background. Run (Blender's python, numpy): python cut_soft.py <in.(webp|png|jpg)> <out.png> [lo hi]
import sys, os, json, base64, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
import pngio
from cdp import Chrome
src, out = sys.argv[1], sys.argv[2]; LO, HI = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (5., 26.)
# decode any format through Chrome -> PNG
mime = {'webp': 'image/webp', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}[src.rsplit('.', 1)[1].lower()]
b64 = base64.b64encode(open(src, 'rb').read()).decode()
c = Chrome(400, 300, 1, port=int(os.environ.get('AF_PORT', '9497')))
try:
    url = c.js("(async s=>{const i=new Image();i.src=s;await i.decode();const c=document.createElement('canvas');c.width=i.naturalWidth;c.height=i.naturalHeight;c.getContext('2d').drawImage(i,0,0);return c.toDataURL('image/png')})(%s)" % json.dumps('data:%s;base64,%s' % (mime, b64)))
finally: c.close()
tmp = out + '.src.png'; open(tmp, 'wb').write(base64.b64decode(url.split(',', 1)[1]))
a = pngio.read(tmp).astype(np.float64); os.remove(tmp); H, W = a.shape[:2]
# background = quadratic surface per channel fitted on a 12 px border frame
Y, X = np.mgrid[0:H, 0:W]; m = np.zeros((H, W), bool); m[:12] = m[-12:] = True; m[:, :12] = m[:, -12:] = True
def basis(x, y): x = x / W; y = y / H; return np.stack([np.ones_like(x), x, y, x * x, y * y, x * y], -1)
A = basis(X[m], Y[m]); bg = np.zeros((H, W, 3))
for ch in range(3):
    coef, *_ = np.linalg.lstsq(A, a[..., ch][m], rcond=None); bg[..., ch] = basis(X, Y) @ coef
d = np.sqrt(((a[..., :3] - bg) ** 2).sum(-1))
al = np.clip((d - LO) / (HI - LO), 0, 1); al = al * al * (3 - 2 * al)
fg = np.where(al[..., None] > .02, (a[..., :3] - (1 - al[..., None]) * bg) / np.maximum(al[..., None], .02), a[..., :3])
o = np.dstack([np.clip(fg, 0, 255), al * 255])
ys, xs = np.nonzero(al > .08); y0, y1, x0, x1 = max(0, ys.min() - 4), min(H, ys.max() + 5), max(0, xs.min() - 4), min(W, xs.max() + 5)
pngio.write(out, o[y0:y1, x0:x1]); print('ok', out, (x1 - x0, y1 - y0), 'crop', (x0, y0))
