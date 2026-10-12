# V17.89 bristlenose review clips + measurements (throw-away headless game, never the owner's save).
# Run: D:/Blender/5.2/python/bin/python.exe takes_anc89.py <take> [--film]
import os, sys, json, math, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CLUTCH = ("(()=>{const a=tankArrayV14('breeder'),m=a.find(f=>f.sex==='M'),f=a.find(f=>f.sex==='F');"
          "st.ancClutch={id:'t89',stage:'%(stage)s',phase:'%(phase)s',seconds:0,count:34,mom:f.id,dad:m.id,parents:{mom:JSON.parse(JSON.stringify(f)),dad:JSON.parse(JSON.stringify(m))},"
          "attempt:1,lossRoll:.9,lastDay:st.day,laidDay:st.day-%(laid)d,hatchDay:st.day+%(hatch)d,releaseDay:st.day+%(rel)d,fungus:0,trapDay:st.day,trapDays:2};return 1})()")
FISH_JS = ("(id=>{const e=document.querySelector('[data-fish-id=\"'+id+'\"]');if(!e)return null;const d=e.dataset,m=/scaleX\\(([-\\d.]+)\\)/.exec(e.style.transform||'');"
           "return {x:+d.ancX,y:+d.ancY,m:d.ancMode,sx:m?+m[1]:null,op:e.style.opacity,fp:d.fanPh89?+d.fanPh89:null}})")

def cave_clip(c, zoom=2.0, dx=-40, dy=-20):
    b = json.loads(c.js("JSON.stringify((()=>{const r=document.querySelector('.tank .ancBreedingCave').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})())"))
    w, h = VW / zoom, VH / zoom
    x = min(max(b['x'] + b['w'] / 2 + dx - w / 2, 0), VW - w); y = min(max(b['y'] + b['h'] / 2 + dy - h / 2, 0), VH - h)
    return dict(x=x, y=y, width=w, height=h, scale=zoom)

def encode(name, w=960, h=540):
    out = os.path.join(ROOT, 'AFNICA_Anc89_%s.mp4' % name)
    subprocess.run([r'D:\Blender\blender.exe', '-b', '-P', os.path.join(HERE, 'encode_plain.py'), '--', os.path.join(HERE, 'raw', 'a89_' + name), out, str(w), str(h)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('clip', out, os.path.exists(out))

def analyse(L, key, fps=30, label=''):
    """max step per frame, backwards frames (moving against the drawn facing)"""
    pts = [l.get(key) for l in L]
    mx = 0; back = 0; at = None
    for i in range(1, len(pts)):
        a, b = pts[i - 1], pts[i]
        if not a or not b or a['x'] != a['x'] or b['x'] != b['x']: continue
        d = math.hypot(b['x'] - a['x'], b['y'] - a['y'])
        if d > mx: mx, at = d, (i, a.get('m'), b.get('m'))
        vx = b['x'] - a['x']
        if abs(vx) > .25 and b.get('sx') and (vx > 0) != (b['sx'] > 0): back += 1
    modes = []
    for p in pts:
        m = p and p.get('m')
        if not modes or modes[-1][0] != m: modes.append([m, 1])
        else: modes[-1][1] += 1
    print(label, key, 'max step %.2f px/frame' % mx, at, 'backward frames', back)
    print('  modes', [(m, round(n / fps, 1)) for m, n in modes])

# ------------------------------------------------------------------ 1 + 6: fanning with the tail out, then guarding
def take_fan(film=False):
    c = anc_game()
    try:
        m, f = ids(c)
        c.js(CLUTCH % dict(stage='eggs', phase='done', laid=1, hatch=4, rel=9))
        c.js("(()=>{const D=ancDebugV1789().DBG;D.fan=6;D.guard=6;return 1})()")
        c.js("(()=>{const a=tankArrayV14('breeder');a.splice(a.findIndex(f=>f.sex==='F'),1);renderV103Breeder();return 1})()")   # the female out of the shot
        for k in range(80):
            md = c.js(FISH_JS + "('%s')" % m)
            if md and md.get('m') == 'fanning' and md.get('fp') is not None: break
            advance(c, .5)
        print('fanning after', k * .5, 's', md)
        c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1")
        cap = lambda i: '1+6  Male in the cave: tail out of the mouth, slow fanning strokes with holds (ref. 1:35). Then he turns inside and guards the entrance, head and bristles out (ref. 1:17); leaves head first, turns, walks back in.'
        L = []
        def log(i): return {'m': c.js(FISH_JS + "('%s')" % m), 'f': c.js(FISH_JS + "('%s')" % f)}
        clip = cave_clip(c, 2.0, dx=-60) if film else None
        if film:
            film_(c, 'a89_fan', 36, cap, clip, L, log)
        else:
            for i in range(40 * 30):
                c.js('__afStep(%f, 2)' % (1000 / 30)); L.append(log(i))
        analyse(L, 'm', label='male'); print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
        shot(c, os.path.join(HERE, 'raw', 'anc_probe', 'fan_end.jpg'), clip=cave_clip(c, 3.0, dx=-60))
    finally: c.close()
    if film: encode('fan')

def film_(c, name, seconds, cap, clip, L, log):
    film(c, name, seconds, caption=cap, clip=clip, log=lambda i: L.append(log(i)) or {})


# ------------------------------------------------------------------ 2: the spawning visit (both inside, fins churning)
PHASE = "(()=>{const c=st.ancClutch;return c?(c.stage==='spawning'?c.phase:c.stage):null})()"
def take_spawn(do_film=False):
    c = anc_game()
    try:
        m, f = ids(c)
        c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1")
        c.js(CLUTCH % dict(stage='spawning', phase='female-approach', laid=0, hatch=5, rel=10))
        c.js("(()=>{const D=ancDebugV1789().DBG;D.fan=6;D.guard=5;return 1})()")
        for k in range(200):
            if c.js(PHASE) == 'female-back': break
            advance(c, .25)
        print('female-back after', k * .25, 's')
        T = {'trapped': None}
        def every(i):
            ph = c.js(PHASE)
            if ph == 'trapped':
                if T['trapped'] is None: T['trapped'] = i
                elif i - T['trapped'] > 30 * 11: c.js("st.ancClutch.trapDays=0;1")     # end the (1-2 game day) wait after 11 s
        CAPS = {'female-back': '2  She walks into his cave head first (the old code backed her in)',
                'male-approach': '2  He follows her to the cave', 'male-enter': '2  He follows her in',
                'trapped': '2  Both inside: his tail churning at the mouth, she pushes to the entrance now and then (ref. 2:08-2:28)',
                'laying': '2  Laying: still both inside, fins churning (ref. 2:08-2:28)',
                'female-exit': '2  She leaves head first; he stays with the clutch',
                'eggs': '2  Eggs laid: he turns round inside and guards, then fans (point 1/6)'}
        L = []
        def log(i): return {'m': c.js(FISH_JS + "('%s')" % m), 'f': c.js(FISH_JS + "('%s')" % f), 'ph': c.js(PHASE)}
        if do_film:
            film(c, 'a89_spawn', 50, caption=lambda i: CAPS.get(c.js(PHASE), ''), clip=cave_clip(c, 2.0, dx=-60), every=every, log=lambda i: L.append(log(i)) or {})
        else:
            for i in range(50 * 30):
                every(i); c.js('__afStep(%f, 2)' % (1000 / 30)); L.append(log(i))
        analyse(L, 'm', label='male'); analyse(L, 'f', label='female')
        ph = []
        for l in L:
            if not ph or ph[-1][0] != l['ph']: ph.append([l['ph'], 1])
            else: ph[-1][1] += 1
        print('phases', [(p, round(n / 30, 1)) for p, n in ph]); print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
    finally: c.close()
    if do_film: encode('spawn')


# ------------------------------------------------------------------ 3: young - still clusters, short hops, a heads-in pile on a wafer
YOUNG = "[" + ",".join("T.fish('anc','%s',%d)" % (sx, a) for sx, a in [('M', 5), ('F', 6), ('M', 7), ('F', 8), ('M', 6), ('F', 9), ('M', 10)]) + "]"
def ystats(c, ids_, tank):
    return c.js("JSON.stringify(%s.map(id=>{const e=document.querySelector('#tank-%s [data-fish-id=\"'+id+'\"]');return e?[+e.dataset.ancX,+e.dataset.ancY,e.dataset.ancMode,e.dataset.ancSurface]:null}))" % (json.dumps(ids_), tank))
def take_young(do_film=False):
    c = anc_game(tank='fry', fish=YOUNG, warm=2)
    try:
        c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1")
        I = ids(c, 'fry'); advance(c, 45)                      # let them settle into their rhythm
        L = []
        def every(i):
            if i == 30 * 22:      # filming only: the wafer lands near the group (they still have to notice it and come)
                c.js("(()=>{st.wafers=5;const t=document.getElementById('tank-fry'),xs=%s.map(id=>+(t.querySelector('[data-fish-id=\"'+id+'\"]')||{dataset:{}}).dataset.ancX).filter(x=>x>0),gx=xs.reduce((a,b)=>a+b,0)/xs.length+60,q=Math.max(0,Math.min(1,(gx/t.clientWidth-.28)/.44)),r=Math.random;Math.random=()=>q;try{dropWaferV1743('fry')}finally{Math.random=r}return q})()" % json.dumps(I))
        def cap(i):
            return ('3  Young bristlenose: long still clings close together, short hops (ref. 6:09-6:16)' if i < 30 * 23 else
                    '3  On a wafer the young pile up heads-in, overlapping, barely moving, tails wiggling (ref. 4:06-5:57)')
        if do_film:
            CAMS = {'x': None}
            def follow(i):
                P = json.loads(ystats(c, I, 'fry')); xs = sorted(p[0] for p in P if p and p[3] == 'substrate')
                mx = xs[len(xs) // 2] if xs else VW / 2
                CAMS['x'] = mx if CAMS['x'] is None else CAMS['x'] + (mx - CAMS['x']) * .03
                w, h = VW / 2.4, VH / 2.4
                return dict(x=min(max(CAMS['x'] - w / 2, 0), VW - w), y=VH - h, width=w, height=h, scale=2.4)
            film(c, 'a89_young', 50, caption=cap, clip=follow, every=every, log=lambda i: L.append(json.loads(ystats(c, I, 'fry'))) or {})
        else:
            for i in range(50 * 30):
                every(i); c.js('__afStep(%f, 2)' % (1000 / 30)); L.append(json.loads(ystats(c, I, 'fry')))
        for part, (a, b) in (('cling', (0, 660)), ('wafer', (1050, 1500))):
            still = mv = 0; mx = 0; spreads = []
            for i in range(a + 1, b):
                xs = [p[0] for p in L[i] if p]; spreads.append(max(xs) - min(xs))
                for p0, p1 in zip(L[i - 1], L[i]):
                    if not p0 or not p1: continue
                    d = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); mx = max(mx, d)
                    if d > 3: print('  jump', i, round(d, 2), p0, p1)
                    if d < .05: still += 1
                    else: mv += 1
            print(part, 'still %.0f%%' % (100 * still / max(1, still + mv)), 'max step %.2f' % mx, 'x-spread avg %.0f px' % (sum(spreads) / len(spreads)))
        from collections import Counter
        print('modes in wafer part', Counter(p[2] for l in L[1050:1500] for p in l if p).most_common()); print('wafers', c.js("JSON.stringify([st.wafers,document.querySelectorAll('#tank-fry [class*=afer]').length])"))
        print('modes end', [p[2] for p in L[-1] if p]); print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
    finally: c.close()
    if do_film: encode('young')

def take_emerge(do_film=False):
    c = anc_game()
    try:
        c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1")
        c.js(CLUTCH % dict(stage='yolk', phase='done', laid=9, hatch=-4, rel=0))
        advance(c, 3)
        c.js("(()=>{st.ancClutch.lastDay=-1;advanceAncClutch40();renderV103Breeder();return st.ancClutch.stage})()"); advance(c, .3)
        cap = '3  Fry leave the cave: short darts, then they settle close together near the cave and sit still'
        if do_film:
            film(c, 'a89_emerge', 16, caption=cap, clip=cave_clip(c, 2.0, dx=-100, dy=0))
        else: advance(c, 16)
        print('stage', c.js("st.ancClutch.stage"), 'errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
    finally: c.close()
    if do_film: encode('emerge')


# ------------------------------------------------------------------ 4: glass - long still holds, slow glide; quick head-first turn on the sand
GL_JS = (r"(id=>{const e=document.querySelector('#tank-main [data-fish-id=\"'+id+'\"]');if(!e)return null;const d=e.dataset,m=/scaleX\(([-\d.]+)\)/.exec(e.style.transform||'');"
         r"return [+d.ancX,+d.ancY,d.ancMode,d.ancSurface,m?+m[1]:1,+(e.style.getPropertyValue('--anc-glass')||0)]})")
SEED = "(s=>{let a=s>>>0;Math.random=()=>{a=(a+0x6D2B79F5)>>>0;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296};})(%d);"
def first_turn(seed):
    c = anc_game(tank='main', fish="[T.fish('anc','F',36)]", warm=2, pre=SEED % seed)
    try:
        fid = ids(c, 'main')[0]
        for i in range(60 * 30):
            c.js('__afStep(%f, 2)' % (1000 / 30)); p = c.js(GL_JS + "('%s')" % fid)
            if p and abs(p[4]) < .999 and p[3] == 'substrate': return i
    finally: c.close()
def take_glass(do_film=False):
    seed = 7; ft = first_turn(seed); print('first sand turn at frame', ft)
    c = anc_game(tank='main', fish="[T.fish('anc','F',36)]", warm=2, pre=SEED % seed)
    for i in range(max(0, (ft or 0) - 45)): c.js('__afStep(%f, 2)' % (1000 / 30))
    try:
        fid = ids(c, 'main')[0]
        # part A: on the sand (turns)
        LA = []
        p0 = c.js(GL_JS + "('%s')" % fid); w_, h_ = VW / 2.2, VH / 2.2
        clipA = dict(x=min(max(p0[0] - w_ / 2, 0), VW - w_), y=min(max(p0[1] - h_ / 2, 0), VH - h_), width=w_, height=h_, scale=2.2)
        if do_film: film(c, 'a89_turn', 5, caption='4  On the sand: a quick head-first turn, about half a second (ref. 10:05)', clip=clipA, log=lambda i: LA.append(c.js(GL_JS + "('%s')" % fid)) or {})
        else:
            for i in range(5 * 30): c.js('__afStep(%f, 2)' % (1000 / 30)); LA.append(c.js(GL_JS + "('%s')" % fid))
        turns = []; t0 = None
        for i, p in enumerate(LA):
            if p and abs(p[4]) < .999 and t0 is None: t0 = i
            if p and abs(p[4]) >= .999 and t0 is not None: turns.append(round((i - t0) / 30, 2)); t0 = None
        print('sand turns (s)', turns)
        for k in range(600):
            p = c.js(GL_JS + "('%s')" % fid)
            if p and p[3] == 'glass' and p[2] == 'graze': break
            advance(c, 1)
        print('on glass after', k, 's', p)
        c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1")
        LB = []
        def clipB(i):
            p = LB[-1] if LB else c.js(GL_JS + "('%s')" % fid)
            w, h = VW / 2.2, VH / 2.2
            return dict(x=min(max(p[0] - w / 2, 0), VW - w), y=min(max(p[1] - h / 2, 0), VH - h), width=w, height=h, scale=2.2)
        if do_film: film(c, 'a89_glass', 24, caption='4  On the glass: long still holds (5-14 s), then a slow continuous glide (ref. 9:58-10:05)', clip=clipB, log=lambda i: LB.append(c.js(GL_JS + "('%s')" % fid)) or {})
        else:
            for i in range(24 * 30): c.js('__afStep(%f, 2)' % (1000 / 30)); LB.append(c.js(GL_JS + "('%s')" % fid))
        holds = []; run = 0; mx = 0; sp = []
        for a, b in zip(LB, LB[1:]):
            if not a or not b or a[0] is None or b[0] is None: continue
            d = math.hypot(b[0] - a[0], b[1] - a[1]); mx = max(mx, d)
            if d < .02: run += 1
            else:
                if run > 30: holds.append(round(run / 30, 1))
                run = 0; sp.append(d * 30)
        if run > 30: holds.append(round(run / 30, 1))
        print('glass holds (s)', holds, 'glide speed avg %.1f px/s max step %.2f' % (sum(sp) / max(1, len(sp)), mx), 'modes', sorted(set(p[2] for p in LB if p)))
        print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
    finally: c.close()
    if do_film: encode('turn'); encode('glass')


# ------------------------------------------------------------------ 5: the brood seen in the mouth (eggs, then wrigglers)
def take_brood(do_film=False):
    c = anc_game()
    try:
        m, f = ids(c)
        c.js(CLUTCH % dict(stage='eggs', phase='done', laid=0, hatch=5, rel=10))
        c.js("(()=>{const a=tankArrayV14('breeder');a.splice(a.findIndex(f=>f.sex==='F'),1);renderV103Breeder();const D=ancDebugV1789().DBG;D.fan=60;return 1})()")
        for k in range(80):
            md = c.js(FISH_JS + "('%s')" % m)
            if md and md.get('m') == 'fanning' and md.get('fp') is not None: break
            advance(c, .5)
        advance(c, 1)
        def every(i):
            if i == 150: c.js("(()=>{const c=st.ancClutch;c.laidDay=st.day-4;c.hatchDay=st.day+1;return 1})()")     # eyed eggs
            if i == 300: c.js("(()=>{const c=st.ancClutch;c.stage='yolk';c.hatchDay=st.day;c.releaseDay=st.day+5;return 1})()")
        cap = lambda i: ('5  Fresh eggs: a bright orange grape-like clump, seen in the mouth beside his tail (ref. 1:45, 8:15)' if i < 150 else
                         '5  Eyed eggs: darker, eye spots showing' if i < 300 else '5  Hatched: wrigglers on their big orange yolk sacs, twitching now and then')
        if do_film: film(c, 'a89_brood', 15, caption=cap, clip=cave_clip(c, 3.2, dx=-55, dy=10), every=every)
        print('done')
    finally: c.close()
    if do_film: encode('brood')


# ------------------------------------------------------------------ main tank readiness: he walks in, stops tail-out, cycles, then readiness ends
def take_mainready(do_film=False):
    c = anc_game(tank='main', fish="[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36)]", warm=1)
    try:
        c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1")
        c.js("(()=>{const D=ancDebugV1789().DBG;D.fan=8;D.guard=5;return 1})()")
        m = ids(c, 'main')[0]; FJ = FISH_JS.replace("document.querySelector('[data-fish-id", "document.querySelector('#tank-main [data-fish-id")
        L = []
        for i in range(70 * 30):
            if i == 60 * 30: c.js("(()=>{const f=tankArrayV14('main')[0];f.ancCaveCycleStart=st.day-5;return 1})()")   # readiness over
            c.js('__afStep(%f, 2)' % (1000 / 30)); L.append({'m': c.js(FJ + "('%s')" % m)})
        analyse(L, 'm', label='main male'); print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
    finally: c.close()


# ------------------------------------------------------------------ D + C: on the sand - burst, glide, dead stop; flat fins
def take_sand(do_film=False):
    c = anc_game(tank='main', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", warm=3, pre=SEED % 11)
    try:
        I = ids(c, 'main'); fid = I[1]; CAMS = {'x': None, 'y': None}
        def follow(i):
            p = c.js(GL_JS + "('%s')" % fid); w, h = VW / 2.6, VH / 2.6
            if p and p[0] is not None:
                CAMS['x'] = p[0] if CAMS['x'] is None else CAMS['x'] + (p[0] - CAMS['x']) * .06
                CAMS['y'] = p[1] if CAMS['y'] is None else CAMS['y'] + (p[1] - CAMS['y']) * .06
            return dict(x=min(max(CAMS['x'] - w / 2, 0), VW - w), y=min(max(CAMS['y'] - h / 2, 0), VH - h), width=w, height=h, scale=2.6)
        cap = 'On the sand: long stays rasping (head pressed down), slow smooth crawl with the fins stepping, a low swim only for long trips (ref. ILotQrXzuu0 24-31 s)'
        if do_film: film(c, 'a89_sand', 40, caption=cap, clip=follow)
    finally: c.close()
    if do_film: encode('sand')

if __name__ == '__main__':
    globals()['take_' + sys.argv[1]]('--film' in sys.argv)
