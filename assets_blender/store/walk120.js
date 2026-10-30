/* ===== V17.120 WALK RIG: a real walk cycle for the single-image customer sprites =====
   rigSpriteV120(img) splits a side-view cut-out (facing right, mid-stride) into upper body + back leg + front leg:
   the crotch is the lowest row where the legs merge, the legs are the two biggest blobs below it (left = back leg),
   the hip pivot sits a little above the crotch. drawWalkV120 swings each leg about the hip: stance = the foot slides
   back linearly (sin of the leg angle linear in phase, so no foot slip), swing = eased forward with a small lift;
   the body rides on the stance leg (highest at mid-stance). Phase 0 = the original image. */
(function(){
'use strict';
function rigSpriteV120(img,opt){
 opt=opt||{};const w=img.naturalWidth||img.width,h=img.naturalHeight||img.height,cv=document.createElement('canvas');cv.width=w;cv.height=h;
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
 /* fingertips that hang below the hem went to a thigh layer: give the pixels around each hand that are not leg-coloured back to the upper body */
 {const fh0=findHands(cv,w,h,(()=>{let y=0;while(y<h&&!runs(y).length)y++;return y;})(),yB);if(fh0){const rr=.075*h,gu=L.upper.getContext('2d'),U=gu.getImageData(0,0,w,h);
  for(const lc of [L.back,L.front]){const gl=lc.getContext('2d'),G=gl.getImageData(0,0,w,h);let ch=false;
   for(const q of fh0.hands)for(let y=Math.max(0,Math.floor(q.y-rr));y<Math.min(h,q.y+rr);y++)for(let x=Math.max(0,Math.floor(q.x-rr));x<Math.min(w,q.x+rr);x++){const k=(y*w+x)*4;if(!G.data[k+3])continue;
    const R0=G.data[k],G0=G.data[k+1],B0=G.data[k+2];if(Math.hypot(R0-low[0],G0-low[1],B0-low[2])<70)continue;   /* not trouser/leg coloured = part of the hand (skin, shading, soft edge) */
    for(let c=0;c<4;c++){U.data[k+c]=G.data[k+c];G.data[k+c]=0;}ch=true;}
   if(ch)gl.putImageData(G,0,0);}
  gu.putImageData(U,0,0);}}
 /* foot = the lowest 6% of each leg blob, mean x */
 const footX=c=>{let sx=0,n=0;for(let y=Math.round(c.maxY-h*.06);y<=c.maxY;y++)for(let x=0;x<w;x++)if(lab[y*w+x]===c.i){sx+=x;n++;}return n?sx/n:c.cx;};
 const leg=(c)=>{const fx=footX(c),fy=c.maxY,dx=fx-pv.x,dy=fy-pv.y;return {L:Math.hypot(dx,dy),a:Math.atan2(dx,dy),fy};};
 const B=leg(back),F=leg(front);
 const sF=Math.sin(F.a),sB=Math.sin(B.a);
 const arms=(opt.noArms||window.ARMS120===false)?null:armRig(L.upper,w,h,yT,yB,hem,opt.armSide),   /* arm swing: smooth field warp (V17.120b); window.ARMS120=false turns it off */
 fh=findHands(L.upper,w,h,yT,yB);
 const pt=fh?pointRig(L.upper,w,h,fh,yB-yT):null;
 /* waist filler source: the upper body's last rows above the hem without the hands (they swing; a copy left here showed as bars) */
 const wf=document.createElement('canvas');wf.width=w;wf.height=h;{const wg=wf.getContext('2d');wg.drawImage(L.upper,0,0);if(fh){wg.globalCompositeOperation='destination-out';for(const q of fh.hands){wg.beginPath();wg.arc(q.x,q.y,.055*(yB-yT),0,7);wg.fill();}}
  /* only over the thighs: outside them nothing is hidden under the legs, and a copy there would show */
  wg.globalCompositeOperation='destination-out';const xL=Math.min(KB.x,KF.x)-bw,xR=Math.max(KB.x,KF.x)+bw;wg.fillRect(0,0,Math.max(0,xL),h);wg.fillRect(xR,0,w,h);}
 return {w,h,pv,yc,hem,L,B,F,arms,fh,pt,wf,A:(sF-sB)/2,C:(sF+sB)/2,Lm:(B.L+F.L)/2,ground:Math.max(B.fy,F.fy)};
}
/* arms: the hands are the outermost silhouette points between 42% and 66% height (back hand left, front hand right);
   the shoulder sits at 22% height in the middle of the torso. Each arm is swung by a smooth rotation warp around the
   shoulder that fades out away from the shoulder-hand line, so the sleeve bends with the arm and nothing tears.
   16 walking frames (arm angle mirrored at half a cycle) + 1 standing frame are rendered once. */
function findHands(up,w,h,yT,yB){
 const H=yB-yT,S=up.getContext('2d').getImageData(0,0,w,h).data,op=(x,y)=>S[(y*w+x)*4+3]>110;
 const sy=Math.round(yT+.22*H);let a0=-1,a1=-1;for(let x=0;x<w;x++)if(op(x,sy)){if(a0<0)a0=x;a1=x;}
 if(a0<0)return null;
 const sh={x:(a0+a1)/2,y:sy};
 /* skin blobs in the hand band; on each side of the shoulder line the hand is the blob furthest out (a centroid of all skin
    on that side was pulled in by necklines, bare forearms and the other hand) */
 const y0=Math.round(yT+.42*H),y1=Math.round(yT+.62*H),lab=new Int32Array(w*h).fill(-1),blobs=[];
 const skin=(x,y)=>{if(!op(x,y))return false;const k=(y*w+x)*4,R=S[k],G=S[k+1],B=S[k+2];return R>95&&G>45&&B>25&&R>G+10&&R>B+25&&R-B<150;};
 for(let y=y0;y<y1;y++)for(let x=0;x<w;x++){if(lab[y*w+x]>=0||!skin(x,y))continue;const id=blobs.length,st=[[x,y]],b={n:0,sx:0,sy:0};lab[y*w+x]=id;
  while(st.length){const [px,py]=st.pop();b.n++;b.sx+=px;b.sy+=py;for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=px+dx,ny=py+dy;if(nx<0||nx>=w||ny<y0||ny>=y1||lab[ny*w+nx]>=0||!skin(nx,ny))continue;lab[ny*w+nx]=id;st.push([nx,ny]);}}
  blobs.push(b);}
 const sk=[0,1].map(side=>{let best=null,bd=-1;for(const b of blobs){if(b.n<=12)continue;const cx=b.sx/b.n;if((cx<sh.x?0:1)!==side)continue;const d=Math.abs(cx-sh.x);if(d>bd){bd=d;best=b;}}return best?[best.sx,best.sy,best.n]:[0,0,0];});
 const hands=sk.filter(v=>v[2]>12).map(v=>{const p={x:v[0]/v[2],y:v[1]/v[2]};const a=Math.atan2(p.x-sh.x,p.y-sh.y);return {...p,a,amp:Math.sign(a||1)*Math.min(Math.abs(a),window.ARMAMP120||.08)};});
 return hands.length?{sh,hands}:null;
}
function armRig(up,w,h,yT,yB,hem,armSide){
 /* arm swing from one walking picture: a smooth displacement field, strongest at each hand and fading towards the shoulder and
    sideways over about an arm's width, slides the forearm + hand forward/back (the sleeve and coat edge bend
    with it like cloth). The field is smooth everywhere, so nothing tears. The two hands move in opposite directions:
    dx = +-A*cos(2*pi*phase); at phase 0 the drawn pose is exaggerated a little, at half a cycle the arms have swung the other way. */
 const H=yB-yT,S=up.getContext('2d').getImageData(0,0,w,h).data;
 const fh=findHands(up,w,h,yT,yB);if(!fh)return null;const sh=fh.sh;
 const hs=fh.hands.slice().sort((a,b)=>a.x-b.x).filter(hd=>!armSide||(armSide==='front')===(hd.x>=fh.sh.x));   /* back hand (left) first, front hand (right) */
 const A=(window.ARMAMP120||.09)*H,sx=(window.ARMSX120||.1)*H;
 const arms=hs.map(hd=>({hd,dir:hd.x<sh.x?-1:1,y0:sh.y+(hd.y-sh.y)*.15,sy:Math.max(4,(hd.y-sh.y)*.85)}));
 const wt=(a,x,y)=>{const tl=Math.max(0,Math.min(1,(y-sh.y)/Math.max(1,a.hd.y-sh.y))),lx=sh.x+(a.hd.x-sh.x)*(.5+.5*tl),out=(x-lx)*(a.hd.x<sh.x?-1:1),ax=out>=-.045*H?0:(out+.045*H)/(.025*H);   /* the whole hand width and everything outside it moves as one (only background there), so the hand is never stretched */if(ax*ax>9)return 0;const v=(y-a.y0)/(a.hd.y+.12*H-a.y0);if(v<=0)return 0;const vv=Math.min(1,v),s2=vv*vv*(3-2*vv);
  const below=y>a.hd.y?Math.exp(-Math.pow((y-a.hd.y)/(.1*H),2)):1;
  const nearHand=ax===0||Math.hypot(x-a.hd.x,y-a.hd.y)<.1*H,hemF=hem&&!nearHand?Math.max(0,Math.min(1,(hem-2-y)/6)):1;return Math.exp(-ax*ax/2)*s2*below*hemF;};
 const W=arms.map(a=>{const f=new Float32Array(w*h);for(let y=0;y<h;y++)for(let x=0;x<w;x++)f[y*w+x]=wt(a,x,y);return f;});
 const frame=q=>{   /* q = cos(2*pi*phase) scaled; each hand moves dir*A*q */
  const o=document.createElement('canvas');o.width=w;o.height=h;const og=o.getContext('2d'),O=og.createImageData(w,h),T=O.data;
  const dAt=(xs,y)=>{const xi=Math.max(0,Math.min(w-1,Math.round(xs)));let d=0;for(let i=0;i<arms.length;i++){const ww=W[i][y*w+xi];if(ww)d+=arms[i].dir*A*q*ww;}return d;};
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){let dx=0,dy=0;
   /* the picture pixel s that the field carries onto x (x = s + d(s)), by fixed-point steps: the hand keeps its shape as it moves */
   {const sol=s0=>{let s2=s0;for(let it=0;it<8;it++)s2=x-dAt(s2,y);return Math.abs(s2+dAt(s2,y)-x)<.6?s2:null;};
    const full=arms.length?Math.max(...arms.map(a=>Math.abs(A*q))):0,cands=[sol(x)];for(const a of arms)cands.push(sol(x-a.dir*A*q));
    let best=null;for(const c of cands){if(c===null)continue;const xi=Math.max(0,Math.min(w-1,Math.round(c)));const op2=S[(y*w+xi)*4+3]>40,wg=Math.abs(dAt(c,y));
     if(!best||(op2&&!best.op)||(op2===best.op&&wg>best.wg))best={c,op:op2,wg};}
    dx=best?x-best.c:0;}
   const k=(y*w+x)*4;if(!dx&&!dy){T[k]=S[k];T[k+1]=S[k+1];T[k+2]=S[k+2];T[k+3]=S[k+3];continue;}
   const fx=x-dx,fy=y-dy,x0=Math.floor(fx),y0=Math.floor(fy),ax=fx-x0,ay=fy-y0;if(x0<0||y0<0||x0>=w-1||y0>=h-1)continue;
   /* premultiplied bilinear sample, so the soft edges do not darken */
   let a4=0,c0=0,c1=0,c2=0;for(const [xx,yy,f] of [[x0,y0,(1-ax)*(1-ay)],[x0+1,y0,ax*(1-ay)],[x0,y0+1,(1-ax)*ay],[x0+1,y0+1,ax*ay]]){const kk=(yy*w+xx)*4,al=S[kk+3]*f;a4+=al;c0+=S[kk]*al;c1+=S[kk+1]*al;c2+=S[kk+2]*al;}
   if(a4>0){T[k]=c0/a4;T[k+1]=c1/a4;T[k+2]=c2/a4;T[k+3]=a4;}}
  og.putImageData(O,0,0);return o;};
 /* q from 0 (as drawn) to -1 (hands in along the body) and back each cycle: the hands swing in towards the body between the drawn steps */
 const walk=[];for(let n=0;n<16;n++)walk.push(frame(-(1-Math.cos(2*Math.PI*n/16))/2));
 return {sh,hands:fh.hands,arms,A,walk,stand:frame(-.6)};   /* standing: hands a little closer to the body than drawn */
}
/* parent + child holding hands in one image (parent left, child right): cut at the emptiest column between them
   (where only the joined hands cross), rig each person on its own; no arm swing (they hold hands). */
function rigPairV120(img){
 const w=img.naturalWidth,h=img.naturalHeight,cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d');g.drawImage(img,0,0);
 const D=g.getImageData(0,0,w,h).data;let best=-1,bn=1e9;
 for(let x=Math.round(w*.35);x<w*.75;x++){let n=0;for(let y=0;y<h;y++)if(D[(y*w+x)*4+3]>60)n++;if(n<bn){bn=n;best=x;}}
 if(best<0)return null;
 const part=(x0,x1,crop)=>{let y0=0;if(crop){y0=h;for(let y=0;y<h&&y0===h;y++)for(let x=x0;x<x1;x++)if(D[(y*w+x)*4+3]>110){y0=Math.max(0,y-2);break;}}   /* the child is cropped to its own height so the rig's proportions fit it */
  const c=document.createElement('canvas');c.width=x1-x0;c.height=h-y0;c.getContext('2d').drawImage(cv,x0,y0,x1-x0,h-y0,0,0,x1-x0,h-y0);return c;};
 const still=c=>{const h=c.height,d=c.getContext('2d').getImageData(0,0,c.width,h).data;let yT=0,yB=h-1;const row=y=>{for(let x=0;x<c.width;x++)if(d[(y*c.width+x)*4+3]>110)return true;return false;};
  while(yT<h&&!row(yT))yT++;while(yB>0&&!row(yB))yB--;return {still:true,c,w:c.width,h,ground:yB,fh:findHands(c,c.width,h,yT,yB)};};
 const ca=part(0,best),cb=part(best,w,true);
 const A=rigSpriteV120(ca,{armSide:'back'})||still(ca),B=rigSpriteV120(cb,{armSide:'front'})||still(cb);   /* only the free hands swing; the joined hands stay together */
 if(A.still&&B.still)return null;
 return {pair:true,w,h,cut:best,parts:[{R:A,ox:0},{R:B,ox:best}]};
}
/* pointing: the front arm (shoulder -> front hand band) is lifted out of the upper body into its own layer; the hole it leaves
   is filled from the body pixels just behind it in the same row, so the arm can swing up towards a tank */
function pointRig(up,w,h,fh,H){
 const hd=fh.hands.slice().sort((a,b)=>b.x-a.x)[0],S=fh.sh,aw=.032*H,src=up.getContext('2d').getImageData(0,0,w,h),D=src.data;
 const vx=hd.x-S.x,vy=hd.y-S.y,L2=vx*vx+vy*vy,inArm=(x,y)=>{const t=((x-S.x)*vx+(y-S.y)*vy)/L2;if(t<.12||t>1.18)return false;const tc=Math.min(1,t);return Math.hypot(x-S.x-tc*vx,y-S.y-tc*vy)<aw;};
 const A=new ImageData(w,h),B=new ImageData(new Uint8ClampedArray(D),w,h);
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){if(!inArm(x,y))continue;const k=(y*w+x)*4;for(let c=0;c<4;c++)A.data[k+c]=D[k+c];
  let f=-1;for(let xx=x-1;xx>=Math.max(0,x-14);xx--){if(!inArm(xx,y)&&D[(y*w+xx)*4+3]>150){f=(y*w+xx)*4;break;}}
  if(f>=0&&D[k+3]>40){for(let c=0;c<3;c++)B.data[k+c]=D[f+c];B.data[k+3]=D[k+3];}else B.data[k+3]=0;}
 const cv=I=>{const o=document.createElement('canvas');o.width=w;o.height=h;o.getContext('2d').putImageData(I,0,0);return o;};
 /* rotation that takes the arm from its drawn angle to pointing forward, a little above level */
 return {S,arm:cv(A),base:cv(B),rot:hd.a-Math.PI*.56};
}
/* a clear fish bag hanging from a hand point (image px), knot in the fist */
function drawBagV120(ctx,x,y,col,ang,img){
 ctx.save();ctx.translate(x,y+2);if(ang)ctx.rotate(ang);
 const body=()=>{ctx.beginPath();ctx.moveTo(-3,2);ctx.quadraticCurveTo(-14,12,-12,27);ctx.quadraticCurveTo(0,33,12,27);ctx.quadraticCurveTo(14,12,3,2);ctx.closePath();};
 body();ctx.fillStyle='rgba(200,238,255,.5)';ctx.fill();
 ctx.save();body();ctx.clip();ctx.fillStyle='rgba(47,170,214,.55)';ctx.fillRect(-15,13,30,22);
 if(img&&img.complete&&img.naturalWidth){const fw=15,fh=fw*img.naturalHeight/img.naturalWidth;ctx.drawImage(img,-fw/2,21-fh/2,fw,fh);}   /* the fish that was bought */
 else{ctx.fillStyle=col||'#ff9a3c';ctx.beginPath();ctx.ellipse(-1,21,5,2.6,0,0,7);ctx.fill();ctx.beginPath();ctx.moveTo(4,21);ctx.lineTo(8,18);ctx.lineTo(8,24);ctx.closePath();ctx.fill();}
 ctx.restore();
 body();ctx.strokeStyle='rgba(235,250,255,.95)';ctx.lineWidth=1.2;ctx.stroke();
 ctx.beginPath();ctx.moveTo(-6,10);ctx.quadraticCurveTo(-9,17,-8,23);ctx.strokeStyle='rgba(255,255,255,.7)';ctx.lineWidth=1.5;ctx.stroke();
 ctx.fillStyle='rgba(225,245,255,.95)';ctx.beginPath();ctx.ellipse(0,1.5,3.5,2,0,0,7);ctx.fill();
 ctx.restore();
}
/* hand point for this frame: the drawn hand rotated by the same arm angle as the warp frames */
function handAt(R,phase,m,which){
 const fh=R.fh;if(!fh)return null;const hs=fh.hands.slice().sort((a,b)=>a.x-b.x);const hd=which==='back'?hs[0]:hs[hs.length-1];
 let ang=0;if(R.arms){const n=Math.round((((phase%1)+1)%1)*16)%16,q=m*-(1-Math.cos(2*Math.PI*n/16))/2+(1-m)*-.6,a=R.arms.arms.find(x=>x.hd.x===hd.x&&x.hd.y===hd.y);if(a)return {x:hd.x+a.dir*R.arms.A*q,y:hd.y};}
 const dx=hd.x-fh.sh.x,dy=hd.y-fh.sh.y,c=Math.cos(ang),s2=Math.sin(ang);return {x:fh.sh.x+dx*c-dy*s2,y:fh.sh.y+dx*s2+dy*c};
}
/* leg state for phase q in [0,1): stance first half (foot slides back linearly), swing second half (eased forward) */
function legS(R,q){q=((q%1)+1)%1;if(q<.5)return {s:R.C+R.A*(1-4*q),sw:0};const v=(q-.5)/.5;return {s:R.C-R.A*Math.cos(Math.PI*v),sw:Math.sin(Math.PI*v)};}
/* draws the rig into ctx with its feet-centre at (0,0) scaled by k; phase = cycle position, m = 0 standing .. 1 walking */
function drawWalkV120(ctx,R,phase,m,k,bag,pt,over){
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
 /* waist filler: the last rows above the hem smeared a few px down behind the legs, so no light seam shows where the thighs turn */
 if(R.wf){const y0=Math.round(R.hem)-3;for(const d of [2,4,6])ctx.drawImage(R.wf,0,y0,R.w,3,0,y0+d,R.w,3);}
 drawLeg(R.L.back,R.B.a,tB,B.sw);
 drawLeg(R.L.front,R.F.a,tF,F.sw);
 /* upper body: a slight forward lean when walking and a small sway with each step (about the hip) */
 {const a=m*(.035+.012*Math.sin(4*Math.PI*phase));ctx.translate(R.pv.x,R.pv.y);ctx.rotate(a);ctx.translate(-R.pv.x,-R.pv.y);}
if(pt>0&&R.pt){ctx.drawImage(R.pt.base,0,0);ctx.save();ctx.translate(R.pt.S.x,R.pt.S.y);ctx.rotate(R.pt.rot*pt);ctx.translate(-R.pt.S.x,-R.pt.S.y);ctx.drawImage(R.pt.arm,0,0);ctx.restore();}
 else if(R.arms){const n=Math.round((((phase%1)+1)%1)*16)%16;
  if(m<1){ctx.globalAlpha=1-m;ctx.drawImage(R.arms.stand,0,0);}
  if(m>0){ctx.globalAlpha=m;ctx.drawImage(R.arms.walk[n],0,0);}
  ctx.globalAlpha=1;}
 else ctx.drawImage(R.L.upper,0,0);
 if(bag){const hp=handAt(R,phase,m,bag.hand);if(hp)drawBagV120(ctx,hp.x,hp.y,bag.col,bag.ang||0,bag.img);}
 if(over)over(ctx);   /* drawn in the picture's own pixels (e.g. the bought fish in a bag pose) */
 ctx.restore();
}
function drawPairV120(ctx,P,dist,m,k,bag,pt){
 P.parts.forEach((q,i)=>{const R=q.R,b=i===0&&bag?{col:bag.col,hand:'back',ang:bag.ang,img:bag.img}:null;ctx.save();ctx.translate((q.ox+R.w/2-P.w/2)*k,0);
  if(R.still){const bob=-Math.abs(Math.sin(dist*.12))*1.6*m;ctx.scale(k,k);ctx.translate(-R.w/2,-R.ground+bob);ctx.drawImage(R.c,0,0);
   if(b&&R.fh){const hd=R.fh.hands.slice().sort((a,c)=>a.x-c.x)[0];drawBagV120(ctx,hd.x,hd.y,b.col,bag.ang||0,bag.img);}}
  else drawWalkV120(ctx,R,dist/(cycleLenV120(R)*k),m,k,b,i===1?pt:0);   /* the child points with its free hand */
  ctx.restore();});
}
window.drawPairV120=drawPairV120;
/* image px travelled per full cycle (two steps): during stance the foot moves 2*A*L back relative to the hip */
function cycleLenV120(R){return 4*R.A*R.Lm;}
window.rigSpriteV120=rigSpriteV120;window.rigPairV120=rigPairV120;window.drawWalkV120=drawWalkV120;window.cycleLenV120=cycleLenV120;
})();
