# V17.110 (owner's correction): yolk-sac fry huddle in the Fry Tank (nursery) under a decoration / in a corner and do not roam;
# once the yolk is gone they become free fry. Also tests moveAncWrigglers110 (cave brood -> Fry Tank).
# Run: D:/Blender/5.2/python/bin/python.exe measure_fry110c.py   (env SECS, AF_PORT)
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
SECS = int(os.environ.get('SECS', '100'))
Y = "Object.assign(T.fish('anc','%s',1),{yolkStart110:st.day-1,yolkEnd110:st.day+3})"
FISH = "[" + ",".join(Y % s for s in 'FMFMF') + ",T.fish('anc','M',3.5),T.fish('anc','F',40)]"
PRE = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};"
c = anc_game(tank='fry', fish=FISH, warm=2, pre=PRE)
def rec():
    return json.loads(c.js("JSON.stringify([...document.querySelectorAll('.tank [data-fish-id]')].map(e=>[e.dataset.fishId,+e.dataset.ancX,+e.dataset.ancY,e.dataset.ancMode,e.dataset.yolk110||'',e.style.zIndex]))"))
try:
    L = []
    for i in range(SECS * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30))
        if i % 3 == 0: L.append(rec())
    print('tank ids', c.js("JSON.stringify([...document.querySelectorAll('.tank')].map(t=>t.id))"))
    print('spots', c.js('JSON.stringify(ancFryDebugV17110())')[:300])
    print('decor', c.js("JSON.stringify([...document.querySelectorAll('[data-v177-editable]')].map(d=>{const r=d.getBoundingClientRect();return [d.className.slice(0,30),Math.round(r.left),Math.round(r.bottom),Math.round(r.width)]}))")[:300])
    n = len(L[0]); print('fish', n)
    ys = [r for r in L[0] if r[4] not in ('', '0.00')]
    xs_end = [[r[1] for r in fr if r[0] == y[0]][0] for y in ys for fr in [L[-1]]]
    mv = []
    for y in ys:
        xs = [[r[1] for r in fr if r[0] == y[0]][0] for fr in L[len(L) // 3:]]
        mv.append((round(max(xs) - min(xs), 1)))
    print('yolk fish: end x', [round(v) for v in xs_end], 'x range over last 2/3 (px)', mv, 'yolk k', [y[4] for y in ys], 'zIndex', [y[5] for y in ys])
    print('errors', c.js('JSON.stringify(window.__err)'))
    # day passes: the yolk is used up -> free fry
    c.js("st.day+=5;1")
    for i in range(60): c.js('__afStep(%f, 2)' % (1000 / 30))
    print('after yolk: k', [r[4] for r in rec()][:5], 'amber px', c.js(r"""(()=>{let n=0;document.querySelectorAll('.ancArt canvas[data-wk="anc|120|238"],.ancArt canvas[data-wk="anc|0|238"]').forEach(c=>{const D=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=0;i<D.length;i+=4)if(D[i+3]>150&&D[i]>200&&D[i+1]>120&&D[i+1]<200&&D[i+2]<110)n++});return n})()"""))
    # the move button
    r = c.js("""(()=>{const mom=st.fry.find(f=>f.sex==='F'),dad=st.fry.find(f=>f.sex==='M');const n0=st.fry.length;st.ancClutch={id:'tc1',stage:'yolk',count:4,hatchDay:st.day-2,releaseDay:st.day+3,parents:{mom,dad}};moveAncWrigglers110(1);return JSON.stringify([st.fry.length-n0,st.ancClutch.stage,st.fry.filter(f=>f.yolkEnd110!=null).length,String(st.fry[st.fry.length-1].yolkEnd110)])})()""")
    print('move test (added, stage, with yolk, yolkEnd):', r, 'errors', c.js('JSON.stringify(window.__err)'))
finally:
    c.close()
