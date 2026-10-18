# Sheet cell check (2026-10-17): does any fish photo in the bristlenose sheet run past its 120x70 css-px cell window
# (the fin canvases crop exactly that window, so anything outside is cut off)? Prints opaque pixels on each cell border
# and the opaque bounding box of the fish in the cell + 20 px around it.
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
P = r"""(async()=>{const side=document.querySelector('#tank-main .ancSide');const u=/url\(["']?(.*?)["']?\)/.exec(side.dataset.originalImage||getComputedStyle(side).backgroundImage)[1];
 const im=new Image();im.src=u;await im.decode();const f=im.naturalWidth/480,c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;
 const g=c.getContext('2d');g.drawImage(im,0,0);const d=g.getImageData(0,0,c.width,c.height).data,W=c.width,H=c.height,A=(x,y)=>x<0||y<0||x>=W||y>=H?0:d[(y*W+x)*4+3];
 const out=[];for(const sy of [38,138,238,338,438,538])for(const sx of [0,120,240,360]){
  const x0=Math.round(sx*f),y0=Math.round(sy*f),x1=Math.round((sx+120)*f)-1,y1=Math.round((sy+70)*f)-1;let b={l:0,r:0,t:0,b:0};
  for(let y=y0;y<=y1;y++){if(A(x0,y)>60)b.l++;if(A(x1,y)>60)b.r++;}for(let x=x0;x<=x1;x++){if(A(x,y0)>60)b.t++;if(A(x,y1)>60)b.b++;}
  let bx0=1e9,by0=1e9,bx1=-1,by1=-1;const m=Math.round(20*f);for(let y=y0;y<=y1;y++)for(let x=x0-m;x<=x1+m;x++)if(A(x,y)>60){bx0=Math.min(bx0,x);bx1=Math.max(bx1,x);by0=Math.min(by0,y);by1=Math.max(by1,y);}
  out.push([sx,sy,b,bx1<0?null:[+((bx0-x0)/f).toFixed(1),+((by0-y0)/f).toFixed(1),+((bx1-x0)/f).toFixed(1),+((by1-y0)/f).toFixed(1)]]);}
 return JSON.stringify({f,out});})()"""
c = anc_game(tank='main', fish="[T.fish('anc','F',36)]", warm=1)
try:
    r = json.loads(c.js(P, await_=True) if 'await_' in c.js.__code__.co_varnames else c.js(P))
    print('sheet scale', r['f'])
    for sx, sy, b, bb in r['out']: print('cell %3d,%3d border opaque %s  fish box (css px, cell is 0..120 x 0..70) %s' % (sx, sy, b, bb))
finally: c.close()
