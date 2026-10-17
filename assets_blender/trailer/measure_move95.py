# V17.95 movement stats (throw-away headless game, fake 30 fps clock): main tank 1 male + 1 female bristlenose, daytime.
# Per fish: share of time still / crawling / on the glass / swimming, speed while moving (px/s and body lengths/s),
# length of moving bouts and of still periods, number of short darts (> 1.5 body lengths/s), max step per frame.
# Run: D:/Blender/5.2/python/bin/python.exe measure_move95.py   (env SEED, SECS, AF_PORT, AF_GAME)
import os, sys, json, math, re
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = os.environ.get('FISH') or "[T.fish('anc','M',40),T.fish('anc','F',36)]"
SECS = int(os.environ.get('SECS', '120'))
HOOK = r"""window.__S=new WeakMap();window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};
 setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1"""
REC = r"""JSON.stringify([...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>{const tr=e.style.transform||'',m=/scale\(([-\d.e]+)\)/.exec(tr);
 return [+e.dataset.ancX,+e.dataset.ancY,e.dataset.ancMode,e.dataset.ancSurface,parseFloat(e.style.getPropertyValue('--anc-glass'))||0,m?+m[1]:1,e.dataset.swim91==='1'?1:0,(__S.get(e)||{}).dart95?1:0,+(((__S.get(e)||{}).r95||0)*11).toFixed(2)]}))"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=HOOK + ';' + os.environ.get('PRE', '') + ';' + (SEED % int(os.environ['SEED']) if os.environ.get('SEED') else '1'))
try:
    L = []
    for i in range(SECS * 30):
        if i == 30 and os.environ.get('AT1'): c.js(os.environ['AT1'])
        c.js('__afStep(%f, 2)' % (1000 / 30)); L.append(json.loads(c.js(REC)))
    for k in range(len(L[0])):
        BL = 112 * L[-1][k][5]
        sp = []; mx = 0; still = mov = glass = swim = 0; bouts = []; stills = []; run = 0; srun = 0; darts = 0; modes = {}
        for i in range(1, len(L)):
            a, b = L[i - 1][k], L[i][k]; modes[b[2]] = modes.get(b[2], 0) + 1
            d = math.hypot(b[0] - a[0], b[1] - a[1]); v = d * 30
            if i == 30 and os.environ.get('AT1'): continue
            mx = max(mx, d)
            if b[4] > .5: glass += 1
            if b[6]: swim += 1
            if v > 3:
                mov += 1; sp.append(v); run += 1
                if srun: stills.append(srun / 30); srun = 0
            else:
                still += 1; srun += 1
                if run: bouts.append(run / 30); run = 0
        mxnd = 0; dfr = 0; tilt = 0; rests = []; rr = 0; gz = []; gr = 0
        dmx = 0
        for i in range(1, len(L)):
            a, b = L[i - 1][k], L[i][k]; d = math.hypot(b[0] - a[0], b[1] - a[1])
            if i == 30 and os.environ.get('AT1'): continue
            if b[7]: dfr += 1; dmx = max(dmx, d)
            elif a[2] == b[2] and b[2] not in ('fanning',): mxnd = max(mxnd, d)
            if b[3] == 'substrate': tilt = max(tilt, b[8])
            if b[2] == 'rest': rr += 1
            elif rr: rests.append(rr / 30); rr = 0
            if b[2] == 'graze': gr += 1
            elif gr: gz.append(gr / 30); gr = 0
        dart = 0; prev = False
        for v in sp:
            if v > 1.5 * BL and not prev: dart += 1
            prev = v > 1.5 * BL
        n = len(L) - 1; sp.sort(); q = lambda p: sp[int(p * (len(sp) - 1))] if sp else 0
        md = lambda x: sorted(x)[len(x) // 2] if x else 0
        print('fish %d  body %.0f px | moving %d%% still %d%% | on glass %d%% swim %d%%' % (k, BL, 100 * mov / n, 100 * still / n, 100 * glass / n, 100 * swim / n))
        print('   speed moving: median %.1f px/s (%.2f BL/s), p90 %.1f (%.2f BL/s), max step %.2f px/frame, darts>1.5BL/s: %d' % (q(.5), q(.5) / BL, q(.9), q(.9) / BL, mx, dart))
        print('   moving bouts: n %d median %.1f s | still periods: n %d median %.1f s, longest %.1f s' % (len(bouts), md(bouts), len(stills), md(stills), max(stills or [0])))
        print('   dart frames %d (max step in darts %.2f) | max step outside darts %.2f px/frame | rest bouts n %d median %.1f s max %.1f | graze sessions n %d median %.1f s | max rasp tilt %.1f deg' % (dfr, dmx, mxnd, len(rests), md(rests), max(rests or [0]), len(gz), md(gz), tilt))
        print('   modes (s):', {m: round(v / 30, 1) for m, v in sorted(modes.items(), key=lambda x: -x[1])[:8]})
    print('dart counters', c.js('JSON.stringify(anc90Debug().D95)'))
    print('errors', c.js("JSON.stringify(window.__err.slice(0,5))"))
finally: c.close()
