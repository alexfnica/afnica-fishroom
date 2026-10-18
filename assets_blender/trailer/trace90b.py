# Seed 3, frames 740-790: old facing (s.face) vs V17.90 drawn yaw, transform string, x, mode - for each fish.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30)]"
HOOK = r"""window.__S={};(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s,f){if(f)window.__S[f.id]=s;return p.apply(this,arguments)}})();1"""
REC = r"""JSON.stringify([...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>{const s=window.__S[e.dataset.fishId]||{},f=anc90Debug().ST.get(e)||{};
 return [e.dataset.fishId.slice(-3),s.face,f.a,f.turn?1:0,(+e.dataset.ancX).toFixed(1),s.x!=null?s.x.toFixed(1):null,e.dataset.ancMode,(/scaleX\([^)]*\)/.exec(e.style.transform)||[''])[0]]}))"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=SEED % 3)
try:
    c.js(HOOK)
    for i in range(1, 800):
        c.js('__afStep(%f, 2)' % (1000 / 30))
        if 752 <= i <= 768 and i % 2 == 0: print(i, c.js(REC))
finally: c.close()
