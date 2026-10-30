# V17.120: Marco, the weekly importer (Gemini, green screen).
#   marco/marco_portrait.webp -> marco/marco_face.png (square head-and-shoulders, transparent, 200 px) for the import pop-up
#   marco/marco_sheet.webp    -> marco/marco_wave.png, marco_box.png, marco_thumbs.png (cut_sheet.py, 220 px tall)
# Needs: cd D:\ClaudeWork\outro && python -m http.server 8792
import sys, os, time, base64, shutil, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
W = r'D:\ClaudeWork\outro'
shutil.copy(os.path.join(HERE, 'marco', 'marco_portrait.webp'), os.path.join(W, 'marco_portrait.webp'))
JS = r"""(async()=>{const im=new Image();im.src='marco_portrait.webp';await im.decode();const w=im.naturalWidth,h=im.naturalHeight;
const cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d');g.drawImage(im,0,0);const I=g.getImageData(0,0,w,h),p=I.data,c0=[p[0],p[1],p[2]];
for(let i=0;i<p.length;i+=4){const d=Math.hypot(p[i]-c0[0],p[i+1]-c0[1],p[i+2]-c0[2]);let a=Math.max(0,Math.min(1,(d-42)/38));
 const m=Math.max(p[i],p[i+2]);if(p[i+1]>m+8&&(a<1||d<95))p[i+1]=a<1?m:Math.min(p[i+1],m+8);p[i+3]=Math.round(a*255);}
g.putImageData(I,0,0);
/* square crop: the head's top and the middle of the face; a little room above the hair */
let top=h,sx=0,n=0;for(let y=0;y<h;y++){for(let x=0;x<w;x++)if(p[(y*w+x)*4+3]>120){if(y<top)top=y;if(y<h*.45){sx+=x;n++;}}}
const cx=n?sx/n:w/2,S=Math.round(h*.98),x0=Math.round(cx-S/2),y0=Math.max(0,top-12);
const o=document.createElement('canvas');o.width=200;o.height=200;const og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(cv,x0,y0,S,S,0,0,200,200);
return o.toDataURL('image/png');})()"""
c = Chrome(800, 800, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    u = c.js(JS); open(os.path.join(HERE, 'marco', 'marco_face.png'), 'wb').write(base64.b64decode(u.split(',')[1])); print('face ok')
finally: c.close()
# the three poses
py = sys.executable
subprocess.run([py, os.path.join(HERE, 'cut_sheet.py'), os.path.join('marco', 'marco_sheet.webp'), os.path.join('marco', 'marco_tmp')], check=True)
for a, b in (('walk', 'wave'), ('bag', 'box'), ('point', 'thumbs')):
    os.replace(os.path.join(HERE, 'marco', 'marco_tmp_%s.png' % a), os.path.join(HERE, 'marco', 'marco_%s.png' % b))
print('poses ok')
