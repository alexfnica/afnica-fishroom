# One close-up of the belly view on the glass during a push (largest fin swing) -> argv[1]
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
HOOK = r"""window.__S=new WeakMap();setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1;"""
c = anc_game(tank='main', fish="[T.fish('anc','M',40)]", warm=1, pre=HOOK + SEED % 7)
try:
    c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e);s.mode='toWall';s.wall=s.x<480?-1:1;s.transition=null;s.wait=0;return 1})()")
    best = 0
    for i in range(80 * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30))
        r = json.loads(c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e),b=e.getBoundingClientRect();return JSON.stringify([s.mode,+(parseFloat(e.style.getPropertyValue('--anc-glass'))||0),+e.dataset.ancStroke||0,b.left+b.width/2,b.top+b.height/2])})()"))
        if r[0] == 'graze' and r[1] >= 1 and r[2] > max(.4, best):
            best = r[2]; c.shot(sys.argv[1], clip=dict(x=r[3] - 45, y=r[4] - 45, width=90, height=90, scale=5), q=92); print('shot at', i, r)
            if best > .9: break
finally: c.close()
