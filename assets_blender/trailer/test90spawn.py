# V17.90: during a spawning visit in the breeder the old drawing comes back (no 3D tube, no hidden fish); after it, 3D again.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import CLUTCH, PHASE
ERR = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,300));_ce.apply(console,arguments)};1"
STATE = r"""JSON.stringify((()=>{const t=document.getElementById('tank-breeder');return {ph:(st.ancClutch||{}).stage+'/'+(st.ancClutch||{}).phase,cv:!!t.querySelector('canvas.anc90cv'),cls:['anc90on','anc90cave'].filter(c=>t.classList.contains(c)),
 fish:[...t.querySelectorAll('[data-fish-id]')].map(e=>[e.dataset.ancMode,e.classList.contains('anc90')?'3d':'old',getComputedStyle(e).opacity])}})())"""
c = anc_game(pre=ERR + ';')
try:
    m, f = ids(c)
    print('before', c.js(STATE))
    c.js(CLUTCH % dict(stage='spawning', phase='male-approach', laid=0, hatch=5, rel=10))
    c.js("(()=>{let n=0;setInterval(()=>{const c=st.ancClutch;if(c&&c.phase==='trapped'&&++n>40)c.trapDays=0},250);return 1})()")
    for i in range(8):
        advance(c, 6); print(i * 6 + 6, 's', c.js(STATE))
    shot(c, os.path.join(HERE, 'raw', 't90', 'spawn_end.jpg'))
    print('errors', c.js("JSON.stringify(window.__err.slice(0,6))"))
finally: c.close()
