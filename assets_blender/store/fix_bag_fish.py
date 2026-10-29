# V17.120: the Gemini bag pictures all show the same orange fish. This finds that fish (the biggest cluster of saturated orange
# pixels), paints it out with the water around it (row by row, between the nearest non-fish pixels) and writes <name>_clean.png +
# poses/bagfish.json {name: [x, y, w, h, imgW, imgH]} so the game can draw the fish the customer really bought in its place.
# Run after cut_owner_poses.py / cut_sheet.py:  python fix_bag_fish.py
# Needs: cd D:\ClaudeWork\outro && python -m http.server 8792
import sys, os, time, base64, shutil, json, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
PZ = os.path.join(HERE, 'poses'); W = r'D:\ClaudeWork\outro'
files = [f for f in sorted(glob.glob(os.path.join(PZ, 'owner_bag.png')) + glob.glob(os.path.join(PZ, 'owner_give.png')) + glob.glob(os.path.join(PZ, 'person*_bag.png')))]
JS = r"""(async(name,cust)=>{const im=new Image();im.src=name;await im.decode();const w=im.naturalWidth,h=im.naturalHeight;
const cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d');g.drawImage(im,0,0);const I=g.getImageData(0,0,w,h),p=I.data;
const orange=k=>{const r=p[k*4],gg=p[k*4+1],b=p[k*4+2];return p[k*4+3]>60&&r>190&&gg>(cust?75:45)&&gg<175&&b<110&&r-gg>55&&r-b>110;};
/* biggest 8-connected orange cluster */
const lab=new Int32Array(w*h).fill(-1);let best=-1,bn=0,bb=null;
/* customers: the bag hangs from the front hand, so only look there (red hair / mustard sweaters are orange too) */
const inReg=k=>{if(!cust)return true;const x=k%w,y=(k-x)/w;return x>=w*.5&&y>=h*.3&&y<=h*.66;};
for(let k=0;k<w*h;k++){if(lab[k]>=0||!inReg(k)||!orange(k))continue;const id=k,st=[k];lab[k]=id;let n=0,x0=w,x1=0,y0=h,y1=0;
 while(st.length){const q=st.pop(),x=q%w,y=(q-x)/w;n++;if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=w||ny>=h)continue;const nk=ny*w+nx;if(lab[nk]<0&&inReg(nk)&&orange(nk)){lab[nk]=id;st.push(nk);}}}
 if(n>bn){bn=n;best=id;bb=[x0,y0,x1,y1];}}
if(!bb||bn<8)return JSON.stringify({err:'no fish',bn});
/* grow the cluster over the fish's shaded parts (any orange / red-ish pixel connected to it, within a box around it) */
const relaxed=k=>{const r=p[k*4],gg=p[k*4+1],b=p[k*4+2];return p[k*4+3]>40&&r>120&&r-b>45&&r-gg>18;};
const fw=bb[2]-bb[0]+1,fh=bb[3]-bb[1]+1,EX=Math.round(Math.max(fw,fh)*.7)+3,X0=Math.max(0,bb[0]-EX),Y0=Math.max(0,bb[1]-EX),X1=Math.min(w-1,bb[2]+EX),Y1=Math.min(h-1,bb[3]+EX);
const m=new Uint8Array(w*h),st2=[];for(let k=0;k<w*h;k++)if(lab[k]===best){m[k]=1;st2.push(k);}
while(st2.length){const q=st2.pop(),x=q%w,y=(q-x)/w;for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const nx=x+dx,ny=y+dy;if(nx<X0||ny<Y0||nx>X1||ny>Y1)continue;const nk=ny*w+nx;if(!m[nk]&&relaxed(nk)){m[nk]=1;st2.push(nk);}}}
const dil=(src,R)=>{const o=new Uint8Array(w*h);for(let y=Y0;y<=Y1;y++)for(let x=X0;x<=X1;x++){let hit=0;for(let dy=-R;dy<=R&&!hit;dy++)for(let dx=-R;dx<=R;dx++){const nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=w||ny>=h)continue;if(src[ny*w+nx]&&dx*dx+dy*dy<=R*R){hit=1;break;}}if(hit)o[y*w+x]=1;}return o;};
const R=Math.max(2,Math.round(Math.max(fw,fh)*.08)),m2=dil(m,R),ring=dil(m2,R+3);
/* water colour = average of the ring around the mask (not orange, not transparent) */
let acc=[0,0,0,0],n=0;for(let y=Y0;y<=Y1;y++)for(let x=X0;x<=X1;x++){const k=y*w+x;if(!ring[k]||m2[k]||relaxed(k)||p[k*4+3]<60)continue;for(let c=0;c<4;c++)acc[c]+=p[k*4+c];n++;}
const wc=n?acc.map(v=>v/n):[190,225,235,200];
/* cover: the grown mask plus an ellipse around the fish (the small sheet fish are blurry, their edges are not orange enough) */
const cx=(bb[0]+bb[2])/2,cy=(bb[1]+bb[3])/2,rx=Math.max(fw,fh*1.6)*.75+2,ry=Math.max(fh,fw*.55)*.8+2;
for(let y=Y0;y<=Y1;y++)for(let x=X0;x<=X1;x++){const k=y*w+x;if(p[k*4+3]<20)continue;const e=((x-cx)/rx)**2+((y-cy)/ry)**2;
 let f=m2[k]?1:e<=1?1:e<=1.45?(1.45-e)/.45:0;if(!f)continue;for(let c=0;c<3;c++)p[k*4+c]=p[k*4+c]*(1-f)+wc[c]*f;}
g.putImageData(I,0,0);
return JSON.stringify({url:cv.toDataURL('image/png'),box:[bb[0],bb[1],bb[2]-bb[0]+1,bb[3]-bb[1]+1,w,h],n:bn});})"""
meta = {}
c = Chrome(800, 800, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    for f in files:
        n = os.path.splitext(os.path.basename(f))[0]; shutil.copy(f, os.path.join(W, 'bf_' + n + '.png'))
        r = json.loads(c.js(JS + "(%s,%s)" % (json.dumps('bf_' + n + '.png'), 'true' if n.startswith('person') else 'false')))
        if 'err' in r: print('SKIP', n, r); continue
        open(os.path.join(PZ, n + '_clean.png'), 'wb').write(base64.b64decode(r['url'].split(',')[1])); meta[n] = r['box']; print(n, r['box'], r['n'])
finally: c.close()
json.dump(meta, open(os.path.join(PZ, 'bagfish.json'), 'w'), indent=1)
