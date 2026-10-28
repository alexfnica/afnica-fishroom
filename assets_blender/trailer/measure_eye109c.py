# V17.109 young rows: eye grid (rows night / dusk / day; columns fry, black juvenile, olive juvenile), docs/eye109_young_grid.png
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
c = anc_game(tank='main', fish="[T.fish('anc','M',2),T.fish('anc','F',9),T.fish('anc','M',9),T.fish('anc','F',2),T.fish('anc','M',10),T.fish('anc','F',8)]", warm=2,
             pre="window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};")
def step(sec):
    for i in range(int(sec * 30)): c.js('__afStep(%f, 2)' % (1000 / 30))
GRID = r"""(()=>{const E={'anc|120|238':[214.7,55.9],'anc|120|438':[211.4,71.6],'anc|0|438':[206.4,59.9]},seen={},o=document.createElement('canvas');o.width=3*280;o.height=200;const g=o.getContext('2d');g.imageSmoothingEnabled=false;
 [...document.querySelectorAll('.ancArt canvas[data-wk^="anc|"]')].forEach(cv=>{const k=cv.dataset.wk,e=E[k];if(!e||seen[k])return;seen[k]=1;const i=Object.keys(E).indexOf(k);g.drawImage(cv,e[0]-14,e[1]+20-10,28,20,i*280,0,280,200)});return o.toDataURL('image/png')})()"""
try:
    c.js("window.ANC109TAU=.05;1"); rows = []
    for nm, h in (('night', 23), ('dusk', 19), ('day', 12)):
        c.js("window.__afHourOverride=%d;1" % h); step(1.5); rows.append(c.js(GRID))
    c.js("window.__rows=%s;1" % json.dumps(rows))
    png = c.js(r"""(async()=>{const o=document.createElement('canvas');o.width=840;o.height=600;const g=o.getContext('2d');for(let i=0;i<3;i++){const im=new Image();im.src=__rows[i];await im.decode();g.drawImage(im,0,i*200)}return o.toDataURL('image/png')})()""")
    print('errors', c.js('JSON.stringify(window.__err)'), 'keys', c.js("JSON.stringify([...document.querySelectorAll('.ancArt canvas[data-wk^=\"anc|\"]')].map(x=>x.dataset.wk))"))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'eye109_young_grid.png'), 'wb').write(base64.b64decode(png.split(',')[1]))
finally:
    c.close()
