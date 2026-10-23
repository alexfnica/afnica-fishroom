# V17.106 cave check (2026-10-22): headless main tank, 1 male (cave cycle) + 1 female + cave, daytime, fake 30 fps clock,
# the owner's save never touched. The cave cycle is shortened (fan DBG.fan s, guard DBG.guard s) so entry -> fanning ->
# exit -> turn -> entry loops. Per frame: mode, the drawn body centroid (photo canvas or turn canvas, tank px), element
# opacity (the model must never be swapped out), fish pixels over the tube that no clip hides, fanning phase/strength.
# Reports the max drawn step per mode and at every mode change, overlap pixels, swaps, console errors.
# Run: D:/Blender/5.2/python/bin/python.exe measure_cave106.py   (env SECS, FAN, GUARD, AF_PORT, GRID=out.jpg for a frame grid)
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
SECS = int(os.environ.get('SECS', '75')); FAN = float(os.environ.get('FAN', '6')); GUARD = float(os.environ.get('GUARD', '4'))
HOOK = (r"""window.__S=new WeakMap();window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};
 setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);
 (function w(){if(window.ancDebugV1789){const D=ancDebugV1789().DBG;D.fan=%s;D.guard=%s;}else setTimeout(w,50)})();1;""" % (FAN, GUARD))
FISH = "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36)]"
REC = r"""(()=>{const tk=document.getElementById('tank-main'),T=tk.getBoundingClientRect(),k=T.width/(tk.clientWidth||T.width)||1,cave=tk.querySelector('.ancBreedingCave');
 const L=parseFloat(cave.style.left)||0,T0=parseFloat(cave.style.top)||0,Mx=L+13.8,My=T0+42;
 const e=[...tk.querySelectorAll('[data-fish-id]')].find(q=>q.querySelector('.ancArt:not(.ancFemale)'));if(!e)return 'null';
 const t3=e.querySelector(':scope>canvas.anc94t'),on3=t3&&t3.style.display==='block',c=on3?t3:e.querySelector('.ancArt canvas[data-wk^="anc|"]');
 const clip=(e.style.clipPath||'none')!=='none',mir=/scaleX\(-/.test(e.style.transform||'');let cen=null,ov=0,vis=0;
 if(c&&c.width){const r=c.getBoundingClientRect(),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let sx=0,sy=0,sw=0;
  for(let y=0;y<c.height;y+=2)for(let x=0;x<c.width;x+=2){const a=d[(y*c.width+x)*4+3];if(a<=40)continue;const u=x/c.width,v=y/c.height;
   const px=(r.left-T.left+(mir?1-u:u)*r.width)/k,py=(r.top-T.top+v*r.height)/k;sx+=px*a;sy+=py*a;sw+=a;
   const behind=px>Mx&&((px-Mx)/7)**2+((py-My)/22.6)**2>1,inTube=px>Mx&&px<L+160&&py>T0+12&&py<T0+75;
   if(behind&&inTube&&!clip)ov++;if(!(behind&&clip))vis++;}
  if(sw)cen=[+(sx/sw).toFixed(2),+(sy/sw).toFixed(2)];}
 return JSON.stringify({m:e.dataset.ancMode||'',x:+(+e.dataset.ancX).toFixed(2),cen,on3,op:+(parseFloat(getComputedStyle(e).opacity)).toFixed(2),
  art:+(parseFloat(getComputedStyle(e.querySelector('.ancArt')).opacity)).toFixed(2),clip,ov,vis,psi:e.dataset.psi89||'',ph:e.dataset.fanPh89||'',env:e.dataset.fanEnv89||'',L,T0});})()"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=HOOK + SEED % int(os.environ.get('SEED', '7')))
ev = {}; R = []; GRID = os.environ.get('GRID'); tiles = []; want = None
try:
    for i in range(SECS * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30)); r = json.loads(c.js(REC)); R.append(r)
        if GRID and r:
            # entry (start, at the mouth, pushing in), fanning (4 frames 0.1 s apart, 1 s in), guard (head out), exit, turn, re-entry
            m = r['m']; prev = R[-2]['m'] if len(R) > 1 and R[-2] else ''
            if m != prev: ev[m] = i
            dt = lambda md: (i - ev[md]) / 30 if md in ev and m == md else -1
            key = None
            for md, at, lab in (('cave-enter', 0, 'enter'), ('cave-enter', .7, 'at the mouth'), ('cave-enter', 1.9, 'pushing in'),
                                ('fanning', 1.0, 'fan 1.0 s'), ('fanning', 1.1, 'fan 1.1 s'), ('fanning', 1.2, 'fan 1.2 s'), ('fanning', 1.3, 'fan 1.3 s'),
                                ('cave-guard', .5, 'guard (head out)'), ('cave-exit', 1.0, 'exit'), ('cave-turn', .27, 'turn (mid)'), ('cave-enter', 3.0, 're-entry')):
                if abs(dt(md) - at) < .017 and lab not in [t[1] for t in tiles] and (lab != 're-entry' or len(tiles) >= 10): key = lab
            if key and not os.environ.get('ZOOM'):
                p = os.path.join(os.path.dirname(GRID), '_c%02d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=max(0, r['L'] - 150), y=max(0, r['T0'] - 15), width=240, height=100, scale=2), q=90)
                tiles.append((p, key))
            if os.environ.get('ZOOM') and m == 'fanning' and 'fanning' in ev and i - ev['fanning'] >= 45 and len(tiles) < 12 and float(r['env'] or 0) > .9:
                p = os.path.join(os.path.dirname(GRID), '_c%02d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=r['L'] - 45, y=r['T0'] + 22, width=56, height=35, scale=4), q=92); tiles.append((p, '%.3f s  ph %s' % ((i - ev['fanning']) / 30, r['ph'])))
            if len(tiles) == (12 if os.environ.get('ZOOM') else 11): break
finally:
    pass
json.dump(R, open('D:/ClaudeWork/v106/rec.json', 'w'))
modes = {}; worst = []; swaps = 0; ovl = 0; last = None
for i, r in enumerate(R):
    if not r: last = None; continue
    if r['op'] < .99 or r['art'] < .99: swaps += 1
    ovl = max(ovl, r['ov'])
    if last and last['cen'] and r['cen']:
        d = math.hypot(r['cen'][0] - last['cen'][0], r['cen'][1] - last['cen'][1]); key = r['m'] if r['m'] == last['m'] else last['m'] + '>' + r['m']
        if d > modes.get(key, (0,))[0]: modes[key] = (round(d, 2), i)
    last = r
print('modes seen', sorted(set(r['m'] for r in R if r)))
for k, v in sorted(modes.items(), key=lambda kv: -kv[1][0]): print('  max drawn step %5.2f px/frame at %5d  %s' % (v[0], v[1], k))
print('frames with the element/drawing faded (model swapped):', swaps)
print('max fish px over the tube with no clip:', ovl)
cyc = [r for r in R if r and r['m'] == 'fanning' and r['env']]
if cyc: print('fanning frames %d, env min %.2f max %.2f' % (len(cyc), min(float(r['env']) for r in cyc), max(float(r['env']) for r in cyc)))
print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
if GRID and tiles:
    print('tiles', [t[1] for t in tiles])
    import base64
    imgs = ''.join('<div style="display:inline-block;margin:3px;text-align:center;font:600 13px system-ui;color:#fff"><img src="data:image/jpeg;base64,%s" style="width:228px;height:95px;display:block">%s</div>' % (base64.b64encode(open(p, 'rb').read()).decode(), t) for p, t in tiles)
    c.js("(h=>{const d=document.createElement('div');d.style.cssText='position:fixed;left:0;top:0;z-index:999999;background:#111;padding:5px;width:950px';d.innerHTML=h;document.body.appendChild(d);return 1})(%s)" % json.dumps(imgs))
    c.shot(GRID, clip=dict(x=0, y=0, width=960, height=12 + 3 * 121), q=88)
    for p, _ in tiles: os.remove(p)
    print('grid', GRID)
