# Close-up frame strips: (A) a female turning on the sand, (B) the male's first cave entry. Throw-away headless game.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
OUT = os.path.join(HERE, 'raw', 'p92'); os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
which = sys.argv[1]
if which == 'turn':
    c = anc_game(tank='main', fish="[T.fish('anc','F',36)]", warm=1, dsf=3, pre=SEED % 7)
    try:
        fid = ids(c, 'main')[0]; got = 0
        for i in range(30 * 120):
            c.js('__afStep(%f, 2)' % (1000 / 30))
            t = c.js("(e=>e.classList.contains('anc90')?1:0)(document.querySelector('#tank-main [data-fish-id=\"%s\"]'))" % fid)
            if t: break
        p = json.loads(c.js("JSON.stringify((e=>{const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})(document.querySelector('#tank-main [data-fish-id=\"%s\"]')))" % fid))
        W, H = VW / 3, VH / 3; clip = dict(x=max(0, min(p[0] - W / 2, VW - W)), y=max(0, min(p[1] - H / 2, VH - H)), width=W, height=H, scale=4)
        for _ in range(3): c.js('__afStep(%f, 2)' % (-1e-9))
        for k in range(30):
            shot(c, os.path.join(OUT, 'turn_%02d.jpg' % k), clip=clip)
            for _ in range(1): c.js('__afStep(%f, 2)' % (1000 / 30))
    finally: c.close()
else:
    c = anc_game(tank='main', fish="[T.fish('anc','M',40,{ancCaveCycleStart:st.day})]", warm=1, dsf=3, pre=SEED % 7)
    try:
        fid = ids(c, 'main')[0]
        for i in range(30 * 60):
            c.js('__afStep(%f, 2)' % (1000 / 30))
            m = c.js("document.querySelector('#tank-main [data-fish-id=\"%s\"]').dataset.ancMode" % fid)
            if m == 'cave-approach': break
        b = json.loads(c.js("JSON.stringify((()=>{const r=document.querySelector('#tank-main .ancBreedingCave').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})())"))
        W, H = VW / 3.5, VH / 3.5; clip = dict(x=max(0, b['x'] - W * .55), y=max(0, min(b['y'] + b['h'] - H * .75, VH - H)), width=W, height=H, scale=3.5)
        L = []
        for k in range(540):
            if k % 6 == 0: shot(c, os.path.join(OUT, 'cave_%03d.jpg' % k), clip=clip)
            L.append(c.js("JSON.stringify((e=>[e.dataset.ancMode,+(+e.dataset.ancX).toFixed(2),(anc90Debug().TK.get(e.closest('.tank'))||{}).want||''])(document.querySelector('#tank-main [data-fish-id=\"%s\"]')))" % fid))
            c.js('__afStep(%f, 2)' % (1000 / 30))
        open(os.path.join(OUT, 'cave_log.txt'), 'w').write('\n'.join(L))
    finally: c.close()
print('done', which)
