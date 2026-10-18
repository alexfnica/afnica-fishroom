# Sand -> glass roll check (2026-10-17): force one climb onto the front pane and log, per frame, --anc-glass, the computed
# opacity of the side and belly elements and which canvases are visible, plus the pixel centroid of the visible canvas.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
HOOK = r"""window.__S=new WeakMap();setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1;"""
P = r"""(()=>{const tk=document.getElementById('tank-main'),T=tk.getBoundingClientRect(),e=tk.querySelector('[data-fish-id]'),s=__S.get(e);
 const sd=e.querySelector('.ancSide'),gl=e.querySelector('.ancGlass'),sc=sd&&sd.querySelector('canvas'),gc=gl&&gl.querySelector('canvas');
 const cen=c=>{if(!c||!c.width)return null;const r=c.getBoundingClientRect(),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let sx=0,sy=0,sw=0;
  for(let y=0;y<c.height;y+=2)for(let x=0;x<c.width;x+=2){const a=d[(y*c.width+x)*4+3];if(a>3){sx+=x*a;sy+=y*a;sw+=a;}}if(!sw)return null;
  /* rotated element: map through the canvas box only roughly (box centre + offset of the centroid from the canvas centre is not rotated) */
  return [Math.round(r.left-T.left+r.width/2),Math.round(r.top-T.top+r.height/2),Math.round(sw/1000)];};
 const op=x=>x?+(+getComputedStyle(x).opacity).toFixed(2):null,vi=x=>x?getComputedStyle(x).visibility[0]:'-';
 return JSON.stringify([s&&s.mode,+(parseFloat(e.style.getPropertyValue('--anc-glass'))||0).toFixed(3),op(sd),vi(sc),op(gl),vi(gc),gl&&gl.classList.contains('gOn')?1:0,cen(sc),cen(gc),+(+e.dataset.ancX).toFixed(1),+(+e.dataset.ancY).toFixed(1)])})()"""
c = anc_game(tank='main', fish="[T.fish('anc','F',36)]", warm=1, pre=HOOK + SEED % 7)
try:
    c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e);s.mode='toWall';s.wall=s.x<480?-1:1;s.transition=null;s.wait=0;return 1})()")
    seen = False; n = 0
    for i in range(40 * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30)); r = json.loads(c.js(P))
        if r[0] == 'attach' or (seen and n < 12):
            if r[0] != 'attach': n += 1
            seen = True
            if i % 3 == 0 or .3 < r[1] < 1: print(i, r)
        if seen and n >= 12: break
finally: c.close()
