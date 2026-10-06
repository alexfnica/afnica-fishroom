# Raw takes for the "What's new: Platy" clip (same rig as takes_molly.py). Run: python takes_platy.py <take> [...]
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
import takes_molly as TM
from takes_molly import game, run, Cam, full, court_ids, PH_COURT, PH_FIGHT, COURT_FIX, VW, VH, QUIET_LOOP, PARADE, HOVER, advance
from takes import BROOD, PICK_FRY, FRY_BOX, FORCE_HUNT

AD, FULL = 18, 32                                  # S.platy.adult = 13: adult at 18 days, full grown from ~29
def P(sex, age, **gx):
    g = dict(color=85, pattern=80, fins=85, vitality=90, mutation=None); g.update(gx)
    return "T.fish('platy','%s',%d,%s)" % (sex, age, json.dumps({'genes': g}))
def ids_of(c): return json.loads(c.js("JSON.stringify(tankArrayV14('main').map(f=>String(f.id)))"))

def take_p_hero():
    c = game("T.tank('main',[%s,%s,%s,%s])" % (P('M', FULL, fins=95), P('F', FULL), P('F', AD), "T.fish('cory','M',30)"), warm=5, dof=6)
    try:
        c.js(QUIET_LOOP); mid = ids_of(c)[0]
        c.js(PARADE % dict(ids=json.dumps([mid]), x0=120, v=18, y0=.42, dy=0)); advance(c, 2)
        run(c, 'p_hero', 8, target=lambda i: c.js("CAM.box(['%s'])" % mid), cam=Cam(tau=.8), zoom=2.8)
    finally: c.close()

def take_p_court():
    # display beside her, nibbling under her belly, then the thrust (120 fps for slow motion)
    c = game("T.tank('main',[%s,%s,%s])" % (P('M', FULL, fins=95), P('F', FULL), "T.fish('cory','M',30)"), warm=5, dof=5)
    try:
        c.js("fightDebugV1748().NEXT.main=1e15;showOffDebugV1752().NX.main=1e15;courtshipV1744.main={next:0}"); advance(c, 1.2)
        for _ in range(30):
            if court_ids(c): break
            advance(c, .6)
        c.js(COURT_FIX % dict(dance=2600, hold=4000, nthr=2, side=-1))
        c.js("(()=>{const cc=courtshipV1744.main;cc.nib=true;return 1})()")
        ids = court_ids(c); print('court', ids)
        run(c, 'p_court', 15, fps=120, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.15, zmin=2.0, zmax=2.9, tau=.4), phase=PH_COURT)
    finally: c.close()

def take_p_stages():
    c = game("T.tank('main',[%s,%s,%s,%s,%s])" % (P('F', 1), P('F', 4), P('F', 8), P('M', AD), P('M', FULL, fins=95)), warm=3, dof=4)
    try:
        c.js(QUIET_LOOP); ids = ids_of(c)
        c.js(PARADE % dict(ids=json.dumps(ids), x0=130, v=14, y0=.22, dy=.13)); advance(c, 3)
        run(c, 'p_stages', 8, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.15, zmin=1.0, zmax=2.2, tau=.8))
    finally: c.close()

def take_p_fight():
    c = game("T.tank('main',[%s,%s,%s,%s])" % (P('M', FULL, fins=95), P('M', AD + 6, fins=82), P('F', FULL), "T.fish('cory','M',30)"), warm=5, dof=5)
    try:
        c.js("fightDebugV1748().NEXT.main=0; courtshipV1744.main={next:1e12}; showOffDebugV1752().NX.main=1e15"); advance(c, .5)
        ids = None
        for _ in range(20):
            ids = json.loads(c.js("JSON.stringify((()=>{const f=fightDebugV1748().FIGHT.main;return f?[f.a,f.b]:null})())") or 'null')
            if ids: break
            c.js("fightDebugV1748().NEXT.main=0"); advance(c, .5)
        print('fight', ids)
        print('seq', c.js("(()=>{const f=fightDebugV1748().FIGHT.main;if(!f)return 0;f.seq=['lateral','nip','spin','nip','lock','nip','pause'];f.si=0;f.segEnd=performance.now()+1600;return f.seq.length})()"))
        run(c, 'p_fight', 12, fps=60, target=lambda i: c.js("CAM.box(%s)" % json.dumps(ids)), cam=Cam(pad=1.1, zmin=2.0, zmax=2.9, tau=.35), phase=PH_FIGHT)
    finally: c.close()

def take_p_breath():
    c = game("T.tank('main',[%s,%s])" % (P('F', FULL), "T.fish('cory','M',30)"), warm=3, dof=6)
    try:
        c.js(QUIET_LOOP); fid = ids_of(c)[0]
        c.js(HOVER % dict(id=fid)); advance(c, 4)
        run(c, 'p_breath', 7, target=lambda i: c.js("CAM.box(['%s'])" % fid), cam=Cam(tau=.6), zoom=5.0)
    finally: c.close()

def take_p_brood():
    # the brood just born: tiny fry hiding in the plants and under the surface, the mother nearby
    c = game("T.tank('main',[%s,%s,%s])" % (P('F', FULL), P('M', FULL, fins=95), "T.fish('cory','M',30)"), warm=3, dof=3)
    try:
        c.js(QUIET_LOOP); c.js(BROOD % dict(sp='platy', n=14, budget=0)); advance(c, 3)
        run(c, 'p_brood', 8, fixed=lambda i: full(i, 1.5 + .3 * i / 240, VW * .62, VH * .62))
    finally: c.close()

def take_p_hunt():
    # an adult snaps up a newborn fry (120 fps for slow motion)
    c = game("T.tank('main',[%s,%s,%s])" % (P('F', FULL), P('M', AD), P('F', AD)), warm=3, dof=3)
    try:
        c.js(BROOD % dict(sp='platy', n=12, budget=6)); advance(c, 2)
        c.js("(()=>{const r=Math.random;Math.random=()=>.45+r()*.55;return 1})()")   # filming only: the strike lands
        ids = json.loads(c.js("JSON.stringify(%s)" % FORCE_HUNT % dict(sp='platy'))); print('hunter', ids)
        tgt = "(()=>{const a=CAM.box(['%s']),b=CAM.sel('#tank-main .brood45Fry[data-fid=\"%s\"]');if(!a)return b;if(!b)return a;const x0=Math.min(a.x-a.w/2,b.x-b.w/2),x1=Math.max(a.x+a.w/2,b.x+b.w/2),y0=Math.min(a.y-a.h/2,b.y-b.h/2),y1=Math.max(a.y+a.h/2,b.y+b.h/2);return {x:(x0+x1)/2,y:(y0+y1)/2,w:x1-x0,h:y1-y0}})()" % (ids[0], ids[1])
        run(c, 'p_hunt', 6, fps=120, target=lambda i: c.js(tgt), cam=Cam(pad=1.25, zmin=2.4, zmax=3.4, tau=.35),
            phase="(()=>{const h=huntDebugV1746().HUNT.main;return h?Object.fromEntries(Object.entries(h).filter(([k,v])=>typeof v!=='object').map(([k,v])=>[k,typeof v==='number'?+v.toFixed(0):v])):null})()")
    finally: c.close()

def take_p_net():
    c = game("T.tank('main',[%s,%s,%s])" % (P('F', FULL), P('M', AD), "T.fish('cory','M',30)"), warm=3, dof=3)
    try:
        c.js(BROOD % dict(sp='platy', n=12, budget=0)); advance(c, 3)
        st = {'fid': c.js(PICK_FRY % dict(x=270, y=480, k=0))}; print('net fry', st['fid'])
        TAP = "(()=>{const im=document.querySelector('#tank-main .brood45Fry[data-fid=\"%s\"]');if(!im)return 0;const r=Math.random;Math.random=()=>%s;try{brood45Tap(im)}finally{Math.random=r}return 1})()"
        def every(i):
            if i == 40: c.js(TAP % (st['fid'], '.05'))          # it senses the net and darts away
            if i == 110: c.js(TAP % (st['fid'], '.95'))         # second try: caught
        run(c, 'p_net', 6.5, every=every, target=lambda i: c.js("(()=>{const b=%s;const n=CAM.sel('#tank-main .brood45Net');return b||n})()" % (FRY_BOX % st['fid'])), cam=Cam(tau=.45), zoom=3.4)
    finally: c.close()

def take_p_oxygen():
    fish = [P('F', FULL), P('M', FULL, fins=95), P('F', AD), P('M', AD), P('F', AD), "T.fish('cory','M',30)", "T.fish('anc','F',50)"]
    c = game("window.bioPercentV14=()=>140;T.tank('main',[%s])" % ','.join(fish), warm=2, dof=0)
    try:
        c.js("window.bioPercentV14=()=>140;" + QUIET_LOOP)
        c.js("(()=>{const B=behaviorDebugV1764().B;tankArrayV14('main').filter(f=>f.species==='platy').forEach((f,k)=>{const s=v16MotionStates.get(String(f.id));if(s){s.y=16+k*4;s.ty=s.y;}const b=B[f.id]||(B[f.id]={});b.nextDip=performance.now()+1e9;});setInterval(()=>{tankArrayV14('main').forEach(f=>{const b=B[f.id];if(b)b.nextDip=performance.now()+1e9;})},500);return 1})()")
        advance(c, 6)
        def every(i):
            if i in (45, 180): c.js("AFNiCA_CoryV1712.forceDash();1")
        run(c, 'p_oxygen', 8, every=every, fixed=lambda i: full(i, 2.1 + .15 * i / 240, VW * .45, VH * .12))
    finally: c.close()

TAKES = {k[5:]: v for k, v in globals().items() if k.startswith('take_')}
if __name__ == '__main__':
    for name in (sys.argv[1:] or list(TAKES)):
        t = time.time()
        try: TAKES[name]()
        except Exception as e: print('FAILED', name, repr(e)[:600], flush=True)
        print('take', name, round(time.time() - t), 's', flush=True)
