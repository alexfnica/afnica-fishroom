/* ================= V17.108 BRISTLENOSE SPAWNING IN THE CAVE (spec docs/ANCISTRUS_SPAWNING_SPEC.md, choreography B) =================
   Owner (2026-10-23): the male waits in his cave head out (inviting) -> the female comes, he walks out and steps aside ->
   she slides in HEAD FIRST, slowly, to the back -> he follows head first and lies over her, tail out of the mouth, fanning
   (V17.106 bouts + soft tail wave) -> she backs out slowly under him and swims off -> he is already head in / tail out,
   which is the egg guard pose (V17.89 cave cycle 'fan').
   Owns the pair in the breeder while st.ancClutch.stage==='spawning' (wraps ancBreedingMotion40, V17.40 + V17.89 wraps
   are skipped for the pair). Same phases, same save fields and the same eggs code as V17.40; positions live in a runtime
   map (no new st fields). Drawing: V17.89 helpers (place + tube clip, fin data), the V17.90 draw chain (turns), the V17.106
   fanning tail (data-sp108='fan'). V17.89 post skips its own spawning branches while data-sp108 is set; the V17.90 facing
   follow ignores a fish that backs out (data-back108). Switch: window.ANC108=false (back to V17.40/V17.89).
   Test only: window.__T108={inv:s} = invite length (never set by the game); ancSpawnDebugV17108() = runtime map. */
(function(){
 const clamp=(v,a,b)=>v<a?a:v>b?b:v,rand=(a,b)=>a+Math.random()*(b-a),sm=q=>{q=clamp(q,0,1);return q*q*(3-2*q);};
 const R=new Map(),ERR=new Set();   /* ERR: clutch ids handed back to V17.40 after an error */                                      /* clutch id -> {m:actor, f:actor, inv} */
 const SPD={walk:28,aside:30,slide:13,back:18,away:30,inner:16};   /* px/s at scale 1 (body 112 px): slide 0.12 BL/s, walk 0.25 */
 /* smooth 1-D move: eases in and out (accel <= 30 px/s2), no snap; true on arrival */
 function mv(a,to,spd,dt){const d=to-a.x;if(Math.abs(d)<.4&&Math.abs(a.v)<3){a.x=to;a.v=0;return true;}
  const want=Math.sign(d)*Math.min(spd,Math.sqrt(2*30*Math.abs(d)));a.v+=(want-a.v)*Math.min(1,dt*3);
  const step=a.v*dt;a.x+=Math.abs(step)>Math.abs(d)?d:step;return false;}
 function to(a,st){a.st=st;a.t=0;}
 function art108(el,fish){   /* = the V17.89 breeder wrap (box + articulated side art), which the pair skips now */
  for(const[k,v]of [['position','absolute'],['width','120px'],['height','70px'],['right','auto'],['bottom','auto'],['transform-origin','center']])el.style.setProperty(k,v,'important');
  const side=el.querySelector('.ancSide');
  if(side&&!side.dataset.articulated){const cs=getComputedStyle(side);const bg={image:cs.backgroundImage,size:cs.backgroundSize,position:cs.backgroundPosition};
   for(const part of ['Body','Tail']){const piece=document.createElement('i');piece.className='anc'+part+'Piece';piece.style.cssText='position:absolute;inset:0;background-image:'+bg.image+';background-size:'+bg.size+';background-position:'+bg.position+';background-repeat:no-repeat;';piece.style.clipPath=part==='Tail'?'inset(0 74px 0 0)':'inset(0 0 0 45px)';side.append(piece);}
   side.dataset.originalImage=bg.image;side.style.backgroundImage='none';side.dataset.articulated='1';}
  if(side&&fish&&fish.sex==='F'&&!side.dataset.femaleFixed&&side.querySelector('.ancTailPiece')){side.dataset.femaleFixed='1';side.style.backgroundImage=side.dataset.originalImage;side.querySelector('.ancTailPiece').style.display='none';side.querySelector('.ancBodyPiece').style.display='none';}
 }
 function clean(el){if(el.dataset.sp108!=null){delete el.dataset.sp108;delete el.dataset.back108;delete el.dataset.ancNudge;}}
 /* the tube's outer left edge per row, read once from the cave photo's alpha (cave box px, x from L, y from T) */
 let SIL=null;
 function silhouette(cave){
  if(SIL&&SIL.ok)return SIL;const img=cave&&cave.querySelector('img.cave89');
  if(!img||!img.complete||!img.naturalWidth)return {ok:0,rows:[[12,1],[76,1]]};
  try{const W=img.naturalWidth,H=img.naturalHeight,cv=document.createElement('canvas');cv.width=W;cv.height=H;const g=cv.getContext('2d');g.drawImage(img,0,0);
   const d=g.getImageData(0,0,W,H).data,kx=160/W,ky=67.5/H,rows=[];
   for(let y=0;y<H;y+=2){let xl=-1;for(let x=0;x<W*.5;x++)if(d[(y*W+x)*4+3]>110){xl=x;break;}if(xl>=0)rows.push([9.5+y*ky,xl*kx]);}
   SIL={ok:1,rows:rows.length>2?rows:[[12,1],[76,1]]};}catch(e){console.error('AFNICA V17.108 cave outline',e);SIL={ok:1,rows:[[12,1],[76,1]]};}
  return SIL;}
 /* visible = left of the tube's outer edge, and at the opening's height up to the opening's left edge (ellipse 7.6 x 23
    at 13.8,42): a fish slides into the dark opening, the ceramic hides what is above/below it, nothing inside shows */
 function mouthClip(el,cave,L,T,sc,face){
  const S=silhouette(cave),R=S.rows,sx=sc*(face<0?-1:1),cx=(parseFloat(el.style.left)||0)+60,cy=(parseFloat(el.style.top)||0)+35;
  const X=px=>((px-cx)/sx+60).toFixed(1),Y=py=>((py-cy)/sc+35).toFixed(1),hx=7.6,hy=23,hcx=13.8,hcy=42;
  const edge=(ry,rx)=>{const v=(ry-hcy)/hy;return Math.abs(v)<1?Math.max(rx,hcx+hx*Math.sqrt(1-v*v)):rx;};   /* up to the opening's far edge: a fish inside shows through the opening */
  const P=[[L-3000,cy-600],[L+edge(R[0][0],R[0][1]),cy-600]];
  const ys=new Set(R.map(q=>q[0]));for(let i=0;i<=24;i++)ys.add(hcy-hy+2*hy*i/24);
  const rowX=y=>{let best=R[0];for(const q of R)if(Math.abs(q[0]-y)<Math.abs(best[0]-y))best=q;return best[1];};
  for(const y of [...ys].sort((p,q)=>p-q))P.push([L+edge(y,rowX(y)),T+y]);
  const yl=Math.max(...ys);P.push([L+edge(yl,rowX(yl)),cy+600],[L-3000,cy+600]);
  el.style.setProperty('clip-path','polygon('+P.map(([px,py])=>X(px)+'px '+Y(py)+'px').join(',')+')','important');}
 /* the inside of the tube seen through the opening (ellipse 7.6 x 23 at 13.8,42 of the cave box): the inner wall under the
    fish (lit terracotta at the rim, into shadow deeper in), a light depth shade over the fish (dimmer deeper in) */
 function shade108(tank,cave){
  const L=parseFloat(cave.style.left)||0,T=parseFloat(cave.style.top)||0,box='position:absolute;pointer-events:none;width:22px;height:52px;clip-path:ellipse(7.6px 23px at 10.8px 26px);left:'+(L+3)+'px;top:'+(T+16)+'px;display:block;';
  let w=tank.querySelector(':scope>.anc108inner');if(!w){w=document.createElement('div');w.className='anc108inner';cave.after(w);}   /* right after the cave image (z 42): over it, under every fish */
  w.style.cssText=box+'z-index:42;background:radial-gradient(ellipse 9px 22px at 15px 27px,rgba(22,12,7,.96) 0%,rgba(48,25,14,.9) 45%,rgba(105,55,30,.85) 80%,rgba(140,78,44,.8) 100%),linear-gradient(90deg,rgba(150,85,48,.9),rgba(70,36,20,.9))';
  let d=tank.querySelector(':scope>.anc108shade');if(!d){d=document.createElement('div');d.className='anc108shade';tank.append(d);}
  d.style.cssText=box+'z-index:49;background:linear-gradient(90deg,rgba(20,11,6,0) 3px,rgba(20,11,6,.22) 9px,rgba(18,10,5,.45) 14px,rgba(16,9,5,.6) 18.4px)';
 }
 function phase(c,next){c.phase=next;c.seconds=0;save();}

 function install(){
  const old=window.ancBreedingMotion40;if(typeof old!=='function'||old.v108)return false;
  const w=function(tank,el,s,fish,dt,wd,base,scale){
   const c=st.ancClutch;
   const own=window.ANC108!==false&&!(c&&ERR.has(c.id))&&tank&&tank.dataset.tank==='breeder'&&fish&&c&&c.stage==='spawning'&&(String(fish.id)===String(c.mom)||String(fish.id)===String(c.dad));
   const D=own&&window.ancDebugV1789&&ancDebugV1789();
   const mom=own&&st.breederTank.find(f=>f.id===c.mom&&!f.dead),dad=own&&st.breederTank.find(f=>f.id===c.dad&&!f.dead);
   if(tank&&tank.dataset.tank==='breeder'&&window.ANC108!==false){const cv0=tank.querySelector('.ancBreedingCave');if(cv0)try{shade108(tank,cv0);}catch(e){}else{const d0=tank.querySelector(':scope>.anc108shade');if(d0)d0.style.display='none';}}
   if(!own||!D||!D.place||!mom||!dad||mom.disease||dad.disease){if(el)clean(el);if(HAND.size)try{takeHand(s,fish);}catch(e){console.error('AFNICA V17.108 hand-over',e);}if(c&&R.size&&!(c.stage==='spawning'))R.clear();return old.apply(this,arguments);}
   try{const cv=tank.querySelector('.ancBreedingCave'),rim=tank.querySelector('.ancCaveRim'),lf=Math.max(5,Math.min(wd-165,wd*.72-78));   /* = V17.40 */
    for(const q of [cv,rim])if(q){q.style.left=lf+'px';q.style.top=(base-43)+'px';}
    return pair(tank,el,s,fish,dt,base,scale,c,D,String(fish.id)===String(c.dad));}
   catch(e){console.error('AFNICA V17.108 spawning',e);ERR.add(c.id);clean(el);return old.apply(this,arguments);}
  };
  w.v108=1;window.ancBreedingMotion40=w;return true;
 }

 function pair(tank,el,s,fish,dt,base,scale,c,D,isDad){
  const blocked=document.hidden||tank.matches('.waterChanging,.persistentWaterActive');dt=blocked?0:Math.min(dt,.1);
  const cave=tank.querySelector('.ancBreedingCave');if(!cave)return false;
  const sc=scale||1,geo=D.caveGeo(cave),L=geo.L,Mx=L+13.8,H=56*sc,P=D.malePos(geo,sc);
  let r=R.get(c.id);if(!r){r={inv:rand(6,12)};R.set(c.id,r);}
  const T=window.__T108;if(T&&T.inv!=null)r.inv=T.inv;
  let a=isDad?r.m:r.f;
  const A0=L-2-46*sc,B0=L+162+46*sc,Hc=Math.max(0,geo.cy+sc-(geo.T+10)+6);
  if(!a){   /* start from where the fish is drawn now (no jump), or straight in the pose after a reload mid-spawn */
   const tp=parseFloat(el.style.top);
   a={x:Number.isFinite(parseFloat(el.dataset.ancX))?parseFloat(el.dataset.ancX):s.x,y:Number.isFinite(tp)?tp+35+3*sc:s.y+3*sc,v:0,dy:0,face:s.face<0?-1:1,st:'',t:0};
   a.cross=a.x>A0-48&&!(a.x>Mx-20&&a.x<L+150);   /* on or right of the tube: goes over it to the left side first */
   const deep=['trapped','laying','female-exit'].includes(c.phase)||(isDad?false:['male-approach','male-enter'].includes(c.phase));
   if(isDad){if(['trapped','laying','female-exit'].includes(c.phase)){a.x=P.fan;a.face=1;a.dy=c.phase==='female-exit'?5:0;a.snap=1;a.cross=false;to(a,'fan');}
    else if(c.phase==='male-enter'){a.cross=false;to(a,'enter');}
    else if(c.phase==='male-approach'){to(a,'aside');}
    else if(c.phase==='female-back')to(a,'out');
    else to(a,a.x>Mx-20&&a.x<L+150?(a.face<0?'peek':'in'):'walk');}
   else{if(deep){a.x=Mx+108-H;a.face=1;a.dy=2;a.snap=1;a.cross=false;to(a,c.phase==='female-exit'?'back':'deep');}
    else to(a,c.phase==='female-back'?'go':'walk');}
   if(isDad)r.m=a;else r.f=a;
  }
  const m=r.m,f=r.f;a.t+=dt;
  /* a standing turn (V17.104 pivot: the head holds its spot, the body swings round it and carries s.x) - nothing else moves */
  const TT=Math.max(.5,window.ancTurnSecV1789||1);let turning=false;
  if(s.turn){s.turn.t+=dt;a.x=Number.isFinite(s.x)?s.x:a.x;a.v=0;const u=s.turn.t/TT;a.face=u<.5?s.turn.from:s.turn.to;turning=true;if(u>=1){a.face=s.turn.to;s.turn=null;}}
  const turnTo=fc=>{if(a.face===fc)return true;if(!s.turn)s.turn={from:a.face,to:fc,t:0};return false;};
  const liftAt=x=>{const gap=x<A0?A0-x:x>B0?x-B0:0;return Hc*sm(1-gap/48);};
  const walk=(tx,spd)=>{const d=tx-a.x;if(Math.abs(d)>20&&Math.sign(d)!==a.face&&!a.v){turnTo(Math.sign(d));return false;}return mv(a,tx,spd,dt);};
  let lift=0;
  const wait=Mx-40-H,aside=(f?f.x:Mx-40-H)-2*H-24,front=Mx-6-H,deepF=Mx+108-H,outF=Mx-70-H,away=Math.max(70,L-260);
  if(!turning){
  if(isDad){
   switch(a.st){
    case 'walk': if(a.cross){lift=liftAt(a.x);if(walk(A0-52,SPD.walk)){a.cross=false;to(a,'walk2');}}else to(a,'walk2');break;
    case 'walk2': if(walk(Mx-10-H,SPD.walk)&&turnTo(1))to(a,'in');break;
    case 'in': if(mv(a,P.hid,SPD.inner,dt))to(a,'flip');break;
    case 'flip': if(a.t>.15&&a.face>0){a.face=-1;const F=window.anc90Debug&&anc90Debug().ST.get(el);if(F){F.df=-1;F.turn=null;F.wt=0;F.mv=0;}}   /* turns round deep inside, out of sight: no pivot (the tail would swing out of the closed end) */
     if(a.t>.6)to(a,'peek');break;
    case 'peek': if(mv(a,P.guard,SPD.inner,dt))to(a,'invite');break;
    case 'invite': if(c.phase==='female-back')to(a,'out');break;
    case 'out': a.dy+=(0-a.dy)*Math.min(1,dt*1.2);if(mv(a,aside,SPD.aside,dt))to(a,'aside');break;   /* walks out head first and past her, behind her (z 42), on the sand */
    case 'aside': a.dy+=(0-a.dy)*Math.min(1,dt*1.2);if(turnTo(1)&&c.phase==='male-approach')to(a,'approach');break;   /* pivots to face the mouth */
    case 'approach':{a.dy+=(0-a.dy)*Math.min(1,dt*1.2);const tx=Math.min(front,f?f.x-2*H-8:front);
     if(walk(tx,SPD.walk)&&(tx>=front-.5||(f&&f.st==='deep'))&&Math.abs(a.dy)<1.5&&c.phase==='male-approach')phase(c,'male-enter');
     if(c.phase==='male-enter')to(a,'enter');break;}
    case 'enter': a.dy+=(0-a.dy)*Math.min(1,dt*1.2);mv(a,P.fan,SPD.slide,dt);if(a.x>=P.fan-.5)to(a,'fan');break;
    case 'fan': mv(a,P.fan,SPD.slide,dt);a.dy+=((c.phase==='female-exit'&&f&&f.st!=='back'&&f.st!=='deep'?5:0)-a.dy)*Math.min(1,dt*.8);break;   /* settles onto the tube floor once she is out */
   }
   if(c.phase==='male-enter'&&a.st==='fan'&&f&&f.st==='deep'){c.trapDay=st.day;c.trapDays=1+Math.floor(Math.random()*2);phase(c,'trapped');toast('Male bristlenose has trapped the female inside the cave');}
   if(a.st==='invite'&&c.phase==='female-approach'&&f&&f.st==='wait'&&f.t>.5&&a.t>=r.inv)phase(c,'female-back');
   if(c.phase==='trapped'&&st.day>=c.trapDay+c.trapDays)phase(c,'laying');
   else if(c.phase==='laying'){c.seconds+=dt;if(c.seconds>=5)phase(c,'female-exit');}
  }else{
   switch(a.st){
    case 'walk': if(a.cross)lift=liftAt(a.x);if(walk(wait,SPD.walk)&&turnTo(1)){a.cross=false;to(a,'wait');}break;
    case 'wait': if(c.phase==='female-back'&&m&&(m.st==='aside'||m.x+H<Mx-30))to(a,'go');break;
    case 'go':{const sn=a.x+H;a.dy+=((sn>Mx?2:0)-a.dy)*Math.min(1,dt*1.5);
     if(mv(a,deepF,sn<Mx-8?SPD.walk:SPD.slide,dt))to(a,'deep');
     if(c.phase==='female-back'&&sn>Mx+60)phase(c,'male-approach');break;}
    case 'deep': if(c.phase==='female-exit')to(a,'back');break;
    case 'back':{const sn=a.x+H;if(mv(a,outF,sn>Mx-10?SPD.back:SPD.walk,dt))to(a,'turnout');break;}   /* backs out under him, head still in; clear of the mouth before the pivot */
    case 'turnout': a.dy+=(0-a.dy)*Math.min(1,dt*1.5);if(turnTo(-1))to(a,'away');break;
    case 'away':
     if(walk(away,SPD.away)&&c.phase==='female-exit'){   /* same as V17.40: the clutch is laid when she has left */
      const hatchIn=4+Math.floor(Math.random()*3),yolkIn=4+Math.floor(Math.random()*3);
      c.stage='eggs';c.laidDay=st.day;c.hatchDay=st.day+hatchIn;c.releaseDay=c.hatchDay+yolkIn;c.lastDay=st.day;save();
      toast('Female bristlenose laid '+c.count+' eggs and left the cave · male fanning them for about '+hatchIn+' days');
      {let g=D.G.get(s);if(!g){g={};D.G.set(s,g);}g.y=a.y;g.lx=a.x;g.lface=a.face;}   /* V17.89 'leave' blend */
      handover(D,tank,r);}
     break;
   }
  }}
  /* body line: the cave floor near the mouth, the sand line (s.y = base, as V17.40) further away - no step at either end */
  const right=a.x+H,k=sm(1-clamp((Mx-right)/120,0,1)),cyO=geo.cy-5,yLine=base+3*sc+(cyO-(base+3*sc))*k;   /* cyO: the opening's lower half (owner: lower when going in; was geo.cy-11, centred) */
  const yT=yLine+a.dy-lift;if(a.snap){a.y=yT;a.snap=0;}else a.y+=(yT-a.y)*Math.min(1,dt*4);
  const over=a.cross&&(yLine+a.dy-a.y)>Hc*.85;   /* drawn above the tube top: in front of it */
  s.x=a.x;s.y=base;s.face=a.face;s.angle=0;s.surface='substrate';s.glass=0;s.atWall=false;s.transition=null;s.time=(s.time||0)+dt;
  const fan=isDad&&a.st==='fan'&&['trapped','laying','female-exit'].includes(c.phase);
  s.mode=fan?'fanning':'courtship';
  el.dataset.sp108=fan?'fan':'1';
  if(!isDad&&a.st==='back')el.dataset.back108='1';else delete el.dataset.back108;
  if(isDad&&a.st==='invite')el.dataset.ancNudge='.35';else delete el.dataset.ancNudge;
  art108(el,fish);
  const zz=a.cross?(over?46:isDad?44:43):isDad?(['out','aside','approach'].includes(a.st)?46:48):47;   /* over the tube's rim layer, the clip decides; crossing: behind the tube while low; he walks behind her */
  D.place(el,a.x,a.y,a.face,sc,1,null,zz,1);if(!a.cross)mouthClip(el,cave,L,geo.T,sc,a.face);
  if(fan){let g=D.G.get(s);if(!g){g={};D.G.set(s,g);}const sw=D.sweep(g,dt,false);D.fanOn(el,true,sw.ph,.006,sw.env);D.tailPiece(el,sw.v*9);}
  else{el.classList.remove('ancFanning');el.classList.remove('ancInCave');delete el.dataset.fanPh89;delete el.dataset.fanAmp89;delete el.dataset.fanEnv89;D.tailPiece(el,0);}
  el.dataset.ancMode=fan?'fanning':'courtship';   /* one mode for every walk: V17.91 changes the dorsal/gait by mode */
  const clip=el.style.getPropertyValue('clip-path');
  if(window.ancPostV1789)try{ancPostV1789(tank,el,s,fish,dt,sc,blocked,'breed',cave);}catch(e){console.error('AFNICA V17.108 post',e);}
  if(!a.cross&&!s.turn&&clip&&clip!=='none'&&el.style.getPropertyValue('clip-path')!==clip)el.style.setProperty('clip-path',clip,'important');   /* V17.106 sets its own fan clip (with the opening) */
  if(el.style.zIndex!==String(zz))el.style.setProperty('z-index',String(zz),'important');
  if(el.style.zIndex!==String(zz))el.style.setProperty('z-index',String(zz),'important');
  return true;
 }
 /* eggs laid: the male's V17.89 cave cycle starts exactly where he lies (its 'fan' window), from the same height -
    applied on his next frame (the eggs are laid on hers) */
 const HAND=new Map();
 function handover(D,tank,r){const c=st.ancClutch;if(r.m)HAND.set(String(c.dad),{x:r.m.x,y:r.m.y});R.delete(c.id);}
 function takeHand(s,fish){const h=fish&&HAND.get(String(fish.id));if(!h||!window.ancDebugV1789)return;HAND.delete(String(fish.id));
  const D=ancDebugV1789();let g=D.G.get(s);if(!g){g={};D.G.set(s,g);}g.ph=null;g.x=h.x;g.y=h.y;g.face=1;}
 if(!install()){const t=setInterval(()=>{if(install())clearInterval(t);},500);setTimeout(()=>clearInterval(t),30000);}
 window.ancSpawnDebugV17108=()=>({R,SPD});
})();
