# V17.109: heads of the fry / juvenile bristlenose records (sprite cache), 10x with a pixel grid, to place the eye.
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
c = anc_game(tank='main', fish="[T.fish('anc','M',2),T.fish('anc','F',9),T.fish('anc','M',9),T.fish('anc','F',2),T.fish('anc','M',10),T.fish('anc','F',8)]", warm=3, pre="")
try:
    for i in range(60): c.js('__afStep(%f, 2)' % (1000 / 30))
    print(c.js("JSON.stringify([...document.querySelectorAll('.ancArt canvas[data-wk^=\"anc|\"]')].map(x=>x.dataset.wk))"))
    png = c.js(r"""(()=>{const C=curlDebugV1744().cache,W={'anc|120|238':[180,40],'anc|120|438':[180,55],'anc|0|438':[180,45]},ks=Object.keys(W).filter(k=>C.get(k));const o=document.createElement('canvas');o.width=2*420;o.height=Math.ceil(ks.length/2)*300;const g=o.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#ddd';g.fillRect(0,0,o.width,o.height);
 ks.forEach((k,i)=>{const r=C.get(k),ox=(i%2)*420,oy=Math.floor(i/2)*300,[xa,ya]=W[k];g.drawImage(r.base,xa,ya,60,40,ox,oy+14,420,280);g.fillStyle='#08f';g.font='11px sans-serif';g.fillText(k,ox+2,oy+11);for(let x=0;x<60;x+=10){g.fillRect(ox+x*7,oy+14,1,280);g.fillText(xa+x,ox+x*7+2,oy+26)}for(let y=0;y<40;y+=10){g.fillRect(ox,oy+14+y*7,420,1);g.fillText(ya+y,ox+2,oy+14+y*7+11)}});window.__ks=ks;return o.toDataURL('image/png')})()""")
    print(c.js('JSON.stringify(window.__ks)'))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','docs','young109_dump.png'),'wb').write(base64.b64decode(png.split(',')[1]))
finally:
    c.close()
