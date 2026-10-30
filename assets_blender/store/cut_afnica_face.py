# V17.120: AFNICA's round face for tip pop-ups: a square crop centred on his head, from the 'greet' counter pose (poses/owner_greet.png, looking at the player)
# -> poses/afnica_face.png (200 px). Needs: cd D:\ClaudeWork\outro && python -m http.server 8792
import sys, os, time, base64, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
shutil.copy(os.path.join(HERE, 'poses', 'owner_greet.png'),   # the welcome pose: he looks straight at the player
            r'D:\ClaudeWork\outro\afn_idle.png')
JS = r"""(async()=>{const im=new Image();im.src='afn_idle.png';await im.decode();const w=im.naturalWidth,h=im.naturalHeight;
const cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d');g.drawImage(im,0,0);const p=g.getImageData(0,0,w,h).data;
let top=h;for(let y=0;y<h&&top===h;y++)for(let x=0;x<w;x++)if(p[(y*w+x)*4+3]>120){top=y;break;}
/* the head: opaque pixels in the band from the top of the hair down to ~38% of the height -> its middle column */
const hb=top+Math.round(h*.38);let sx=0,n=0,x0=w,x1=0;for(let y=top;y<hb;y++)for(let x=0;x<w;x++)if(p[(y*w+x)*4+3]>120){sx+=x;n++;if(x<x0)x0=x;if(x>x1)x1=x;}
/* centre = the middle between the head's left and right edges at eye/cheek height (hair and shoulders are not symmetric) */
let ml=0,mr=0,rn=0;for(let y=top+Math.round(h*.12);y<top+Math.round(h*.22);y++){let l=-1,r=-1;for(let x=0;x<w;x++)if(p[(y*w+x)*4+3]>120){if(l<0)l=x;r=x;}if(l>=0){ml+=l;mr+=r;rn++;}}
const cx=rn?(ml+mr)/rn/2:sx/n,S=Math.round((hb-top)*1.75),X=Math.round(cx-S/2+S*.04),   /* owner: face a little more to the left in the circle */Y=Math.max(0,top-Math.round(S*.1));
const o=document.createElement('canvas');o.width=200;o.height=200;const og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(cv,X,Y,S,S,0,0,200,200);
return o.toDataURL('image/png');})()"""
c = Chrome(600, 600, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    open(os.path.join(HERE, 'poses', 'afnica_face.png'), 'wb').write(base64.b64decode(c.js(JS).split(',')[1])); print('ok')
finally: c.close()
