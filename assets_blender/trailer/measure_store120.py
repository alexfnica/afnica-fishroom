# V17.120 fish store: headless run on the fake clock (never the owner's save). Builds a test stock, runs the store for N simulated seconds and
# reports sales, coins, customers, jumps (> 12 units per 40 ms step), min distance between customers, errors.
# Run: D:/Blender/5.2/python/bin/python.exe measure_store120.py [seconds]
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from scene import open_game
SEC = int(sys.argv[1]) if len(sys.argv) > 1 else 300
PRE = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};"
SETUP = PRE + """(()=>{window.dispatchEvent(new Event('pointerdown'));window.__afHourOverride=12;
const mk=(sp,sex,age,id,g,fins)=>({id,name:id,species:sp,sex,age,genes:{color:g,pattern:g,fins:g,vitality:g,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0,finTorn:fins||0});
const a=tankArrayV14('main');a.length=0;
a.push(mk('guppy','M',40,'g1',70),mk('molly','F',60,'m1',88),mk('platy','M',50,'p1',95),mk('neon','F',40,'n1',80,2),mk('xipho','M',70,'x1',65),mk('cory','F',60,'c1',90),mk('anc','M',60,'a1',85));
ensureHealthState();['g1','m1','p1','n1','x1','c1','a1'].forEach(id=>{stStock120(id);stPrice120(id,-%d)});
st.coins=300;renderStoreV120();window.__c0=st.coins;window.__minD=999;window.__jump=0;window.__maxN=0;window.__prev=new Map();window.__states={};return 1})()"""
PCT = int(os.environ.get('PCT', '10'))
c = open_game(960, 640, 1, port=int(os.environ.get('AF_PORT', '9333')))
try:
    c.js(SETUP % PCT)
    print("stocked", c.js("st.storeFish.length"), c.js("typeof storeDebugV120"), c.js("JSON.stringify(window.__err)"))
    TRACK = """(()=>{const d=storeDebugV120(),C=d.S.cust;window.__maxN=Math.max(__maxN,C.length);
for(const c of C){const p=__prev.get(c.id);if(p&&c.alpha>0){const j=Math.hypot(c.x-p.x,c.y-p.y);if(j>__jump)__jump=j;}__prev.set(c.id,{x:c.x,y:c.y});__states[c.state]=(__states[c.state]||0)+1}
for(let i=0;i<C.length;i++)for(let j=i+1;j<C.length;j++){const q=Math.hypot(C[i].x-C[j].x,(C[i].y-C[j].y)*1.4);if(q<__minD)__minD=q}return 1})()"""
    for i in range(SEC * 25):
        c.js('__afStep(40, 1)')
        if i % 2 == 0: c.js(TRACK)
    r = json.loads(c.js("JSON.stringify({sales:st.store.day.sales,rev:st.store.day.revenue,cust:st.store.day.customers,walk:st.store.day.walkouts,rep:st.store.rep,coins:st.coins-__c0,left:st.storeFish.length,maxN:__maxN,maxJump:+__jump.toFixed(1),minDist:+__minD.toFixed(1),states:__states,err:__err})"))
    print(json.dumps(r))
finally:
    c.close()
