# V17.111 wriggler (yolk-sac larva): same cut, tuned for a pure WHITE background and a translucent pale body (no pocket step). Preview over a dark cave floor: <out>_dark.png
# Cut a fish photo off its plain grey background (headless Chrome, no PIL): the background and the soft floor shadow are
# flood-filled from the borders (neutral, light pixels), the fish keeps a 1 px soft edge. Output: RGBA PNG trimmed to the fish.
# Run: python cut_photo.py <in.(webp|jpg|png)> <out.png>
import sys, os, json, base64, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
src, out = sys.argv[1], sys.argv[2]
mime = {'webp': 'image/webp', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}[src.rsplit('.', 1)[1].lower()]
b64 = base64.b64encode(open(src, 'rb').read()).decode()
JS = r"""(async (src)=>{const im=new Image();im.src=src;await im.decode();const W=im.naturalWidth,H=im.naturalHeight;
const c=document.createElement('canvas');c.width=W;c.height=H;const g=c.getContext('2d');g.drawImage(im,0,0);const D=g.getImageData(0,0,W,H),d=D.data;
const sat=i=>Math.max(d[i],d[i+1],d[i+2])-Math.min(d[i],d[i+1],d[i+2]),L=i=>(d[i]+d[i+1]+d[i+2])/3;
/* background-like: neutral and light (the grey card and its soft shadow) */
const bgl=new Uint8Array(W*H);for(let p=0;p<W*H;p++){const i=p*4;bgl[p]=(sat(i)<14&&L(i)>172)?1:0;}
/* flood fill from every border pixel */
const bg=new Uint8Array(W*H),st=[];for(let x=0;x<W;x++){st.push(x,(H-1)*W+x);}for(let y=0;y<H;y++){st.push(y*W,y*W+W-1);}
while(st.length){const p=st.pop();if(bg[p]||!bgl[p])continue;bg[p]=1;const x=p%W,y=(p/W)|0;if(x>0)st.push(p-1);if(x<W-1)st.push(p+1);if(y>0)st.push(p-W);if(y<H-1)st.push(p+W);}
/* soft edge: fish pixels next to the background get partial alpha by how background-like they are */
let x0=W,y0=H,x1=0,y1=0;
for(let p=0;p<W*H;p++){const i=p*4;if(bg[p]){d[i+3]=0;continue;}const x=p%W,y=(p/W)|0;
 let nb=0;if(x>0&&bg[p-1])nb++;if(x<W-1&&bg[p+1])nb++;if(y>0&&bg[p-W])nb++;if(y<H-1&&bg[p+W])nb++;
 if(nb){const a=Math.min(1,Math.max(.25,(150-L(i))/60+sat(i)/40));d[i+3]=Math.round(255*a);}else d[i+3]=255;
 if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;}
/* translucent fins (BOXES [x0,x1,y0,y1]): alpha from how far each pixel is from the white card, colour kept; floor shadow rule (FLOOR [yShadow,xMin,yCut]) */
const BOXES=__BOXES__,FLOOR=__FLOOR__;
for(let p=0;p<W*H;p++){const i=p*4,x=p%W,y=(p/W)|0;
 for(const b of BOXES)if(x>=b[0]&&x<b[1]&&y>b[2]&&y<b[3]){const m=Math.min(d[i],d[i+1],d[i+2]);const a=Math.min(1,Math.max(0,(255-m-__THR__)/30));if(a>d[i+3]/255)d[i+3]=Math.round(255*a);break;}
 if(FLOOR){if(y>FLOOR[0]&&x>FLOOR[1]&&sat(i)<45)d[i+3]=0;if(y>FLOOR[2])d[i+3]=0;}}
g.putImageData(D,0,0);const pad=3;x0=Math.max(0,x0-pad);y0=Math.max(0,y0-pad);x1=Math.min(W-1,x1+pad);y1=Math.min(H-1,y1+pad);
const o=document.createElement('canvas');o.width=x1-x0+1;o.height=y1-y0+1;o.getContext('2d').drawImage(c,x0,y0,o.width,o.height,0,0,o.width,o.height);
const pv=document.createElement('canvas');pv.width=o.width;pv.height=o.height;const pg=pv.getContext('2d');pg.fillStyle='#2b1d15';pg.fillRect(0,0,pv.width,pv.height);pg.drawImage(o,0,0);return JSON.stringify({png:o.toDataURL('image/png'),dark:pv.toDataURL('image/png'),W,H,crop:[x0,y0,x1,y1]});})"""
BOXES = os.environ.get('BOXES', '[[90,250,262,352]]'); FLOOR = os.environ.get('FLOOR', '[335,300,378]')
JS = JS.replace('__THR__', os.environ.get('THR', '14')).replace('__BOXES__', BOXES).replace('__FLOOR__', FLOOR)
c = Chrome(400, 300, 1, port=int(os.environ.get('AF_PORT', '9471')))
try:
    r = json.loads(c.js(JS + "(%s)" % json.dumps('data:%s;base64,%s' % (mime, b64))))
    open(out, 'wb').write(base64.b64decode(r.pop('png').split(',')[1])); open(out.replace('.png','_dark.png'), 'wb').write(base64.b64decode(r.pop('dark').split(',')[1])); print(r)
finally: c.close()
