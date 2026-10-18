# Glass cut-off probe (2026-10-17): every 5th frame, for each visible anc canvas, count opaque pixels on its border
# (drawing clipped by its own canvas) and whether the fish box leaves the tank (clipped by the tank overflow).
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
P = r"""(()=>{const tk=document.getElementById('tank-main'),T=tk.getBoundingClientRect(),out=[];
 tk.querySelectorAll('[data-fish-id]').forEach((e,k)=>{const md=e.dataset.ancMode||'',gl=parseFloat(e.style.getPropertyValue('--anc-glass'))||0;
  for(const [nm,c] of [['side',e.querySelector('.ancSide>canvas')],['belly',e.querySelector('.ancGlass>canvas')],['t3',e.querySelector(':scope>canvas.anc94t')]]){
   if(!c||!c.width||getComputedStyle(c).visibility==='hidden'||getComputedStyle(c).display==='none')continue;
   const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,W=c.width,H=c.height;let b={t:0,b:0,l:0,r:0};
   for(let x=0;x<W;x++){if(d[x*4+3]>60)b.t++;if(d[((H-1)*W+x)*4+3]>60)b.b++;}for(let y=0;y<H;y++){if(d[y*W*4+3]>60)b.l++;if(d[(y*W+W-1)*4+3]>60)b.r++;}
   const r=c.getBoundingClientRect(),o=Math.max(0,T.left-r.left,r.right-T.right,T.top-r.top,r.bottom-T.bottom);
   if(b.t+b.b+b.l+b.r>0||o>2)out.push([k,md,nm,+gl.toFixed(2),b,Math.round(o)]);}});return JSON.stringify(out)})()"""
c = anc_game(tank='main', fish="[T.fish('anc','M',40),T.fish('anc','F',36),T.fish('anc','M',38)]", warm=1, pre=SEED % int(os.environ.get('SEED', '7')))
try:
    agg = {}
    for i in range(int(os.environ.get('SECS', '200')) * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30))
        if i % 10: continue
        for k, md, nm, gl, b, o in json.loads(c.js(P)):
            key = (md, nm, 'gl' if gl > .02 else 'sand'); a = agg.setdefault(key, [0, {'t': 0, 'b': 0, 'l': 0, 'r': 0}, 0])
            a[0] += 1; a[2] = max(a[2], o)
            for s in b: a[1][s] = max(a[1][s], b[s])
    for k, v in sorted(agg.items(), key=lambda x: -x[1][0]): print(k, 'samples', v[0], 'max opaque border px', v[1], 'max outside tank px', v[2])
finally: c.close()
