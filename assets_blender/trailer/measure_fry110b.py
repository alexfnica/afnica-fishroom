# V17.110: fry in the BREEDER tank (with the cave). 7 yolk/free fry; counts jitter (direction reversals, max step), time over the cave zone, errors.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
SECS = int(os.environ.get('SECS', '100'))
FISH = "[" + ",".join("T.fish('anc','%s',%s)" % (s, a) for s, a in [('F', 1), ('M', 1.2), ('F', 1.6), ('M', 2), ('F', 2.4), ('M', 3.5), ('F', 4)]) + "]"
PRE = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};"
c = anc_game(tank='breeder', fish=FISH, warm=2, pre=PRE)
try:
    L = []
    for i in range(SECS * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30))
        L.append(json.loads(c.js("JSON.stringify([...document.querySelectorAll('#tank-breeder [data-fish-id], .tank [data-fish-id]')].map(e=>[e.dataset.fishId,+e.dataset.ancX,+e.dataset.ancY,e.dataset.ancMode,e.dataset.ancSurface]))")))
    geo = c.js("JSON.stringify((window.ancDebugV1789&&ancDebugV1789().caveGeo)||null)")
    print('n fish', len(L[0]), 'cave geo', str(geo)[:160], 'errors', c.js('JSON.stringify(window.__err)'))
    for k in range(len(L[0])):
        xs = [f[k][1] for f in L]; ys = [f[k][2] for f in L]
        st = [math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]) for i in range(1, len(xs))]
        rev = 0; last = 0
        for i in range(1, len(xs)):
            d = xs[i] - xs[i - 1]
            if abs(d) > .15:
                sg = 1 if d > 0 else -1
                if last and sg != last: rev += 1
                last = sg
        modes = {}
        for f in L: modes[f[k][3]] = modes.get(f[k][3], 0) + 1
        print(L[0][k][0][-4:], 'x %d->%d' % (xs[0], xs[-1]), 'max step %.1f' % max(st), 'reversals', rev, 'modes', modes)
finally:
    c.close()
