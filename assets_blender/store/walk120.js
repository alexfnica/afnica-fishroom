/* ===== V17.120 WALK RIG: a real walk cycle for the single-image customer sprites =====
   rigSpriteV120(img) splits a side-view cut-out (facing right, mid-stride) into upper body + back leg + front leg:
   the crotch is the lowest row where the legs merge, the legs are the two biggest blobs below it (left = back leg),
   the hip pivot sits a little above the crotch. drawWalkV120 swings each leg about the hip: stance = the foot slides
   back linearly (sin of the leg angle linear in phase, so no foot slip), swing = eased forward with a small lift;
   the body rides on the stance leg (highest at mid-stance). Phase 0 = the original image. */
(function(){
'use strict';
function rigSpriteV120(img){
 const w=img.naturalWidth,h=img.naturalHeight,cv=document.createElement('canvas');cv.width=w;cv.height=h;
 const g=cv.getContext('2d');g.drawImage(img,0,0);const D=g.getImageData(0,0,w,h).data;
 const op=(x,y)=>D[(y*w+x)*4+3]>110;
 const runs=y=>{const r=[];let s=-1;for(let x=0;x<=w;x++){const o=x<w&&op(x,y);if(o&&s<0)s=x;if(!o&&s>=0){if(x-s>=2)r.push([s,x-1]);s=-1;}}return r;};
 let yB=h-1;while(yB>0&&!runs(yB).length)yB--;
 /* crotch: going up from the feet, the first row (above the lower 15%) whose runs no longer include two leg runs */
 let yc=-1;
 for(let y=Math.round(yB-h*.15);y>h*.3;y--){const r=runs(y);if(r.length<2){yc=y;break;}}
 if(yc<0)return null;
 /* components below the crotch */
 const lab=new Int32Array(w*h).fill(-1),comps=[];
 for(let y=yc+1;y<=yB;y++)for(let x=0;x<w;x++){
  if(!op(x,y)||lab[y*w+x]>=0)continue;
  const id=comps.length,st=[[x,y]],c={n:0,sx:0,maxY:0,feet:[]};lab[y*w+x]=id;
  while(st.length){const [px,py]=st.pop();c.n++;c.sx+=px;if(py>c.maxY)c.maxY=py;
   for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=px+dx,ny=py+dy;if(nx<0||nx>=w||ny<=yc||ny>yB)continue;const k=ny*w+nx;if(lab[k]<0&&op(nx,ny)){lab[k]=id;st.push([nx,ny]);}}}
  comps.push(c);
 }
 const legs=comps.map((c,i)=>({i,...c,cx:c.sx/c.n})).sort((a,b)=>b.n-a.n).slice(0,2);
 if(legs.length<2||legs[1].n<legs[0].n*.25)return null;
 legs.sort((a,b)=>a.cx-b.cx);
 const [back,front]=legs;
 /* knees = top of each lower-leg blob; the thighs overlap above them in a side view */
 const knee=c=>{for(let y=yc+1;y<yc+8;y++){let sx=0,n=0;for(let x=0;x<w;x++)if(lab[y*w+x]===c.i){sx+=x;n++;}if(n)return {x:sx/n,y};}return {x:c.cx,y:yc+1};};
 const KB=knee(back),KF=knee(front);
 let yT=0;while(yT<h&&!runs(yT).length)yT++;
 const pv={x:(KB.x+KF.x)/2,y:yT+.53*(yB-yT)};
 const bw=h*.085;
 const dseg=(x,y,K)=>{const vx=K.x-pv.x,vy=K.y-pv.y,t=Math.max(0,Math.min(1,((x-pv.x)*vx+(y-pv.y)*vy)/(vx*vx+vy*vy)));return Math.hypot(x-pv.x-t*vx,y-pv.y-t*vy);};
 /* hem: going down from the hip, the first rows whose colour inside the thigh band matches the lower legs (trousers / skin)
    = where the legs come out from under a jacket, coat or skirt */
 const rowCol=y=>{let r=0,g2=0,b2=0,n=0;for(let x=0;x<w;x++){if(!op(x,y))continue;if(Math.min(dseg(x,y,KB),dseg(x,y,KF))>bw)continue;const k=(y*w+x)*4;r+=D[k];g2+=D[k+1];b2+=D[k+2];n++;}return n?[r/n,g2/n,b2/n]:null;};
 let low=[0,0,0],ln=0;for(let y=yc+4;y<Math.min(yB,yc+24);y++)for(let x=0;x<w;x++){const l=lab[y*w+x];if(l!==back.i&&l!==front.i)continue;const k=(y*w+x)*4;low[0]+=D[k];low[1]+=D[k+1];low[2]+=D[k+2];ln++;}
 low=low.map(v=>v/(ln||1));
 let hem=yc,run2=0;
 for(let y=Math.round(pv.y);y<yc;y++){const c=rowCol(y);if(c&&Math.hypot(c[0]-low[0],c[1]-low[1],c[2]-low[2])<50){if(++run2>=2){hem=y-1;break;}}else run2=0;}
 /* soft edge pixels (alpha below the blob threshold) join the leg blob next to them, so nothing is left behind */
 for(let y=yc+1;y<=Math.min(h-1,yB+2);y++)for(let x=0;x<w;x++){const k=y*w+x;if(lab[k]>=0||!D[k*4+3])continue;
  let best=-1;for(let r=1;r<=3&&best<0;r++)for(let dy=-r;dy<=r&&best<0;dy++)for(let dx=-r;dx<=r;dx++){const nx=x+dx,ny=y+dy;if(nx<0||nx>=w||ny<=yc||ny>=h)continue;const l=lab[ny*w+nx];if(l===back.i||l===front.i){best=l;break;}}
  if(best>=0)lab[k]=best;}
 /* which leg a pixel belongs to: lower legs by blob, thighs (hem..crotch) by the nearer hip-knee band */
 const legOf=(x,y,l)=>{if(y>yc)return l===back.i?1:l===front.i?2:0;if(y<hem)return 0;const db=dseg(x,y,KB),df=dseg(x,y,KF);if(Math.min(db,df)>bw)return 0;return db<df?1:2;};
 const layer=pick=>{const o=document.createElement('canvas');o.width=w;o.height=h;const og=o.getContext('2d');const I=og.createImageData(w,h);
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const k=y*w+x;if(D[k*4+3]&&pick(legOf(x,y,lab[k]))){I.data[k*4]=D[k*4];I.data[k*4+1]=D[k*4+1];I.data[k*4+2]=D[k*4+2];I.data[k*4+3]=D[k*4+3];}}
  og.putImageData(I,0,0);return o;};
 const L={back:layer(v=>v===1),front:layer(v=>v===2),upper:layer(v=>v===0)};
 /* foot = the lowest 6% of each leg blob, mean x */
 const footX=c=>{let sx=0,n=0;for(let y=Math.round(c.maxY-h*.06);y<=c.maxY;y++)for(let x=0;x<w;x++)if(lab[y*w+x]===c.i){sx+=x;n++;}return n?sx/n:c.cx;};
 const leg=(c)=>{const fx=footX(c),fy=c.maxY,dx=fx-pv.x,dy=fy-pv.y;return {L:Math.hypot(dx,dy),a:Math.atan2(dx,dy),fy};};
 const B=leg(back),F=leg(front);
 const sF=Math.sin(F.a),sB=Math.sin(B.a);
 const arms=armRig(L.upper,w,h,yT,yB);
 return {w,h,pv,yc,hem,L,B,F,arms,A:(sF-sB)/2,C:(sF+sB)/2,Lm:(B.L+F.L)/2,ground:Math.max(B.fy,F.fy)};
}
/* arms: the hands are the outermost silhouette points between 42% and 66% height (back hand left, front hand right);
   the shoulder sits at 22% height in the middle of the torso. Each arm is swung by a smooth rotation warp around the
   shoulder that fades out away from the shoulder-hand line, so the sleeve bends with the arm and nothing tears.
   16 walking frames (arm angle mirrored at half a cycle) + 1 standing frame are rendered once. */
function armRig(up,w,h,yT,yB){
 const H=yB-yT,g=up.getContext('2d'),I=g.getImageData(0,0,w,h),S=I.data,op=(x,y)=>S[(y*w+x)*4+3]>110;
 const sy=Math.round(yT+.22*H);let a0=-1,a1=-1;for(let x=0;x<w;x++)if(op(x,sy)){if(a0<0)a0=x;a1=x;}
 if(a0<0)return null;
 const sh={x:(a0+a1)/2,y:sy};
 /* hands = skin-coloured pixels between 42% and 62% height, left / right of the shoulder line (coats and sleeves are ignored) */
 const sk=[[0,0,0],[0,0,0]];
 for(let y=Math.round(yT+.42*H);y<yT+.62*H;y++)for(let x=0;x<w;x++){if(!op(x,y))continue;const k=(y*w+x)*4,R=S[k],G=S[k+1],B=S[k+2];
  if(!(R>95&&G>45&&B>25&&R>G+10&&R>B+25&&R-B<150))continue;const i=x<sh.x?0:1;sk[i][0]+=x;sk[i][1]+=y;sk[i][2]++;}
 const hands=sk.filter(v=>v[2]>12).map(v=>{const p={x:v[0]/v[2],y:v[1]/v[2]};return {...p,a:Math.atan2(p.x-sh.x,p.y-sh.y)};});
 if(!hands.length)return null;
 const aw=.02*H;
 const warp=angs=>{const o=document.createElement('canvas');o.width=w;o.height=h;const og=o.getContext('2d'),O=og.createImageData(w,h),T=O.data;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
   let sx=x,sy2=y;
   for(let i=0;i<hands.length;i++){const hd=hands[i],vx=hd.x-sh.x,vy=hd.y-sh.y,L2=vx*vx+vy*vy,t=((x-sh.x)*vx+(y-sh.y)*vy)/L2;
    if(t<-.05||t>1.25)continue;const tc=Math.max(0,Math.min(1,t)),d=Math.hypot(x-sh.x-tc*vx,y-sh.y-tc*vy);
    const wd=d<aw?1:d>1.5*aw?0:1-(d-aw)/(.5*aw),wt=Math.max(0,Math.min(1,(t-.12)/.35));const wgt=wd*wd*(3-2*wd)*wt;if(!wgt)continue;
    const ph=-angs[i]*wgt,c=Math.cos(ph),sn=Math.sin(ph),dx=sx-sh.x,dy=sy2-sh.y;sx=sh.x+dx*c-dy*sn;sy2=sh.y+dx*sn+dy*c;}
   const x0=Math.floor(sx),y0=Math.floor(sy2),fx=sx-x0,fy=sy2-y0,k=(y*w+x)*4;
   if(x0<0||y0<0||x0>=w-1||y0>=h-1)continue;
   for(let ch=0;ch<4;ch++){const q=(yy,xx)=>S[(yy*w+xx)*4+ch];T[k+ch]=(q(y0,x0)*(1-fx)+q(y0,x0+1)*fx)*(1-fy)+(q(y0+1,x0)*(1-fx)+q(y0+1,x0+1)*fx)*fy;}}
  og.putImageData(O,0,0);return o;};
 /* rotation that takes each hand from its drawn angle a to a*cos(2*pi*phase) (mirrored at half a cycle); standing = arms hanging at 20% */
 const amp=hd=>Math.sign(hd.a||1)*Math.min(Math.abs(hd.a),.15);
 const walk=[];for(let n=0;n<16;n++){const cph=Math.cos(2*Math.PI*n/16);walk.push(warp(hands.map(hd=>amp(hd)*(cph-1))));}
 return {sh,hands,walk,stand:warp(hands.map(hd=>-amp(hd)*.8))};
}
/* leg state for phase q in [0,1): stance first half (foot slides back linearly), swing second half (eased forward) */
function legS(R,q){q=((q%1)+1)%1;if(q<.5)return {s:R.C+R.A*(1-4*q),sw:0};const v=(q-.5)/.5;return {s:R.C-R.A*Math.cos(Math.PI*v),sw:Math.sin(Math.PI*v)};}
/* draws the rig into ctx with its feet-centre at (0,0) scaled by k; phase = cycle position, m = 0 standing .. 1 walking */
function drawWalkV120(ctx,R,phase,m,k){
 const f=legS(R,phase),b=legS(R,phase+.5);
 const st={s:R.C+R.A*.12,sw:0},sb={s:R.C-R.A*.12,sw:0};
 const mix=(a,s)=>({s:s.s+(a.s-s.s)*m,sw:a.sw*m});
 const F=mix(f,st),B=mix(b,sb);
 const tF=Math.asin(Math.max(-.99,Math.min(.99,F.s))),tB=Math.asin(Math.max(-.99,Math.min(.99,B.s)));
 /* the body rides on the leg that is not swinging (the one with the smaller swing lift) */
 const stance=F.sw<=B.sw?{t:tF,L:R.F.L}:{t:tB,L:R.B.L};
 const hip0=R.ground-R.pv.y,lift=-(stance.L*Math.cos(stance.t)-hip0);
 ctx.save();ctx.scale(k,k);ctx.translate(-R.w/2,-R.ground+lift);
 const drawLeg=(cv,base,t,sw)=>{ctx.save();ctx.translate(R.pv.x,R.pv.y);ctx.rotate(-(t-base));ctx.scale(1,1-.07*sw);ctx.translate(-R.pv.x,-R.pv.y);ctx.drawImage(cv,0,0);ctx.restore();};
 drawLeg(R.L.back,R.B.a,tB,B.sw);
 drawLeg(R.L.front,R.F.a,tF,F.sw);
if(R.arms){const n=Math.round((((phase%1)+1)%1)*16)%16;
  if(m<1){ctx.globalAlpha=1-m;ctx.drawImage(R.arms.stand,0,0);}
  if(m>0){ctx.globalAlpha=m;ctx.drawImage(R.arms.walk[n],0,0);}
  ctx.globalAlpha=1;}
 else ctx.drawImage(R.L.upper,0,0);
 ctx.restore();
}
/* image px travelled per full cycle (two steps): during stance the foot moves 2*A*L back relative to the hip */
function cycleLenV120(R){return 4*R.A*R.Lm;}
window.rigSpriteV120=rigSpriteV120;window.drawWalkV120=drawWalkV120;window.cycleLenV120=cycleLenV120;
})();
