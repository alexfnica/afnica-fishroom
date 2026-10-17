# V17.95 turn diagnosis (throw-away headless game, fake 30 fps clock): main tank, 1 male + 1 female bristlenose + cave,
# daytime. Logs every turn of each fish: which system drives it (old s.turn = fish stays put, or the V17.90 facing-follow
# = the fish keeps moving), duration, drawn position per frame (box x + the V17.94 translate), facing sign, 3D frame,
# photo opacity; max step per frame of the drawn position; backward frames. Saves a 4-frame strip of the first turns.
# Run: D:/Blender/5.2/python/bin/python.exe measure_turn95.py   (env SEED, SECS, AF_PORT, STRIP=1)
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = os.environ.get('FISH') or "[T.fish('anc','M',40),T.fish('anc','F',36)]"
SECS = int(os.environ.get('SECS', '60'))
HOOK = r"""window.__S=new WeakMap();window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,300));_ce.apply(console,arguments)};
 setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1"""
REC = r"""JSON.stringify([...document.querySelectorAll('#tank-main [data-fish-id]')].map(e=>{const s=__S.get(e)||{},f=anc90Debug().ST.get(e)||{};
 const tr=e.style.transform||'',mx=/scaleX\(([-\d.e]+)\)/.exec(tr),tl=parseFloat((e.style.translate||'0').split(' ')[0])||0,art=e.querySelector('.ancArt');
 const c=e.querySelector(':scope>canvas.anc94t');
 return {x:+e.dataset.ancX,y:+e.dataset.ancY,tl,sx:mx?+mx[1]:1,m:e.dataset.ancMode,sf:e.dataset.ancSurface,g:parseFloat(e.style.getPropertyValue('--anc-glass'))||0,
  old:s.turn?+(s.turn.t/(window.ancTurnSecV1789||1)).toFixed(3):-1,fol:f.turn?+(f.turn.t).toFixed(3):-1,c3:c&&c.style.display==='block'?1:0,
  op:art&&art.style.opacity!==''?+art.style.opacity:1,face:s.face,fv:s.fv,rot:(/rotate\(([-\d.e]+)deg/.exec(tr)||[0,0])[1]*1}}))"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=HOOK + ';' + (SEED % int(os.environ['SEED']) if os.environ.get('SEED') else ''))
try:
    L = []; strip = []
    for i in range(SECS * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30)); L.append(json.loads(c.js(REC)))
        if os.environ.get('STRIP') and len(strip) < 12:
            for k, r in enumerate(L[-1]):
                if r['c3'] and (r['old'] >= 0 or r['fol'] >= 0):
                    u = r['old'] if r['old'] >= 0 else r['fol'] / 1.0
                    for q in (0.05, .35, .65, .95):
                        if abs(u - q) < .021 and not any(s[0] == k and s[1] == q and i - s[2] < 40 for s in strip):
                            p = os.path.join(HERE, 'raw', 'turn95_%02d.png' % len(strip))
                            c.shot(p, clip={'x': r['x'] - 110, 'y': r['y'] - 60, 'width': 220, 'height': 110, 'scale': 2}, q=92)
                            strip.append((k, q, i, p))
    n = len(L[0])
    for k in range(n):
        turns = []; cur = None; mx = 0; mxat = None; back = mv = 0; bm = {}
        for i in range(1, len(L)):
            a, b = L[i - 1][k], L[i][k]
            src = 'old' if b['old'] >= 0 else 'follow' if b['fol'] >= 0 else None
            if src and not cur: cur = {'src': src, 'i0': i, 'x0': b['x'], 'mode': b['m'], 'sf': b['sf'], 'c3': 0, 'sxflip': [], 'xs': []}
            if cur:
                cur['c3'] += b['c3']; cur['xs'].append(round(b['x'] + b['tl'], 1))
                if a['sx'] * b['sx'] < 0: cur['sxflip'].append((i - cur['i0'], round(b['op'], 2), b['c3']))
                if not src:
                    cur['n'] = i - cur['i0']; cur['dx_box'] = round(b['x'] - cur['x0'], 1); turns.append(cur); cur = None
            if a['m'] in ('fanning',) or b['m'] in ('fanning',): continue
            d = math.hypot(b['x'] + b['tl'] - a['x'] - a['tl'], b['y'] - a['y'])
            if d > mx: mx, mxat = d, (i, a['m'], b['m'], round(b['tl'], 1))
            vx = (b['x'] + b['tl']) - (a['x'] + a['tl'])
            if b['g'] < .3 and not b['c3'] and abs(vx) > .25:
                mv += 1
                if (vx > 0) != (b['sx'] > 0): back += 1; bm[(b['m'], b['fol'] >= 0, b['old'] >= 0)] = bm.get((b['m'], b['fol'] >= 0, b['old'] >= 0), 0) + 1
        print('fish', k, 'turns', len(turns), '| max drawn step %.2f px/frame' % mx, mxat, '| backward (photo, sand) %d of %d moving frames' % (back, mv), '(mode, follow, old):', bm)
        for t in turns[:10]:
            xs = t['xs']; st = [abs(xs[j] - xs[j - 1]) for j in range(1, len(xs))] or [0]
            print('  %-6s t=%5.1fs %3d fr (%.2fs) mode=%s/%s 3D frames=%d box dx=%+.1f drawn x path %s..max-dev %.1f, max step %.2f, flips(fr,photoOp,3D)=%s' % (
                t['src'], t['i0'] / 30, t['n'], t['n'] / 30, t['mode'], t['sf'], t['c3'], t['dx_box'], xs[0], max(abs(v - xs[0]) for v in xs), max(st), t['sxflip']))
    print('errors', c.js("JSON.stringify(window.__err.slice(0,6))"))
    print('strip', [s[3] for s in strip])
finally: c.close()
