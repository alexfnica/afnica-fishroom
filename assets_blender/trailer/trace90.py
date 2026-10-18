# Who moves a grazing female backwards? Seed 3, frames 700-820: trap writes that move s.x against the facing, log the stack.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30)]"
HOOK = r"""window.__S={};window.__T=[];(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s,f){if(f)window.__S[f.id]=s;return p.apply(this,arguments)}})();1"""
TRAP = r"""((id)=>{const s=window.__S[id];if(!s)return 0;let x=s.x;Object.defineProperty(s,'x',{get(){return x},set(v){const f=s.face<0?-1:1;
 if((v-x)*f<-.2&&window.__T.length<14)window.__T.push([id,+(v-x).toFixed(2),s.mode,s.surface,f,(new Error()).stack.split('\n').slice(2,5).map(l=>l.trim().slice(0,110)).join(' | ')]);x=v},configurable:true});return 1})(%s)"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=SEED % 3)
try:
    c.js(HOOK)
    for i in range(700): c.js('__afStep(%f, 2)' % (1000 / 30))
    ids = json.loads(c.js("JSON.stringify(tankArrayV14('main').map(f=>f.id))"))
    print('trapped', [c.js(TRAP % json.dumps(fid)) for fid in ids[1:]])
    for i in range(120): c.js('__afStep(%f, 2)' % (1000 / 30))
    for t in json.loads(c.js("JSON.stringify(window.__T)")): print(t)
finally: c.close()
