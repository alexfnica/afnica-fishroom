# V17.96 male fights: headless main tank (2 adult males + 1 female by default), fake 30 fps clock. Counts fights and how they
# ended, fight length, 3D frames shown, max step per frame of each fish outside darts, photo opacity during the 3D part, errors.
# Run: D:/Blender/5.2/python/bin/python.exe measure_fight96.py   (env SEED, SECS, AF_PORT, PRE, FISH)
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = os.environ.get('FISH') or "[T.fish('anc','M',40),T.fish('anc','M',38),T.fish('anc','F',36)]"
SECS = int(os.environ.get('SECS', '300'))
HOOK = r"""window.__S=new WeakMap();window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};
 window.__ends=[];setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1;"""
REC = r"""(()=>{const F=anc90Debug().F96['tank-main'];const L=window.__f96last;if(L&&!L.logged){L.logged=1;__ends.push([L.end,+L.t.toFixed(1),L.ph,L.T?+L.T.toFixed(1):0]);}
 return JSON.stringify({f:F?[F.ph,F.cur||'',F.n]:null,fish:[...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>{const s=__S.get(e)||{},a=e.querySelector('.ancArt');
 return [+e.dataset.ancX,e.dataset.ancMode,s.dart95?1:0,a&&a.style.opacity!==''?+a.style.opacity:1,!!e.querySelector('canvas.anc96p')]})})})()"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=HOOK + os.environ.get('PRE', '') + ';' + (SEED % int(os.environ['SEED']) if os.environ.get('SEED') else '1'))
try:
    L = []
    for i in range(SECS * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30)); L.append(json.loads(c.js(REC)))
    fights = {}; fr3 = 0; op = []
    for i, r in enumerate(L):
        if r['f']:
            fights.setdefault(r['f'][2], []).append(r['f'][0])
            if r['f'][0] == 'fight' and r['f'][1]: fr3 += 1; op.append(min(x[3] for x in r['fish'][:2]))
    print('fights started %d | frames with the 3D pair %d (%.1f s) | min photo opacity during 3D %.2f' % (len(fights), fr3, fr3 / 30, min(op) if op else 1))
    for n, ph in fights.items(): print('  fight %d: walk %.1f s, 3D %.1f s' % (n, ph.count('walk') / 30, ph.count('fight') / 30))
    print('ends', c.js('JSON.stringify(__ends)'), 'counters', c.js('JSON.stringify(anc90Debug().C96)'), 'cooldowns', c.js('JSON.stringify(anc90Debug().CD96)'))
    for k in range(len(L[0]['fish'])):
        mx = 0; at = None
        for i in range(1, len(L)):
            a, b = L[i - 1]['fish'][k], L[i]['fish'][k]
            if b[2] or a[1] != b[1] and 'cave' in (a[1] + b[1]): continue
            d = abs(b[0] - a[0])
            if d > mx: mx, at = d, (i, a[1], b[1])
        print('fish %d max step outside darts %.2f px/frame at %s' % (k, mx, at))
    print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
finally: c.close()
