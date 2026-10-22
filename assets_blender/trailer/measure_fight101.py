# V17.101 head-to-head male fight: headless main tank, 2 adult males, no female, noon, fake 30 fps clock; a new fight is
# forced whenever none is running (anc96Force + cooldown cleared). Reports per fight: how it ended, walk / 3D length,
# rounds (holds, whirls); per frame: the photo x step of each fish outside darts, backward frames (moving against the
# drawn facing), the 3D pair's pixel centroid step, photo opacity under the 3D, errors. Shots every 0.5 s of the first
# fight that ends "done" (+2 s after) go to raw/fight101/ for the grid.
# Run: D:/Blender/5.2/python/bin/python.exe measure_fight101.py   (env SEED, SECS, AF_PORT)
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = os.environ.get('FISH') or "[T.fish('anc','M',40),T.fish('anc','M',38)]"
SECS = int(os.environ.get('SECS', '150'))
DIRN = 1 if os.environ.get('LEFT') == 'R' else -1   # LEFT=1: both face left first; LEFT=R: both face right
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw', os.environ.get('OUTN', 'fight101')); os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
HOOK = r"""window.__S=new WeakMap();window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};
 window.__ends=[];setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1;"""
REC = r"""(()=>{const D=anc90Debug(),F=D.F96['tank-main'];const L=window.__f96last;if(L&&!L.logged){L.logged=1;__ends.push([L.end,L.n,+L.t.toFixed(1),L.ph,L.T?+L.T.toFixed(1):0,L.q?L.q.filter(e=>e.ph==='H').length:0,L.q?L.q.filter(e=>e.ph==='W').length:0,L.sg||0]);}
 if(!F&&L&&L.end==='done')window.__hold=1;if(!F&&!window.__hold){for(const k in D.CD96)delete D.CD96[k];window.anc96Force=1;}
 let cen=null;const cv=document.querySelector('#tank-main canvas.anc96p');
 if(cv&&F&&F.ph==='fight'){const CW=cv.width,d=cv.getContext('2d').getImageData(0,0,CW,260).data;let sx=0,sy=0,sw=0;for(let y=0;y<260;y+=2)for(let x=0;x<CW;x+=2){const a=d[(y*CW+x)*4+3];if(a>0){sx+=x*a;sy+=y*a;sw+=a;}}
  if(sw){const r=cv.getBoundingClientRect(),cx=sx/sw,cy=sy/sw;cen=[+(r.left+((F.sg||1)>0?cx:CW-cx)/CW*r.width).toFixed(2),+(r.top+cy/260*r.height).toFixed(2)];}}
 const box=[...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>{const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];});
 return JSON.stringify({f:F?[F.ph,F.cur||'',F.n,+F.t.toFixed(2)]:null,cen,box,fish:[...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>{const s=__S.get(e)||{},a=e.querySelector('.ancArt');
 return [+e.dataset.ancX,e.dataset.ancMode,s.dart95?1:0,a&&a.style.opacity!==''?+a.style.opacity:1,s.face<0?-1:1,!!s.turn]})})})()"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=HOOK + (SEED % int(os.environ['SEED']) if os.environ.get('SEED') else '1;'))
try:
    L = []; shoot = None; shots = 0; done_n = None
    for i in range(SECS * 30):
        if os.environ.get('LEFT') and i == 0: c.js('window.__hold=1')   # LEFT=1: both males walk left first, so the pair faces left (mirrored canvas)
        if os.environ.get('LEFT') and i >= 5 and i % 120 == 5 and c.js('window.__hold?1:0'):   # nudge both left until both face left and are still, then let the fight start
            st = json.loads(c.js("JSON.stringify([...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>{const s=__S.get(e)||{};return [s.face,s.mode,!!s.turn]}))"))
            if all(x[0] is not None and x[0] * DIRN > 0 and x[1] in ('rest', 'graze') and not x[2] for x in st): c.js('window.__hold=0')
            else: c.js("document.querySelectorAll('#tank-main [data-fish-id]').forEach(e=>{const s=__S.get(e);if(s&&!(s.face*%d>0)){s.mode='move';s.tx=Math.min(880,Math.max(80,s.x+%d*120));s.ty=s.y;s.wait=0;s.dk95=s.tx;s.force95=null;s.fg=null;}})" % (DIRN, DIRN))
        c.js('__afStep(%f, 2)' % (1000 / 30)); r = json.loads(c.js(REC)); L.append(r)
        if done_n is None and r['f'] and shoot is None: shoot = r['f'][2]
        if shoot is not None and i % 15 == 0 and (r['f'] and r['f'][2] == shoot or done_n == shoot and i < end_i + 150):
            bx = r['box']; cx = sum(b[0] for b in bx) / len(bx); cy = sum(b[1] for b in bx) / len(bx)
            c.shot(os.path.join(OUT, '%05d.jpg' % i), clip={'x': min(max(cx - 200, 0), VW - 400), 'y': min(max(cy - 100, 0), VH - 170), 'width': 400, 'height': 170, 'scale': 1}, q=88); shots += 1
        if shoot is not None and done_n is None and not r['f']:
            ends = json.loads(c.js('JSON.stringify(__ends)'))
            e = [x for x in ends if x[1] == shoot]
            if e and e[0][0] == 'done': done_n = shoot; end_i = i; c.js('window.__hold=1')
            elif e: shoot = None; [os.remove(os.path.join(OUT, f)) for f in os.listdir(OUT)]
        if done_n is not None and i > end_i + 150: break
    json.dump(L, open(os.path.join(OUT, 'log.json'), 'w'))
    fights = {}
    for r in L:
        if r['f']: fights.setdefault(r['f'][2], []).append(r['f'][0])
    print('fights %d, shots %d (fight %s)' % (len(fights), shots, done_n))
    for n, ph in fights.items(): print('  fight %d: walk %.1f s, 3D %.1f s' % (n, ph.count('walk') / 30, ph.count('fight') / 30))
    print('ends [why, n, t, ph, T, holds, whirls, sg]', c.js('JSON.stringify(__ends)'))
    for k in range(len(L[0]['fish'])):
        mx = 0; at = None; back = 0; mv = 0
        for i in range(1, len(L)):
            a, b = L[i - 1]['fish'][k], L[i]['fish'][k]
            if b[2] or a[1] != b[1] and 'cave' in (a[1] + b[1]) or min(a[3], b[3]) < .05: continue   # dart, cave, or photo not visible
            d = b[0] - a[0]
            if abs(d) > mx: mx, at = abs(d), (i, a[1], b[1])
            if abs(d) > .2 and not b[5]: mv += 1; back += (d > 0) != (b[4] > 0)
        print('fish %d max photo step outside darts %.2f px/frame at %s | backward %d of %d moving frames' % (k, mx, at, back, mv))
    mx = 0; at = None; op = 0
    for i in range(1, len(L)):
        a, b = L[i - 1], L[i]
        if b['f'] and b['f'][0] == 'fight': op = max(op, max(x[3] for x in b['fish'])) if .5 < b['f'][3] < 15 else op
        if a['cen'] and b['cen'] and a['f'][2] == b['f'][2]:
            d = ((b['cen'][0] - a['cen'][0]) ** 2 + (b['cen'][1] - a['cen'][1]) ** 2) ** .5
            if d > mx: mx, at = d, (i, a['f'][1], b['f'][1])
    print('3D pair centroid max step %.2f px/frame at %s | max photo opacity in the 3D middle %.2f' % (mx, at, op))
    print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
finally: c.close()
