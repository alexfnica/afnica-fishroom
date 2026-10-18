# Bristlenose diagnosis (owner's 7 points, 2026-10-17): headless main tank, fake 30 fps clock, the owner's save never touched.
# Per frame and fish: the DRAWN position (centre of the visible drawing: side photo, belly photo or 3D turn canvas), mode,
# glass, facing sign, which drawing is showing. Reports the max drawn step per frame in each mode change window (sand ->
# glass, cave approach/enter), how every facing change was drawn (3D turn frames or an instant flat flip), fight rotations.
# Run: D:/Blender/5.2/python/bin/python.exe measure_diag99.py   (env SCN=cave|fight, SECS, SEED)
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
SCN = os.environ.get('SCN', 'cave'); SECS = int(os.environ.get('SECS', '240'))
FISH = {"cave": "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','M',38)]",
        "fight": "[T.fish('anc','M',40),T.fish('anc','M',38)]", "cave2": "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36)]"}[SCN]
HOOK = r"""window.__S=new WeakMap();window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};
 setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1;"""
REC = r"""(()=>{const T=document.getElementById('tank-main').getBoundingClientRect();const F=anc90Debug().F96['tank-main'];
 const D=anc90Debug(),tk=document.getElementById('tank-main'),tm=D.TK.get(tk),m=tm&&tm.m;let cvp=null;
 if(m&&m.name&&window.__CV){const A=D.ATL.C2;window.__CC=window.__CC||{};const cc=n=>{if(n in __CC)return __CC[n];const p=A.pos[n];if(!p)return __CC[n]=null;const w=A.idx.w,h=A.idx.h,c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.drawImage(A.img,p[0],p[1],w,h,0,0,w,h);
   const d=g.getImageData(0,0,w,h).data;let sx=0,sy=0,sw=0;for(let y=0;y<h;y+=2)for(let x=0;x<w;x+=2){const a=d[(y*w+x)*4+3];if(a>40){sx+=x*a;sy+=y*a;sw+=a;}}return __CC[n]=sw?[sx,sy,sw]:null;};
  const parts=[cc(m.name+'_in'),cc(m.name+'_out')].filter(Boolean);const sw=parts.reduce((t,q)=>t+q[2],0);
  const cv=tk.querySelector('canvas.anc90cv.front');
  if(sw&&cv){const L=parseFloat(cv.style.left),Tp=parseFloat(cv.style.top);cvp=[L+(parts.reduce((t,q)=>t+q[0],0)/sw+m.shift)/2,Tp+(parts.reduce((t,q)=>t+q[1],0)/sw+(m.dy||0))/2,m.name,+m.a.toFixed(2)];}}
 const cen=e=>{if(!e)return null;const r=e.getBoundingClientRect();return r.width?[r.left+r.width/2-T.left,r.top+r.height/2-T.top]:null};
 return JSON.stringify({cv:cvp,f:F?[F.ph,F.cur||'',F.n]:null,fish:[...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>{const s=__S.get(e)||{};
  const t3=e.querySelector(':scope>canvas.anc94t'),on3=t3&&t3.style.display==='block',sop=parseFloat(e.style.getPropertyValue('--anc-sop')||'1');
  const vis=on3?'3d':(parseFloat(e.style.opacity||'1')<.5?'cave':sop>=.5?'side':'glass');
  const cv=on3?t3:vis==='side'?e.querySelector('.ancSide>canvas'):null,mir=/scaleX\(-/.test(e.style.transform||'');
  const pc=(()=>{if(!cv||!cv.width||!window.__PC)return null;const r=cv.getBoundingClientRect();if(!r.width)return null;const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;let sx=0,sy=0,sw=0;
   for(let y=0;y<cv.height;y+=3)for(let x=0;x<cv.width;x+=3){const a=d[(y*cv.width+x)*4+3];if(a>40){sx+=x*a;sy+=y*a;sw+=a;}}if(!sw)return null;
   const u=sx/sw/cv.width,v=sy/sw/cv.height;return [r.left-T.left+(mir?1-u:u)*r.width,r.top-T.top+v*r.height];})();
  const p=pc||(on3?cen(t3):vis==='side'?cen(e.querySelector('.ancSide')):vis==='glass'?cen(e.querySelector('.ancGlass')):null);
  const tr=e.style.transform||'',m=/scaleX\(([-\d.e]+)\)/.exec(tr),ro=/rotate\(([-\d.e]+)deg\)/.exec(tr);
  return [p,e.dataset.ancMode||'',vis,m&&+m[1]<0?-1:1,ro?+ro[1]:0,s.dart95?1:0,+e.dataset.ancX,+e.dataset.ancY]})})})()"""
pre = ('window.__CV=1;' if os.environ.get('CV') else '') + ('window.__PC=1;' if os.environ.get('PC') else '') + HOOK + (SEED % int(os.environ.get('SEED', '7')))
c = anc_game(tank='main', fish=FISH, warm=1, pre=pre)
try:
    L = []
    for i in range(SECS * 30):
        if SCN == 'fight' and i % (40 * 30) == 30: c.js('window.anc96Force=1')
        c.js('__afStep(%f, 2)' % (1000 / 30)); L.append(json.loads(c.js(REC)))
    n = len(L[0]['fish'])
    for k in range(n):
        worst = {}; flips = {'3d': 0, 'flat': 0}; flat_at = {}; rot = 0
        for i in range(1, len(L)):
            a, b = L[i - 1]['fish'][k], L[i]['fish'][k]
            if b[3] != a[3]:
                near3 = any(L[j]['fish'][k][2] == '3d' for j in range(max(0, i - 3), min(len(L), i + 3)))
                key = '3d' if near3 else 'flat'; flips[key] += 1
                if not near3: flat_at[b[1] + '/' + b[2] + ('/tilt' if abs(b[4]) > 10 else '')] = flat_at.get(b[1] + '/' + b[2] + ('/tilt' if abs(b[4]) > 10 else ''), 0) + 1
            if b[5] or not a[0] or not b[0] or not os.environ.get('PC') and '3d' in (a[2], b[2]): continue   # the 3D canvas box differs from the photo box
            d = math.hypot(b[0][0] - a[0][0], b[0][1] - a[0][1])
            tag = a[1] if a[1] == b[1] else a[1] + '>' + b[1]
            if a[2] != b[2]: tag += ' [' + a[2] + '>' + b[2] + ']'
            if d > worst.get(tag, (0,))[0]: worst[tag] = (round(d, 1), i, round(abs(b[7] - a[7]), 1))
        print('fish %d facing changes: %s; flat flips by mode/view: %s' % (k, flips, flat_at))
        for tag, v in sorted(worst.items(), key=lambda x: -x[1][0])[:8]:
            print('   max drawn step %5.1f px/frame (logic y step %4.1f) at frame %d  %s' % (v[0], v[2], v[1], tag))
    if os.environ.get('CV'):
        mx = (0,); prev = None; ph = None
        for i, r in enumerate(L):
            cv = r['cv']; fm = r['fish'][0]
            if cv and prev: 
                d = math.hypot(cv[0] - prev[0], cv[1] - prev[1])
                if d > mx[0]: mx = (round(d, 1), i, prev[2] + '>' + cv[2], fm[1])
                if d > 4: print('  cave jump %.1f px frame %d %s>%s mode %s a %.2f' % (d, i, prev[2], cv[2], fm[1], cv[3]))
            if cv and fm[0] and 0 < cv[3] < 1: ph = max(ph or 0, math.hypot(cv[0] - fm[0][0], cv[1] - fm[0][1]))
            if cv and fm[0] and 0 < cv[3] < 1 and os.environ.get('XF'): print('  xfade frame %d a %.2f photo-cave dx %.1f dy %.1f  %s %s' % (i, cv[3], fm[0][0] - cv[0], fm[0][1] - cv[1], cv[2], fm[1]))
            prev = cv
        print('cave male (cave canvas) max centroid step %s ; photo vs cave-frame offset during the cross-fade max %s px' % (mx, ph and round(ph, 1)))
    if SCN == 'fight':
        seq = [r['f'] for r in L if r['f']]
        print('fight phases seen:', sorted(set((x[0], x[1][:1]) for x in seq)))
        # walk phase: how many facing changes each male made while walking into the fight
        for k in range(2):
            ch = sum(1 for i in range(1, len(L)) if L[i]['f'] and L[i]['f'][0] == 'walk' and L[i]['fish'][k][3] != L[i - 1]['fish'][k][3])
            print('male %d facing changes during fight walk-ins: %d' % (k, ch))
    print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
finally: c.close()
