# V17.120: the owner's counter poses (Gemini, 1365x768, green screen) -> poses/owner_<pose>.png, all cut with ONE crop box so they line up
# for crossfades: idle (hands on the counter), greet (open hand), bag (holding the bag up), give (holding the bag out to the viewer's right).
# The counter strip at the bottom of the images is cut off (crop ends at y 712). Needs: cd D:\ClaudeWork\outro && python -m http.server 8792
import sys, os, time, base64, shutil, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
W = r'D:\ClaudeWork\outro'; P = ('idle', 'greet', 'bag', 'give')
X0, Y0, X1, Y1, OW = 380, 20, 1270, 712, 356
JS = """(async(name)=>{const im=new Image();im.src=name;await im.decode();const w=%d,h=%d;const cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d');g.drawImage(im,%d,%d,w,h,0,0,w,h);
const D=g.getImageData(0,0,w,h),p=D.data;const c0=[p[0],p[1],p[2]];
for(let i=0;i<p.length;i+=4){const d=Math.hypot(p[i]-c0[0],p[i+1]-c0[1],p[i+2]-c0[2]);let a=Math.max(0,Math.min(1,(d-42)/38));
 /* green spill: no pixel keeps more green than its red/blue allow (also inside the clear bag, which lets the green through) */
 const m=Math.max(p[i],p[i+2]);if(p[i+1]>m+8){if(a>0&&a<1)p[i+1]=m;else if(a>=1)p[i+1]=Math.min(p[i+1],m+8);}
 p[i+3]=Math.round(a*255)}
g.putImageData(D,0,0);const o=document.createElement('canvas');o.width=%d;o.height=Math.round(h*%d/w);const og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(cv,0,0,o.width,o.height);return o.toDataURL('image/png')})"""
c = Chrome(800, 800, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    for k in P:
        u = c.js(JS % (X1 - X0, Y1 - Y0, X0, Y0, OW, OW) + "(%s)" % json.dumps('owner_%s.jpg' % k))
        open(os.path.join(HERE, 'poses', 'owner_%s.png' % k), 'wb').write(base64.b64decode(u.split(',')[1])); print('cut', k)
finally: c.close()
