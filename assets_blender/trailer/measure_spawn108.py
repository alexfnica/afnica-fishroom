# V17.108 spawning check (2026-10-23): headless breeder, 1 male + 1 female + cave, daytime (hour 12), fake 30 fps clock,
# the owner's save never touched. The spawning sequence is forced in a loop: invite shortened (__T108.inv), trapped ended
# after TRAP s (trapDays=0), and LOOPS clutches in a row. Per frame: drawn pixel centroid of both fish (fin canvas / 3D
# canvas), unhidden fish px inside the tube, faded elements, console errors. GRID=out.jpg = one 8-tile grid of the 1st loop.
# Run: D:/Blender/5.2/python/bin/python.exe measure_spawn108.py   (env LOOPS, INV, TRAP, SEED, GRID)
import os, sys, json, math, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
LOOPS = int(os.environ.get('LOOPS', '2')); INV = float(os.environ.get('INV', '4')); TRAP = float(os.environ.get('TRAP', '6'))
GRID = os.environ.get('GRID')
HOOK = r"""window.__S=new WeakMap();setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1;"""
START = r"""(()=>{const a=tankArrayV14('breeder'),m=a.find(f=>f.sex==='M'),f=a.find(f=>f.sex==='F');window.__T108={inv:%f};
 st.ancClutch={id:'t108-'+(window.__n108=(window.__n108||0)+1),stage:'spawning',phase:'female-approach',seconds:0,mom:f.id,dad:m.id,count:30,attempt:1,lossRoll:1,lastDay:st.day};return 1})()""" % INV
REC = r"""(()=>{const tk=document.getElementById('tank-breeder'),T=tk.getBoundingClientRect(),k=T.width/(tk.clientWidth||T.width)||1,cave=tk.querySelector('.ancBreedingCave');
 const L=parseFloat(cave.style.left)||0,T0=parseFloat(cave.style.top)||0,Mx=L+13.8,My=T0+42,c=st.ancClutch,D=ancSpawnDebugV17108(),r=c&&D.R.get(c.id);
 const out={ph:c?(c.stage==='spawning'?c.phase:c.stage):'',ms:r&&r.m?r.m.st:'',fs:r&&r.f?r.f.st:'',L,T0,F:{}};
 for(const e of tk.querySelectorAll('[data-fish-id]')){const fish=tankArrayV14('breeder').find(q=>String(q.id)===e.dataset.fishId);if(!fish)continue;
  const t3=e.querySelector(':scope>canvas.anc94t'),on3=t3&&t3.style.display==='block',cv=on3?t3:e.querySelector('.ancArt canvas[data-wk^="anc|"]');
  const z=+getComputedStyle(e).zIndex||0,mir=/scaleX\(-/.test(e.style.transform||'');let cen=null,ov=0;
  if(cv&&cv.width){const R0=cv.getBoundingClientRect(),d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;let sx=0,sy=0,sw=0;
   for(let y=0;y<cv.height;y+=2)for(let x=0;x<cv.width;x+=2){const a=d[(y*cv.width+x)*4+3];if(a<=40)continue;const u=x/cv.width,v=y/cv.height;
    const px=(R0.left-T.left+(mir?1-u:u)*R0.width)/k,py=(R0.top-T.top+v*R0.height)/k;sx+=px*a;sy+=py*a;sw+=a;
    const behind=px>Mx&&((px-Mx)/7)**2+((py-My)/22.6)**2>1,inTube=px>Mx&&px<L+160&&py>T0+12&&py<T0+75;
    if(behind&&inTube&&z>=45)ov++;}
   if(sw)cen=[+(sx/sw).toFixed(2),+(sy/sw).toFixed(2)];}
  out.F[fish.sex]={x:+(+e.dataset.ancX).toFixed(2),y:+(+e.dataset.ancY).toFixed(2),cen,ov,z,m:e.dataset.ancMode||'',
   op:+(parseFloat(getComputedStyle(e).opacity)).toFixed(2),tn:(()=>{const q=__S.get(e);return q&&q.turn?[q.turn.from,q.turn.to,+q.turn.t.toFixed(2),q.turn.x104!=null]:null})(),t3:!!on3,face:mir?-1:1,env:e.dataset.fanEnv89||'',f106:e.dataset.fan106||''};}
 return JSON.stringify(out);})()"""
c = anc_game(tank='breeder', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", warm=2, pre=HOOK + SEED % int(os.environ.get('SEED', '7')))
c.js(START)
REC_ = []; tiles = []; loops = 1; ev = {}; eggs_at = None; trap_at = None
SHOTS = [('invite', lambda r, t: r['ms'] == 'invite' and t('m:invite') >= 2, '1 He invites, head out'),
         ('wait', lambda r, t: r['fs'] == 'wait' and t('f:wait') >= 1.5, '2 She waits by the mouth'),
         ('out', lambda r, t: r['ms'] == 'out' and t('m:out') >= 1.6, '2 He walks out and aside'),
         ('go', lambda r, t: r['fs'] == 'go' and r['F']['F']['x'] + 56 > r['L'] + 13.8 + 40, '3 She slides in head first'),
         ('enter', lambda r, t: r['ms'] == 'enter' and t('m:enter') >= 2.5, '3 He follows her in'),
         ('trap', lambda r, t: r['ph'] == 'trapped' and t('p:trapped') >= 2.5, '4 Over her, tail out, fanning'),
         ('back', lambda r, t: r['fs'] == 'back' and t('f:back') >= 3, '5 She backs out under him'),
         ('eggs', lambda r, t: r['ph'] == 'eggs' and t('p:eggs') >= 3, '5 Eggs: he guards, head in, fanning')]
try:
    for i in range(int(os.environ.get('SECS', '400')) * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30)); r = json.loads(c.js(REC)); REC_.append(r)
        for key in ('p:' + r['ph'], 'm:' + r['ms'], 'f:' + r['fs']):
            if len(REC_) < 2 or key not in (('p:' + REC_[-2]['ph']), ('m:' + REC_[-2]['ms']), ('f:' + REC_[-2]['fs'])): ev[key] = i
        t = lambda key: (i - ev[key]) / 30 if key in ev else -1
        if r['ph'] == 'trapped' and t('p:trapped') >= TRAP: c.js("st.ancClutch.trapDays=0;1")
        if GRID and loops == 1 and len(tiles) < len(SHOTS):
            name, cond, lab = SHOTS[len(tiles)]
            if cond(r, t):
                p = os.path.join(os.path.dirname(GRID), '_p%d.jpg' % len(tiles)); L = r['L']
                c.shot(p, clip=dict(x=L - 250, y=r['T0'] - 40, width=430, height=135, scale=2), q=90); tiles.append((p, lab))
        if r['ph'] == 'eggs':
            if t('p:eggs') >= 6:
                if loops >= LOOPS: break
                loops += 1; c.js(START); ev = {}
finally:
    pass
json.dump(REC_, open('D:/ClaudeWork/rec108.json', 'w'))
# ---- analysis: max drawn step per fish per (phase, sub-state), phase lengths, overlap, fades, errors
steps = {}; ovl = 0; fades = 0; seq = []
for i in range(1, len(REC_)):
    a, b = REC_[i - 1], REC_[i]
    for sx in ('M', 'F'):
        fa, fb = a['F'].get(sx), b['F'].get(sx)
        if not fa or not fb: continue
        ovl = max(ovl, fb['ov']); fades += fb['op'] < .99
        if fa['cen'] and fb['cen']:
            d = math.hypot(fb['cen'][0] - fa['cen'][0], fb['cen'][1] - fa['cen'][1])
            k = '%s %s/%s%s' % (sx, b['ph'], b['ms'] if sx == 'M' else b['fs'] or fb['m'], ' (V17.104 pivot)' if (fa.get('tn') or fb.get('tn')) else '')
            if d > steps.get(k, (0,))[0]: steps[k] = (round(d, 2), i)
for r in REC_:
    if not seq or seq[-1][0] != r['ph']: seq.append([r['ph'], 0])
    seq[-1][1] += 1
print('phases', [(p, round(n / 30, 1)) for p, n in seq])
for k, v in sorted(steps.items(), key=lambda kv: -kv[1][0])[:12]: print('  max drawn step %5.2f px/frame at %5d  %s' % (v[0], v[1], k))
print('unhidden fish px inside the tube (max/frame):', ovl, '| faded frames:', fades)
fan = [r['F']['M'] for r in REC_ if r['ph'] in ('trapped', 'laying') and r['F'].get('M')]
if fan: print('spawn fanning frames %d, V17.106 tail on in %d, env %.2f..%.2f' % (len(fan), sum(1 for q in fan if q['f106']), min(float(q['env'] or 0) for q in fan), max(float(q['env'] or 0) for q in fan)))
print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
if GRID and tiles:
    imgs = ''.join('<div style="display:inline-block;vertical-align:top;width:228px;margin:3px;text-align:center;font:600 12px system-ui;color:#fff"><img src="data:image/jpeg;base64,%s" style="width:228px;display:block">%s</div>' % (base64.b64encode(open(p, 'rb').read()).decode(), t) for p, t in tiles)
    c.js("(h=>{const d=document.createElement('div');d.id='g108';d.style.cssText='position:fixed;left:0;top:0;z-index:999999;background:#111;padding:5px;width:950px';d.innerHTML=h;document.body.appendChild(d);return 1})(%s)" % json.dumps(imgs))
    g = json.loads(c.js("JSON.stringify((r=>[r.width,r.height])(document.getElementById('g108').getBoundingClientRect()))"))
    c.shot(GRID, clip=dict(x=0, y=0, width=g[0], height=g[1], scale=1), q=88)
    for p, _ in tiles: os.remove(p)
    print('grid', GRID, [t[1] for t in tiles])
c.close()
