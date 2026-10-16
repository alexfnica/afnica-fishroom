# Bristlenose audit stills (throw-away headless game, never the owner's save): one sharp close-up per state.
# Run: D:/Blender/5.2/python/bin/python.exe audit_anc90.py <main|breeder|fry>
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import CLUTCH, PHASE, SEED
OUT = os.path.join(HERE, 'raw', 'audit90'); os.makedirs(OUT, exist_ok=True)
INFO = r'''((tank)=>{const t=document.getElementById('tank-'+tank),cv=t.querySelector('.ancBreedingCave');const cr=cv?cv.getBoundingClientRect():null;
 return JSON.stringify([...t.querySelectorAll('[data-fish-id]')].filter(e=>e.dataset.ancMode!==undefined).map(e=>{const r=e.getBoundingClientRect(),m=/scaleX\(([-\d.]+)\)/.exec(e.style.transform||'');
 return {id:e.dataset.fishId,m:e.dataset.ancMode,s:e.dataset.ancSurface,x:r.x,y:r.y,w:r.width,h:r.height,sx:m?+m[1]:1,tr:e.style.transform,
  cave:cr?(r.right>cr.x+10&&r.x<cr.right-10&&r.bottom>cr.y&&r.y<cr.bottom):false}}))})'''
def clip_on(f, zoom=3.0, w=None):
    cx, cy = f['x'] + f['w'] / 2, f['y'] + f['h'] / 2; W, H = VW / zoom, VH / zoom
    return dict(x=min(max(cx - W / 2, 0), VW - W), y=min(max(cy - H / 2, 0), VH - H), width=W, height=H, scale=zoom)
def run(c, tank, want, seconds, step=.2):
    got = {}
    for i in range(int(seconds / step)):
        advance(c, step)
        F = json.loads(c.js(INFO + "('%s')" % tank)); ph = c.js(PHASE)
        for f in F:
            for k, cond in want.items():
                if k in got: continue
                try: ok = cond(f, ph)
                except Exception: ok = False
                if ok:
                    shot(c, os.path.join(OUT, k + '.jpg'), clip=clip_on(f)); got[k] = round(i * step, 1); print('shot', k, got[k], f.get('m'), f.get('s'), ph, flush=True)
        if len(got) == len(want): break
    print('missing', [k for k in want if k not in got])

def main():
    c = anc_game(tank='main', fish="[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30)]", warm=2, pre=SEED % 11, dsf=2)
    try:
        shot(c, os.path.join(OUT, 'main_overview.jpg'))
        run(c, 'main', {
            'rest': lambda f, p: f['m'] == 'rest' and f['s'] == 'substrate',
            'crawl': lambda f, p: f['m'] == 'move' and f['s'] == 'substrate' and abs(f['sx']) > .99,
            'turn': lambda f, p: f['s'] == 'substrate' and abs(f['sx']) < .6,
            'rasp': lambda f, p: f['m'] in ('graze', 'forage') and f['s'] == 'substrate',
            'glass': lambda f, p: f['s'] == 'glass' and f['m'] == 'graze',
            'cross': lambda f, p: f['cave'] and 'translate' in f['tr'] and f['m'] in ('move', 'toWall'),
            'mainfan': lambda f, p: f['m'] == 'fanning',
        }, 240)
    finally: c.close()

def breeder():
    c = anc_game(dsf=2)
    try:
        c.js(CLUTCH % dict(stage='spawning', phase=os.environ.get('PH', 'male-approach'), laid=0, hatch=5, rel=10))
        c.js("(()=>{const D=ancDebugV1789().DBG;D.fan=6;D.guard=6;return 1})()")
        c.js("(()=>{let n=0;const t=setInterval(()=>{const c=st.ancClutch;if(c&&c.phase==='trapped'&&++n>40)c.trapDays=0},250);return 1})()")
        run(c, 'breeder', {
            'pair_enter': lambda f, p: p in ('male-approach', 'male-enter') and f['cave'],
            'pair_in': lambda f, p: p in ('trapped',) and f['cave'],
            'laying': lambda f, p: p == 'laying' and f['cave'],
            'fan': lambda f, p: f['m'] == 'fanning' and p == 'eggs',
            'leave': lambda f, p: p == 'eggs' and f['m'] not in ('fanning','cave-guard','attach','rest','graze','forage','move') and 'cave' in f['m'],
            'guard': lambda f, p: f['m'] == 'cave-guard',
        }, 160)
        print('modes now', c.js(INFO + "('breeder')")[:300])
    finally: c.close()

def fry():
    c = anc_game(dsf=2)
    try:
        c.js(CLUTCH % dict(stage='yolk', phase='done', laid=9, hatch=-4, rel=0)); advance(c, 3)
        c.js("(()=>{st.ancClutch.lastDay=-1;advanceAncClutch40();renderV103Breeder();return st.ancClutch.stage})()"); advance(c, 6)
        shot(c, os.path.join(OUT, 'fry_emerge.jpg'), clip=dict(x=0, y=VH * .55, width=VW / 2.5, height=VH / 2.5, scale=2.5))
        b = json.loads(c.js("JSON.stringify((()=>{const r=document.querySelector('.tank .ancBreedingCave').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})())"))
        shot(c, os.path.join(OUT, 'fry_cave.jpg'), clip=dict(x=max(0, b['x'] - 120), y=min(VH - VH / 3, b['y'] - 40), width=VW / 3, height=VH / 3, scale=3))
    finally: c.close()
    c = anc_game(tank='fry', fish="[" + ",".join("T.fish('anc','%s',%d)" % (s, a) for s, a in [('M', 3), ('F', 4), ('M', 6), ('F', 9), ('M', 12)]) + "]", warm=20, dsf=2)
    try:
        F = json.loads(c.js(INFO + "('fry')")); F = [f for f in F if f['s'] == 'substrate'] or F
        shot(c, os.path.join(OUT, 'young.jpg'), clip=clip_on(F[0], 2.5))
        shot(c, os.path.join(OUT, 'fry_overview.jpg'))
    finally: c.close()

if __name__ == '__main__':
    globals()[sys.argv[1]]()

def cross():
    seed = int(os.environ.get('SEED', '3'))
    c = anc_game(tank='main', fish="[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30),T.fish('anc','M',30)]", warm=2, pre=SEED % seed, dsf=2)
    try:
        run(c, 'main', {'cross%d' % seed: lambda f, p: f['cave'] and 'translate' in f['tr'] and f['m'] not in ('fanning',) and not f['m'].startswith('cave')}, 300)
    finally: c.close()
