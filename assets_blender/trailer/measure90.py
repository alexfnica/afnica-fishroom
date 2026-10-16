# V17.90 measurements (throw-away headless game, fake 30 fps clock): main tank, 1 ready male + 2 females, 90 s.
# Per fish: max step of the box centre per frame (owner: no jumps > 3 px/frame), backward frames (moving against the
# DRAWN facing = the V17.90 yaw), time in each mode, cave frames used; console errors.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = os.environ.get('FISH') or "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30)]"
ERR = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,300));_ce.apply(console,arguments)};1"
REC = r"""JSON.stringify((()=>{const D=anc90Debug();const t=document.getElementById('tank-main');const tk=D.TK.get(t)||{};
 return {cave:tk.want&&performance.now()-tk.at<250?tk.want:'tube',f:[...t.querySelectorAll('[data-fish-id]')].map(e=>{const s=D.ST.get(e)||{};const mx=/scaleX\(([-\d.e]+)\)/.exec(e.style.transform||''),dr=e.classList.contains('anc90')?s.a:(mx&&+mx[1]<0?-180:0);return [+e.dataset.ancX,+e.dataset.ancY,dr,e.dataset.ancMode,e.classList.contains('anc90hid')?1:0,(s.turn?1:0),e.dataset.ancSurface,parseFloat(e.style.getPropertyValue('--anc-glass'))||0,e.style.transform]})}})())"""
c = anc_game(tank='main', fish=FISH, warm=1, pre=ERR + ';' + (SEED % int(os.environ['SEED']) if os.environ.get('SEED') else ''))
try:
    L = []
    for i in range(90 * 30):
        c.js('__afStep(%f, 2)' % (1000 / 30)); L.append(json.loads(c.js(REC)))
    n = len(L[0]['f'])
    for k in range(n):
        mx = 0; at = None; back = 0; mv = 0; modes = {}; bs = {}; gm = [0, 0]
        for i in range(1, len(L)):
            a, b = L[i - 1]['f'][k], L[i]['f'][k]; modes[b[3]] = modes.get(b[3], 0) + 1
            if a[4] or b[4]: continue
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            if d > mx: mx, at = d, (i, a[3], b[3])
            vx = b[0] - a[0]
            if b[7] > .5:                                  # on the glass: velocity against the drawn heading (rotation + mirror)
                import re
                m = re.search(r'rotate\(([-\d.e]+)deg\)', b[8] or ''); ang = math.radians(float(m.group(1))) if m else 0
                hx, hy = math.cos(ang), math.sin(ang)
                if b[2] == -180: hx, hy = -hx, -hy
                vy = b[1] - a[1]
                if math.hypot(vx, vy) > .25:
                    gm[0] += 1
                    if vx * hx + vy * hy < -.1 * math.hypot(vx, vy): gm[1] += 1
                continue
            if abs(vx) > .25 and not b[5] and b[2] in (0, -180):
                mv += 1
                key = (b[6], b[3], 'g%.0f' % b[7])
                if (vx > 0) != (b[2] == 0):
                    back += 1; bs[key] = bs.get(key, 0) + 1

        print('fish', k, 'max step %.2f px/frame' % mx, at, 'backward %d of %d moving frames' % (back, mv))
        print('   on the glass: %d moving frames, %d against the drawn heading' % (gm[0], gm[1]))
        print('   backward by (surface, mode, glass):', sorted(bs.items(), key=lambda x: -x[1])[:6])
        print('   modes (s):', {m: round(v / 30, 1) for m, v in sorted(modes.items(), key=lambda x: -x[1])})
    cv = {}
    for l in L: cv[l['cave']] = cv.get(l['cave'], 0) + 1
    print('cave frames used:', len(cv), sorted(cv.items(), key=lambda x: -x[1])[:8])
    print('errors', c.js("JSON.stringify(window.__err.slice(0,6))"))
finally: c.close()
