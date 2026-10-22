# V17.102 arc-turn probe: one fish on the sand (FID a1 = black male, a2 = olive male; SEX=F for a female), noon. Every
# ~6 s it is sent 120 px behind itself -> a 3D turn. Per frame, from the turn canvas (canvas.anc94t): shown?, drawn
# pixel centroid and the lowest opaque row (belly / fin line) in page px; from the fish box: x. Reports per turn: duration,
# max centroid step per frame, the belly line's range (no lift = it stays put), backward frames (drawn x moving against the
# facing), errors. Shots every 2nd frame of the first turn (+6 frames before/after) -> grid.
# Run: D:/Blender/5.2/python/bin/python.exe probe_turn102.py <out.jpg>   (env FID, SEX, SECS, AF_PORT)
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anc_rig import *
OUT = sys.argv[1]; FID = os.environ.get('FID', 'a1'); SECS = int(os.environ.get('SECS', '40'))
FISH = "[{id:'%s',name:'%s',species:'anc',sex:'%s',age:36,genes:{color:92,pattern:82,fins:90,vitality:90,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0}]" % (FID, FID, os.environ.get('SEX', 'M'))
HOOK = r"""window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};
window.__S=new WeakMap();setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1;"""
ST = r"""(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e)||{},t=e.querySelector(':scope>canvas.anc94t'),r=e.getBoundingClientRect();
 let c=null;if(t&&t.style.display!=='none'){const d=t.getContext('2d').getImageData(0,0,t.width,t.height).data;let sx=0,sy=0,sw=0,lo=-1,xl=1e9,xr=-1;
  for(let y=0;y<t.height;y++)for(let x=0;x<t.width;x+=2){const a=d[(y*t.width+x)*4+3];if(a>0){sx+=x*a;sy+=y*a;sw+=a;}if(a>160){lo=Math.max(lo,y);xl=Math.min(xl,x);xr=Math.max(xr,x);}}
  if(sw>2000){const q=t.getBoundingClientRect(),m=getComputedStyle(e).transform,neg=/matrix\(-/.test(m)||(e.style.transform||'').includes('scaleX(-1)');
   const fx=sx/sw/t.width,fy=sy/sw/t.height;c=[+(q.left+(neg?1-fx:fx)*q.width).toFixed(2),+(q.top+fy*q.height).toFixed(2),+(q.top+lo/t.height*q.height).toFixed(2),Math.round(sw/1000),+(q.left+(neg?1-xr/t.width:xl/t.width)*q.width).toFixed(1),+(q.left+(neg?1-xl/t.width:xr/t.width)*q.width).toFixed(1)];}}
 const T=document.getElementById('tank-main').getBoundingClientRect();return JSON.stringify({tl:T.left,tr:T.right,x:+(r.left+r.width/2).toFixed(2),mode:s.mode,face:s.face<0?-1:1,turn:!!s.turn,c});})()"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=HOOK)
TMP = os.path.join(os.path.dirname(OUT) or '.', 'turn102_shots'); os.makedirs(TMP, exist_ok=True)
for f in os.listdir(TMP): os.remove(os.path.join(TMP, f))
try:
    L = []; shots = []; first = None
    for i in range(SECS * 30):
        if os.environ.get('WALL') and i == 1: c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e),W=document.getElementById('tank-main').clientWidth;if(s){s.mode='toWall';s.wall=1;s.wait=0;}return 1})()")
        if os.environ.get('WALL') and i % 180 == 30 and i > 200: c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e),W=document.getElementById('tank-main').clientWidth;if(s){s.x=W-70;s.face=1;s.fv=1;s.mode='move';s.tx=W-200;s.ty=s.y;s.wait=0;s.dk95=s.tx;s.force95=null;s.fg=null;}return 1})()"); continue
        if i % 180 == 30 and not os.environ.get('WALL'):
            c.js(r"""(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e);if(!s||s.mode==='rest'&&s.wait>100)return 0;const W=document.getElementById('tank-main').clientWidth;
              let tx=s.x-(s.face<0?-1:1)*120;if(tx<90||tx>W-90)tx=s.x+(s.face<0?-1:1)*120;s.mode='move';s.tx=tx;s.ty=s.y;s.wait=0;s.dk95=tx;s.force95=null;s.fg=null;return 1})()""")
        c.js('__afStep(%f, 2)' % (1000 / 30)); r = json.loads(c.js(ST)); L.append(r)
        if r['c'] and first is None: first = i
        if first is not None and (i - first) % 2 == 0 and -8 <= i - first < 76 and len(shots) < 38:
            p = os.path.join(TMP, '%05d.jpg' % i); CL = CL if shots else dict(x=max(0, r['x'] - 110), y=max(0, (r['c'][1] if r['c'] else 480) - 60), width=220, height=100, scale=2); c.shot(p, clip=CL, q=88); shots.append(p)
    err = c.js('JSON.stringify(window.__err.slice(0,5))')
finally: c.close()
turns = []; cur = None
for i, r in enumerate(L):
    if r['c'] and cur is None: cur = [i]
    if not r['c'] and cur is not None: cur.append(i); turns.append(cur); cur = None
print('turns', len(turns), [round((b - a) / 30, 2) for a, b in turns])
for a, b in turns:
    cs = [L[i]['c'] for i in range(a, b)]; st = max(((cs[j][0] - cs[j - 1][0]) ** 2 + (cs[j][1] - cs[j - 1][1]) ** 2) ** .5 for j in range(1, len(cs)))
    lows = [x[2] for x in cs[3:-3]]
    ov = max(max((L[i]['c'][5] - L[i]['tr']) for i in range(a, b)), max((L[i]['tl'] - L[i]['c'][4]) for i in range(a, b)))
    print('  past the glass by %.1f px max' % ov)
    print('  turn %d-%d: max 3D centroid step %.2f px/frame, belly line %.1f..%.1f (range %.1f), x drift start->end %.1f, fwd reach %.1f' % (a, b, st, min(lows), max(lows), max(lows) - min(lows), cs[-1][0] - cs[0][0], max(abs(x[0] - cs[0][0]) for x in cs)))
mx = 0; back = 0; mv = 0
for i in range(1, len(L)):
    d = L[i]['x'] - L[i - 1]['x']
    if abs(d) > mx and not L[i]['c']: mx = abs(d)
    if abs(d) > .2 and not L[i]['turn']: mv += 1; back += (d > 0) != (L[i]['face'] > 0)
print('photo max step outside turns %.2f px/frame, backward %d of %d moving frames, errors %s' % (mx, back, mv, err))
if shots:
    subprocess.run([r'D:\Blender\blender.exe', '-b', '--python', r'D:\ClaudeWork\scratch101\grid101.py', '--', OUT, '8', '.5'] + shots[::2][:24], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('grid', OUT, os.path.exists(OUT))
