# Cave frame registration (2026-10-18): alpha centroid (2x canvas px) of the male's in+out layers for every walk-in
# frame C2_i (depth q) and the fanning frames C2_f, so the depth where the walk-in pose matches the fanning pose is known.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
P = r"""(()=>{const A=anc90Debug().ATL.C2,w=A.idx.w,h=A.idx.h,res={};
 const cc=n=>{const p=A.pos[n];if(!p)return null;const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.drawImage(A.img,p[0],p[1],w,h,0,0,w,h);
  const d=g.getImageData(0,0,w,h).data;let sx=0,sy=0,sw=0,x0=1e9,x1=-1;for(let y=0;y<h;y+=2)for(let x=0;x<w;x+=2){const a=d[(y*w+x)*4+3];if(a>40){sx+=x*a;sy+=y*a;sw+=a;if(x<x0)x0=x;if(x>x1)x1=x;}}return [sx,sy,sw,x0,x1];};
 for(const n of A.idx.names){const m=/^(C2_[io][+-]\d{3}|C2_f\d\d)_out$/.exec(n);if(!m)continue;const a=cc(m[1]+'_out'),b=cc(m[1]+'_in');const q=[a,b].filter(Boolean),sw=q.reduce((t,v)=>t+v[2],0);
  res[m[1]]=sw?[+(q.reduce((t,v)=>t+v[0],0)/sw).toFixed(1),+(q.reduce((t,v)=>t+v[1],0)/sw).toFixed(1),Math.min(...q.map(v=>v[3])),Math.max(...q.map(v=>v[4]))]:null;}
 return JSON.stringify(res)})()"""
c = anc_game(tank='main', fish="[T.fish('anc','M',40)]", warm=1)
try:
    for i in range(20):
        if c.js("(()=>{const A=anc90Debug().ATL.C2;return A.img.complete&&A.img.naturalWidth>0})()"): break
        c.js('__afStep(100, 1)')
    r = json.loads(c.js(P))
    f = [v for k, v in r.items() if k.startswith('C2_f') and v]
    print('fan frames: centroid x %.1f..%.1f  y %.1f..%.1f  (mean %.1f, %.1f)' % (min(v[0] for v in f), max(v[0] for v in f), min(v[1] for v in f), max(v[1] for v in f), sum(v[0] for v in f) / len(f), sum(v[1] for v in f) / len(f)))
    for k in sorted(r):
        if k.startswith('C2_i') and r[k] and 40 <= int(k[4:]) <= 120: print(k, r[k])
finally: c.close()
