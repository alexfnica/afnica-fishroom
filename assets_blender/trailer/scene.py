# Scene helpers for the AFNICA trailer: open the game in a throw-away Chrome, build a tank, trigger behaviour, record frames.
import os, sys, time, json
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome, CLOCK_JS
GAME = 'file:///D:/Retirement/AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html'
HERE = os.path.dirname(os.path.abspath(__file__))

HELPERS = r'''
window.T = {
 n: 0,
 fish(sp, sex, age, extra) { const f = {id: 'tr' + sp + (++T.n), species: sp, sex, age, health: 100, dead: false, disease: null, treatment: null,
   hungerDays: 0, sickDays: 0, genes: {color: 70 + Math.random() * 25, pattern: 70 + Math.random() * 25, fins: 75 + Math.random() * 20, vitality: 90, mutation: null}};
   f.name = f.id; return Object.assign(f, extra || {}); },
 tank(k, list) { const a = tankArrayV14(k); a.length = 0; list.forEach(f => a.push(f)); },
 show(k) { try { switchTankV8(k); } catch (e) { render(); } },
 clean() {                                    // cinematic: hide the badges that sit on top of the water
   let s = document.getElementById('trClean'); if (!s) { s = document.createElement('style'); s.id = 'trClean'; document.head.appendChild(s); }
   s.textContent = '.tank [class*=wafer i],.tank [class*=Wafer],.tank .tankBadge,.toast,.toastV9,#toast{display:none!important}';
 },
 rect(sel) { const e = document.querySelector(sel); if (!e) return null; const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; },
};
'''

def open_game(w=540, h=960, scale=2, port=9333):
    c = Chrome(w, h, scale, port)
    c.cmd('Page.addScriptToEvaluateOnNewDocument', source=CLOCK_JS)
    c.cmd('Page.navigate', url=GAME); c.wait_event('Page.loadEventFired', 90)
    c.js(HELPERS); c.js('save=()=>{}; window.save=save; 1')   # nothing is ever written (and it is a throw-away profile anyway)
    c.js('__afStep(500, 10)')
    return c

def record(c, out_dir, seconds, fps=30, clip=None, sub=2, every=None, q=93, on_frame=None):
    os.makedirs(out_dir, exist_ok=True); n = int(round(seconds * fps)); t = time.time()
    for i in range(n):
        if on_frame: on_frame(i)
        c.js('__afStep(%f, %d)' % (1000.0 / fps, sub))
        c.shot(os.path.join(out_dir, '%05d.jpg' % i), clip=clip, q=q)
    print('recorded', out_dir, n, 'frames in', round(time.time() - t, 1), 's')

def advance(c, seconds, fps=30):
    c.js('__afStep(%f, %d)' % (seconds * 1000.0, max(1, int(seconds * fps))))
