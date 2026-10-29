# V17.121 screen system: headless phone-size run (throw-away profile, save blocked). Opens every screen, saves one PNG per screen into docs/ui121_*.png
# and prints layout checks (page scroll, horizontal overflow, errors). Run: D:/Blender/5.2/python/bin/python.exe shot_ui121.py [width height]
import os, sys, time, json
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome
W = int(sys.argv[1]) if len(sys.argv) > 1 else 375
H = int(sys.argv[2]) if len(sys.argv) > 2 else 812
TAG = os.environ.get('TAG', 'ui121')
GAME = 'http://127.0.0.1:8791/AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html'
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'docs')
c = Chrome(W, H, 2, port=9355)
try:
    c.cmd('Page.navigate', url=GAME); c.wait_event('Page.loadEventFired', 120)
    c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};window.addEventListener('error',e=>window.__err.push('ERR '+e.message));1")
    for _ in range(80):
        if c.js("typeof calibV1773!=='undefined'"): break
        time.sleep(.5)
    time.sleep(2.5)
    c.js("window.save=()=>{};window.__afHourOverride=12;1")
    c.js("""(()=>{const mk=(sp,sex,age,id,fins)=>({id,name:id,species:sp,sex,age,genes:{color:92,pattern:82,fins,vitality:90,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0});
const a=tankArrayV14('main');a.length=0;a.push(mk('guppy','M',20,'g1',90),mk('guppy','F',20,'g2',80),mk('molly','M',30,'m1',90),mk('platy','F',24,'p1',85),mk('xipho','M',36,'x1',98));
st.coins=1240;st.playerLevel=4;st.xp=180;return 1})()""")
    CHECK = """(()=>{const s=document.getElementById('screen'),r=e=>{if(!e)return null;const b=e.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)]};
return JSON.stringify({cur:ui121Debug().cur,pageScrollY:document.documentElement.scrollHeight-innerHeight,pageScrollX:document.documentElement.scrollWidth-innerWidth,screenScroll:s.scrollHeight-s.clientHeight,screenScrollX:s.scrollWidth-s.clientWidth,tank:r(document.querySelector('.tank')),dock:r(document.querySelector('.v8dock')),errs:window.__err.slice(-4)})})()"""
    names = [('home', "u121go('home')"), ('tank', "u121go('tank')"), ('tank_fry', "switchTankV8('fry')"), ('breed_breeder', "u121go('breed')"),
             ('breed_fry', "u121breedTab('fry')"), ('breed_info', "u121breedTab('info')"), ('market', "u121go('market')"), ('dex', "u121go('dex')"),
             ('shop', "u121go('shop')"), ('store', "u121go('store')"), ('progress', "u121go('progress')"), ('settings', "u121go('settings')"),
             ('more', "u121nav('more')"), ('notes', "u121layer('notes')"), ('tank_sheet', "u121go('tank');u121sheet(true)")]
    only = os.environ.get('ONLY')
    for name, js in names:
        if only and name not in only.split(','): continue
        c.js(js); time.sleep(1.6)
        c.shot(os.path.join(OUT, '%s_%s.png' % (TAG, name)), fmt='png')
        print(name, c.js(CHECK))
finally:
    c.close()
