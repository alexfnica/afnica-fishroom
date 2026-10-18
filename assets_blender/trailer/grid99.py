# Frame grid for the owner (2026-10-17): a headless scene, one fish, clips around it at chosen moments, tiled into one JPEG.
# GRID=roll: a forced climb onto the front pane, at --anc-glass 0 / .2 / .4 / .6 / .8 / .95 / 1 (+ 1 s later).
# Run: D:/Blender/5.2/python/bin/python.exe grid99.py <out.jpg>   (env GRID, AF_PORT)
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
OUT = sys.argv[1]; GRID = os.environ.get('GRID', 'roll')
HOOK = r"""window.__S=new WeakMap();setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1;"""
ST = r"""(()=>{const tk=document.getElementById('tank-main'),T=tk.getBoundingClientRect(),e=tk.querySelector('[data-fish-id]'),s=__S.get(e),r=e.getBoundingClientRect();
 return JSON.stringify([s&&s.mode,parseFloat(e.style.getPropertyValue('--anc-glass'))||0,r.left+r.width/2,r.top+r.height/2])})()"""
FISH0 = "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36)]" if GRID == 'cave' else "[T.fish('anc','M',40),T.fish('anc','M',38)]" if GRID == 'fight' else None
c = anc_game(tank='main', fish=FISH0 or "[T.fish('anc','%s',%d)]" % ((os.environ.get('SEX', 'F'), 40) if os.environ.get('SEX') == 'M' else ('F', 36)), warm=1, pre=HOOK + SEED % 7)
tiles = []
try:
    if GRID == 'roll':
        c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e);s.mode='toWall';s.wall=s.x<480?-1:1;s.transition=null;s.wait=0;return 1})()")
        marks = [0, .3, .45, .5, .55, .7, 1]; k = 0; cx = cy = None; after = None
        for i in range(60 * 30):
            c.js('__afStep(%f, 2)' % (1000 / 30)); md, g, x, y = json.loads(c.js(ST))
            if md != 'attach' and not tiles: continue
            cx, cy = x, y
            take = k < len(marks) and g >= marks[k] - 1e-3 and (marks[k] > 0 or md == 'attach')
            if after is None and k >= len(marks): after = i + 30
            if take or i == after:
                p = os.path.join(os.path.dirname(OUT), '_t%d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=max(0, cx - 80), y=max(0, cy - 90), width=160, height=180, scale=2), q=90)
                tiles.append((p, 'glass %.2f' % g if take else '+1 s on the glass')); k += take
            if i == after: break
    if GRID == 'cave':
        want = ['C2_i-060', 'C2_i-040', 'C2_i+000', 'C2_i+032', 'C2_i+056', 'C2_i+072', 'C2_f', '+1s']; k = 0; after = None
        NM = "(()=>{const t=anc90Debug().TK.get(document.getElementById('tank-main')),m=t&&t.m,cv=document.querySelector('#tank-main .ancBreedingCave');return JSON.stringify([m&&m.name||'',parseFloat(cv.style.left),parseFloat(cv.style.top)])})()"
        for i in range(150 * 30):
            c.js('__afStep(%f, 2)' % (1000 / 30)); nm, L, T0 = json.loads(c.js(NM))
            hit = k < 7 and nm.startswith(want[k]); 
            if k == 7 and after is None: after = i + 30
            if hit or i == after:
                p = os.path.join(os.path.dirname(OUT), '_t%d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=max(0, L - 120), y=max(0, T0 - 60), width=220, height=150, scale=2), q=90)
                tiles.append((p, nm if hit else '+1 s fanning')); k += 1
            if i == after: break
    if GRID == 'glass':
        c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};1")
        c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e);s.mode='toWall';s.wall=s.x<480?-1:1;s.transition=null;s.wait=0;return 1})()")
        on = None
        GS = "(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e),c=e.querySelector('.ancGlass>canvas');return JSON.stringify([s.mode,e.dataset.ancStroke||'',+(parseFloat(e.style.getPropertyValue('--anc-glass'))||0).toFixed(2)])})()"
        for i in range(90 * 30):
            c.js('__afStep(%f, 2)' % (1000 / 30)); md, stk, g = json.loads(c.js(GS)); _, _, x, y = json.loads(c.js(ST))
            if md == 'graze' and g >= 1 and on is None and i > 0 and (float(stk or 0) > .3): on = i
            if on is not None and i >= on and (i - on) % 4 == 0:
                p = os.path.join(os.path.dirname(OUT), '_t%d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=max(0, x - 50), y=max(0, y - 55), width=100, height=110, scale=3), q=92)
                tiles.append((p, '%.2f s  stroke %s' % ((i - on) / 30, stk[:4]))); 
                if len(tiles) == 8: break
        print('errors', c.js("JSON.stringify(window.__err.slice(0,3))"))
    if GRID == 'tent':
        HS = r"(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e),r=e.getBoundingClientRect(),f=/scaleX\(-/.test(e.style.transform||'')?-1:1;const v=window.__px==null?0:Math.abs(+e.dataset.ancX-window.__px)*30;window.__px=+e.dataset.ancX;return JSON.stringify([s.mode,Math.round(v),r.left+r.width/2+f*r.width*.3,r.top+r.height*.42,e.dataset.ancSurface||''])})()"
        c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e);s.mode='move';s.tx=s.x<480?s.x+260:s.x-260;s.ty=s.y;s.wait=0;return 1})()")
        on = None
        for i in range(40 * 30):
            c.js('__afStep(%f, 2)' % (1000 / 30)); md, v, x, y, sf = json.loads(c.js(HS))
            if on is None and md == 'move' and v > 15: on = i
            if on is not None and (i - on) % 3 == 0 and len(tiles) < 8:
                p = os.path.join(os.path.dirname(OUT), '_t%d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=max(0, x - 30), y=max(0, y - 30), width=60, height=60, scale=4), q=92)
                tiles.append((p, '%.1f s  %s  v %d' % ((i - on) / 30, md, v)))
            if len(tiles) == 8: break
    if GRID == 'fight':
        FS = "(()=>{const F=anc90Debug().F96['tank-main'],c=document.querySelector('#tank-main canvas.anc96p');if(!F||!c)return JSON.stringify(null);const r=c.getBoundingClientRect();return JSON.stringify([F.ph,F.cur||'',r.left+r.width/2,r.top+r.height/2])})()"
        k = 0; last = None
        for i in range(120 * 30):
            if i % 300 == 10: c.js('window.anc96Force=1')
            c.js('__afStep(%f, 2)' % (1000 / 30)); r = json.loads(c.js(FS))
            WANT = ['A6', 'B3', 'B9', 'C4', 'C10', 'D3', 'D8', 'D16']
            if r and r[0] == 'fight' and r[1] and r[1] != last and len(tiles) < 8 and r[1] == WANT[len(tiles)]:
                p = os.path.join(os.path.dirname(OUT), '_t%d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=max(0, r[2] - 85), y=max(0, r[3] - 35), width=170, height=76, scale=3), q=90)
                tiles.append((p, r[1]))
            if r and r[1] != last: k += 1; last = r[1]
            if len(tiles) == 8: break
    if GRID == 'turn':
        TS = "(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),c=e.querySelector(':scope>canvas.anc94t'),r=e.getBoundingClientRect();return JSON.stringify([!!(c&&c.style.display==='block'),r.left+r.width/2,r.top+r.height/2])})()"
        c.js("(()=>{const e=document.querySelector('#tank-main [data-fish-id]'),s=__S.get(e);s.mode='move';s.tx=s.x<480?s.x-200:s.x+200;s.ty=s.y;s.wait=0;return 1})()")
        on = None
        for i in range(30 * 30):
            c.js('__afStep(%f, 2)' % (1000 / 30)); t3, x, y = json.loads(c.js(TS))
            if on is None and t3: on = i; cx, cy = x, y
            if on is not None and (i - on) % 8 == 0 and len(tiles) < 8:
                p = os.path.join(os.path.dirname(OUT), '_t%d.jpg' % len(tiles))
                c.shot(p, clip=dict(x=max(0, cx - 70), y=max(0, cy - 40), width=140, height=80, scale=3), q=92)
                tiles.append((p, '%.2f s' % ((i - on) / 30)))
            if len(tiles) == 8: break
    TH = 154 if GRID == 'cave' else 249 if GRID == 'glass' else 226 if GRID == 'tent' else 103 if GRID == 'fight' else 129 if GRID == 'turn' else 254
    imgs = ''.join('<div style="display:inline-block;margin:4px;text-align:center;font:600 14px system-ui;color:#fff"><img src="data:image/jpeg;base64,%s" style="width:226px;height:%dpx;display:block">%s</div>' % (base64.b64encode(open(p, 'rb').read()).decode(), TH, t) for p, t in tiles)
    c.js("(h=>{const d=document.createElement('div');d.style.cssText='position:fixed;left:0;top:0;z-index:999999;background:#111;padding:6px;width:948px';d.innerHTML=h;document.body.appendChild(d);return 1})(%s)" % json.dumps(imgs))
    rows = (len(tiles) + 3) // 4
    c.shot(OUT, clip=dict(x=0, y=0, width=960, height=min(540, 12 + rows * (TH + 30))), q=88)
    for p, _ in tiles: os.remove(p)
    print('grid', OUT, len(tiles), 'tiles')
finally: c.close()
