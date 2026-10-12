# Cut the owner's terracotta cave photo (incoming/anc_cave_photo.jpg, flat grey background) for the game (V17.89):
# tube opaque with a soft edge, the photo's floor shadow kept as a transparent black shadow, the dark opening measured.
# Output: incoming/anc_cave_cut.png (2x the in-game size) + incoming/anc_cave_geo.json. Runs in headless Chrome.
import os, sys, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trailer'))
from cdp import Chrome
HERE = os.path.dirname(os.path.abspath(__file__))
src = base64.b64encode(open(os.path.join(HERE, 'incoming', 'anc_cave_photo.jpg'), 'rb').read()).decode()
JS = r"""(async src=>{const im=new Image();im.src='data:image/jpeg;base64,'+src;await im.decode();
const W=im.naturalWidth,H=im.naturalHeight,c=document.createElement('canvas');c.width=W;c.height=H;const g=c.getContext('2d');g.drawImage(im,0,0);
const D=g.getImageData(0,0,W,H),d=D.data;let br=0,bg=0,bb=0,n=0;
for(const[x0,y0]of[[5,5],[W-30,5],[5,H-30],[W-30,H-30],[W/2,8]])for(let y=y0;y<y0+20;y++)for(let x=x0;x<x0+20;x++){const p=(y*W+(x|0))*4;br+=d[p];bg+=d[p+1];bb+=d[p+2];n++;}
br/=n;bg/=n;bb/=n;const bl=(br+bg+bb)/3,sm=(a,b,v)=>{const t=Math.max(0,Math.min(1,(v-a)/(b-a)));return t*t*(3-2*t);};
let x0=W,x1=0,y0=H,y1=0;
for(let i=0;i<d.length;i+=4){const r=d[i],G=d[i+1],b=d[i+2],L=(r+G+b)/3,sat=Math.max(r,G,b)-Math.min(r,G,b);
 let a=Math.max(sm(14,34,sat-(Math.max(br,bg,bb)-Math.min(br,bg,bb))),sm(bl-70,bl-120,L));            /* clay (saturated) or the dark inside */
 const sh=Math.max(0,Math.min(1,(bl-L-4)/(bl*.55)));                                                   /* the floor shadow: darker grey */
 if(a<1){const A=a+(1-a)*sh;if(A>0){d[i]=a*r/A;d[i+1]=a*G/A;d[i+2]=a*b/A;}d[i+3]=Math.round(A*255);}else d[i+3]=255;
 if(d[i+3]>20){const x=(i/4)%W,y=(i/4/W)|0;if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;}}
g.putImageData(D,0,0);
/* the opening: dark pixels in the left third */
let ox0=W,ox1=0,oy0=H,oy1=0;const E=g.getImageData(0,0,W,H).data;
for(let y=0;y<H;y++)for(let x=0;x<W*.35;x++){const p=(y*W+x)*4;const L=(E[p]+E[p+1]+E[p+2])/3;if(E[p+3]>250&&L<70){if(x<ox0)ox0=x;if(x>ox1)ox1=x;if(y<oy0)oy0=y;if(y>oy1)oy1=y;}}
/* tube body (opaque) bbox without the shadow */
let tx0=W,tx1=0,ty0=H,ty1=0;for(let y=0;y<H;y++)for(let x=0;x<W;x++){const p=(y*W+x)*4;if(E[p+3]>250){if(x<tx0)tx0=x;if(x>tx1)tx1=x;if(y<ty0)ty0=y;if(y>ty1)ty1=y;}}
const pad=4;x0=Math.max(0,x0-pad);y0=Math.max(0,y0-pad);x1=Math.min(W-1,x1+pad);y1=Math.min(H-1,y1+pad);
const OW=320,sc=OW/(x1-x0),OH=Math.round((y1-y0)*sc),o=document.createElement('canvas');o.width=OW;o.height=OH;const q=o.getContext('2d');q.imageSmoothingQuality='high';q.drawImage(c,x0,y0,x1-x0,y1-y0,0,0,OW,OH);
const f=v=>+(v).toFixed(1);
return JSON.stringify({png:o.toDataURL('image/png'),W:OW,H:OH,scale:sc,bg:[br,bg,bb].map(Math.round),
 open:{x0:f((ox0-x0)*sc),x1:f((ox1-x0)*sc),y0:f((oy0-y0)*sc),y1:f((oy1-y0)*sc)},tube:{x0:f((tx0-x0)*sc),x1:f((tx1-x0)*sc),y0:f((ty0-y0)*sc),y1:f((ty1-y0)*sc)}});})"""
c = Chrome(400, 300, 1, port=9370)
try:
    r = json.loads(c.js(JS + "(%s)" % json.dumps(src)))
    png = r.pop('png'); open(os.path.join(HERE, 'incoming', 'anc_cave_cut.png'), 'wb').write(base64.b64decode(png.split(',')[1]))
    json.dump(r, open(os.path.join(HERE, 'incoming', 'anc_cave_geo.json'), 'w'), indent=1); print(r)
finally: c.close()
