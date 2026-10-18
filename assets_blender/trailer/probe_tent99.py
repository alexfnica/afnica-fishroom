# Bristle mask prototype (2026-10-18): in a male cell of the bristlenose sheet, separate the thin snout tentacles from the
# head by a morphological opening (erode + dilate) of the alpha, front part of the fish only. Writes a debug JPEG:
# cell (left), bristle mask in red over a darkened cell (right).   Run: python probe_tent99.py <out.jpg> [sx sy]
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
OUT = sys.argv[1]; SX, SY = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 38)
P = r"""(async(SX,SY)=>{const side=document.querySelector('#tank-main .ancSide');const u=/url\(["']?(.*?)["']?\)/.exec(side.dataset.originalImage||getComputedStyle(side).backgroundImage)[1];
 const im=new Image();im.src=u;await im.decode();const f=im.naturalWidth/480,cw=Math.round(120*f),ch=Math.round(70*f);
 const W=260,k=W/120,H=Math.round(ch*W/cw),c=document.createElement('canvas');c.width=W;c.height=H;const g=c.getContext('2d');g.drawImage(im,SX*f,SY*f,cw,ch,0,0,W,H);
 const d=g.getImageData(0,0,W,H).data,A=new Uint8Array(W*H);for(let i=0;i<W*H;i++)A[i]=d[i*4+3]>40?1:0;
 let x0=1e9,x1=-1;for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(A[y*W+x]){if(x<x0)x0=x;if(x>x1)x1=x;}const BL=x1-x0,xa=Math.round(x1-window.__U*BL);
 const R=Math.round(window.__R*k),mf=(src,fn)=>{const o=new Uint8Array(W*H);for(let y=0;y<H;y++)for(let x=0;x<W;x++){let v=fn==='min'?1:0;
   for(let yy=y-R;yy<=y+R&&(fn==='min'?v:!v);yy++)for(let xx=x-R;xx<=x+R;xx++){const q=xx<0||yy<0||xx>=W||yy>=H?0:src[yy*W+xx];if(fn==='min'&&!q){v=0;break;}if(fn==='max'&&q){v=1;break;}}o[y*W+x]=v;}return o;};
 const O=mf(mf(A,'min'),'max');let n=0;const M=new Uint8Array(W*H);for(let y=0;y<H;y++)for(let x=xa;x<W;x++){const i=y*W+x;if(A[i]&&!O[i]){M[i]=1;n++;}}
 const o=document.createElement('canvas');o.width=W*2;o.height=H;const q=o.getContext('2d');q.fillStyle='#235';q.fillRect(0,0,W*2,H);q.drawImage(c,0,0);q.globalAlpha=.35;q.drawImage(c,W,0);q.globalAlpha=1;
 const od=q.getImageData(W,0,W,H);for(let i=0;i<W*H;i++)if(M[i]){od.data[i*4]=255;od.data[i*4+1]=40;od.data[i*4+2]=40;od.data[i*4+3]=255;}q.putImageData(od,W,0);
 q.strokeStyle='#ff0';q.beginPath();q.moveTo(W+xa,0);q.lineTo(W+xa,H);q.stroke();
 return JSON.stringify({n,BL,xa,url:o.toDataURL('image/jpeg',.92)});})"""
c = anc_game(tank='main', fish="[T.fish('anc','M',40)]", warm=1)
try:
    c.js('window.__U=%s;window.__R=%s;1' % (os.environ.get('U', '.3'), os.environ.get('R', '1.6')))
    r = json.loads(c.js(P + '(%d,%d)' % (SX, SY)))
    open(OUT, 'wb').write(base64.b64decode(r.pop('url').split(',', 1)[1])); print(r)
finally: c.close()
