# Records the raw takes for the AFNICA trailer: each take is a fresh throw-away game, a tank built in memory, a behaviour
# triggered, and a virtual camera (follows the action, smooth pan + zoom) cropping 1080x1920 frames out of a 540x960
# portrait page rendered at 4x. Run: python takes.py <take> [<take> ...]   (frames go to raw/<take>/00000.jpg ...)
import os, sys, json, math, time
sys.path.insert(0, os.path.dirname(__file__))
from scene import open_game, advance, HERE
VW, VH, DSF, FPS = 540, 960, 6, 30

FULLBLEED = r'''(()=>{const s=document.createElement('style');s.id='trBleed';s.textContent=
 '#tank-main{position:fixed!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;z-index:9000!important;border-radius:0!important;margin:0!important;aspect-ratio:auto!important;max-width:none!important;max-height:none!important;box-shadow:none!important}body{overflow:hidden!important}';
 document.head.appendChild(s);window.dispatchEvent(new Event('resize'));return 1;})()'''

# camera helpers (JS): rectangles of fish, in page px
CAM_JS = r'''
window.CAM = {
 box(ids) { let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9,n=0;
  ids.forEach(id=>{const e=document.querySelector('#tank-main [data-fish-id="'+id+'"]');if(!e)return;const r=e.getBoundingClientRect();if(!r.width)return;
   x0=Math.min(x0,r.left);y0=Math.min(y0,r.top);x1=Math.max(x1,r.right);y1=Math.max(y1,r.bottom);n++;});
  return n?{x:(x0+x1)/2,y:(y0+y1)/2,w:x1-x0,h:y1-y0}:null; },
 sel(q) { let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9,n=0;
  document.querySelectorAll(q).forEach(e=>{const r=e.getBoundingClientRect();if(!r.width||r.left>540||r.right<0)return;x0=Math.min(x0,r.left);y0=Math.min(y0,r.top);x1=Math.max(x1,r.right);y1=Math.max(y1,r.bottom);n++;});
  return n?{x:(x0+x1)/2,y:(y0+y1)/2,w:x1-x0,h:y1-y0}:null; },
};
'''

PH_COURT = "(()=>{const c=courtshipV1744.main;if(!c||!c.mId)return null;return {T:+((performance.now()-c.t0-c.danceAt)/1000).toFixed(2),hold:c.hold,res:c.res,hit:c.hitT?+((performance.now()-c.hitT)/1000).toFixed(2):null}})()"
PH_FIGHT = "(()=>{const f=fightDebugV1748().FIGHT.main;return f?{seg:f.seg,round:f.round,win:f.win||null}:null})()"
COURT_FIX = r'''(()=>{const c=courtshipV1744.main;if(!c||!c.mId||c.__fixed)return 0;c.__fixed=1;
 c.sneak=false;c.thrust=true;c.danceAt=%(dance)d;c.hold=%(hold)d;c.nThr=%(nthr)d;c.side=%(side)d;
 c.until=c.t0+c.danceAt+8100+c.hold+c.nThr*800+2500;return 1;})()'''

def court_ids(c):
    v = c.js("JSON.stringify(courtshipV1744.main&&courtshipV1744.main.mId?[courtshipV1744.main.mId,courtshipV1744.main.fId]:null)")
    return json.loads(v) if v else None

class Cam:
    def __init__(self, x=VW / 2, y=VH / 2, z=1.0, tau=.45, ztau=.9, pad=1.9, zmin=1.0, zmax=2.4):
        self.x, self.y, self.z, self.tau, self.ztau, self.pad, self.zmin, self.zmax = x, y, z, tau, ztau, pad, zmin, zmax
        self.first = True
    def update(self, box, dt, zoom=None):
        if box:
            tz = zoom or max(self.zmin, min(self.zmax, min(VW / max(1, box['w'] * self.pad), VH / max(1, box['h'] * self.pad * 1.7))))
            tx, ty = box['x'], box['y']
            if self.first: self.x, self.y, self.z, self.first = tx, ty, tz, False
            a = 1 - math.exp(-dt / self.tau); b = 1 - math.exp(-dt / self.ztau)
            self.x += (tx - self.x) * a; self.y += (ty - self.y) * a; self.z += (tz - self.z) * b
        w, h = VW / self.z, VH / self.z
        x = min(max(self.x - w / 2, 0), VW - w); y = min(max(self.y - h / 2, 0), VH - h)
        return dict(x=x, y=y, width=w, height=h, scale=1080 / (w * DSF))

def run(c, name, seconds, target=None, cam=None, every=None, zoom=None, fixed=None, phase=None):
    out = os.path.join(HERE, 'raw', name); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    cam = cam or Cam(); n = int(seconds * FPS); dt = 1 / FPS; t0 = time.time(); log = []
    for i in range(n):
        if every: every(i)
        c.js('__afStep(%f, 2)' % (1000 / FPS))
        box = target(i) if target else None
        if fixed: clip = fixed(i)
        else: clip = cam.update(box, dt, zoom(i) if callable(zoom) else zoom)
        c.shot(os.path.join(out, '%05d.jpg' % i), clip=clip, q=94)
        log.append({'clip': clip, 'ph': c.js(phase) if phase else None})
        if i % 60 == 0: print(name, i, '/', n, round(time.time() - t0), 's', flush=True)
    json.dump(log, open(os.path.join(out, 'cam.json'), 'w'))
    print('DONE', name, n, 'frames', round(time.time() - t0), 's', flush=True)

# filming only: every fish gets a preferred depth spread over the whole (tall) water column, and starts there
SPREAD = r'''(()=>{if(window.__spreadOn)return 0;window.__spreadOn=1;const o=v16ChooseTarget;
 v16ChooseTarget=function(el,state,now,force){o.apply(this,arguments);try{const b=v16Bounds(el,state);if(!b)return;
  if(state.__homeF==null)state.__homeF=%(lo)f+Math.random()*%(span)f;const home=b.minY+(b.maxY-b.minY)*state.__homeF;
  state.ty=state.ty*.45+home*.55;}catch(e){}};
 v16MotionStates.forEach(s=>{if(s.__homeF==null)s.__homeF=%(lo)f+Math.random()*%(span)f;s.y=12+(960-120)*s.__homeF;s.ty=s.y;});return 1;})()'''

DOF = r'''(()=>{let s=document.getElementById('trDof');if(!s){s=document.createElement('style');s.id='trDof';document.head.appendChild(s);}
 s.textContent='#tank-main .v171BackPlantGroup,#tank-main .v171Wood,#tank-main .v171Rocks,#tank-main .v175SubstrateAssetLayer,#tank-main .v174SurfaceAssetLayer,#tank-main .v176EpiphyteAssetLayer,#tank-main .floor,#tank-main .v17SubstrateGlow{filter:blur(%(b)spx) brightness(.9)!important}#tank-main .v13Debris,#tank-main .v17WaterCaustics{filter:blur(%(d)spx)!important}#tank-main .waterTimer,#tank-main .waterMeter{display:none!important}';return 1;})()'''

def game(tank_js, bleed=True, warm=4, lo=.25, span=.4, dof=0):
    c = open_game(VW, VH, DSF)
    c.js(CAM_JS)
    if dof: c.js(DOF % dict(b=dof, d=dof * .6))
    if bleed: c.js(FULLBLEED)
    c.js('(()=>{' + tank_js + ';T.show("main");T.clean();return 1;})()')
    if bleed: c.js(FULLBLEED)
    advance(c, .3); c.js(SPREAD % dict(lo=lo, span=span))
    advance(c, warm)
    return c

def full(i, z=1.0, cx=VW / 2, cy=VH / 2):
    w, h = VW / z, VH / z
    return dict(x=min(max(cx - w / 2, 0), VW - w), y=min(max(cy - h / 2, 0), VH - h), width=w, height=h, scale=1080 / (w * DSF))

# ------------------------------------------------------------------ takes
def take_guppy_court():
    c = game("T.tank('main',[T.fish('guppy','M',30),T.fish('guppy','M',28),T.fish('guppy','M',26),T.fish('guppy','F',30),T.fish('cory','M',30),T.fish('anc','F',40)])", warm=5, dof=5)
    try:
        c.js("courtshipV1744.main={next:0}"); advance(c, 1.2)
        for _ in range(20):
            if court_ids(c): break
            advance(c, .6)
        c.js(COURT_FIX % dict(dance=2600, hold=6500, nthr=1, side=1))
        ids = court_ids(c); print('court', ids)
        run(c, 'guppy_court', 16, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.08, zmin=2.6, zmax=3.6, tau=.4), phase=PH_COURT)
    finally: c.close()

def take_xipho_court():
    c = game("T.tank('main',[T.fish('xipho','M',34),T.fish('xipho','F',34),T.fish('cory','M',30),T.fish('anc','M',40)])", warm=5, dof=5)
    try:
        c.js("courtshipV1744.main={next:0}"); advance(c, 1.2)
        for _ in range(20):
            if court_ids(c): break
            advance(c, .6)
        c.js(COURT_FIX % dict(dance=3000, hold=5200, nthr=2, side=-1))
        ids = court_ids(c); print('court', ids)
        run(c, 'xipho_court', 18, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.08, zmin=2.2, zmax=3.1, tau=.4), phase=PH_COURT)
    finally: c.close()

def take_fight():
    c = game("T.tank('main',[T.fish('xipho','M',40),T.fish('xipho','M',36),T.fish('xipho','F',34),T.fish('cory','M',30)])", warm=5, dof=5)
    try:
        c.js("fightDebugV1748().NEXT.main=0; courtshipV1744.main={next:1e12}"); advance(c, .5)
        ids = json.loads(c.js("JSON.stringify((()=>{const f=fightDebugV1748().FIGHT.main;return f?[f.a,f.b]:null})())") or 'null'); print('fight', ids)
        run(c, 'fight', 20, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.1, zmin=2.1, zmax=3.0, tau=.35), phase=PH_FIGHT)
    finally: c.close()

BROOD = r'''(()=>{const mom=tankArrayV14('main').find(f=>f.sex==='F'&&f.species==='%(sp)s');const fry=[];
 for(let i=0;i<%(n)d;i++)fry.push(T.fish('%(sp)s',Math.random()<.5?'M':'F',1));
 st.broods45=st.broods45||[];st.broods45.push({id:'btr',tank:'main',species:'%(sp)s',born:st.day,momId:mom&&mom.id,fry,eaten:0,start:%(n)d,budget:%(budget)d});
 render();return document.querySelectorAll('.brood45Fry').length;})()'''

PICK_FRY = r"""(()=>{const c={x:%(x)d,y:%(y)d};const L=[...document.querySelectorAll('#tank-main .brood45Fry:not([data-caught])')].map(e=>{const r=e.getBoundingClientRect();return {e,d:Math.hypot(r.left+r.width/2-c.x,r.top+r.height/2-c.y)}}).sort((a,b)=>a.d-b.d);return L.length?L[%(k)d%%L.length].e.dataset.fid:null})()"""
FRY_BOX = "CAM.sel('#tank-main .brood45Fry[data-fid=\"%s\"]')"

def take_fry():
    c = game("T.tank('main',[T.fish('guppy','F',30),T.fish('guppy','M',30),T.fish('xipho','F',30)])", warm=3, dof=3)
    try:
        c.js(BROOD % dict(sp='guppy', n=22, budget=0)); advance(c, 3)
        fid = c.js(r"""(()=>{const ad=[...document.querySelectorAll('#tank-main .modelFish')].map(e=>e.getBoundingClientRect());
          const L=[...document.querySelectorAll('#tank-main .brood45Fry')].map(e=>{const r=e.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
           return {e,d:Math.min(...ad.map(a=>Math.hypot(a.left+a.width/2-x,a.top+a.height/2-y)))-Math.abs(x-270)*.3}}).sort((a,b)=>b.d-a.d);return L[0].e.dataset.fid})()""")
        print('fry', fid)
        run(c, 'fry', 8, target=lambda i: c.js(FRY_BOX % fid), cam=Cam(tau=.6), zoom=6.0)
    finally: c.close()

def take_net():
    c = game("T.tank('main',[T.fish('guppy','F',30),T.fish('xipho','F',30),T.fish('cory','M',30)])", warm=3, dof=3)
    try:
        c.js(BROOD % dict(sp='guppy', n=12, budget=0)); advance(c, 3)
        st = {'fid': c.js(PICK_FRY % dict(x=270, y=480, k=0))}; print('net fry', st['fid'])
        TAP = "(()=>{const im=document.querySelector('#tank-main .brood45Fry[data-fid=\"%s\"]');if(!im)return 0;const r=Math.random;Math.random=()=>%s;try{brood45Tap(im)}finally{Math.random=r}return 1})()"
        def every(i):
            if i == 40: c.js(TAP % (st['fid'], '.05'))          # it senses the net and darts away
            if i == 110: c.js(TAP % (st['fid'], '.95'))         # second try: caught
        run(c, 'net', 6.5, every=every, target=lambda i: c.js("(()=>{const b=%s;const n=CAM.sel('#tank-main .brood45Net');return b||n})()" % (FRY_BOX % st['fid'])), cam=Cam(tau=.45), zoom=3.4)
    finally: c.close()

FORCE_HUNT = r"""(()=>{const k='main',H=huntDebugV1746().HUNT;const f=tankArrayV14(k).find(x=>x.species==='%(sp)s'&&x.sex==='F');if(!f)return null;
 const e=document.querySelector('#tank-main [data-fish-id="'+f.id+'"]'),s=v16MotionStates.get(String(f.id));
 const hx=s.x+e.offsetWidth/2,hy=s.y+e.offsetHeight/2;
 const L=[...document.querySelectorAll('#tank-main .brood45Fry:not([data-caught])')].map(sp=>({sp,d:Math.hypot(sp.offsetLeft+sp.offsetWidth/2-hx,sp.offsetTop+sp.offsetHeight/2-hy)})).sort((a,b)=>a.d-b.d);
 if(!L.length)return null;const sp=L[0].sp;sp.style.setProperty('--d','.7s');H[k]={fishId:String(f.id),fid:sp.dataset.fid,until:performance.now()+14000};return [String(f.id),sp.dataset.fid];})()"""

def take_hunt():
    c = game("T.tank('main',[T.fish('xipho','F',34),T.fish('guppy','F',30),T.fish('platy','F',30)])", warm=3, dof=3)
    try:
        c.js(BROOD % dict(sp='guppy', n=12, budget=6)); advance(c, 2)
        c.js("(()=>{const r=Math.random;Math.random=()=>.45+r()*.55;return 1})()")   # filming only: the strike lands
        ids = json.loads(c.js("JSON.stringify(%s)" % FORCE_HUNT % dict(sp='xipho'))); print('hunter', ids)
        tgt = "(()=>{const a=CAM.box(['%s']),b=CAM.sel('#tank-main .brood45Fry[data-fid=\"%s\"]');if(!a)return b;if(!b)return a;const x0=Math.min(a.x-a.w/2,b.x-b.w/2),x1=Math.max(a.x+a.w/2,b.x+b.w/2),y0=Math.min(a.y-a.h/2,b.y-b.h/2),y1=Math.max(a.y+a.h/2,b.y+b.h/2);return {x:(x0+x1)/2,y:(y0+y1)/2,w:x1-x0,h:y1-y0}})()" % (ids[0], ids[1])
        run(c, 'hunt', 9, target=lambda i: c.js(tgt), cam=Cam(pad=1.25, zmin=2.4, zmax=3.4, tau=.35),
            phase="(()=>{const h=huntDebugV1746().HUNT.main;return h?Object.fromEntries(Object.entries(h).filter(([k,v])=>typeof v!=='object').map(([k,v])=>[k,typeof v==='number'?+v.toFixed(0):v])):null})()")
    finally: c.close()

def take_feed():
    c = game("T.tank('main',[T.fish('xipho','M',34),T.fish('xipho','F',34),T.fish('guppy','M',30),T.fish('guppy','F',30),T.fish('platy','M',30),T.fish('molly','M',30),T.fish('cory','M',30)])", warm=6)
    try:
        def every(i):
            if i == 15: c.js("animateFeedV13('main');1")
        run(c, 'feed', 9, every=every, fixed=lambda i: full(i, 1.15 + .35 * i / 270, VW / 2, VH * .36))
    finally: c.close()

def take_neon():
    c = game("T.tank('main',[" + ','.join("T.fish('neon','%s',30)" % ('M' if k % 2 else 'F') for k in range(7)) + "])", warm=8, dof=5)
    try:
        run(c, 'neon', 8, target=lambda i: c.js("CAM.sel('#tank-main .modelFish')"), cam=Cam(pad=1.0, zmin=2.0, zmax=3.2, tau=.6, ztau=1.4))
    finally: c.close()

def take_anc():
    c = game("T.tank('main',[T.fish('anc','M',60),T.fish('anc','F',50),T.fish('cory','M',30),T.fish('cory','F',30),T.fish('guppy','M',30)])", warm=5, dof=4)
    try:
        def every(i):
            if i == 10: c.js("try{dropWaferV1743('main')}catch(e){};1")
        ids = json.loads(c.js("JSON.stringify(tankArrayV14('main').filter(f=>f.species==='anc'||f.species==='cory').map(f=>f.id))"))
        run(c, 'anc', 9, every=every, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids[:1])), cam=Cam(pad=1.6, zmax=2.4, tau=.8))
    finally: c.close()

def take_hero():
    c = game("T.tank('main',[T.fish('xipho','M',40),T.fish('xipho','F',36),T.fish('guppy','M',30),T.fish('guppy','F',30),T.fish('molly','M',30),T.fish('platy','F',30),T.fish('anc','M',60)])", warm=8)
    try:
        run(c, 'hero', 10, fixed=lambda i: full(i, 1.0 + .18 * (i / 300) ** 1.2, VW / 2, VH * .5))
    finally: c.close()

def take_ui():
    c = open_game(VW, VH, 2)
    try:
        c.js(CAM_JS)
        c.js("(()=>{T.tank('main',[T.fish('xipho','M',40),T.fish('xipho','F',36),T.fish('guppy','M',30),T.fish('guppy','F',30),T.fish('platy','F',30),T.fish('cory','M',30),T.fish('anc','M',60)]);T.show('main');T.clean();return 1})()")
        advance(c, 5)
        r = json.loads(c.js("JSON.stringify(T.rect('#tank-main'))")); c.js("window.scrollTo(0,%d)" % int(r['y'] - 150)); advance(c, .3)
        mid = c.js("tankArrayV14('main').find(f=>f.species==='xipho'&&f.sex==='M').id")
        def every(i):
            if i == 40: c.js("inspectFishV1750('%s');1" % mid)
        out = os.path.join(HERE, 'raw', 'ui'); os.makedirs(out, exist_ok=True)
        for i in range(int(6 * FPS)):
            every(i); c.js('__afStep(%f, 2)' % (1000 / FPS)); c.shot(os.path.join(out, '%05d.jpg' % i), q=94)
        print('DONE ui')
    finally: c.close()

def take_anc_fan():
    # the male bristlenose in the driftwood cave, fanning a clutch of eggs (the cave and the brood are drawn by the game)
    c = game("T.tank('main',[T.fish('anc','M',60,{ancCaveCycleStart:st.day}),T.fish('anc','F',50),T.fish('cory','M',30)]);"
             "const m=tankArrayV14('main')[0],f=tankArrayV14('main')[1];"
             "st.ancClutch={id:'trclutch',stage:'eggs',count:34,mom:f.id,dad:m.id,parents:{mom:JSON.parse(JSON.stringify(f)),dad:JSON.parse(JSON.stringify(m))},attempt:1,lossRoll:.9,lastDay:st.day,laidDay:st.day-3,hatchDay:st.day+2,releaseDay:st.day+7,fungus:0}", warm=4, dof=0)
    try:
        mid = c.js("String(tankArrayV14('main')[0].id)")
        for k in range(40):
            mode = c.js("(document.querySelector('#tank-main [data-fish-id=\"%s\"]')||{dataset:{}}).dataset.ancMode" % mid)
            if mode == 'fanning': break
            advance(c, 1)
        print('anc mode', mode, 'after', k, 's')
        advance(c, 2)
        run(c, 'anc_fan', 6, target=lambda i: c.js("CAM.sel('#tank-main .ancBreedingCave')"), cam=Cam(tau=.8), zoom=3.4,
            phase="(document.querySelector('#tank-main [data-fish-id=\"%s\"]')||{dataset:{}}).dataset.ancMode" % mid)
    finally: c.close()

def take_anc_glass():
    # the female grazing algae on the front glass (belly view): fast-forward until she is up on the pane, then film
    c = game("T.tank('main',[T.fish('anc','F',50),T.fish('cory','M',30),T.fish('guppy','M',30)])", warm=3, dof=0)
    try:
        fid = c.js("String(tankArrayV14('main')[0].id)"); sel = "#tank-main [data-fish-id=\"%s\"]" % fid
        for k in range(150):
            b = c.js("(()=>{const e=document.querySelector('%s');return e?[e.dataset.belly||'',e.dataset.ancSurface||'',e.dataset.ancMode||'']:null})()" % sel)
            if b and b[0] and float(b[0]) > .6 and b[2] not in ('detach',): break
            advance(c, 1)
        print('glass', b, 'after', k, 's')
        advance(c, 1.5)
        run(c, 'anc_glass', 7, target=lambda i: c.js("CAM.box(['%s'])" % fid), cam=Cam(tau=.9), zoom=2.7,
            phase="(()=>{const e=document.querySelector('%s');return e?[e.dataset.belly||'',e.dataset.ancSurface||'',e.dataset.ancMode||'']:null})()" % sel)
    finally: c.close()

def take_beauty():
    # SELL: a show-quality male swordtail cruising, close and slow
    c = game("T.tank('main',[T.fish('xipho','M',60),T.fish('cory','M',30)])", warm=5, dof=6)
    try:
        c.js("courtshipV1744.main={next:1e12};fightDebugV1748().NEXT.main=1e12;1")
        mid = c.js("String(tankArrayV14('main')[0].id)")
        run(c, 'beauty', 7, target=lambda i: c.js("CAM.box(['%s'])" % mid), cam=Cam(tau=.7), zoom=3.5)
    finally: c.close()

TAKES = {k[5:]: v for k, v in globals().items() if k.startswith('take_')}
if __name__ == '__main__':
    for name in sys.argv[1:]:
        t = time.time()
        try: TAKES[name]()
        except Exception as e: print('FAILED', name, repr(e)[:600], flush=True)
        print('take', name, round(time.time() - t), 's', flush=True)
