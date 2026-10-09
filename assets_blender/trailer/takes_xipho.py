# Raw takes for the "What's new: Swordtail" clip (same rig as takes_molly.py / takes_platy.py).
# Run: python takes_xipho.py <take> [...]
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
import takes_molly as TM
from takes_molly import game, run, Cam, full, court_ids, PH_COURT, PH_FIGHT, COURT_FIX, VW, VH, QUIET_LOOP, PARADE, HOVER, advance
from takes import BROOD, PICK_FRY, FRY_BOX, FORCE_HUNT

AD, FULL = 18, 36                                  # S.xipho.adult = 14: adult at 18 days, full grown from ~31
def P(sex, age, extra=None, **gx):
    g = dict(color=92, pattern=80, fins=92, vitality=90, mutation=None); g.update(gx)
    o = {'genes': g}; o.update(extra or {})
    return "T.fish('xipho','%s',%d,%s)" % (sex, age, json.dumps(o))
def ids_of(c): return json.loads(c.js("JSON.stringify(tankArrayV14('main').map(f=>String(f.id)))"))

def take_x_hero():
    c = game("T.tank('main',[%s,%s,%s,%s])" % (P('M', FULL, fins=98), P('F', FULL), P('F', AD), "T.fish('cory','M',30)"), warm=5, dof=6)
    try:
        c.js(QUIET_LOOP); mid = ids_of(c)[0]
        c.js(PARADE % dict(ids=json.dumps([mid]), x0=120, v=18, y0=.42, dy=0)); advance(c, 2)
        run(c, 'x_hero', 8, target=lambda i: c.js("CAM.box(['%s'])" % mid), cam=Cam(tau=.8), zoom=2.5)
    finally: c.close()

PH_COURT2 = ("(()=>{const c=courtshipV1744.main;if(!c||!c.mId)return null;const q=id=>{const e=document.querySelector('#tank-main [data-fish-id=\"'+id+'\"]');if(!e)return null;const r=e.getBoundingClientRect();return [Math.round(r.left+r.width/2),Math.round(r.top+r.height/2)]};"
             "return {T:+((performance.now()-c.t0-c.danceAt)/1000).toFixed(2),hold:c.hold,res:c.res,hit:c.hitT?+((performance.now()-c.hitT)/1000).toFixed(2):null,m:q(c.mId),f:q(c.fId),kap:(document.querySelector('#tank-main [data-fish-id=\"'+c.mId+'\"]')||{dataset:{}}).dataset.kap||null}})()")

def _court(name, xvar, dy=70):
    # the swordtail display in front of her, then the jab (120 fps for slow motion); camera close, pair in the upper third
    c = game("T.tank('main',[%s,%s,%s])" % (P('M', FULL, fins=98), P('F', FULL), "T.fish('cory','M',30)"), warm=5, dof=2)
    try:
        c.js("window.__xvarForce=%d;window.__xcycForce=2;window.__resForce=1;fightDebugV1748().NEXT.main=1e15;showOffDebugV1752().NX.main=1e15;courtshipV1744.main={next:0}" % xvar); advance(c, 1.2)
        for _ in range(30):
            if court_ids(c): break
            advance(c, .6)
        c.js(COURT_FIX % dict(dance=2600, hold=5000, nthr=2, side=-1))
        ids = court_ids(c); print('court', ids)
        # paler, warmer female so the pair reads clearly (filming only)
        c.js("setInterval(()=>{const e=document.querySelector('#tank-main [data-fish-id=\"%s\"]');if(e)e.style.filter='hue-rotate(34deg) saturate(.6) brightness(1.4)'},200);1" % ids[1])
        def tgt(i):
            b = c.js("CAM.box(%s)" % json.dumps(ids))
            if b: b = dict(b); b['y'] += dy
            return b
        run(c, name, 15, fps=120, target=tgt, cam=Cam(pad=1.25, zmin=2.0, zmax=2.7, tau=.5), phase=PH_COURT2)
    finally: c.close()

def take_x_court(): _court('x_court', 0)            # variant 0: alongside, round her, backs in
def take_x_b_court(): _court('x_b_court', 2)        # variant 2/3: face to face, body bent round her snout

def take_x_stages():
    c = game("T.tank('main',[%s,%s,%s,%s,%s])" % (P('F', 1), P('F', 4), P('F', 9), P('M', AD), P('M', FULL, fins=98)), warm=3, dof=4)
    try:
        c.js(QUIET_LOOP); ids = ids_of(c)
        c.js(PARADE % dict(ids=json.dumps(ids), x0=130, v=14, y0=.22, dy=.13)); advance(c, 3)
        run(c, 'x_stages', 8, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.15, zmin=1.0, zmax=2.0, tau=.8))
    finally: c.close()

PH_FIGHT2 = ("(()=>{const f=fightDebugV1748().FIGHT.main;if(!f)return null;const g=id=>{const e=document.querySelector('#tank-main [data-fish-id=\\\"'+id+'\\\"]');return e?[e.dataset.m3||null,+(e.dataset.kap||0)]:null};"
             "return {seg:f.seg,round:f.round,win:f.win||null,a:g(f.a),b:g(f.b)}})()")

def take_x_fight():
    # swordtail males really fight: side by side, nips, circling, jaw lock
    c = game("T.tank('main',[%s,%s,%s,%s])" % (P('M', FULL, fins=98), P('M', AD + 8, fins=84), P('F', FULL), "T.fish('cory','M',30)"), warm=5, dof=5)
    try:
        c.js("fightDebugV1748().NEXT.main=0; courtshipV1744.main={next:1e12}; showOffDebugV1752().NX.main=1e15"); advance(c, .5)
        ids = None
        for _ in range(20):
            ids = json.loads(c.js("JSON.stringify((()=>{const f=fightDebugV1748().FIGHT.main;return f?[f.a,f.b]:null})())") or 'null')
            if ids: break
            c.js("fightDebugV1748().NEXT.main=0"); advance(c, .5)
        print('fight', ids)
        for _ in range(100):      # the engine builds its own sequence after 'approach': set ours once 'lateral' starts
            if c.js("(()=>{const f=fightDebugV1748().FIGHT.main;return f&&f.seg==='lateral'?1:0})()"): break
            advance(c, .1)
        print('seq', c.js("(()=>{const f=fightDebugV1748().FIGHT.main;if(!f)return 0;f.seq=['lateral','slap','nip','slap','pursue','spin','nip','pause'];f.si=0;return f.seq.length})()"))
        run(c, 'x_fight', 20, fps=60, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.1, zmin=1.8, zmax=2.6, tau=.35), phase=PH_FIGHT2)
    finally: c.close()

def take_x_breath():
    c = game("T.tank('main',[%s,%s])" % (P('F', FULL), "T.fish('cory','M',30)"), warm=3, dof=6)
    try:
        c.js(QUIET_LOOP); fid = ids_of(c)[0]
        c.js("(()=>{const B=behaviorDebugV1764().B;setInterval(()=>{const b=B['%s'];if(b){b.gz=null;b.nextGraze=performance.now()+1e9;}},200);return 1})()" % fid)
        c.js(HOVER % dict(id=fid)); advance(c, 4)
        run(c, 'x_breath', 7, target=lambda i: c.js("CAM.box(['%s'])" % fid), cam=Cam(tau=.6), zoom=4.6)
    finally: c.close()

def take_x_brood():
    c = game("T.tank('main',[%s,%s,%s])" % (P('F', FULL), P('M', FULL, fins=98), "T.fish('cory','M',30)"), warm=3, dof=3)
    try:
        c.js(QUIET_LOOP); c.js(BROOD % dict(sp='xipho', n=14, budget=0)); advance(c, 3)
        run(c, 'x_brood', 8, fixed=lambda i: full(i, 1.5 + .3 * i / 240, VW * .62, VH * .62))
    finally: c.close()

def take_x_hunt():
    c = game("T.tank('main',[%s,%s,%s])" % (P('F', FULL), P('M', AD), P('F', AD)), warm=3, dof=3)
    try:
        c.js(BROOD % dict(sp='xipho', n=12, budget=6)); advance(c, 2)
        c.js("(()=>{const r=Math.random;Math.random=()=>.45+r()*.55;return 1})()")   # filming only: the strike lands
        ids = json.loads(c.js("JSON.stringify(%s)" % FORCE_HUNT % dict(sp='xipho'))); print('hunter', ids)
        tgt = "(()=>{const a=CAM.box(['%s']),b=CAM.sel('#tank-main .brood45Fry[data-fid=\"%s\"]');if(!a)return b;if(!b)return a;const x0=Math.min(a.x-a.w/2,b.x-b.w/2),x1=Math.max(a.x+a.w/2,b.x+b.w/2),y0=Math.min(a.y-a.h/2,b.y-b.h/2),y1=Math.max(a.y+a.h/2,b.y+b.h/2);return {x:(x0+x1)/2,y:(y0+y1)/2,w:x1-x0,h:y1-y0}})()" % (ids[0], ids[1])
        run(c, 'x_hunt', 6, fps=120, target=lambda i: c.js(tgt), cam=Cam(pad=1.25, zmin=2.2, zmax=3.2, tau=.35),
            phase="(()=>{const h=huntDebugV1746().HUNT.main;return h?Object.fromEntries(Object.entries(h).filter(([k,v])=>typeof v!=='object').map(([k,v])=>[k,typeof v==='number'?+v.toFixed(0):v])):null})()")
    finally: c.close()

def take_x_net():
    c = game("T.tank('main',[%s,%s,%s])" % (P('F', FULL), P('M', AD), "T.fish('cory','M',30)"), warm=3, dof=3)
    try:
        c.js(BROOD % dict(sp='xipho', n=12, budget=0)); advance(c, 3)
        st = {'fid': c.js(PICK_FRY % dict(x=270, y=480, k=0))}; print('net fry', st['fid'])
        TAP = "(()=>{const im=document.querySelector('#tank-main .brood45Fry[data-fid=\"%s\"]');if(!im)return 0;const r=Math.random;Math.random=()=>%s;try{brood45Tap(im)}finally{Math.random=r}return 1})()"
        def every(i):
            if i == 40: c.js(TAP % (st['fid'], '.05'))
            if i == 110: c.js(TAP % (st['fid'], '.95'))
        run(c, 'x_net', 6.5, every=every, target=lambda i: c.js("(()=>{const b=%s;const n=CAM.sel('#tank-main .brood45Net');return b||n})()" % (FRY_BOX % st['fid'])), cam=Cam(tau=.45), zoom=3.4)
    finally: c.close()

def take_x_shimmy():
    # a weak swordtail shimmying: rocking on the spot, fins clamped, a faint white film; then the salt goes in
    c = game("T.tank('main',[%s,%s])" % (P('M', FULL, {'health': 50}, fins=98), "T.fish('cory','M',30)"), warm=3, dof=6)
    try:
        c.js(QUIET_LOOP); fid = ids_of(c)[0]
        c.js(HOVER % dict(id=fid)); advance(c, 3)
        c.js("(()=>{const B=behaviorDebugV1764().B;setInterval(()=>{const b=B['%s'],now=performance.now();if(!b)return;b.gz=null;b.nextGraze=now+1e9;b.nextShim=now+1e9;if(!b.shimUntil){const s=v16MotionStates.get('%s');b.shimUntil=now+60000;b.sx=s.x;b.sy=s.y;}},200);return 1})()" % (fid, fid))
        advance(c, 2.5)
        run(c, 'x_shimmy', 7, target=lambda i: c.js("CAM.box(['%s'])" % fid), cam=Cam(tau=.6), zoom=3.0)
    finally: c.close()

def take_x_oxygen():
    fish = [P('F', FULL), P('M', FULL, fins=98), P('F', AD), P('M', AD), P('F', AD), "T.fish('cory','M',30)", "T.fish('anc','F',50)"]
    c = game("window.bioPercentV14=()=>140;T.tank('main',[%s])" % ','.join(fish), warm=2, dof=0)
    try:
        c.js("window.bioPercentV14=()=>140;" + QUIET_LOOP)
        c.js("(()=>{const B=behaviorDebugV1764().B;tankArrayV14('main').filter(f=>f.species==='xipho').forEach((f,k)=>{const s=v16MotionStates.get(String(f.id));if(s){s.y=16+k*4;s.ty=s.y;}const b=B[f.id]||(B[f.id]={});b.nextDip=performance.now()+1e9;});setInterval(()=>{tankArrayV14('main').forEach(f=>{const b=B[f.id];if(b)b.nextDip=performance.now()+1e9;})},500);return 1})()")
        advance(c, 6)
        def every(i):
            if i in (45, 180): c.js("AFNiCA_CoryV1712.forceDash();1")
        run(c, 'x_oxygen', 8, every=every, fixed=lambda i: full(i, 2.1 + .15 * i / 240, VW * .45, VH * .12))
    finally: c.close()

TAKES = {k[5:]: v for k, v in globals().items() if k.startswith('take_')}
if __name__ == '__main__':
    for name in (sys.argv[1:] or list(TAKES)):
        t = time.time()
        try: TAKES[name]()
        except Exception as e: print('FAILED', name, repr(e)[:600], flush=True)
        print('take', name, round(time.time() - t), 's', flush=True)
