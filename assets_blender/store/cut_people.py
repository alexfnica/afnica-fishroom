# V17.120: keys out the flat (green / white) background of the Gemini customer images in people_src/, trims, resizes to 220 px tall
# -> people/pNN.png (transparent). Needs the little http server: cd D:\ClaudeWork\outro && python -m http.server 8792 (images are copied there).
import sys, os, time, base64, shutil, json, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
SRC = os.path.join(HERE, 'people_src'); OUT = os.path.join(HERE, 'people'); W = r'D:\ClaudeWork\outro'
os.makedirs(OUT, exist_ok=True)
files = sorted(sum([glob.glob(os.path.join(SRC, e)) for e in ('*.png', '*.webp', '*.jpg', '*.jpeg')], []))
if not files: sys.exit('no images in ' + SRC)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
JS = """(async(name)=>{const im=new Image();im.src=name;await im.decode();const w=im.naturalWidth,h=im.naturalHeight;const cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d');g.drawImage(im,0,0);
const D=g.getImageData(0,0,w,h),p=D.data;const c0=[p[0],p[1],p[2]];
/* key colour = the corner colour; alpha ramps with the colour distance, green spill pulled out of the edge pixels */
for(let i=0;i<p.length;i+=4){const d=Math.hypot(p[i]-c0[0],p[i+1]-c0[1],p[i+2]-c0[2]);let a=Math.max(0,Math.min(1,(d-42)/38));
 if(a<1&&c0[1]>c0[0]+60){const m=Math.max(p[i],p[i+2]);if(p[i+1]>m)p[i+1]=m}
 p[i+3]=Math.round(a*255)}
g.putImageData(D,0,0);let x0=w,x1=0,y0=h,y1=0;for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(p[(y*w+x)*4+3]>40){if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y}
const oh=220,ow=Math.round((x1-x0)*oh/(y1-y0));const o=document.createElement('canvas');o.width=ow;o.height=oh;const og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(cv,x0,y0,x1-x0,y1-y0,0,0,ow,oh);return o.toDataURL('image/png')})"""
c = Chrome(800, 800, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    for i, f in enumerate(files):
        n = 'people_%d%s' % (i, os.path.splitext(f)[1]); shutil.copy(f, os.path.join(W, n))
        u = c.js(JS + "(%s)" % json.dumps(n))
        open(os.path.join(OUT, 'p%02d.png' % i), 'wb').write(base64.b64decode(u.split(',')[1])); print('cut', os.path.basename(f))
finally: c.close()
