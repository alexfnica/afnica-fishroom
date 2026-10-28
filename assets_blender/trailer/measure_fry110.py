# V17.110 fry: yolk sac + grouping. Headless, fake 30 fps clock, main tank: 3 yolk-sac fry (age 1-2), 2 free fry (3.5, 4), 1 juvenile, 1 adult.
# Prints per group the mean pairwise |dx| (px) and the share of frames moving, with ANC110 on and off, the amber pixels of the sac, errors.
# Run: D:/Blender/5.2/python/bin/python.exe measure_fry110.py   (env SECS, AF_PORT)
import os, sys, json, math, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
SECS = int(os.environ.get('SECS', '90'))
FISH = "[T.fish('anc','F',1),T.fish('anc','M',1.5),T.fish('anc','F',2),T.fish('anc','M',3.5),T.fish('anc','F',4),T.fish('anc','M',8),T.fish('anc','M',40)]"
PRE = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};window.ANC110=%s;"
REC = r"""JSON.stringify([...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>[e.dataset.fishId,+e.dataset.ancX,+e.dataset.ancY,e.dataset.ancMode,e.dataset.yolk110||'']))"""
AMB = r"""(()=>{let n=0;document.querySelectorAll('.ancArt canvas[data-wk="anc|120|238"],.ancArt canvas[data-wk="anc|0|238"]').forEach(c=>{const D=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=0;i<D.length;i+=4)if(D[i+3]>150&&D[i]>200&&D[i+1]>120&&D[i+1]<200&&D[i+2]<110)n++});return n})()"""
def run(flag):
    c = anc_game(tank='main', fish=FISH, warm=2, pre=PRE % flag)
    try:
        ages = json.loads(c.js("JSON.stringify(Object.fromEntries(tankArrayV14('main').map(f=>[String(f.id),f.age])))"))
        L = []
        for i in range(SECS * 30):
            c.js('__afStep(%f, 2)' % (1000 / 30))
            if i % 3 == 0: L.append(json.loads(c.js(REC)))
        amber = c.js(AMB); err = c.js('JSON.stringify(window.__err)')
        shot = None
        if flag == 'true':
            r = json.loads(c.js("(()=>{const R=[...document.querySelectorAll('#tank-main [data-fish-id]')].filter(e=>e.dataset.yolk110&&e.dataset.yolk110!=='0.00').map(e=>e.getBoundingClientRect());const x0=Math.min(...R.map(r=>r.left)),x1=Math.max(...R.map(r=>r.right)),y0=Math.min(...R.map(r=>r.top)),y1=Math.max(...R.map(r=>r.bottom));return JSON.stringify([x0,y0,x1,y1])})()"))
            cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
            c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'fry110_heap.jpg'), clip={'x': cx - 110, 'y': cy - 60, 'width': 220, 'height': 120, 'scale': 4}, q=90)
        return ages, L, amber, err
    finally:
        c.close()
def stats(ages, L):
    ids = [r[0] for r in L[0]]; grp = {'yolk': [], 'free': []}
    for r in L[0]:
        a = ages[r[0]]
        if a < 3: grp['yolk'].append(r[0])
        elif a < 5: grp['free'].append(r[0])
    out = {}
    for g, m in grp.items():
        sp = []; mov = 0; n = 0
        for fr in L[len(L) // 3:]:
            xs = {r[0]: r[1] for r in fr}; v = [xs[i] for i in m]
            sp.append(sum(abs(a - b) for ai, a in enumerate(v) for b in v[ai + 1:]) / max(1, len(v) * (len(v) - 1) / 2))
        for k in range(len(L) // 3 + 1, len(L)):
            for i in m:
                a = [r for r in L[k - 1] if r[0] == i][0]; b = [r for r in L[k] if r[0] == i][0]
                n += 1; mov += 1 if math.hypot(a[1] - b[1], a[2] - b[2]) > .6 else 0
        out[g] = (len(m), round(sum(sp) / len(sp), 1), round(100 * mov / max(1, n)))
    return out
for flag in os.environ.get('FLAGS', 'false,true').split(','):
    ages, L, amber, err = run(flag)
    print('ANC110', flag, 'group (n, mean pair |dx| px, % moving):', stats(ages, L), 'amber px', amber, 'errors', err)
