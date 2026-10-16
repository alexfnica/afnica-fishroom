# V17.90 check: main tank 1 ready male + 2 females (throw-away headless game), console errors, stills over time.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
OUT = os.path.join(HERE, 'raw', 't90'); os.makedirs(OUT, exist_ok=True)
FISH = "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30)]"
ERR = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,300));_ce.apply(console,arguments)};1"
c = anc_game(tank='main', fish=FISH, warm=1, dsf=2, pre=ERR + ';')
try:
    for i, t in enumerate([2, 6, 10, 15, 20, 30, 40]):
        advance(c, t - ([0, 2, 6, 10, 15, 20, 30][i]))
        shot(c, os.path.join(OUT, 'main_%02ds.jpg' % t))
        print(t, 's', c.js(r"JSON.stringify([...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>[e.dataset.ancMode,e.dataset.ancSurface,e.classList.contains('anc90'),e.style.visibility||'',(/scaleX\(([^)]*)\)/.exec(e.style.transform)||[])[1]]))"),
              c.js("JSON.stringify([!!document.querySelector('#tank-main canvas.anc90cv'),document.getElementById('tank-main').className.includes('anc90cave')])"))
    print('errors', c.js("JSON.stringify(window.__err.slice(0,8))"))
finally: c.close()
