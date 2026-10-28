# V17.109: does the painted eye stay on the baked eye when the female's belly is swollen / thin? (belly forced via femaleBellyV1743)
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
c = anc_game(tank='main', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", warm=2, pre="")
def step(sec):
    for i in range(int(sec * 30)): c.js('__afStep(%f, 2)' % (1000 / 30))
CEN = r"""JSON.stringify([...document.querySelectorAll('.ancArt canvas[data-wk^="anc|"]')].map(cv=>{const m=/anc\|(0|240)\|/.test(cv.dataset.wk),ex=m?198.8:209.2,ey=(m?57:70.5)+20,x0=Math.round(ex-7),y0=Math.round(ey-12),D=cv.getContext('2d').getImageData(x0,y0,15,25).data;
 let n=0,sx=0,sy=0;for(let y=0;y<25;y++)for(let x=0;x<15;x++){const i=(y*15+x)*4;if(D[i+3]>200&&D[i]+D[i+1]+D[i+2]<75&&Math.hypot(x-7,y-12)<7){n++;sx+=x;sy+=y}}return [cv.dataset.wk,n,n?+(sx/n+x0-ex).toFixed(2):null,n?+(sy/n+y0-ey).toFixed(2):null]}))"""
try:
    c.js("window.__afHourOverride=12;window.ANC109TAU=.05;1"); step(1)
    for B in (-0.25, 0, 0.25):
        c.js("window.femaleBellyV1743=()=>%f;document.querySelectorAll('.tank .modelFish[data-fish-id]').forEach(e=>e.dataset.belly='%f');1" % (B, B)); step(1)
        r = {}
        for on in (False, True):
            c.js("window.ANC109=%s;1" % ('true' if on else 'false')); step(.7)
            r[on] = json.loads(c.js(CEN))
        print('belly', B, 'baked(off)', r[False][1], 'painted(on)', r[True][1], ' male off', r[False][0][1:], 'on', r[True][0][1:])
finally:
    c.close()
