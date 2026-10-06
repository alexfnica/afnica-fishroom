# Raw takes for the "What's new: Black Molly" clip (same rig as takes.py: throw-away game, tank built in memory, behaviour
# triggered, virtual camera). Run: python takes_molly.py <take> [<take> ...]   (frames go to raw/<take>/)
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
from scene import advance
import takes as _tk, scene as _sc
if os.environ.get('AF_PORT'):                     # a second rig can film in parallel on another port
    _po = _sc.open_game; _tk.open_game = lambda *a, **k: _po(*a, **dict(k, port=int(os.environ['AF_PORT'])))
from takes import game as _game, run, Cam, full, court_ids, PH_COURT, PH_FIGHT, COURT_FIX, VW, VH
def game(tank_js, **k):
    c = _game('window.__afHourOverride=12;' + tank_js, **k)   # filming in daylight (the device clock may say night)
    c.js("document.querySelectorAll('#tank-main .trStage').forEach(e=>{if(+e.style.zIndex>=40)e.remove()});1")   # no foreground leaves over the fish
    return c

def G(tail, **x):
    g = dict(color=85, pattern=80, fins=90, vitality=90, mutation=None, tail=tail); g.update(x); return json.dumps({'genes': g})
def M(sex, age, tail, extra=None, **gx):
    e = json.loads(G(tail, **gx))
    if extra: e.update(extra)
    return "T.fish('molly','%s',%d,%s)" % (sex, age, json.dumps(e))
QUIET = "courtshipV1744.main={next:1e15};fightDebugV1748().NEXT.main=1e15;showOffDebugV1752().NX.main=1e15;1"
QUIET_LOOP = "setInterval(()=>{try{" + QUIET.replace(';1', '') + "}catch(e){}},300);1"
FULL, ADULT = 34, 18

def ids_of(c):
    return json.loads(c.js("JSON.stringify(tankArrayV14('main').map(f=>String(f.id)))"))

# ------------------------------------------------------------------ takes
def take_m_hero():
    # a full-grown lyretail male cruising, close and slow (intro)
    c = game("T.tank('main',[%s,%s,%s,%s])" % (M('M', FULL, 'LL', gono='short'), M('F', FULL, 'Ll'), M('F', ADULT, 'll'), "T.fish('cory','M',30)"), warm=5, dof=6)
    try:
        c.js(QUIET_LOOP); mid = ids_of(c)[0]
        c.js(PARADE % dict(ids=json.dumps([mid]), x0=120, v=18, y0=.42, dy=0)); advance(c, 2)
        run(c, 'm_hero', 8, target=lambda i: c.js("CAM.box(['%s'])" % mid), cam=Cam(tau=.8), zoom=2.6)
    finally: c.close()

def take_m_court():
    # courtship of a full-grown sailfin male: display, nibbling under her belly, the thrust (120 fps for slow motion)
    c = game("T.tank('main',[%s,%s,%s])" % (M('M', FULL, 'LL', gono='short'), M('F', FULL, 'Ll'), "T.fish('cory','M',30)"), warm=5, dof=5)
    try:
        c.js("fightDebugV1748().NEXT.main=1e15;showOffDebugV1752().NX.main=1e15;courtshipV1744.main={next:0}"); advance(c, 1.2)
        for _ in range(30):
            if court_ids(c): break
            advance(c, .6)
        print('fix', c.js(COURT_FIX % dict(dance=2600, hold=6000, nthr=2, side=-1)))
        ids = court_ids(c); print('court', ids)
        run(c, 'm_court', 16, fps=120, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.1, zmin=2.0, zmax=2.9, tau=.4), phase=PH_COURT)
    finally: c.close()

def take_m_tails():
    # lyretail and roundtail, side by side (both come out of one pairing)
    c = game("T.tank('main',[%s,%s,%s,%s])" % (M('M', FULL, 'LL', gono='short'), M('M', FULL, 'll', gono='short'), M('F', FULL, 'Ll'), M('F', FULL, 'll')), warm=4, dof=5)
    try:
        c.js(QUIET_LOOP); ids = ids_of(c)
        # filming only: the two males cruise together, one above the other
        c.js(PARADE % dict(ids=json.dumps(ids[:2]), x0=130, v=18, y0=.36, dy=.16)); advance(c, 3)
        run(c, 'm_tails', 8, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids[:2])), cam=Cam(pad=1.25, zmin=1.6, zmax=2.6, tau=.7))
    finally: c.close()

# filming only: the listed fish swim side by side in a column that drifts slowly across the tank (a line-up)
PARADE = r"""(()=>{const ids=%(ids)s,t0=performance.now(),o=window.behaviorTargetV1764;
 window.behaviorTargetV1764=function(el,state,now){const k=ids.indexOf(String(el.dataset.fishId));if(k<0)return o?o.apply(this,arguments):null;
  const t=el.closest('.tank'),W=t.clientWidth,H=t.clientHeight,X=Math.min(W-el.offsetWidth-20,%(x0)d+(now-t0)/1000*%(v)d);
  return {x:X,y:H*(%(y0)f+k*%(dy)f),mul:.9,chase:true,calm:true,pitch:0,face:1};};
 ids.forEach((id,k)=>{const s=v16MotionStates.get(id),e=document.querySelector('#tank-main [data-fish-id="'+id+'"]');if(!s||!e)return;const H=e.closest('.tank').clientHeight;s.x=%(x0)d-30;s.y=H*(%(y0)f+k*%(dy)f);s.facing=1;});return ids.length;})()"""

def take_m_stages():
    # five life stages in one line-up: newborn, fry, juvenile, adult, full grown
    c = game("T.tank('main',[%s,%s,%s,%s,%s])" % (M('F', 1, 'Ll'), M('F', 5, 'Ll'), M('F', 9, 'Ll'), M('M', ADULT, 'Ll', gono='short'), M('M', FULL, 'LL', gono='short')), warm=3, dof=4)
    try:
        c.js(QUIET_LOOP); ids = ids_of(c)
        c.js(PARADE % dict(ids=json.dumps(ids), x0=130, v=14, y0=.22, dy=.13)); advance(c, 3)
        run(c, 'm_stages', 8, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.15, zmin=1.0, zmax=2.2, tau=.8))
    finally: c.close()

def take_m_fight():
    # two full-grown sailfin males: lateral display with raised sails, nips at the fins (120 fps)
    c = game("T.tank('main',[%s,%s,%s,%s])" % (M('M', FULL, 'LL', gono='short', fins=95), M('M', FULL, 'll', gono='short', fins=88), M('F', FULL, 'Ll'), "T.fish('cory','M',30)"), warm=5, dof=5)
    try:
        c.js("fightDebugV1748().NEXT.main=0; courtshipV1744.main={next:1e12}; showOffDebugV1752().NX.main=1e15"); advance(c, .5)
        for _ in range(20):
            ids = json.loads(c.js("JSON.stringify((()=>{const f=fightDebugV1748().FIGHT.main;return f?[f.a,f.b]:null})())") or 'null')
            if ids: break
            c.js("fightDebugV1748().NEXT.main=0"); advance(c, .5)
        print('fight', ids)
        print('seq', c.js("(()=>{const f=fightDebugV1748().FIGHT.main;if(!f)return 0;f.seq=['lateral','nip','spin','nip','lock','nip','pause'];f.si=0;f.segEnd=performance.now()+1600;return f.seq.length})()"))
        run(c, 'm_fight', 12, fps=60, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.1, zmin=2.0, zmax=2.9, tau=.35), phase=PH_FIGHT)
    finally: c.close()

# filming only: this fish hovers in mid-water, drifting very slowly (for close-ups of breathing / shimmying)
HOVER = r"""(()=>{const id='%(id)s',t0=performance.now(),o=window.behaviorTargetV1764;
 window.behaviorTargetV1764=function(el,state,now){if(String(el.dataset.fishId)!==id)return o?o.apply(this,arguments):null;
  const r=o?o.apply(this,arguments):null;if(r&&el.dataset.shim)return r;   /* a shimmy keeps its own target */
  const t=el.closest('.tank'),W=t.clientWidth,H=t.clientHeight,q=(now-t0)/1000;
  return {x:W*.36+Math.sin(q*.25)*14,y:H*.45+Math.sin(q*.4)*6,mul:.12,snap:2,chase:true,calm:true,pitch:0,face:1};};
 const s=v16MotionStates.get(id),e=document.querySelector('#tank-main [data-fish-id="'+id+'"]');if(s&&e){const t=e.closest('.tank');s.x=t.clientWidth*.36;s.y=t.clientHeight*.45;s.facing=1;}return 1;})()"""

def take_m_breath():
    # close-up: mouth and lips, gill covers, sculling pectorals
    c = game("T.tank('main',[%s,%s])" % (M('F', FULL, 'Ll'), "T.fish('cory','M',30)"), warm=3, dof=6)
    try:
        c.js(QUIET_LOOP); fid = ids_of(c)[0]
        c.js("(()=>{const B=behaviorDebugV1764().B;setInterval(()=>{const b=B['%s'];if(b){b.gz=null;b.nextGraze=performance.now()+1e9;}},200);return 1})()" % fid)
        c.js(HOVER % dict(id=fid)); advance(c, 4)
        run(c, 'm_breath', 7, target=lambda i: c.js("CAM.box(['%s'])" % fid), cam=Cam(tau=.6), zoom=5.2)
    finally: c.close()

ALGAE = "st.algaeLoad=st.algaeLoad||{};st.algaeLoad.main=13;st.daysNoCleanMain=5;"
FORCE_GRAZE = r"""(()=>{setInterval(()=>{try{const B=behaviorDebugV1764().B,now=performance.now();tankArrayV14('main').forEach(f=>{if(f.species!=='molly')return;const b=B[f.id]||(B[f.id]={});
 if(b.gz&&b.gz.kind!=='front')b.gz=null;if(!b.gz)b.nextGraze=1;});}catch(e){}},250);return 1})()"""

def take_m_algae():
    # algae on the glass: mollies graze it from the front and side panes, clean patches open where they peck
    c = game(ALGAE + "T.tank('main',[%s,%s,%s,%s])" % (M('F', FULL, 'Ll'), M('F', FULL, 'll'), M('M', FULL, 'LL', gono='short'), M('F', ADULT, 'Ll')), warm=2, dof=0)
    try:
        c.js("render();T.clean();" + QUIET_LOOP); c.js(FORCE_GRAZE)
        advance(c, 30)                                   # let them clear a few trails first
        ids = ids_of(c)
        run(c, 'm_algae', 9, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids[:1])), cam=Cam(tau=1.0), zoom=2.1)
    finally: c.close()

def take_m_oxygen():
    # overcrowded, short of oxygen: mollies hang at the surface breathing fast, a cory dashes up for air, the pleco waits
    # high on the glass
    fish = [M('F', FULL, 'Ll'), M('M', FULL, 'LL', gono='short'), M('F', ADULT, 'll'), M('F', FULL, 'll'), "T.fish('cory','M',30)", "T.fish('cory','F',30)", "T.fish('anc','F',50)"]
    c = game("window.bioPercentV14=()=>140;T.tank('main',[%s])" % ','.join(fish), warm=2, dof=0)
    try:
        c.js("window.bioPercentV14=()=>140;" + QUIET_LOOP)
        # filming only: the tall filming tank is 2.5x the game's, so start the mollies just under the surface, no dips
        c.js("(()=>{const B=behaviorDebugV1764().B;tankArrayV14('main').filter(f=>f.species==='molly').forEach((f,k)=>{const s=v16MotionStates.get(String(f.id));if(s){s.y=16+k*4;s.ty=s.y;}const b=B[f.id]||(B[f.id]={});b.nextDip=performance.now()+1e9;});setInterval(()=>{tankArrayV14('main').forEach(f=>{const b=B[f.id];if(b)b.nextDip=performance.now()+1e9;})},500);return 1})()")
        for k in range(90):                                # until the pleco is up on the glass
            y = c.js("(()=>{const e=document.querySelector('#tank-main .modelFish[data-species=\"anc\"]'),t=document.getElementById('tank-main');if(!e)return 1;const r=e.getBoundingClientRect(),q=t.getBoundingClientRect();return (r.top+r.height/2-q.top)/q.height})()")
            if y < .42: break
            advance(c, 1)
        print('anc y', y, 'after', k, 's'); advance(c, 4)
        def every(i):
            if i in (45, 180): c.js("AFNiCA_CoryV1712.forceDash();1")
        run(c, 'm_oxygen', 9, every=every, fixed=lambda i: full(i, 1.12 + .12 * i / 270, VW * .5, VH * .36))
    finally: c.close()

def take_m_shimmy():
    # a weak molly shimmying: rocking on the spot, fins clamped, a faint white film
    c = game("T.tank('main',[%s,%s])" % (M('M', FULL, 'LL', {'health': 50}, gono='short'), "T.fish('cory','M',30)"), warm=3, dof=6)
    try:
        c.js(QUIET_LOOP); fid = ids_of(c)[0]
        c.js(HOVER % dict(id=fid)); advance(c, 3)
        c.js("(()=>{const B=behaviorDebugV1764().B;setInterval(()=>{const b=B['%s'],now=performance.now();if(!b)return;b.gz=null;b.nextGraze=now+1e9;b.nextShim=now+1e9;if(!b.shimUntil){const s=v16MotionStates.get('%s');b.shimUntil=now+60000;b.sx=s.x;b.sy=s.y;}},200);return 1})()" % (fid, fid))
        advance(c, 2.5)
        run(c, 'm_shimmy', 7, target=lambda i: c.js("CAM.box(['%s'])" % fid), cam=Cam(tau=.6), zoom=3.6)
    finally: c.close()

TAKES = {k[5:]: v for k, v in globals().items() if k.startswith('take_')}
if __name__ == '__main__':
    for name in (sys.argv[1:] or list(TAKES)):
        t = time.time()
        try: TAKES[name]()
        except Exception as e: print('FAILED', name, repr(e)[:600], flush=True)
        print('take', name, round(time.time() - t), 's', flush=True)
