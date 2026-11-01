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
 const g=cv.getContext('2d');g.drawImage(img,0,0);const ID=g.getImageData(0,0,w,h),D=ID.data;
 /* green-screen rim: edge pixels (within 2 px of the background) keep no more green than their red/blue allow; it showed as a
    dark green outline round shoes, trousers and hands once the legs moved. Inside the figure nothing changes (green clothes stay). */
 {const A0=new Uint8Array(w*h);for(let i=0;i<w*h;i++)A0[i]=D[i*4+3];
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x,k=i*4;if(!A0[i])continue;let edge=A0[i]<250;
   for(let dy=-2;dy<=2&&!edge;dy++)for(let dx=-2;dx<=2;dx++){const xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=w||yy>=h||A0[yy*w+xx]<20){edge=true;break;}}
   if(!edge)continue;const m=Math.max(D[k],D[k+2]);if(D[k+1]>m+4)D[k+1]=m+4;}
  g.putImageData(ID,0,0);}
 const op=(x,y)=>D[(y*w+x)*4+3]>110;
 const runs=y=>{const r=[];let s=-1;for(let x=0;x<=w;x++){const o=x<w&&op(x,y);if(o&&s<0)s=x;if(!o&&s>=0){if(x-s>=2)r.push([s,x-1]);s=-1;}}return r;};
 let yB=h-1;while(yB>0&&!runs(yB).length)yB--;
 /* crotch: going up from the feet, the first row (above the lower 15%) whose runs no longer include two leg runs */
 let yc=-1;
 for(let y=Math.round(yB-h*.15);y>h*.3;y--){const r=runs(y);if(r.length<2){yc=y;break;}}
 /* short legs that touch low down (small children): going up from the feet, the first single run after the two legs were seen */
 if(yc>=yB-h*.16){let two=0;for(let y=yB-2;y>h*.3;y--){const n=runs(y).length;if(n>=2)two++;else if(two>=4){yc=y;break;}}}
 if(yc<0)return null;
 const lab=new Int32Array(w*h).fill(-1),comps=[];
 /* children (owner: the kid's legs stayed put, only the shoes moved): their short legs often cross at the shins, so "where the
    two legs join" is found too low. For a child the crotch is the top of the gap between the legs, and every pixel below it
    goes to the nearer of two lines, crotch -> back foot and crotch -> front foot. */
 let kidDone=false;
 if(opt.kid){let yT0=0;while(yT0<h&&!runs(yT0).length)yT0++;
  const gapAt=y=>{const r2=runs(y).filter(q=>q[1]-q[0]>=2);for(let i=0;i+1<r2.length;i++){const g2=(r2[i][1]+r2[i+1][0])/2;if(g2>w*.25&&g2<w*.75)return g2;}return -1;};   /* a gap between legs near the middle (a hanging hand at the side is not one) */
  let kc=-1,gx=0;for(let y=Math.round(yT0+.45*(yB-yT0));y<yB-h*.12;y++){const g2=gapAt(y);if(g2<0)continue;let ok=true;for(let d=1;d<=3;d++){const g3=gapAt(y+d);if(g3<0||Math.abs(g3-g2)>5){ok=false;break;}}if(ok){kc=y;gx=g2;break;}}
  const fy0=Math.round(yB-.07*h),fl=new Int32Array(w*h).fill(-1),fc=[];
  for(let y=fy0;y<=yB;y++)for(let x=0;x<w;x++){if(!op(x,y)||fl[y*w+x]>=0)continue;const id=fc.length,st2=[[x,y]],c={n:0,sx:0,sy:0};fl[y*w+x]=id;
   while(st2.length){const [px,py]=st2.pop();c.n++;c.sx+=px;c.sy+=py;for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=px+dx,ny=py+dy;if(nx<0||nx>=w||ny<fy0||ny>yB)continue;const k2=ny*w+nx;if(fl[k2]<0&&op(nx,ny)){fl[k2]=id;st2.push([nx,ny]);}}}fc.push(c);}
  let ft=fc.filter(c=>c.n>4).sort((a,b)=>b.n-a.n).slice(0,2).map(c=>({x:c.sx/c.n,y:c.sy/c.n})).sort((a,b)=>a.x-b.x);
  /* feet touching at the bottom: seed the two legs from the lowest row where they are apart instead */
  let seedRow=null;if(ft.length<2){for(let y=Math.round(yB-.04*h);y>yB-.25*h;y--){const r3=runs(y).filter(q=>q[1]-q[0]>=1);if(r3.length>=2){seedRow={y,a:r3[0],b:r3[r3.length-1]};ft=[{x:(r3[0][0]+r3[0][1])/2,y},{x:(r3[r3.length-1][0]+r3[r3.length-1][1])/2,y}];break;}}}
  if(ft.length===2){if(kc>0&&kc<yc-3)yc=kc;kidDone=true;   /* no gap found (a coat over the legs): grow from the feet up to the split */
   /* each leg grows up from its own foot through the leg's pixels (both at once, one step at a time): where the legs cross or
      touch, each pixel belongs to the foot it is closer to ALONG the leg, which follows bent knees far better than straight lines */
   comps.push({n:0,sx:0,maxY:0,feet:[]},{n:0,sx:0,maxY:0,feet:[]});
   const fid=fc.map((c,i)=>i).filter(i=>fc[i].n>4).sort((a,b)=>fc[b].n-fc[a].n).slice(0,2).sort((a,b)=>fc[a].sx/fc[a].n-fc[b].sx/fc[b].n);
   let q2=[];if(seedRow){for(const [id,rn] of [[0,seedRow.a],[1,seedRow.b]])for(let x=rn[0];x<=rn[1];x++){const k3=seedRow.y*w+x;lab[k3]=id;q2.push(k3);}}
   else for(let y=fy0;y<=yB;y++)for(let x=0;x<w;x++){const f2=fl[y*w+x];const id=f2===fid[0]?0:f2===fid[1]?1:-1;if(id>=0){lab[y*w+x]=id;q2.push(y*w+x);}}
   while(q2.length){const nq=[];for(const k2 of q2){const px=k2%w,py=(k2-px)/w,id=lab[k2];for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=px+dx,ny=py+dy;if(nx<0||nx>=w||ny<=yc||ny>yB)continue;const kk=ny*w+nx;if(lab[kk]<0&&op(nx,ny)){lab[kk]=id;nq.push(kk);}}}q2=nq;}
   for(let y=yc+1;y<=yB;y++)for(let x=0;x<w;x++){const id=lab[y*w+x];if(id<0)continue;const c=comps[id];c.n++;c.sx+=x;if(y>c.maxY)c.maxY=y;}}}
 /* components below the crotch */
 if(!kidDone)for(let y=yc+1;y<=yB;y++)for(let x=0;x<w;x++){
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
 const HANDS0=(()=>{try{const f0=findHands(cv,w,h,yT,yB);return f0?f0.hands.map(q=>{let c=[0,0,0],n=0;for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++){const xx=Math.round(q.x)+dx,yy=Math.round(q.y)+dy;if(xx<0||yy<0||xx>=w||yy>=h)continue;const k3=(yy*w+xx)*4;if(D[k3+3]<200)continue;c[0]+=D[k3];c[1]+=D[k3+1];c[2]+=D[k3+2];n++;}return {...q,c:n?c.map(v=>v/n):[200,150,120]};}):[];}catch(e){return [];}})();
 const dseg=(x,y,K)=>{const vx=K.x-pv.x,vy=K.y-pv.y,t=Math.max(0,Math.min(1,((x-pv.x)*vx+(y-pv.y)*vy)/(vx*vx+vy*vy)));return Math.hypot(x-pv.x-t*vx,y-pv.y-t*vy);};
 /* hem: going down from the hip, the first rows whose colour inside the thigh band matches the lower legs (trousers / skin)
    = where the legs come out from under a jacket, coat or skirt */
 const rowCol=y=>{let r=0,g2=0,b2=0,n=0;for(let x=0;x<w;x++){if(!op(x,y))continue;if(Math.min(dseg(x,y,KB),dseg(x,y,KF))>bw)continue;const k=(y*w+x)*4;r+=D[k];g2+=D[k+1];b2+=D[k+2];n++;}return n?[r/n,g2/n,b2/n]:null;};
 let low=[0,0,0],ln=0;for(let y=yc+4;y<Math.min(yB,yc+24);y++)for(let x=0;x<w;x++){const l=lab[y*w+x];if(l!==back.i&&l!==front.i)continue;const k=(y*w+x)*4;low[0]+=D[k];low[1]+=D[k+1];low[2]+=D[k+2];ln++;}
 low=low.map(v=>v/(ln||1));
 let hem=yc,run2=0;
 for(let y=Math.round(pv.y);y<yc;y++){const c=rowCol(y);if(c&&Math.hypot(c[0]-low[0],c[1]-low[1],c[2]-low[2])<50){if(++run2>=2){hem=y-1;break;}}else run2=0;}
 /* long coat or skirt (legs only show well below the hip): the legs swing from just under the hem, not from the hip far above,
    so their tops stay under the coat instead of sliding out sideways and leaving gaps */
 /* a coat the same colour as the trousers (navy coat, dark jeans): its bottom shows as the outline suddenly getting much narrower */
 {const skinP=(x,y)=>{const k=(y*w+x)*4,R0=D[k],G0=D[k+1],B0=D[k+2];return R0>95&&G0>45&&B0>25&&R0>G0+10&&R0>B0+25&&R0-B0<150;};
  const colOf=(y0,y1)=>{let c=[0,0,0],n=0;for(let y=Math.max(0,y0);y<y1;y++)for(let x=0;x<w;x++){if(!op(x,y)||skinP(x,y))continue;const k=(y*w+x)*4;c[0]+=D[k];c[1]+=D[k+1];c[2]+=D[k+2];n++;}return n?c.map(v=>v/n):null;};
  const torso=colOf(Math.round(pv.y-.25*h),Math.round(pv.y-.15*h)),same=(y0,y1,c)=>{const q=colOf(y0,y1);return !!(q&&c&&Math.hypot(q[0]-c[0],q[1]-c[1],q[2]-c[2])<40);};   /* only a coat: same fabric as the upper body */
  const wid=y=>{let l=-1,r=-1;for(let x=0;x<w;x++)if(op(x,y)&&!skinP(x,y)){if(l<0)l=x;r=x;}return l<0?0:r-l;};   /* hands (skin) left out: they end at the hip too */
  for(let y=Math.round(Math.max(hem,pv.y)+2);y<yc-6;y++){const a0=wid(y),a1=wid(y+4),a2=wid(y+8);if(a0>0&&a1<a0*.5&&a2<a0*.5){if(y+2>hem&&same(y-8,y,torso))hem=y+2;break;}}}
 if(kidDone){hem=Math.max(hem,yc);pv.y=Math.max(pv.y,hem-1);}   /* a child's legs are only what grew from the feet, and they swing from that split (nothing shifts at the seam) */
 const lowSkin=low[0]>95&&low[1]>45&&low[2]>25&&low[0]>low[1]+10&&low[0]>low[2]+25;   /* bare legs (shorts, skirts): the clothing above is not an open coat */
 const coat=!kidDone&&hem-pv.y>.12*h;if(coat){pv.y=pv.y+(hem-pv.y)*(window.COATPV120||.4);
  /* the coat's own lower edge often hangs a little below the split: coat-coloured pixels there stay on the body */
  let cc=[0,0,0],cn=0;for(let y=yc-6;y<yc-1;y++)for(let x=Math.round(pv.x-bw);x<pv.x+bw;x++){if(x<0||x>=w||!op(x,y))continue;const k=(y*w+x)*4;cc[0]+=D[k];cc[1]+=D[k+1];cc[2]+=D[k+2];cn++;}
  if(cn){cc=cc.map(v=>v/cn);if(Math.hypot(cc[0]-low[0],cc[1]-low[1],cc[2]-low[2])>60)for(let y=yc+1;y<Math.min(yB,yc+.07*h);y++)for(let x=0;x<w;x++){const k=y*w+x;if(lab[k]<0)continue;const q=k*4;
   if(Math.hypot(D[q]-cc[0],D[q+1]-cc[1],D[q+2]-cc[2])<Math.hypot(D[q]-low[0],D[q+1]-low[1],D[q+2]-low[2]))lab[k]=-2;}}}   /* -2 = coat, drawn with the body */
 /* soft edge pixels (alpha below the blob threshold) join the leg blob next to them, so nothing is left behind */
 for(let y=yc+1;y<=Math.min(h-1,yB+2);y++)for(let x=0;x<w;x++){const k=y*w+x;if(lab[k]!==-1||!D[k*4+3])continue;
  let best=-1;for(let r=1;r<=3&&best<0;r++)for(let dy=-r;dy<=r&&best<0;dy++)for(let dx=-r;dx<=r;dx++){const nx=x+dx,ny=y+dy;if(nx<0||nx>=w||ny<=yc||ny>=h)continue;const l=lab[ny*w+nx];if(l===back.i||l===front.i){best=l;break;}}
  if(best>=0)lab[k]=best;}
 /* which leg a pixel belongs to: lower legs by blob, thighs (hem..crotch) by the nearer hip-knee band */
 const legOf=(x,y,l)=>{if(y>yc)return l===back.i?1:l===front.i?2:0;
  if(coat&&y<hem){if(lowSkin||y<yT+.5*(yB-yT)||HANDS0.some(q=>Math.hypot(x-q.x,y-q.y)<.14*h))return 0;const k4=(y*w+x)*4;if(Math.hypot(D[k4]-low[0],D[k4+1]-low[1],D[k4+2]-low[2])>55)return 0;const db0=dseg(x,y,KB),df0=dseg(x,y,KF);if(Math.min(db0,df0)>bw*1.5)return 0;return db0<df0?1:2;}   /* open coat: the trousers showing inside it go with the legs, the coat stays */
  if(y<hem)return 0;const db=dseg(x,y,KB),df=dseg(x,y,KF),md=Math.min(db,df);if(md>bw*(kidDone||!coat?1:2))return 0;if(md>bw&&HANDS0.some(q=>Math.hypot(x-q.x,y-q.y)<.14*h&&(()=>{const k2=(y*w+x)*4,dc=Math.hypot(D[k2]-q.c[0],D[k2+1]-q.c[1],D[k2+2]-q.c[2]),dl=Math.hypot(D[k2]-low[0],D[k2+1]-low[1],D[k2+2]-low[2]);return dc<dl*1.5||(D[k2]>95&&D[k2+1]>45&&D[k2+2]>25&&D[k2]>D[k2+1]+10&&D[k2]>D[k2+2]+25);})()))return 0;return db<df?1:2;};   /* (only pixels that look like the hand, not the trousers round it) */   /* the hips (outside the thigh band) go with the nearer leg so no strips of them hang behind; not near a hand */
 const layer=pick=>{const o=document.createElement('canvas');o.width=w;o.height=h;const og=o.getContext('2d');const I=og.createImageData(w,h);
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const k=y*w+x;if(D[k*4+3]&&pick(legOf(x,y,lab[k]))){I.data[k*4]=D[k*4];I.data[k*4+1]=D[k*4+1];I.data[k*4+2]=D[k*4+2];I.data[k*4+3]=D[k*4+3];}}
  og.putImageData(I,0,0);return o;};
 const L={back:layer(v=>v===1),front:layer(v=>v===2),upper:layer(v=>v===0)};
 /* thin strands in a leg layer (the other leg's soft edge that the thigh split gave to this leg) swing out as dotted lines:
    pixels with only a few same-layer neighbours in a 5x5 box are dropped (soft-edge noise) */
 {const gB=L.back.getContext('2d'),gF=L.front.getContext('2d'),IB=gB.getImageData(0,0,w,h),IF=gF.getImageData(0,0,w,h);
  const thin=(A2,B2)=>{const a0=new Uint8ClampedArray(A2),b0=new Uint8ClampedArray(B2);for(let y=2;y<h-2;y++)for(let x=2;x<w-2;x++){const k=(y*w+x)*4;if(!a0[k+3])continue;let n=0,nb=0;for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++){const kk=k+(dy*w+dx)*4+3;if(a0[kk]>60)n++;if(b0[kk]>60)nb++;}
   if(n<10){if(nb>=10&&!B2[k+3]){for(let c=0;c<4;c++)B2[k+c]=a0[k+c];}A2[k+3]=0;}}};   /* a sparse pixel joins the other leg if it is solid there (interleaved thighs), else it is dropped (stray strand) */
  thin(IB.data,IF.data);thin(IF.data,IB.data);
  /* holes inside the body (solid all round in the picture) that no layer got, e.g. where the two legs meet: to the front leg */
  const UD=L.upper.getContext('2d').getImageData(0,0,w,h).data,sol=(x,y)=>D[(y*w+x)*4+3]>200;
  for(let y=Math.max(1,Math.round(hem));y<h-1;y++)for(let x=1;x<w-1;x++){const k=(y*w+x)*4;if(!sol(x,y)||IB.data[k+3]||IF.data[k+3]||UD[k+3])continue;
   if(sol(x-1,y)&&sol(x+1,y)&&sol(x,y-1)&&sol(x,y+1)){for(let c=0;c<4;c++)IF.data[k+c]=D[k+c];}}
  gB.putImageData(IB,0,0);gF.putImageData(IF,0,0);}
 {const gB=L.back.getContext('2d'),gF=L.front.getContext('2d'),IB=gB.getImageData(0,0,w,h),IF=gF.getImageData(0,0,w,h),b0=new Uint8ClampedArray(IB.data),f0=new Uint8ClampedArray(IF.data);
  const grow=(dst,own,oth)=>{for(let y=1;y<h-1;y++)for(let x=1;x<w-1;x++){const k=(y*w+x)*4;if(own[k+3]||!oth[k+3])continue;if(own[k+7]||own[k-1]||own[k+w*4+3]||own[k-w*4+3]){for(let c=0;c<4;c++)dst[k+c]=oth[k+c];}}};
  grow(IB.data,b0,f0);grow(IF.data,f0,b0);gB.putImageData(IB,0,0);gF.putImageData(IF,0,0);}
 /* fingertips that hang below the hem went to a thigh layer: give the pixels around each hand that are not leg-coloured back to the upper body */
 {const fh0=findHands(cv,w,h,(()=>{let y=0;while(y<h&&!runs(y).length)y++;return y;})(),yB);if(fh0){const rr=.11*h,gu=L.upper.getContext('2d'),U=gu.getImageData(0,0,w,h);
  for(const lc of [L.back,L.front]){const gl=lc.getContext('2d'),G=gl.getImageData(0,0,w,h);let ch=false;
   for(const q of fh0.hands)for(let y=Math.max(0,Math.floor(q.y-rr));y<Math.min(h,q.y+rr);y++)for(let x=Math.max(0,Math.floor(q.x-rr));x<Math.min(w,q.x+rr);x++){const k=(y*w+x)*4;if(!G.data[k+3])continue;
    const R0=G.data[k],G0=G.data[k+1],B0=G.data[k+2];{const dl=Math.hypot(R0-low[0],G0-low[1],B0-low[2]),hc=(HANDS0.find(h2=>Math.hypot(h2.x-q.x,h2.y-q.y)<6)||{}).c,dc=hc?Math.hypot(R0-hc[0],G0-hc[1],B0-hc[2]):1e9;if(dl<70&&!(dc<dl))continue;}   /* (skin close to the trouser colour: compared with the hand's own colour) */   /* not trouser/leg coloured = part of the hand (skin, shading, soft edge) */
    for(let c=0;c<4;c++){U.data[k+c]=G.data[k+c];G.data[k+c]=0;}ch=true;}
   if(ch)gl.putImageData(G,0,0);}
  gu.putImageData(U,0,0);}}
 /* foot = the lowest 6% of each leg blob, mean x */
 const footX=c=>{let sx=0,n=0;for(let y=Math.round(c.maxY-h*.06);y<=c.maxY;y++)for(let x=0;x<w;x++)if(lab[y*w+x]===c.i){sx+=x;n++;}return n?sx/n:c.cx;};
 const leg=(c)=>{const fx=footX(c),fy=c.maxY,dx=fx-pv.x,dy=fy-pv.y;return {L:Math.hypot(dx,dy),a:Math.atan2(dx,dy),fy};};
 const B=leg(back),F=leg(front);
 const sF=Math.sin(F.a),sB=Math.sin(B.a);
 const arms=(opt.noArms||window.ARMS120===false)?null:armRig(L.upper,w,h,yT,yB,hem,opt.armSide,coat),   /* arm swing: smooth field warp (V17.120b); window.ARMS120=false turns it off */
 fh=findHands(L.upper,w,h,yT,yB);
 const pt=fh?pointRig(L.upper,w,h,fh,yB-yT):null;
 /* waist filler source: the upper body's last rows above the hem without the hands (they swing; a copy left here showed as bars) */
 const wf=document.createElement('canvas');wf.width=w;wf.height=h;{const wg=wf.getContext('2d');wg.drawImage(L.upper,0,0);if(fh){wg.globalCompositeOperation='destination-out';for(const q of fh.hands){const r0=.06*(yB-yT);wg.fillRect(q.x-r0,0,2*r0,h);}   /* the whole arm column (cuff and hand) */}
  /* only over the thighs: outside them nothing is hidden under the legs, and a copy there would show */
  wg.globalCompositeOperation='destination-out';const xL=Math.min(KB.x,KF.x)-bw,xR=Math.max(KB.x,KF.x)+bw;wg.fillRect(0,0,Math.max(0,xL),h);wg.fillRect(xR,0,w,h);}
 /* behind each hand that hangs over the thighs nothing was drawn (the hand covered it): fill that spot in the leg layers from
    the nearest trouser pixels in the row, so when the hand swings away there are trousers, not a hole */
 {const U2=L.upper.getContext('2d').getImageData(0,0,w,h).data,gB2=L.back.getContext('2d'),gF2=L.front.getContext('2d'),IB2=gB2.getImageData(0,0,w,h),IF2=gF2.getImageData(0,0,w,h);let ch2=false;
  for(const q of HANDS0){const rr2=.12*h;for(let y=Math.max(Math.round(hem)-1,Math.floor(q.y-rr2));y<Math.min(h,q.y+rr2);y++)for(let x=Math.max(0,Math.floor(q.x-rr2));x<Math.min(w,q.x+rr2);x++){const k=(y*w+x)*4;
   if(U2[k+3]<150||IB2.data[k+3]||IF2.data[k+3])continue;let src=null,dst=null;
   for(let dd=1;dd<=14&&!src;dd++)for(const xx of [x+dd,x-dd]){if(xx<0||xx>=w)continue;const kk=(y*w+xx)*4;if(IF2.data[kk+3]>200){src=IF2.data;dst=IF2.data;break;}if(IB2.data[kk+3]>200){src=IB2.data;dst=IB2.data;break;}}
   if(src){let kk=-1;for(let dd=1;dd<=14&&kk<0;dd++)for(const xx of [x+dd,x-dd]){if(xx<0||xx>=w)continue;const k2=(y*w+xx)*4;if(src[k2+3]>200){kk=k2;break;}}if(kk>=0){for(let c=0;c<4;c++)dst[k+c]=src[kk+c];dst[k+3]=255;ch2=true;}}}}
  if(ch2){gB2.putImageData(IB2,0,0);gF2.putImageData(IF2,0,0);}}
 /* open coat: a still copy of the trousers inside the opening, drawn behind the legs (the opening never shows the background) */
 let coatBack=null;if(coat&&!lowSkin){coatBack=document.createElement('canvas');coatBack.width=w;coatBack.height=h;const cg=coatBack.getContext('2d'),yh=Math.round(hem);for(const lc of [L.back,L.front])cg.drawImage(lc,0,0,w,yh,0,0,w,yh);}
 let legTop=h;{const dB=L.back.getContext('2d').getImageData(0,0,w,h).data,dF2=L.front.getContext('2d').getImageData(0,0,w,h).data;for(let y=0;y<h&&legTop===h;y++)for(let x=0;x<w;x++){const k5=(y*w+x)*4+3;if(dB[k5]>110||dF2[k5]>110){legTop=y;break;}}}
 return {w,h,pv,yc,hem,coat,kid:kidDone,low,legTop,coatBack,L,B,F,arms,fh,pt,wf,A:(sF-sB)/2*(coat?.7:1),C:(sF+sB)/2,Lm:(B.L+F.L)/2,ground:Math.max(B.fy,F.fy)};
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
function armRig(up,w,h,yT,yB,hem,armSide,coatArm){
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
  const o=document.createElement('canvas');o.width=w;o.height=h;const og=o.getContext('2d'),O=og.createImageData(w,h),T0=O.data,OB=og.createImageData(w,h),TB=OB.data;let T=T0;
  const bi=arms.findIndex(a=>a.dir<0),fi=arms.findIndex(a=>a.dir>0);
  const dAt=(xs,y)=>{const xi=Math.max(0,Math.min(w-1,Math.round(xs)));let d=0;for(let i=0;i<arms.length;i++){const ww=W[i][y*w+xi];if(ww)d+=arms[i].dir*A*q*ww*(arms[i].dir<0?0:(coatArm?.45:1));}return d;};   /* long coats: the hands pull the coat fabric, so they swing less */   /* the far hand swings only a little (it would have to pass behind the body) */
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){let dx=0,dy=0;
   /* the picture pixel s that the field carries onto x (x = s + d(s)), by fixed-point steps: the hand keeps its shape as it moves */
   {const sol=s0=>{let s2=s0;for(let it=0;it<8;it++)s2=x-dAt(s2,y);return Math.abs(s2+dAt(s2,y)-x)<.6?s2:null;};
    const full=arms.length?Math.max(...arms.map(a=>Math.abs(A*q))):0,cands=[sol(x)];for(const a of arms)cands.push(sol(x-a.dir*A*q));
    let best=null;for(const c of cands){if(c===null)continue;const xi=Math.max(0,Math.min(w-1,Math.round(c)));const op2=S[(y*w+xi)*4+3]>40,wg=Math.abs(dAt(c,y));
     if(!best||(op2&&!best.op)||(op2===best.op&&wg>best.wg))best={c,op:op2,wg};}
    dx=best?x-best.c:0;}
   const k=(y*w+x)*4;T=T0;if(!dx&&!dy){T[k]=S[k];T[k+1]=S[k+1];T[k+2]=S[k+2];T[k+3]=S[k+3];continue;}
   /* the far (back) arm, once it swings in towards the body, is drawn on its own layer UNDER the legs and body */
   if(false&&bi>=0&&Math.abs(q)>.15&&hem&&y>=hem-1){const sx2=Math.max(0,Math.min(w-1,Math.round(x-dx)));if(W[bi][y*w+sx2]>.5){T=TB;const o0=S[(y*w+x)*4+3];if(o0>40&&W[bi][y*w+x]<.25){T0[k]=S[k];T0[k+1]=S[k+1];T0[k+2]=S[k+2];T0[k+3]=o0;}}}
   const fx=x-dx,fy=y-dy,x0=Math.floor(fx),y0=Math.floor(fy),ax=fx-x0,ay=fy-y0;if(x0<0||y0<0||x0>=w-1||y0>=h-1)continue;
   /* premultiplied bilinear sample, so the soft edges do not darken */
   let a4=0,c0=0,c1=0,c2=0;for(const [xx,yy,f] of [[x0,y0,(1-ax)*(1-ay)],[x0+1,y0,ax*(1-ay)],[x0,y0+1,(1-ax)*ay],[x0+1,y0+1,ax*ay]]){const kk=(yy*w+xx)*4,al=S[kk+3]*f;a4+=al;c0+=S[kk]*al;c1+=S[kk+1]*al;c2+=S[kk+2]*al;}
   if(a4>0){T[k]=c0/a4;T[k+1]=c1/a4;T[k+2]=c2/a4;T[k+3]=a4;}}
  /* where a hand swung away from the body there is nothing drawn behind it (the hand covered the hip in the picture): fill
     such holes from the nearest body pixel in the row that the arms do not move */
  if(q){for(let y=0;y<h;y++)for(let x=0;x<w;x++){const k=(y*w+x)*4;if(S[k+3]<200||T0[k+3]>=150)continue;let best=-1;
   for(let dd=1;dd<=10&&best<0;dd++)for(const xx of [x-dd,x+dd]){if(xx<0||xx>=w)continue;const kk=(y*w+xx)*4;let wa=0;for(let i=0;i<arms.length;i++)wa=Math.max(wa,W[i][y*w+xx]);if(T0[kk+3]>200&&S[kk+3]>200&&wa<.3){best=kk;break;}}
   if(best>=0){T0[k]=T0[best];T0[k+1]=T0[best+1];T0[k+2]=T0[best+2];T0[k+3]=255;}}}
  og.putImageData(O,0,0);const ob=document.createElement('canvas');ob.width=w;ob.height=h;ob.getContext('2d').putImageData(OB,0,0);o.back=ob;return o;};
 /* q from 0 (as drawn) to -1 (hands in along the body) and back each cycle: the hands swing in towards the body between the drawn steps */
 const walk=[];for(let n=0;n<16;n++)walk.push(frame(-(.35+.65*(1-Math.cos(2*Math.PI*n/16))/2)));   /* hands always somewhat in towards the body (drawn arms are held out), swinging further in each step */
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
 /* bits of the parent (a shoe tip, a coat edge) that reach past the cut belong to the parent: in the child's strip, small
    blobs not joined to the child go back to the parent, whose strip is widened to hold them */
 let ext=best;{const lab=new Int32Array(w*h).fill(-1),comps=[];
  for(let y=0;y<h;y++)for(let x=best;x<w;x++){const k=y*w+x;if(lab[k]>=0||D[k*4+3]<=60)continue;const id=comps.length,st=[k],c={n:0,minx:x,maxx:x,px:[]};lab[k]=id;
   while(st.length){const q=st.pop(),qx=q%w,qy=(q-qx)/w;c.n++;c.px.push(q);if(qx<c.minx)c.minx=qx;if(qx>c.maxx)c.maxx=qx;for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=qx+dx,ny=qy+dy;if(nx<best||nx>=w||ny<0||ny>=h)continue;const kk=ny*w+nx;if(lab[kk]<0&&D[kk*4+3]>60){lab[kk]=id;st.push(kk);}}}
   comps.push(c);}
  const big=Math.max(0,...comps.map(c=>c.n)),moved=comps.filter(c=>c.n<big*.04&&c.minx<=best+2&&c.px.some(q=>{const qx=q%w;return qx<=best+1&&D[(q-(qx-best+1))*4+3]>60;}));   /* only if it touches the parent's pixels left of the cut (a child's heel stays with the child) */
  if(moved.length){const Dm=g.getImageData(0,0,w,h);for(const c of moved){ext=Math.max(ext,c.maxx+1);}
   const keep=new Uint8Array(w*h);for(const c of moved)for(const q of c.px)keep[q]=1;
   /* clear them from the image used for the child, keep them for the parent */
   const childD=g.getImageData(0,0,w,h);for(const c of moved)for(const q of c.px){childD.data[q*4+3]=0;}
   const cvC=document.createElement('canvas');cvC.width=w;cvC.height=h;cvC.getContext('2d').putImageData(childD,0,0);
   const cvP=document.createElement('canvas');cvP.width=w;cvP.height=h;const pd=g.getImageData(0,0,w,h);for(let y=0;y<h;y++)for(let x=best;x<w;x++){const q=y*w+x;if(!keep[q])pd.data[q*4+3]=0;}cvP.getContext('2d').putImageData(pd,0,0);
   g.clearRect(0,0,w,h);g.drawImage(cvP,0,0);   /* cv now = parent side incl. its stray bits; the child is cut from cvC */
   var childSrc=cvC;}}
 /* and the other way round: the child's back foot often reaches past the cut onto the parent's side (low down, by the feet);
    small blobs there that touch the child at the cut go to the child, whose strip then starts further left */
 let cStart=best;{const pd=g.getImageData(0,0,w,h),P2=pd.data,y0=Math.round(h*.65),lab=new Int32Array(w*h).fill(-1),comps=[];
  for(let y=y0;y<h;y++)for(let x=0;x<best;x++){const k=y*w+x;if(lab[k]>=0||P2[k*4+3]<=60)continue;const id=comps.length,st=[k],c={n:0,minx:x,maxx:x,px:[]};lab[k]=id;
   while(st.length){const q=st.pop(),qx=q%w,qy=(q-qx)/w;c.n++;c.px.push(q);if(qx<c.minx)c.minx=qx;if(qx>c.maxx)c.maxx=qx;for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=qx+dx,ny=qy+dy;if(nx<0||nx>=best||ny<y0||ny>=h)continue;const kk=ny*w+nx;if(lab[kk]<0&&P2[kk*4+3]>60){lab[kk]=id;st.push(kk);}}}
   comps.push(c);}
  const big=Math.max(0,...comps.map(c=>c.n)),toKid=comps.filter(c=>c.n<big*.06&&c.maxx>=best-2&&c.px.some(q=>{const qx=q%w;return qx>=best-2&&D[(q+(best-qx))*4+3]>60;}));
  if(toKid.length){const src=typeof childSrc!=='undefined'?childSrc:(()=>{const c0=document.createElement('canvas');c0.width=w;c0.height=h;c0.getContext('2d').putImageData(new ImageData(new Uint8ClampedArray(D),w,h),0,0);return c0;})();
   const sg=src.getContext('2d'),SD=sg.getImageData(0,0,w,h);for(const c of toKid){cStart=Math.min(cStart,c.minx);for(const q of c.px){for(let ch=0;ch<4;ch++)SD.data[q*4+ch]=P2[q*4+ch];P2[q*4+3]=0;}}
   /* the child's strip starts at cStart: clear everything left of the cut in it except the moved bits */
   const keepK=new Uint8Array(w*h);for(const c of toKid)for(const q of c.px)keepK[q]=1;for(let y=0;y<h;y++)for(let x=cStart;x<best;x++){const q=y*w+x;if(!keepK[q])SD.data[q*4+3]=0;}
   sg.putImageData(SD,0,0);var childSrc=src;g.putImageData(pd,0,0);}}
 const partFrom=(src,x0,x1,crop)=>{const old=cv;return (function(){const c=document.createElement('canvas');let y0=0;if(crop){const d2=src.getContext('2d').getImageData(0,0,w,h).data;y0=h;for(let y=0;y<h&&y0===h;y++)for(let x=x0;x<x1;x++)if(d2[(y*w+x)*4+3]>110){y0=Math.max(0,y-2);break;}}
   c.width=x1-x0;c.height=h-y0;c.getContext('2d').drawImage(src,x0,y0,x1-x0,h-y0,0,0,x1-x0,h-y0);return c;})();};
 const ca=partFrom(cv,0,ext),cb=partFrom(typeof childSrc!=='undefined'?childSrc:cv,cStart,w,true);
 /* the 1-2 px strip along the cut (soft edge of the joined hands / the other figure) swung with a leg as a thin dotted line: legs only */
 const trim=(R)=>R;   /* (the cut strip used to be cleared from the legs here; it tore the parent's thigh edge - the thin-strand filter covers it now) */   /* the feet keep their pixels (shoe tips past the cut) */
 const A=trim(rigSpriteV120(ca,{armSide:'back'}),best-2,ext)||still(ca),B=trim(rigSpriteV120(cb,{armSide:'front',kid:true}),best-cStart,best-cStart+2)||still(cb);   /* only the free hands swing; the joined hands stay together */
 if(A.still&&B.still)return null;
 return {pair:true,w,h,cut:best,parts:[{R:A,ox:0},{R:B,ox:cStart}]};
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
 let ang=0;if(R.arms){const n=Math.round((((phase%1)+1)%1)*16)%16,q=m*-(.35+.65*(1-Math.cos(2*Math.PI*n/16))/2)+(1-m)*-.6,a=R.arms.arms.find(x=>x.hd.x===hd.x&&x.hd.y===hd.y);if(a)return {x:hd.x+a.dir*R.arms.A*q*(a.dir<0?0:(R.coat?.45:1)),y:hd.y};}
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
 if(window.LEGSHEAR120!==false){
  /* bending legs (owner: the waist and trousers distorted, "way too robotic"): each leg picture is drawn in thin rows, every
     row shifted sideways by how far down the leg it is, so the top of the leg (the waist) never moves and the foot goes
     where the step puts it; the swinging leg also bends: the knee leads forward and the foot lifts. The upper body only
     bobs (two small bobs per cycle), so the waist edge always lines up with the trousers. */
  const bob=m*.007*R.h*Math.cos(4*Math.PI*phase);
  let liftR=0;if(!R.coat&&!R.kid&&window.LEGROT120!==false){const tF2=Math.asin(Math.max(-.99,Math.min(.99,F.s))),tB2=Math.asin(Math.max(-.99,Math.min(.99,B.s))),st2=F.sw<=B.sw?{t:tF2,L:R.F.L}:{t:tB2,L:R.B.L};liftR=-(st2.L*Math.cos(st2.t)-(R.ground-R.pv.y));}   /* the body rides on the standing leg, so the turned leg reaches the floor */
  ctx.save();ctx.scale(k,k);ctx.translate(-R.w/2,-R.ground+(liftR||-Math.abs(bob)));
  /* the shoe rolls through the step (owner: "they walk on their heels or on their toes"): heel strike with the toe up, flat
     while standing on it, heel lifting onto the toes to push off, toe hanging a little in the air. The shoe (below the ankle)
     is turned about the point that touches the floor - the heel, or the toe - which stays on the floor line. */
  const soleAt=q=>{q=((q%1)+1)%1;const sm=(a,b,t)=>a+(b-a)*(t*t*(3-2*t));
   return q<.06?sm(-.25,0,q/.06):q<.36?0:q<.5?sm(0,.5,(q-.36)/.14):q<.75?sm(.5,.2,(q-.5)/.25):sm(.2,-.25,(q-.75)/.25);};
  const footOf=(cv,fy)=>{const key=cv===R.L.back?'_fb':'_ff';if(R[key])return R[key];
   const d=cv.getContext('2d').getImageData(0,0,R.w,R.h).data;let x0=R.w,x1=-1;
   /* the ankle = the narrowest row of this leg between 3% and 15% of the height above the sole: everything below it is the shoe */
   const wAt=y=>{let l=-1,r=-1;for(let x=0;x<R.w;x++)if(d[(y*R.w+x)*4+3]>110){if(l<0)l=x;r=x;}return l<0?1e9:r-l;};
   let top=Math.round(fy-.06*R.h),bw2=1e9;for(let y=Math.round(fy-.03*R.h);y>fy-.09*R.h;y--){const ww=wAt(y);if(ww<bw2-.5){bw2=ww;top=y;}}   /* only just above the sole: higher up a skirt or coat edge can be narrower */
   /* a shoe drawn steeply (on its toes) is taller than that: go up while the row is still mostly shoe (not trouser/leg colour), so the cut never goes through the shoe */
   if(R.low){let ys=Math.round(fy-.02*R.h);for(let y=ys;y>fy-.17*R.h;y--){let n=0,sh=0;for(let x=0;x<R.w;x++){const k=(y*R.w+x)*4;if(d[k+3]<=110)continue;n++;if(Math.hypot(d[k]-R.low[0],d[k+1]-R.low[1],d[k+2]-R.low[2])>60)sh++;}if(!n||sh<n*.3)break;ys=y;}top=Math.min(top,ys-1);}
   for(let y=top;y<R.h;y++)for(let x=0;x<R.w;x++)if(d[(y*R.w+x)*4+3]>110){if(x<x0)x0=x;if(x>x1)x1=x;}
   if(x1<0)return R[key]={none:true};
   const low=(xa,xb)=>{let by=-1,bx=xa;for(let x=xa;x<=xb;x++)for(let y=R.h-1;y>=top;y--)if(d[(y*R.w+x)*4+3]>110){if(y>by){by=y;bx=x;}break;}return {x:bx,y:by};};
   const fw=x1-x0,heel=low(x0,x0+Math.max(1,Math.round(fw*.3))),toe=low(x1-Math.max(1,Math.round(fw*.3)),x1);
   const ov=Math.max(0,top-3),fc=document.createElement('canvas');fc.width=R.w;fc.height=R.h;fc.getContext('2d').drawImage(cv,0,ov,R.w,R.h-ov,0,ov,R.w,R.h-ov);   /* starts 3 rows up the leg: no wedge opens at the ankle when the shoe turns */
   return R[key]={top,heel,toe,a0:Math.atan2(toe.y-heel.y,toe.x-heel.x),cv:fc};};
  const y0=Math.floor(R.coat&&R.coatBack?Math.min(R.legTop,R.hem-1):Math.max(R.pv.y,R.hem-1)),legRows=(cv,base,sv,sw,L,fy,q)=>{   /* the legs bend from where they come out of the clothing: nothing shifts at that edge */
   const dF=(sv-Math.sin(base))*L*(R.kid?.8:R.coat?.6:1),y1=R.kid?y0+Math.max(3,(fy-y0)*.3):Math.max(y0+4,fy-.075*R.h),span=y1-y0,   /* y1 = the ankle: the shoe below it moves as one piece; children: short legs bend near the top, the boot moves whole */lift=sw*(R.kid?.03:.04)*R.h,knee=sw*(R.kid?0:.015)*R.h;   /* a walk, not a march: small knee lead, the foot only just clears the floor */
   /* rows are shifted at the picture's own size (1 px rows, whole-pixel lift) on a scratch canvas, then drawn once: no
      stripes or stair steps from scaling thin strips */
   if(R.kid){   /* children: the whole short leg swings from the hip like a pendulum (bending it looked like shuffling); the swinging leg shortens a little to clear the floor */
    const hx=R.pv.x,hy=y0,len=Math.max(4,fy-hy),ang=Math.atan2(dF,len);
    const yh=Math.round(hy);ctx.drawImage(cv,0,yh,R.w,4,0,yh-2,R.w,6);   /* the top of the leg, still, under the turning leg: no seam at the waist */
    ctx.save();ctx.translate(hx,hy);ctx.rotate(-ang);ctx.scale(1,1-.07*sw);ctx.translate(-hx,-hy);ctx.drawImage(cv,0,0);ctx.restore();return;}
   if(!R.coat&&window.LEGROT120!==false){
    /* adults: the whole leg turns about the hip joint (owner: the back leg swung forward stayed attached at the back of the
       hip - the drawn back thigh must come round to the front), with a small knee lead while it swings; the shoe below the
       ankle is placed where the turned ankle is and rolls through the step as before */
    const hx=R.pv.x,hy=R.pv.y,ang=(Math.asin(Math.max(-.99,Math.min(.99,sv)))-base)*(1),c0=Math.cos(-ang),s0=Math.sin(-ang),sc=1-.05*sw;
    const ft=footOf(cv,fy),yCut=ft.none?R.h:Math.max(0,ft.top+2);
    const tc=R._legTmp||(R._legTmp=document.createElement('canvas'));if(tc.width!==R.w||tc.height!==R.h){tc.width=R.w;tc.height=R.h;}
    const tg=tc.getContext('2d');tg.clearRect(0,0,R.w,R.h);
    tg.save();tg.translate(hx,hy);tg.rotate(-ang);tg.scale(1,sc);tg.translate(-hx,-hy);tg.drawImage(cv,0,0,R.w,yCut,0,0,R.w,yCut);tg.restore();
    /* near the hip the leg only slides sideways (no up/down at the thigh's edges, which made steps against the still hip),
       blending into the turned leg lower down */
    {const F=Math.round(.12*R.h),y0b=Math.round(hy);tg.clearRect(0,y0b,R.w,F+1);for(let y=y0b;y<=y0b+F;y++){const t=Math.max(0,(y-hy))/F,dx=(y-hy)*Math.sin(ang)*(t<1?1:1);tg.drawImage(cv,0,y,R.w,1,dx,y,R.w,1);}}
    /* knee lead: rows between hip and ankle pushed forward a little in the middle (swing leg only) */
    const kn=knee;let src2=tc;if(kn>.2){const t2=R._legTmp2||(R._legTmp2=document.createElement('canvas'));if(t2.width!==R.w||t2.height!==R.h){t2.width=R.w;t2.height=R.h;}
     const g2=t2.getContext('2d');g2.clearRect(0,0,R.w,R.h);const span2=Math.max(4,fy-hy);for(let y=0;y<R.h;y++){const t=Math.max(0,Math.min(1,(y-hy)/span2));g2.drawImage(tc,0,y,R.w,1,kn*Math.sin(Math.PI*t),y,R.w,1);}src2=t2;}
    ctx.drawImage(src2,0,0);
    if(!ft.none){const P={x:(ft.heel.x*.6+ft.toe.x*.4),y:ft.top+1},rx=P.x-hx,ry0=(P.y-hy)*sc,Px=hx+rx*c0-ry0*s0,Py=hy+rx*s0+ry0*c0;
     const th=m*soleAt(q),rot=Math.max(-.5,Math.min(.5,th-ft.a0));
     const ry=pt2=>Py+(pt2.x-P.x)*Math.sin(rot)+(pt2.y-P.y)*Math.cos(rot),lowY=Math.max(ry(ft.heel),ry(ft.toe)),up=sw<.05?R.ground-lowY:Math.min(0,R.ground-lowY);
     ctx.save();ctx.translate(Px,Py+up);ctx.rotate(rot);ctx.translate(-P.x,-P.y);ctx.drawImage(ft.cv,0,0);ctx.restore();}
    return;}
   const tc=R._legTmp||(R._legTmp=document.createElement('canvas'));if(tc.width!==R.w||tc.height!==R.h){tc.width=R.w;tc.height=R.h;}
   const tg=tc.getContext('2d');tg.clearRect(0,0,R.w,R.h);tg.drawImage(cv,0,0,R.w,y0,0,0,R.w,y0);   /* above the hip: as drawn */
   {const yx=Math.max(y0,Math.round(R.hem));for(const u of [1,2,3])tg.drawImage(cv,0,yx,R.w,1,0,yx-u,R.w,1);}   /* the leg's top row reaches up under the body: no light seam at the waist */
   const kn=R.coat?0:knee,off=y=>{const t=Math.min(1,Math.max(0,(y-y0)/span)),tt=t*t*(3-2*t);return [R.coat?dF*t:dF*(.35*t+.65*tt)+kn*Math.sin(Math.PI*Math.min(1,t*1.15)),Math.round(-lift*t*t)];};   /* under a long coat/skirt the short visible leg stays straight */
   const ft=R.kid?{none:true}:footOf(cv,fy),yEnd=ft.none?R.h:ft.top;   /* children: the short leg and boot move as one piece */
   for(let y=y0;y<yEnd;y++){const [dx,dy]=off(y);tg.drawImage(cv,0,y,R.w,1,dx,y+dy,R.w,1);if(dy<0)tg.drawImage(cv,0,y,R.w,1,dx,y+dy+1,R.w,1);}
   if(!ft.none){const [dx,dy]=off(ft.top),th=m*soleAt(q)+(1-m)*0,rot=Math.max(-.5,Math.min(.5,th-ft.a0)),
     P={x:(ft.heel.x*.6+ft.toe.x*.4),y:ft.top+1};   /* the ankle: the shoe stays on the leg */
    /* never below the floor: after turning, the lowest of heel and toe is lifted back to the floor line if needed */
    const ry=pt2=>P.y+(pt2.x-P.x)*Math.sin(rot)+(pt2.y-P.y)*Math.cos(rot),lowY=Math.max(ry(ft.heel),ry(ft.toe))+dy,up=Math.min(0,R.ground-lowY);
    tg.save();tg.translate(P.x+dx,P.y+dy+up);tg.rotate(rot);tg.translate(-P.x,-P.y);tg.drawImage(ft.cv,0,0);tg.restore();}
   ctx.drawImage(tc,0,0);};
  if(R.arms&&!(pt>0&&R.pt)&&m>0){const n=Math.round((((phase%1)+1)%1)*16)%16,bk=R.arms.walk[n].back;if(bk){ctx.globalAlpha=m;ctx.drawImage(bk,0,0);ctx.globalAlpha=1;}}   /* far arm behind the legs */
  if(R.coatBack)ctx.drawImage(R.coatBack,0,0);
  const backCopy=!R.coat&&!R.kid&&window.LEGROT120!==false&&window.BACKCOPY120!==false;   /* the drawn back leg is half hidden (too thin when it swings forward): adults use the front leg's picture for it, a little darker */
  if(backCopy){const yb=Math.round(R.hem)-1,hb=Math.round(.14*R.h);ctx.drawImage(R.L.back,0,yb,R.w,hb,0,yb,R.w,hb);   /* the real back thigh's top stays behind as a backing (its spot at the back of the hip is never empty) */
   ctx.save();ctx.filter='brightness(0.8)';legRows(R.L.front,R.F.a,B.s,B.sw,R.F.L,R.F.fy,phase+.5);ctx.restore();}
  else legRows(R.L.back,R.B.a,B.s,B.sw,R.B.L,R.B.fy,phase+.5);
  legRows(R.L.front,R.F.a,F.s,F.sw,R.F.L,R.F.fy,phase);
 }else{
 const stance=F.sw<=B.sw?{t:tF,L:R.F.L}:{t:tB,L:R.B.L};
 const hip0=R.ground-R.pv.y,lift=-(stance.L*Math.cos(stance.t)-hip0);
 ctx.save();ctx.scale(k,k);ctx.translate(-R.w/2,-R.ground+lift);
 const drawLeg=(cv,base,t,sw)=>{ctx.save();ctx.translate(R.pv.x,R.pv.y);ctx.rotate(-(t-base));ctx.scale(1,1-.07*sw);ctx.translate(-R.pv.x,-R.pv.y);ctx.drawImage(cv,0,0);ctx.restore();};
 if(R.wf&&!R.coat){const y0=Math.round(R.hem)-3;for(const d of [2,4,6])ctx.drawImage(R.wf,0,y0,R.w,3,0,y0+d,R.w,3);}
 drawLeg(R.L.back,R.B.a,tB,B.sw);
 drawLeg(R.L.front,R.F.a,tF,F.sw);
 {const a=m*(.035+.012*Math.sin(4*Math.PI*phase));ctx.translate(R.pv.x,R.pv.y);ctx.rotate(a);ctx.translate(-R.pv.x,-R.pv.y);}
 }
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
function cycleLenV120(R){return 4*R.A*R.Lm*(R.kid?.8:R.coat?.6:1);}   /* same factor as the step (dF), so the foot on the floor stays put (no skating) */
window.rigSpriteV120=rigSpriteV120;window.rigPairV120=rigPairV120;window.drawWalkV120=drawWalkV120;window.cycleLenV120=cycleLenV120;
})();
