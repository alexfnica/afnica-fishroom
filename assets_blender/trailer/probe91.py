# V17.91 close-ups: a female resting (dorsal folded), crawling, rasping; the male; zoomed 4x on each fish.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
OUT = os.path.join(HERE, 'raw', 't91'); os.makedirs(OUT, exist_ok=True)
c = anc_game(tank='main', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", warm=2, dsf=3, pre=SEED % 5)
try:
    ids_ = ids(c, 'main')
    for t in range(1, 25):
        advance(c, 1)
        for k, fid in enumerate(ids_):
            st = json.loads(c.js("JSON.stringify((e=>{const r=e.getBoundingClientRect(),q=anc90Debug().Q91.get(e)||{};return {m:e.dataset.ancMode,s:e.dataset.ancSurface,x:r.x,y:r.y,w:r.width,h:r.height,fold:q.fold,sw:e.dataset.swim91}})(document.querySelector('#tank-main [data-fish-id=\"%s\"]')))" % fid))
            if t % 4 == 0:
                cx, cy = st['x'] + st['w'] / 2, st['y'] + st['h'] / 2; W, H = VW / 4, VH / 4
                shot(c, os.path.join(OUT, 'f%d_%02d_%s_fold%.2f.jpg' % (k, t, st['m'], st['fold'] or 0)), clip=dict(x=max(0, min(cx - W / 2, VW - W)), y=max(0, min(cy - H / 2, VH - H)), width=W, height=H, scale=4))
finally: c.close()
print(sorted(os.listdir(OUT)))
