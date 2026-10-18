# V17.99 bristles: per frame the trailing bend (css px at the tip) and sway amplitude for every male bristle layer drawn,
# split by speed; console errors. Run: python probe_t99.py [secs]
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
c = anc_game(tank='main', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", warm=1, pre=SEED % 7 + "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1;")
try:
    c.js('window.__T99=[];1'); L = []
    for i in range(int(sys.argv[1] if len(sys.argv) > 1 else 60) * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30))
        if i % 30 == 29: L += json.loads(c.js('JSON.stringify(window.__T99.splice(0))'))
    for view in ('side', 'glass'):
        for lo, hi, nm in ((0, 3, 'resting'), (3, 20, 'slow'), (20, 1e9, 'moving')):
            q = [r for r in L if r[3] == view and lo <= r[2] < hi]
            if q: print('%-5s %-7s frames %5d  trailing bend max %.2f  sway amp %.2f..%.2f  (css px at the tip)' % (view, nm, len(q), max(abs(r[0]) for r in q), min(r[1] for r in q), max(r[1] for r in q)))
    print('errors', c.js('JSON.stringify(window.__err.slice(0,3))'))
finally: c.close()
