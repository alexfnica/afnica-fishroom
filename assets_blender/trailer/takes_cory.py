# Raw takes for the corydoras mini-story clip "They EAT their own eggs" (same rig as takes_xipho.py / takes_molly.py:
# throw-away game, tank built in memory, behaviour triggered, virtual camera). Timeline: timeline_cory.py.
# Run: python takes_cory.py <take> [...]   (frames go to raw/<take>/)
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
from takes_molly import game, run, Cam, full, VW, VH, advance, QUIET_LOOP
import takes as _tk

AD, FULL = 20, 40                                   # S.cory.adult = 14: adult photo 14-30, full grown from 31
def C(sex, age, extra=None):
    o = {'genes': dict(color=90, pattern=85, fins=88, vitality=92, mutation=None)}; o.update(extra or {})
    return "T.fish('cory','%s',%d,%s)" % (sex, age, json.dumps(o))
def ids_of(c, k='main'): return json.loads(c.js("JSON.stringify(tankArrayV14('%s').map(f=>String(f.id)))" % k))

# the ritual's state for the phase log (compose.py turns the first frame of each phase into an event)
PH_RIT = "(()=>{const R=coryRitualDebugV1781().R;return R?{phase:R.phase,t:+R.t.toFixed(2),round:R.round}:null})()"
FEM = "(()=>{const R=coryRitualDebugV1781().R;return R?R.fem:null})()"
NOLIVE = "st.liveFood=null;"                        # no live-food worms drifting through the takes
HIDEUI = "(()=>{const s=document.createElement('style');s.textContent='.liveBtn82,.coryEggBtn81,.box86Btn,.waferBtn43,.toast,#toast{display:none!important}';document.head.appendChild(s)})();"
# filming only: light sand and a taller floor (corydoras live on the bottom; the camera needs ground under them),
# set before the fish are placed so their sand line follows it
PRE = NOLIVE + HIDEUI + "st.scapes=st.scapes||{};st.scapes.main=st.scapes.main||{};st.scapes.main.ground='sand';(()=>{const s=document.createElement('style');s.textContent='#tank-main .floor{height:170px!important}';document.head.appendChild(s)})();"

def ritual_game(fish, warm=3):
    c = game(PRE + "T.tank('main',[%s])" % ','.join(fish), warm=warm, dof=4)
    c.js("st.soundOn=false;st.corySpawn=null;st.coryEggs81=[];1")
    return c

def start_ritual(c, rounds=2, hard=False):
    c.js("(()=>{coryRitualV1781.start();const R=coryRitualDebugV1781().R;if(!R)return 0;R.rounds=%d;R.breaks=[];return 1})()" % rounds)
    if hard:      # filming only: every lay after the first goes on wood or stone
        c.js("setInterval(()=>{const R=coryRitualDebugV1781().R;if(R&&R.phase==='part'&&R.round>0){R.useHard=true;R.useLeaf=false;R.hardUsed=false;}},100);1")
    fem = c.js(FEM); print('ritual female', fem); return fem

def fem_cam(c, fem, dy=0):
    def tgt(i):
        b = c.js("CAM.box(['%s'])" % fem)
        if b: b = dict(b); b['y'] += dy
        return b
    return tgt

def wait_phase(c, name, limit=120, step=.25):
    for _ in range(int(limit / step)):
        if c.js("(()=>{const R=coryRitualDebugV1781().R;return R?R.phase:''})()") == name: return True
        advance(c, step)
    print('! phase', name, 'not reached'); return False

# ------------------------------------------------------------------ 1: the hook, she eats one of her eggs (60 fps)
def take_c_eat():
    c = ritual_game([C('F', FULL), C('M', FULL), C('M', AD)])
    try:
        fem = start_ritual(c, rounds=3)
        wait_phase(c, 'lay')
        # filming only: the 30%% chance of eating an egg comes up this time
        c.js("(()=>{const r=Math.random;setInterval(()=>{const R=coryRitualDebugV1781().R;Math.random=(R&&R.phase==='lay'&&R.t>3.6&&R.laid>0&&!R.ateEgg)?()=>.1:r;},20);return 1})()")
        advance(c, 2.5)
        run(c, 'c_eat', 7, fps=60, target=fem_cam(c, fem), cam=Cam(tau=.4), zoom=3.6, phase=PH_RIT)
    finally: c.close()

# ------------------------------------------------------------------ 2: group glass surfing (the sign they will spawn)
def take_c_surf():
    c = game(PRE + "T.tank('main',[%s])" % ','.join([C('F', FULL), C('M', FULL), C('M', AD), C('F', AD)]), warm=2, dof=4)
    try:
        c.js("st.corySpawn=null;st.coryEggs81=[];st.coryRitual81={day:st.day,delay:9999};1")
        advance(c, 9); ids = ids_of(c)
        run(c, 'c_surf', 9, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.15, zmin=1.6, zmax=2.6, tau=.6))
    finally: c.close()

# ------------------------------------------------------------------ 3-4: the T-position, then the eggs go on the glass
def take_c_ritual():
    c = ritual_game([C('F', FULL), C('M', FULL), C('M', AD)])
    try:
        fem = start_ritual(c, rounds=2)
        wait_phase(c, 'cut'); advance(c, .2)
        run(c, 'c_ritual', 26, target=fem_cam(c, fem), cam=Cam(tau=.5), zoom=3.0, phase=PH_RIT)
    finally: c.close()

def take_c_hard():
    c = ritual_game([C('F', FULL), C('M', FULL), C('M', AD)])
    try:
        fem = start_ritual(c, rounds=3, hard=True)
        for _ in range(3):                           # skip to the second round's carry (the first lay goes on the glass)
            wait_phase(c, 'carry')
            if c.js("coryRitualDebugV1781().R.round") >= 1: break
            advance(c, 3)
        run(c, 'c_hard', 10, target=fem_cam(c, fem), cam=Cam(tau=.5), zoom=2.8, phase=PH_RIT)
    finally: c.close()

# ------------------------------------------------------------------ 5: a clutch on the glass, a hungry fish comes for it
EGGS = "(()=>{st.corySpawn={startDay:st.day,endDay:st.day+3,count:24,v81:true,tank:'main'};st.coryEggs81=[];for(let i=0;i<24;i++){const col=i%%3;st.coryEggs81.push({x:%(x)f+col*.018+(i%%2)*.006,y:%(y)f-Math.floor(i/3)*.017,k:'g',d:st.day,b:0});}return st.coryEggs81.length})()"
# filming only: the platy cruises in from the left, slows down and noses up to the clutch (it does not eat here)
HUNTER = r"""(()=>{const id='%(id)s',t0=performance.now(),o=window.behaviorTargetV1764;
 window.behaviorTargetV1764=function(el,state,now){if(String(el.dataset.fishId)!==id)return o?o.apply(this,arguments):null;
  const t=el.closest('.tank'),W=t.clientWidth,H=t.clientHeight,q=(now-t0)/1000,ex=%(x)f*W,ey=(%(y)f-.06)*H,fw=el.offsetWidth*(state.scale||1);
  const X=Math.min(ex-fw*.92,40+q*%(v)d);return {x:X,y:ey-el.offsetHeight*(state.scale||1)/2+Math.sin(q*1.3)*4,mul:X<ex-fw*.95?.9:.25,chase:true,calm:true,pitch:0,face:1};};
 const s=v16MotionStates.get(id);if(s){s.x=10;s.y=%(y)f*960-80;s.facing=1;}return 1;})()"""
def take_c_hungry():
    fish = [C('F', FULL), C('M', FULL), C('M', AD), "T.fish('platy','F',30)"]
    c = game(PRE + "T.tank('main',[%s])" % ','.join(fish), warm=2, dof=4)
    try:
        c.js(QUIET_LOOP); c.js(EGGS % dict(x=.55, y=.74))
        pid = [i for i in ids_of(c) if 'platy' in i][0]
        c.js(HUNTER % dict(id=pid, x=.55, y=.74, v=26)); advance(c, 1.5)
        tgt = "(()=>{const a=CAM.box(['%s']),b=CAM.sel('#tank-main .coryEgg81');if(!a)return b;if(!b)return a;const x0=Math.min(a.x-a.w/2,b.x-b.w/2),x1=Math.max(a.x+a.w/2,b.x+b.w/2),y0=Math.min(a.y-a.h/2,b.y-b.h/2),y1=Math.max(a.y+a.h/2,b.y+b.h/2);return {x:(x0+x1)/2,y:(y0+y1)/2+40,w:x1-x0,h:y1-y0}})()" % pid
        run(c, 'c_hungry', 10, target=lambda i: c.js(tgt), cam=Cam(pad=1.15, zmin=1.8, zmax=2.8, tau=.5))
    finally: c.close()

# ------------------------------------------------------------------ 6-8: the breeding box on the tank rim, eggs, larvae, fry
FRYBLEED = _tk.FULLBLEED.replace('#tank-main', '#tank-fry')
def take_c_box():
    c = _tk.open_game(VW, VH, _tk.DSF)
    try:
        c.js(_tk.CAM_JS); c.js('window.__afHourOverride=12;' + NOLIVE + HIDEUI + '1')
        c.js("(()=>{const mk=(age,i)=>T.fish('cory',i%2?'M':'F',age,{id:'yb'+i,name:'yb'+i});st.fry.length=0;[1,1,1,4,4,4].forEach((a,i)=>st.fry.push(mk(a,i)));"
             "st.coins=999;buyBreedingBoxV1786();st.breedingBox86.fish=st.fry.map(f=>String(f.id));"
             "st.corySpawn={startDay:st.day,endDay:st.day+3,count:10,v81:true,tank:'box'};st.coryEggs81=[];for(let i=0;i<10;i++)st.coryEggs81.push({x:.5,y:.5,k:'g',d:st.day,b:0});"
             "T.show('fry');T.clean();return 1})()")
        c.js(FRYBLEED); advance(c, .3); c.js(FRYBLEED); advance(c, 4)
        box = "CAM.sel('#tank-fry .breedBox86.back')"
        def tilt(i):                                  # from the hooks on the rim down to the eggs and young on the grate
            b = c.js(box)
            if not b: return full(i, 2.4)
            u = min(1, i / 75.0); u = u * u * (3 - 2 * u); z = 2.9 + .5 * u
            return full(i, z, b['x'], b['y'] - b['h'] * .32 + b['h'] * .62 * u)
        run(c, 'c_box', 6, fixed=tilt)
        def floor(i):                                 # along the grate, slowly
            b = c.js(box)
            if not b: return full(i, 2.4)
            return full(i, 5.2, b['x'] - b['w'] * .26 + b['w'] * .3 * i / 180, b['y'] + b['h'] * .32)
        run(c, 'c_nursery', 6, fixed=floor)
        for name, age in (('c_larva', 1), ('c_fry', 4)):
            fid = c.js("(()=>{const f=st.fry.find(f=>f.age===%d);return f?String(f.id):null})()" % age)
            run(c, name, 4, target=lambda i: c.js("CAM.sel('#tank-fry [data-fish-id=\"%s\"]')" % fid), cam=Cam(tau=.5), zoom=7.0)
    finally: c.close()

# ------------------------------------------------------------------ growth montage (juvenile, adult, full grown) + the ending
def take_c_stages():
    c = game(PRE + "T.tank('main',[%s])" % ','.join([C('F', 9), C('M', AD), C('M', FULL), C('F', FULL)]), warm=4, dof=5)
    try:
        c.js("st.corySpawn=null;st.coryEggs81=[];st.coryRitual81=null;1"); ids = ids_of(c)
        for name, fid, z in (('c_juv', ids[0], 4.2), ('c_adult', ids[1], 3.6), ('c_full', ids[2], 3.2)):
            run(c, name, 4, target=lambda i, f=fid: c.js("CAM.box(['%s'])" % f), cam=Cam(tau=.5), zoom=z)
    finally: c.close()

def take_c_group():
    c = game(PRE + "T.tank('main',[%s])" % ','.join([C('F', FULL), C('M', FULL), C('M', FULL), C('F', AD)]), warm=8, dof=4)
    try:
        c.js("st.corySpawn=null;st.coryEggs81=[];st.coryRitual81=null;1"); ids = ids_of(c)
        run(c, 'c_group', 7, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.15, zmin=1.8, zmax=2.8, tau=.7))
    finally: c.close()

TAKES = {k[5:]: v for k, v in globals().items() if k.startswith('take_')}
if __name__ == '__main__':
    for name in (sys.argv[1:] or list(TAKES)):
        t = time.time()
        try: TAKES[name]()
        except Exception as e: print('FAILED', name, repr(e)[:600], flush=True)
        print('take', name, round(time.time() - t), 's', flush=True)
