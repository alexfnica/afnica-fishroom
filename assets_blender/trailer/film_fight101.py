# V17.101b: a review clip of one whole male fight (2 adult males, no female, noon), zoomed on the pair.
# Pass 1 (no shots) finds where and when the fight happens; pass 2 (same seed = same run) films from 3 s before the 3D
# starts to 4 s after it ends. -> AFNICA_Anc101_fight.mp4 in the repo root (git-ignored).
# Run: D:/Blender/5.2/python/bin/python.exe film_fight101.py   (env SEED, ZOOM)
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED, encode, ROOT
S = int(os.environ.get('SEED', '3')); Z = float(os.environ.get('ZOOM', '1.6')); NAME = 'fight101'
J = r"""(()=>{const D=anc90Debug(),F=D.F96['tank-main'];const L=window.__f96last;if(!F){if(L&&L.end==='done')return JSON.stringify(['done']);for(const k in D.CD96)delete D.CD96[k];window.anc96Force=1;return '["-"]';}
 const r=F.b.el.getBoundingClientRect();return JSON.stringify([F.ph,r.x+60,r.y+35,F.px||0,F.sg||0]);})()"""
def run(film=None):
    c = anc_game(tank='main', fish="[T.fish('anc','M',40),T.fish('anc','M',38)]", warm=1, pre=SEED % S)
    out = os.path.join(HERE, 'raw', 'a89_' + NAME)
    if film:
        os.makedirs(out, exist_ok=True)
        for f in os.listdir(out): os.remove(os.path.join(out, f))
    info = {}; n = 0
    try:
        for i in range(30 * 150):
            c.js('__afStep(%f, 2)' % (1000 / 30)); r = json.loads(c.js(J))
            if r[0] == 'fight' and 'f0' not in info: info.update(f0=i, x=r[1], y=r[2])
            if r[0] == 'fight': info['xs'] = info.get('xs', []) + [r[1]]
            if r[0] == 'done' and 'f1' not in info: info['f1'] = i
            if film and film['a'] <= i <= film['b']:
                c.shot(os.path.join(out, '%05d.jpg' % n), clip=film['clip'], q=90); n += 1
            if 'f1' in info and i > info['f1'] + 130: break
    finally: c.close()
    return info
I = run()
print('pass 1: fight from frame', I.get('f0'), 'to', I.get('f1'))
xs = I['xs']; cx = (min(xs) + max(xs)) / 2   # the rival's photo stays put; the pair drifts round it - centre on the range
w, h = VW / Z, VH / Z
clip = dict(x=min(max(cx - w / 2, 0), VW - w), y=min(max(I['y'] - h * .62, 0), VH - h), width=w, height=h, scale=Z)
run(dict(a=I['f0'] - 90, b=I['f1'] + 120, clip=clip))
encode(NAME, int(w * Z) // 2 * 2, int(h * Z) // 2 * 2)
src = os.path.join(ROOT, 'AFNICA_Anc89_%s.mp4' % NAME); dst = os.path.join(ROOT, 'AFNICA_Anc101_fight.mp4')
if os.path.exists(src): shutil.move(src, dst); print('clip', dst)
