# V17.120: AFNICA's tip / tutorial poses (Gemini, green screen, waist up) -> afnica/afnica_<pose>.png, transparent, trimmed, 300 px tall.
#   tip (finger up), point (pointing to the viewer's right), thumbs (thumbs up), worried (hand on head)
# In the game: window.ST120_AFNICA_POSES = {tip, point, thumbs, worried} (data URLs), for tip and tutorial pop-ups.
# Needs: cd D:\ClaudeWork\outro && python -m http.server 8792
import sys, os, time, base64, shutil, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
POSES = ('tip', 'point', 'thumbs', 'worried')
JS = r"""(async(name)=>{const im=new Image();im.src=name;await im.decode();const w=im.naturalWidth,h=im.naturalHeight;
const cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d');g.drawImage(im,0,0);const I=g.getImageData(0,0,w,h),p=I.data,c0=[p[0],p[1],p[2]];
for(let i=0;i<p.length;i+=4){const d=Math.hypot(p[i]-c0[0],p[i+1]-c0[1],p[i+2]-c0[2]);let a=Math.max(0,Math.min(1,(d-42)/38));
 const m=Math.max(p[i],p[i+2]);if(p[i+1]>m+8&&(a<1||d<95))p[i+1]=a<1?m:Math.min(p[i+1],m+8);p[i+3]=Math.round(a*255);}
g.putImageData(I,0,0);let x0=w,x1=0,y0=h,y1=0;for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(p[(y*w+x)*4+3]>40){if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;}
const oh=300,ow=Math.round((x1-x0+1)*oh/(y1-y0+1)),o=document.createElement('canvas');o.width=ow;o.height=oh;const og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(cv,x0,y0,x1-x0+1,y1-y0+1,0,0,ow,oh);
return o.toDataURL('image/png');})"""
c = Chrome(800, 800, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    for k in POSES:
        shutil.copy(os.path.join(HERE, 'afnica', 'afnica_%s.jpg' % k), os.path.join(r'D:\ClaudeWork\outro', 'afnica_%s.jpg' % k))
        u = c.js(JS + "(%s)" % json.dumps('afnica_%s.jpg' % k))
        open(os.path.join(HERE, 'afnica', 'afnica_%s.png' % k), 'wb').write(base64.b64decode(u.split(',')[1])); print('cut', k)
finally: c.close()
