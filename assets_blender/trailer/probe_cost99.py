# Frame cost (2026-10-18): time spent in the page's requestAnimationFrame callbacks per frame (fake 30 fps clock),
# for a tank of FISH (default 3 adult males + 1 female), and how much of it the V17.99 bristle layer takes
# (t99draw wrapped through the test hook window.__T99C). Run: python probe_cost99.py [secs]
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = os.environ.get('FISH') or "[T.fish('anc','M',40),T.fish('anc','M',38),T.fish('anc','M',36),T.fish('anc','F',36)]"
HOOK = r"""window.__RT=[];const _raf=window.requestAnimationFrame;window.requestAnimationFrame=function(cb){return _raf.call(window,function(t){const a=performance.now();try{cb(t);}finally{window.__RT.push(performance.now()-a);}});};1;"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=SEED % 7 + HOOK)
try:
    secs = int(sys.argv[1]) if len(sys.argv) > 1 else 30; per = []
    for i in range(secs * 30):
        t0 = time.perf_counter(); c.js('__afStep(%f, 2)' % (1000 / 30)); dt = (time.perf_counter() - t0) * 1000   # wall time (the page clock is fake)
        per.append((dt, i))
        if dt > 150: print('slow', i, round(dt), c.js("JSON.stringify([...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>e.dataset.ancMode).concat([anc90Debug().F96['tank-main']?anc90Debug().F96['tank-main'].ph:'-']))"))
    top = sorted(per, reverse=True)[:6]; per = sorted(d for d, _ in per[61:]); n = len(per); print('slowest steps (ms, frame):', [(round(d), k) for d, k in top])
    print('wall time per frame step (incl. CDP overhead): median %.2f ms, p95 %.2f ms, max %.2f ms (%d frames, %s)' % (per[n // 2], per[int(n * .95)], per[-1], n, FISH))
finally: c.close()
