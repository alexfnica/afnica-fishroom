# The male at the cave hand-over: photo drawing (his element) vs the cave canvas fish, same instant; plus their bottoms.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
OUT = os.path.join(HERE, 'raw', 'p93'); os.makedirs(OUT, exist_ok=True)
FISH = "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30)]"
c = anc_game(tank='main', fish=FISH, warm=1, dsf=4, pre=SEED % 7)
try:
    m = ids(c, 'main')[0]; shots = 0
    Q = r"""JSON.stringify((()=>{const e=document.querySelector('#tank-main [data-fish-id="%s"]'),t=anc90Debug().TK.get(document.getElementById('tank-main'))||{},cv=document.querySelector('#tank-main canvas.anc90cv'),cave=document.querySelector('#tank-main .ancBreedingCave');
      const art=e.querySelector('.ancArt'),r=art.getBoundingClientRect(),cr=cv?cv.getBoundingClientRect():null;
      return {mode:e.dataset.ancMode,x:+e.dataset.ancX,y:+e.dataset.ancY,op:e.style.opacity,cm:t.m||null,artBottom:r.bottom,artTop:r.top,cvTop:cr&&cr.top,caveTop:parseFloat(cave.style.top),caveLeft:parseFloat(cave.style.left)}})())""" % m
    for i in range(30 * 40):
        c.js('__afStep(%f, 2)' % (1000 / 30)); q = json.loads(c.js(Q))
        if q['cm'] and q['cm'].get('name', '').startswith('C2_i') and shots < 8 and i % 4 == 0:
            print(i, q); r = q
            x = q['caveLeft'] - 120; y = q['caveTop'] - 10
            shot(c, os.path.join(OUT, 'h%02d.jpg' % shots), clip=dict(x=x, y=y, width=240, height=100, scale=4)); shots += 1
        if shots >= 8: break
finally: c.close()
