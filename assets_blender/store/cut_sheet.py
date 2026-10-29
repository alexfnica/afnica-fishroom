# V17.120: cuts a Gemini pose sheet (one person three times side by side on green: walk / walk with bag / point) into three
# transparent PNGs, 220 px tall like people/*.png. Figures that touch (a shoe on the next one's shoe, the bag on the next back) are
# split by a multi-source flood fill inside the opaque mask, seeded on each figure's head and body line, so every pixel goes to the
# figure it is connected to by the shortest path; nothing is cut by a straight line.
# Run: python cut_sheet.py <sheet image> <out prefix>   e.g.  poses/person02_sheet.webp poses/person02
# Needs: cd D:\ClaudeWork\outro && python -m http.server 8792 (the sheet is copied there).
import sys, os, time, base64, shutil, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
SRC = os.path.join(HERE, sys.argv[1]); OUT = os.path.join(HERE, sys.argv[2]); W = r'D:\ClaudeWork\outro'
NAMES = ('walk', 'bag', 'point')
shutil.copy(SRC, os.path.join(W, 'sheet_in' + os.path.splitext(SRC)[1]))
JS = r"""(async(name)=>{const im=new Image();im.src=name;await im.decode();const w=im.naturalWidth,h=im.naturalHeight;
const cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d');g.drawImage(im,0,0);
const D=g.getImageData(0,0,w,h),p=D.data;const c0=[p[0],p[1],p[2]];
for(let i=0;i<p.length;i+=4){const d=Math.hypot(p[i]-c0[0],p[i+1]-c0[1],p[i+2]-c0[2]);let a=Math.max(0,Math.min(1,(d-42)/38));
 /* green spill only on the soft edge and on pixels still close to the key colour (green clothes keep their green) */
 const m=Math.max(p[i],p[i+2]);if(p[i+1]>m+8&&(a<1||d<95))p[i+1]=a<1?m:Math.min(p[i+1],m+8);
 p[i+3]=Math.round(a*255)}
const op=k=>p[k*4+3]>20;
/* figures = column bands of opaque pixels in the head region (top 30% of the opaque height) */
let yT=0;for(;yT<h;yT++){let f=false;for(let x=0;x<w;x++)if(op(yT*w+x)){f=true;break;}if(f)break;}
let yB=h-1;for(;yB>0;yB--){let f=false;for(let x=0;x<w;x++)if(op(yB*w+x)){f=true;break;}if(f)break;}
const hy1=yT+Math.round((yB-yT)*.14),col=new Array(w).fill(0);
for(let y=yT;y<hy1;y++)for(let x=0;x<w;x++)if(op(y*w+x))col[x]++;
const heads=[];let s=-1;for(let x=0;x<=w;x++){const o=x<w&&col[x]>2;if(o&&s<0)s=x;if(!o&&s>=0){if(x-s>25)heads.push((s+x-1)/2);s=-1;}}
if(heads.length>3){heads.sort((a,b)=>a-b);}if(heads.length!==3)return JSON.stringify({err:'heads '+heads.length,heads});
/* seeds: every opaque pixel in a narrow column under each head, from the top to 60% height */
/* split by a cheapest-path fill (Dijkstra): a step costs more across a colour edge or a faint pixel, so the boundary between two
   touching figures follows the outline between them instead of the shortest way round */
const lab=new Int8Array(w*h).fill(-1),dist=new Float32Array(w*h).fill(1e9);
const H=[],push=(d,k)=>{H.push([d,k]);let i=H.length-1;while(i){const q=(i-1)>>1;if(H[q][0]<=H[i][0])break;[H[q],H[i]]=[H[i],H[q]];i=q;}},
 pop=()=>{const t=H[0],l=H.pop();if(H.length){H[0]=l;let i=0;for(;;){const a=2*i+1,b=a+1;let m=i;if(a<H.length&&H[a][0]<H[m][0])m=a;if(b<H.length&&H[b][0]<H[m][0])m=b;if(m===i)break;[H[m],H[i]]=[H[i],H[m]];i=m;}}return t;};
heads.forEach((hx,i)=>{for(let y=yT;y<yT+(yB-yT)*.6;y++)for(let x=Math.round(hx-6);x<=hx+6;x++){const k=y*w+x;if(op(k)&&dist[k]>0){dist[k]=0;lab[k]=i;push(0,k);}}});
while(H.length){const [d,k]=pop();if(d>dist[k])continue;const x=k%w,y=(k-x)/w,l=lab[k];
 for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=w||ny>=h)continue;const n=ny*w+nx;if(!op(n))continue;
  const e=Math.abs(p[k*4]-p[n*4])+Math.abs(p[k*4+1]-p[n*4+1])+Math.abs(p[k*4+2]-p[n*4+2]),nd=d+1+e*.25+(255-p[n*4+3])*.2;
  if(nd<dist[n]){dist[n]=nd;lab[n]=l;push(nd,n);}}}
const out=[];
for(let i=0;i<3;i++){let x0=w,x1=0,y0=h,y1=0;for(let k=0;k<w*h;k++)if(lab[k]===i){const x=k%w,y=(k-x)/w;if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;}
 const c=document.createElement('canvas');c.width=x1-x0+1;c.height=y1-y0+1;const cg=c.getContext('2d');const I=cg.createImageData(c.width,c.height);
 for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++){const k=y*w+x;if(lab[k]!==i)continue;const t=((y-y0)*c.width+(x-x0))*4;for(let ch=0;ch<4;ch++)I.data[t+ch]=p[k*4+ch];}
 cg.putImageData(I,0,0);
 const oh=220,ow=Math.round(c.width*oh/c.height),o=document.createElement('canvas');o.width=ow;o.height=oh;const og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(c,0,0,ow,oh);
 out.push({url:o.toDataURL('image/png'),box:[x0,y0,x1,y1]});}
return JSON.stringify({heads,out});})"""
c = Chrome(800, 800, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    r = json.loads(c.js(JS + "(%s)" % json.dumps('sheet_in' + os.path.splitext(SRC)[1])))
    if 'err' in r: sys.exit(json.dumps(r))
    for n, o in zip(NAMES, r['out']):
        open('%s_%s.png' % (OUT, n), 'wb').write(base64.b64decode(o['url'].split(',')[1])); print(n, o['box'])
finally: c.close()
