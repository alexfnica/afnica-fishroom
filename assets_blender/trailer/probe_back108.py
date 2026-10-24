# V17.108 probe (2026-10-23, owner: "we have corruption" at the mouth while the female backs out): headless breeder, the
# spawning sequence forced (invite 2 s, trapped 3 s), close-ups of the mouth at moments of her backing out, plus the
# per-layer facts (her clip / z, the rim). Run: D:/Blender/5.2/python/bin/python.exe probe_back108.py <out.jpg>
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
OUT = sys.argv[1]
c = anc_game(tank='breeder', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", warm=2, pre=SEED % 7)
c.js(r"""(()=>{const a=tankArrayV14('breeder'),m=a.find(f=>f.sex==='M'),f=a.find(f=>f.sex==='F');window.__T108={inv:2};
 st.ancClutch={id:'pb108',stage:'spawning',phase:'female-approach',seconds:0,mom:f.id,dad:m.id,count:30,attempt:1,lossRoll:1,lastDay:st.day};return 1})()""")
ST = r"""(()=>{const c=st.ancClutch,r=ancSpawnDebugV17108().R.get(c.id),cv=document.querySelector('#tank-breeder .ancBreedingCave'),b=cv.getBoundingClientRect();
 const e=document.querySelector('#tank-breeder [data-fish-id="'+c.mom+'"]');
 return JSON.stringify({ph:c.stage==='spawning'?c.phase:c.stage,fs:r&&r.f?r.f.st:'',ms:r&&r.m?r.m.st:'',mt:r&&r.m?r.m.t:0,ft:r&&r.f?r.f.t:0,fx:r&&r.f?r.f.x:0,L:parseFloat(cv.style.left),T:parseFloat(cv.style.top),b:[b.left,b.top,b.width],z:e&&e.style.zIndex,clip:e&&(e.style.clipPath||'').slice(0,40)})})()"""
tiles = []; trap = None
WANT = [('f', 'go', 6.0)] if os.environ.get('TRIPLE') else [('m', 'out', 1.5), ('f', 'go', 3.0), ('f', 'go', 6.0), ('m', 'enter', 3.0), ('m', 'fan', 2.0), ('f', 'back', 2.0), ('f', 'back', 5.0), ('m', 'fan', 30.0)]
want = WANT
for i in range(240 * 30):
    c.js('__afStep(%f, 2)' % (1000 / 30)); s = json.loads(c.js(ST))
    if s['ph'] == 'trapped':
        trap = trap if trap is not None else i
        if i - trap > 90: c.js("st.ancClutch.trapDays=0;1")
    w = WANT[len(tiles)] if len(tiles) < len(WANT) else None
    if w and s[w[0] + 's'] == w[1] and s[w[0] + 't'] >= w[2]:
        if os.environ.get('NOCLIP'): c.js("document.querySelectorAll('#tank-breeder [data-fish-id]').forEach(e=>e.style.setProperty('clip-path','none','important'));1")   # test: does the rim layer hide them?
        if os.environ.get('NORIM'): c.js("document.querySelector('#tank-breeder .ancCaveRim').style.setProperty('display','none','important');1")
        if os.environ.get('TRIPLE'):   # the same frame three ways, close on the mouth: current clip / no fish clip / no rim layer
            k = s['b'][2] / 160.0
            for lab, js in (('current clip', '1'), ('fish clip none', "document.querySelectorAll('#tank-breeder [data-fish-id]').forEach(e=>e.style.setProperty('clip-path','none','important'));1"),
                            ('rim layer hidden', "document.querySelector('#tank-breeder .ancCaveRim').style.setProperty('display','none','important');1")):
                c.js(js); p = os.path.join(os.path.dirname(OUT), '_b%d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=s['b'][0] - 30 * k, y=s['b'][1] + 5 * k, width=70 * k, height=75 * k, scale=6), q=92); tiles.append((p, lab))
            break
        k = s['b'][2] / 160.0; p = os.path.join(os.path.dirname(OUT), '_b%d.jpg' % len(tiles))
        c.shot(p, clip=dict(x=s['b'][0] - 200 * k, y=s['b'][1] + 5 * k, width=250 * k, height=75 * k, scale=3), q=92)
        tiles.append((p, '%s %s %.1f s' % ('male' if w[0] == 'm' else 'female', w[1], s[w[0] + 't'])))
        print(json.dumps(s))
    if len(tiles) == len(want): break
html = ''.join('<div style="display:inline-block;width:300px;margin:3px;text-align:center;font:600 12px system-ui;color:#fff"><img src="data:image/jpeg;base64,%s" style="width:300px;display:block">%s</div>' % (base64.b64encode(open(p, 'rb').read()).decode(), t) for p, t in tiles)
c.js("(h=>{const d=document.createElement('div');d.id='g';d.style.cssText='position:fixed;left:0;top:0;z-index:999999;background:#111;padding:5px;width:950px';d.innerHTML=h;document.body.appendChild(d);return 1})(%s)" % json.dumps(html))
g = json.loads(c.js("JSON.stringify((r=>[r.width,r.height])(document.getElementById('g').getBoundingClientRect()))"))
c.shot(OUT, clip=dict(x=0, y=0, width=g[0], height=g[1], scale=1), q=90)
for p, _ in tiles: os.remove(p)
c.close(); print('probe', OUT)
