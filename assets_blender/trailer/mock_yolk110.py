# V17.110 static mock: yolk sac on the fry photo (record anc|120|238) at 3 sizes: age 1 (full), age 2 (half), age 3 (gone).
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
c = anc_game(tank='main', fish="[T.fish('anc','F',2)]", warm=3, pre="")
try:
    for i in range(30): c.js('__afStep(%f, 2)' % (1000 / 30))
    cx, cy, rx, ry = [float(v) for v in os.environ.get('SAC', '168,86,22,12').split(',')]
    png = c.js(r"""(()=>{const r=curlDebugV1744().cache.get('anc|120|238');const S=[%s,%s,%s,%s];const o=document.createElement('canvas');o.width=620;o.height=3*300;const g=o.getContext('2d');g.fillStyle='#10394d';g.fillRect(0,0,o.width,o.height);g.imageSmoothingEnabled=false;
 [1,.5,0].forEach((k,i)=>{const oy=i*300,Z=4,xa=100,ya=40;g.save();g.translate(0,oy);g.scale(Z,Z);g.translate(-xa,-ya);
  g.drawImage(r.base,0,0);
  if(k>0){const [cx,cy,rx,ry]=S,x=cx,y=cy+(1-k)*2,a=rx*(.55+.45*k),b=ry*(.5+.5*k);const t=document.createElement('canvas');t.width=260;t.height=152;const q=t.getContext('2d');
   const gr=q.createRadialGradient(x-a*.25,y-b*.3,1,x,y,a);gr.addColorStop(0,'#f6c46a');gr.addColorStop(.6,'#e19a2e');gr.addColorStop(1,'#a8681c');q.fillStyle=gr;q.beginPath();q.ellipse(x,y,a,b,0,0,7);q.fill();
   q.fillStyle='#ffffff66';q.beginPath();q.ellipse(x-a*.3,y-b*.3,a*.28,b*.18,0,0,7);q.fill();
   q.globalCompositeOperation='destination-in';const m=q.createLinearGradient(0,y-b*.75,0,y-b*.05);m.addColorStop(0,'rgba(0,0,0,0)');m.addColorStop(1,'rgba(0,0,0,1)');q.fillStyle=m;q.fillRect(0,0,260,152);
   g.drawImage(t,0,0)}
  g.restore();g.fillStyle='#fff';g.font='13px sans-serif';g.fillText(['age 1: full yolk sac','age 2: half','age 3: gone (free fry)'][i],6,oy+14)});return o.toDataURL('image/png')})()""" % (cx, cy, rx, ry))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'yolk110_mock.png'), 'wb').write(base64.b64decode(png.split(',')[1]))
finally:
    c.close()
