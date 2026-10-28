# V17.109 bristlenose eye: pupil follows the light. Headless, fake clock, 1 male + 1 female, noon -> night -> dusk -> noon.
# Prints the eased level over time (default tau) and the pupil pixel counts per state, writes docs/eye109_grid.png.
# Run: D:/Blender/5.2/python/bin/python.exe measure_eye109.py   (env AF_PORT)
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
HERE2 = os.path.dirname(os.path.abspath(__file__))
c = anc_game(tank='main', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", warm=2,
             pre="window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};")
def step(sec):
    for i in range(int(sec * 30)): c.js('__afStep(%f, 2)' % (1000 / 30))
MEAS = r"""JSON.stringify([...document.querySelectorAll('.ancArt canvas[data-wk^="anc|"]')].map(cv=>{const m=/anc\|(0|240)\|/.test(cv.dataset.wk),ex=m?198.8:209.2,ey=(m?57:70.5)+20,D=cv.getContext('2d').getImageData(Math.round(ex-6),Math.round(ey-8),13,17).data;
 let n=0,sy=0,top=0;for(let y=0;y<17;y++)for(let x=0;x<13;x++){const i=(y*13+x)*4;if(D[i+3]>200&&D[i]+D[i+1]+D[i+2]<75){n++;sy+=y;if(y<8)top++}}return [cv.dataset.wk,n,n?+(sy/n).toFixed(1):-1,top]}))"""
try:
    c.js("window.__afHourOverride=12;1"); step(1)
    print('noon', c.js(MEAS), 'lv', c.js('JSON.stringify(ancEyeDebugV17109())'))
    c.js("window.__afHourOverride=23;1")
    for k in range(1, 13):
        step(5); d = json.loads(c.js('JSON.stringify(ancEyeDebugV17109())'))
        print('t+%3ds lv %.3f' % (k * 5, d['lv']), c.js(MEAS) if k in (1, 6, 12) else '')
    # static states with a fast tau
    c.js("window.ANC109TAU=.05;1")
    states = [('night', 23), ('dusk', 19), ('day', 12)]
    shots = []
    for nm, h in states:
        c.js("window.__afHourOverride=%d;1" % h); step(1.5)
        print(nm, 'lv', json.loads(c.js('JSON.stringify(ancEyeDebugV17109())'))['lv'], c.js(MEAS))
        shots.append(c.js(r"""(()=>{const out=document.createElement('canvas');out.width=2*30*9;out.height=24*9;const g=out.getContext('2d');g.imageSmoothingEnabled=false;
 [...document.querySelectorAll('.ancArt canvas[data-wk^="anc|"]')].forEach((cv,i)=>{const m=/anc\|(0|240)\|/.test(cv.dataset.wk),ex=m?198.8:209.2,ey=(m?57:70.5)+20;g.drawImage(cv,ex-15,ey-12,30,24,i*270,0,270,216)});return out.toDataURL('image/png')})()"""))
    # compose 3 rows (night/dusk/day) x 2 fish
    comp = c.js("(()=>{window.__rows=[];return 1})()")
    allrows = json.dumps(shots)
    c.js("window.__rows=%s;1" % allrows)
    png = c.js(r"""(async()=>{const o=document.createElement('canvas');o.width=540;o.height=216*3;const g=o.getContext('2d');for(let i=0;i<3;i++){const im=new Image();im.src=__rows[i];await im.decode();g.drawImage(im,0,i*216)}return o.toDataURL('image/png')})()""")
    print('errors', c.js('JSON.stringify(window.__err)'))
    out = os.path.join(HERE2, '..', '..', 'docs', 'eye109_grid.png')
    open(out, 'wb').write(base64.b64decode(png.split(',')[1])); print('wrote', os.path.abspath(out))
finally:
    c.close()
