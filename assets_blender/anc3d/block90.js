/* ================= V17.90 BRISTLENOSE 3D (real 3D fish + cave rendered together) =================
   The owner judged the flat sprite + two-flank shader "hideous". The bristlenose is now a real 3D model made in Blender
   (assets_blender/anc3d) from the owner's specimen photos: full-grown male (olive-brown, bristles) and female (black),
   each from its own side + top + belly photo. Pre-rendered frames (2x game px, contact shadow baked in):
     yaw 0..90 deg (the other half mirrored)  - a real turn through depth, head toward the viewer, instead of a flip/squash
     crawl x8 (advanced by the distance walked, no skating), rasp x2 (head pressed down), swim x6, glass belly view x3.
   The cave: owner "no cut-off between the bristlenose and the caves - no overlapping". While the male is at the cave
   (walking in, fanning tail-out, head out inviting, walking out) the tube AND the male are one frame rendered together in
   3D, picked by how deep his snout is in the tube; the clay hides exactly what it should. Empty cave = the tube frame.
   Movement, timing and every decision stay with the old code (V17.89 and older); this block only draws.
   Hook: wraps window.ancPostV1789 (called after the old code has placed each Ancistrus). Off switch: window.ANC90=false.
   Not done yet: the spawning visit (both fish inside) keeps the old drawing; fry/young use the adult frames scaled. */
(function(){
 window.ANC90=true;
 window.ancTurnSecV1789=.8;                                  /* V17.94: a quicker turn (ref. 10:05), smooth start and stop */
 window.ANC3D_V1789=false;                                  /* the V17.89 shader path drew the sprite without the stepping fins; turns are 3D frames now */
 const SHEET='@@SHEET@@';
 try{const P=window.ancDebugV1789&&ancDebugV1789().PFIN;if(P)for(const k of Object.keys(P))P[k]=[];}catch(e){console.error('AFNICA V17.93 fins',e);}   /* the photos already show the fins as they lie: no erase-and-redraw (it cut them) */
 const ATL={T:{src:'@@ATLAS_T@@',idx:@@INDEX_T@@},C2:{src:'@@ATLAS_C2@@',idx:@@INDEX_C2@@}};   /* V17.92: T = U-turn frames (M, F, JO, JB), C2 = tube + the male's cave layers */
 for(const k in ATL){const a=ATL[k];a.img=new Image();a.img.src=a.src;a.pos={};a.idx.names.forEach((n,i)=>a.pos[n]=a.idx.pos[i]);}
 const ready=a=>a.img.complete&&a.img.naturalWidth>0;   /* a broken image is 'complete' too */
 const clamp=(v,a,b)=>v<a?a:v>b?b:v,sm=q=>{q=clamp(q,0,1);return q*q*(3-2*q);};
 const PIVX=155.4,PIVY=96.8;                                 /* frame px of the mid-body ground point (2x) */
 const CAVEMODES={'fanning':1,'cave-in':1,'cave-flip':1,'cave-peek':1,'cave-guard':1,'cave-exit':1,'cave-enter':1};
 const ST=new WeakMap(),TK=new WeakMap();
 const css=document.createElement('style');
 css.textContent='html .ancArt i{background-image:url('+SHEET+');background-size:240px 620px}html .ancArt .ancSide{transform:none!important;filter:none!important}'+   /* no squash, no washed-out colours on the photos */
  /* V17.91 young rows: fry side 238 / belly 338, juvenile side 438 / belly 538 (css px of the 240 px wide sheet) */
  'html .ancArt[data-stage91=fry] .ancSide{background-position:0 -238px}html .ancArt[data-stage91=fry].ancFemale .ancSide{background-position:-120px -238px}'+
  'html .ancArt[data-stage91=fry] .ancGlass{background-position:0 -338px}html .ancArt[data-stage91=fry].ancFemale .ancGlass{background-position:-120px -338px}'+
  'html .ancArt[data-stage91=juv][data-col91=o] .ancSide{background-position:0 -438px}html .ancArt[data-stage91=juv][data-col91=b] .ancSide{background-position:-120px -438px}'+
  'html .ancArt[data-stage91=juv][data-col91=o] .ancGlass{background-position:0 -538px}html .ancArt[data-stage91=juv][data-col91=b] .ancGlass{background-position:-120px -538px}'+   /* the old animated drawing runs on the owner's photos */

  '.tank.anc90cave .ancBreedingCave,.tank.anc90cave .ancCaveRim,.tank.anc90cave .ancCaveShade89,.tank.anc90cave canvas.ancBrood89{opacity:0!important}'+
  'canvas.anc90c{position:absolute;left:-20px;top:-10px;width:160px;height:90px;pointer-events:none;transform:none!important}'+
  'canvas.anc94t{position:absolute;left:-52.3px;width:240px;height:110px;pointer-events:none;transform:none!important;display:none}'+
  'canvas.anc90cv{position:absolute;width:340px;height:110px;pointer-events:none;z-index:42}canvas.anc90cv.front{z-index:47}';   /* front: his part outside the tube, closer than the fish lane */
 document.head.appendChild(css);

 function spawning(){const c=typeof st!=='undefined'&&st?st.ancClutch:null;return !!(c&&c.stage==='spawning');}   /* st is a top-level let, not window.st */
 /* V17.94 turn canvas: 240x110 game px, the fish's mid-body ground point at the start of the turn at (110,64) */
 function turnCanvas(el,sex){
  let c=el.querySelector(':scope>canvas.anc94t');
  if(!c){c=document.createElement('canvas');c.className='anc94t';c.width=480;c.height=220;el.appendChild(c);}
  c.style.top=((sex==='F'||sex==='JB'?-4:-10)+48.4-64)+'px';return c;
 }
 function canvasFor(el,sex){
  let c=el.querySelector(':scope>canvas.anc90c');
  if(!c){c=document.createElement('canvas');c.className='anc90c';c.width=320;c.height=180;el.appendChild(c);}
  c.style.top=(sex==='F'||sex==='JB'?-4:-10)+'px';   /* JB sits in the female column, JO in the male one */                        /* the old female sprite sat 6 px lower in its box */
  return c;
 }
 function blit(g,atl,name,mirror,alpha,piv){
  const p=atl.pos[name];if(!p||!ready(atl))return false;
  const w=atl.idx.w,h=atl.idx.h;g.save();g.globalAlpha=alpha;
  if(mirror){g.translate(2*(piv||PIVX),0);g.scale(-1,1);}
  g.drawImage(atl.img,p[0],p[1],w,h,0,0,w,h);g.restore();return true;
 }
 function off(el,tank){
  el.classList.remove('anc90','anc90hid');const f0=ST.get(el);if(f0&&f0.hid){f0.hid=0;el.style.setProperty('opacity','1','important');}const c=el.querySelector(':scope>canvas.anc90c');if(c)c.remove();
  el.classList.remove('anc90hid');
 }

 /* ---------- the cave (V17.92): tube alone + the male in two layers ----------
    _in  = his part behind the mouth plane, shown only through the mouth opening (ellipse 7 x 22.6 at 173.8,72);
    _out = his part in front of it, never hidden by the clay (the camera is on the mouth side). Drawn at the exact
    sub-pixel position (frames every 4 px + the remainder as a shift), so he moves smoothly and never overlaps the clay. */
 const MX=173.8*2,MY=72*2,MRX=7*2,MRY=22.6*2;
 function caveState(el,cave,face,sc,mode){
  const L=parseFloat(cave.style.left)||0,mouth=L+13.8,x=+el.dataset.ancX;
  if(!Number.isFinite(x))return null;
  if(mode==='cave-flip')return {hide:1};                     /* turning round deep inside: nothing shows */
  if(mode==='fanning'){const ph=+el.dataset.fanPh89||0,fp=(((ph/(2*Math.PI))%1)+1)%1*24,i0=Math.floor(fp)%24,i1=(i0+1)%24;   /* 24 frames a beat, blended */
   return {name:'C2_f'+String(i0).padStart(2,'0'),name2:'C2_f'+String(i1).padStart(2,'0'),mix:fp-Math.floor(fp),shift:0,dy:0,a:1};}
  /* the tube stands closer to the viewer than the lane the fish walk in (17 px lower on screen): he walks down to its
     level gradually while lining up with it (V17.92, owner: no drop from above the sand) */
  const T0=parseFloat(cave.style.top)||0,y=+el.dataset.ancY,lift=Number.isFinite(y)?(T0-30+103.2)-(y+4*sc):0;
  if(face>0){
   const d=(x+56*sc-mouth)/sc;if(d<-64)return null;if(d>146)return {hide:1};
   const q=clamp(Math.round(d/4)*4,-64,144);return {name:'C2_i'+(q<0?'-':'+')+String(Math.abs(q)).padStart(3,'0'),shift:(d-q)*2,dy:-2*lift*(1-sm((d+64)/54)),a:sm((d+64)/16)};
  }
  const d=(mouth-(x-56*sc))/sc;if(d>124)return null;if(d<-54)return {hide:1};
  const q=clamp(Math.round(d/4)*4,-52,124);return {name:'C2_o'+(q<0?'-':'+')+String(Math.abs(q)).padStart(3,'0'),shift:-(d-q)*2,dy:-2*lift*sm((d-70)/54),a:1-sm((d-108)/16)};
 }
 function drawCave(tank,cave,m){
  let t=TK.get(tank);if(!t){t={};TK.set(tank,t);}
  let cv=tank.querySelector('canvas.anc90cv');
  if(!cv){cv=document.createElement('canvas');cv.className='anc90cv';cv.width=680;cv.height=220;tank.insertBefore(cv,tank.querySelector('.modelFish')||null);t.last='';}
  let fv=tank.querySelector('canvas.anc90cv.front');
  if(!fv){fv=document.createElement('canvas');fv.className='anc90cv front';fv.width=680;fv.height=220;tank.append(fv);}
  for(const c of [cv,fv]){c.style.left=((parseFloat(cave.style.left)||0)-160)+'px';c.style.top=((parseFloat(cave.style.top)||0)-30)+'px';}
  if(!ready(ATL.C2))return;
  const sig=m&&m.name?m.name+'|'+(m.name2||'')+'|'+(m.mix||0).toFixed(2)+'|'+m.shift.toFixed(2)+'|'+(m.dy||0).toFixed(1)+'|'+m.a.toFixed(2):'tube';if(t.last===sig)return;
  const g=cv.getContext('2d'),gf=fv.getContext('2d');g.clearRect(0,0,680,220);gf.clearRect(0,0,680,220);
  if(!blit(g,ATL.C2,'C_tube00',false,1))return;t.last=sig;tank.classList.add('anc90cave');   /* old cave hidden once the new one is drawn */
  if(m&&m.name){
   g.save();g.beginPath();g.ellipse(MX,MY,MRX,MRY,0,0,7);g.clip();g.translate(m.shift,m.dy||0);blit(g,ATL.C2,m.name+'_in',false,m.a);if(m.name2&&m.mix>.02)blit(g,ATL.C2,m.name2+'_in',false,m.a*m.mix);g.restore();
   gf.save();gf.translate(m.shift,m.dy||0);blit(gf,ATL.C2,m.name+'_out',false,m.a);if(m.name2&&m.mix>.02)blit(gf,ATL.C2,m.name2+'_out',false,m.a*m.mix);gf.restore();
  }
 }
 function caveLoop(){
  try{
   if(window.ANC90)document.querySelectorAll('.tank').forEach(tank=>{
    const cave=tank.querySelector('.ancBreedingCave');const t=TK.get(tank)||{};
    if(!cave||spawning()&&tank.id==='tank-breeder'){const cvs=tank.querySelectorAll('canvas.anc90cv');if(cvs.length){cvs.forEach(c=>c.remove());tank.classList.remove('anc90cave');}return;}
    drawCave(tank,cave,t.m&&performance.now()-t.at<250?t.m:null);
   });
   if(!window.ANC90)document.querySelectorAll('canvas.anc90cv').forEach(c=>{c.parentElement&&c.parentElement.classList.remove('anc90cave');c.remove();});
  }catch(e){console.error('AFNICA V17.92 cave',e);}
  requestAnimationFrame(caveLoop);
 }
 requestAnimationFrame(caveLoop);

 /* ---------- one fish ----------
    Owner (v2): the old animated drawing must stay (fins stepping, body flex, breathing, mouth rasping on the glass) - it now
    runs on the owner's photos (SHEET). V17.90 draws only what the old system did badly: the TURN (3D yaw frames instead
    of a flat squash) and the CAVE (tube + male rendered together). */
 function shadowOf(tank,el){return tank.querySelector('[data-anc-shadow="'+el.dataset.fishId+'"]');}
 function fade(tank,el,o){                                  /* the old drawing + its shadow at opacity o */
  const art=el.querySelector('.ancArt');if(art){if(o>=1)art.style.removeProperty('opacity');else art.style.setProperty('opacity',o.toFixed(3),'important');}
  const sh=shadowOf(tank,el);if(sh){if(o>=1)sh.style.removeProperty('opacity');else sh.style.setProperty('opacity',o.toFixed(3),'important');}
 }
 function oldDraw(tank,el,f){
  el.classList.remove('anc90','anc90hid');if(f&&f.hid){f.hid=0;el.style.setProperty('opacity','1','important');}
  el.querySelectorAll(':scope>canvas.anc90c,:scope>canvas.anc94t').forEach(c=>c.style.display='none');
  fade(tank,el,1);if(f&&f.tx94){f.tx94=0;el.style.removeProperty('translate');}if(f)f.tr94=null;
 }
 /* V17.91: a fish younger than 5 days is drawn from the fry rows; when its stage changes the fin canvas is set up again */
 function stage91(el,fish){
  const art=el.querySelector('.ancArt');if(!art)return;
  const age=fish?+fish.age:NaN,adult=(typeof S!=='undefined'&&S.anc&&S.anc.adult)||16;   /* S is a top-level const, not window.S */
  const stg=Number.isFinite(age)&&age<5?'fry':Number.isFinite(age)&&age<adult?'juv':'';
  /* juveniles come out mixed (owner): olive-brown or black, fixed per fish (from its id) */
  let h=0;const id=String(fish&&fish.id||'');for(let i=0;i<id.length;i++)h=(h*31+id.charCodeAt(i))|0;
  h^=h>>>16;h=Math.imul(h,0x45d9f3b);h^=h>>>16;h=Math.imul(h,0x45d9f3b);h^=h>>>16;   /* mix well: ids differ by one character */
  const col=stg==='juv'?(h&1?'b':'o'):'';
  if((art.dataset.stage91||'')===stg&&(art.dataset.col91||'')===col)return;
  if(stg)art.dataset.stage91=stg;else delete art.dataset.stage91;
  if(col)art.dataset.col91=col;else delete art.dataset.col91;
  /* the old articulated body/tail pieces keep the cell they were made with: point them at the new one */
  const px=col==='o'?0:col==='b'?-120:art.classList.contains('ancFemale')?-120:0,py=stg==='fry'?-238:stg==='juv'?-438:-38;
  art.querySelectorAll('.ancBodyPiece,.ancTailPiece').forEach(p=>p.style.backgroundPosition=px+'px '+py+'px');
  const side=art.querySelector('.ancSide');if(side){side.querySelectorAll(':scope>canvas').forEach(c=>c.remove());side.classList.remove('finWarp');delete side.dataset.finSkip;}
  const gl=art.querySelector('.ancGlass');if(gl){gl.querySelectorAll(':scope>canvas').forEach(c=>c.remove());gl.classList.remove('finWarpG','gOn');}
 }
 function drawFish(tank,el,s,fish,dt,sc,blocked,via,cave){
  stage91(el,fish);
  let f=ST.get(el);
  if(!window.ANC90||(spawning()&&tank.id==='tank-breeder')){oldDraw(tank,el,f);return;}
  const art91=el.querySelector('.ancArt'),stg91=art91&&art91.dataset.stage91;
  if(stg91==='fry'){oldDraw(tank,el,f);return;}   /* fry: tiny, the plain flat turn is enough */
  const sex=stg91==='juv'?(art91.dataset.col91==='b'?'JB':'JO'):(fish&&fish.sex==='F'?'F':'M');if(!ready(ATL.T)){oldDraw(tank,el,f);return;}
  const tr=el.style.transform||'',m=/scaleX\(([-\d.e]+)\)/.exec(tr),face=s&&s.face!=null?(s.face<0?-1:1):(m&&+m[1]<0?-1:1);
  const scm=/scale\(([-\d.e]+)\)/.exec(tr),scl=scm?+scm[1]:(sc||1),now=performance.now(),mode=el.dataset.ancMode||'';
  if(!f){f={df:face,turn:null};ST.set(el,f);}
  life91(tank,el,s,mode,now);
  /* cave (adult male): drawn by the cave canvas; his own element fades out as the cave layers fade in */
  if(cave&&(CAVEMODES[mode]||mode==='cave-approach')&&!spawning()&&fish&&fish.sex==='M'&&!stg91){
   if(mode==='cave-enter'&&face>0&&s&&!s.p91done){const dIn=+el.dataset.ancX+56*scl-((parseFloat(cave.style.left)||0)+13.8);if(dIn>=-3){s.p91done=1;s.p91until=now+800+Math.random()*600;}}   /* V17.91: pause at the mouth */
   const cs=caveState(el,cave,face,scl,mode);
   if(cs){let t=TK.get(tank);if(!t){t={};TK.set(tank,t);}t.m=cs.hide?null:cs;t.at=now;
    const a=cs.hide?1:cs.a;el.style.setProperty('opacity',(1-a).toFixed(3),'important');f.hid=1;f.df=face;f.turn=null;f.x=+el.dataset.ancX;f.vx=0;f.mv=0;
    const c=el.querySelector(':scope>canvas.anc90c');if(c)c.style.display='none';fade(tank,el,1);return;}
  }
  if(f.hid){f.hid=0;el.classList.remove('anc90hid');el.style.setProperty('opacity','1','important');}
  const glass=clamp(parseFloat(el.style.getPropertyValue('--anc-glass'))||(s&&s.glass)||0,0,1);
  /* never drawn crawling backwards: on the sand a clear, sustained movement decides the facing (head first) */
  const x=+el.dataset.ancX,dx=Number.isFinite(x)&&Number.isFinite(f.x)&&dt>0&&dt<.2?x-f.x:0;f.x=x;   /* no velocity across a gap */
  f.vx=(f.vx||0)+((dt>0?dx/dt:0)-(f.vx||0))*Math.min(1,dt*6);
  const th=Math.max(2,9*scl),opp=glass<.3&&!blocked&&Math.abs(f.vx)>th&&Math.sign(f.vx)!==face;f.ot=opp?(f.ot||0)+dt:0;   /* thresholds scale with the fish: young hop slowly */
  if(glass<.3&&!blocked){if(f.ot>(scl<.8?.3:.6))f.mv=Math.sign(f.vx);   /* young react quicker (short hops) */else if(Math.abs(f.vx)<th/3)f.mv=0;else if(f.mv&&Math.sign(f.vx)!==f.mv)f.mv=0;}else f.mv=0;
  /* V17.92 turn: the old turn's own timer (s.turn, during which the fish stays put) or a facing-follow turn of our own */
  const T=Math.max(.5,window.ancTurnSecV1789||1);let tu=null;
  if(f.df==null)f.df=face;
  if(s&&s.turn&&glass<=.3){tu={u:clamp(s.turn.t/T,0,1),from:s.turn.from<0?-1:1,to:s.turn.to<0?-1:1};f.df=tu.to;f.turn=null;}
  else{
   const wantF=f.mv||face;
   if(glass>.3){f.df=wantF;f.turn=null;}
   else{
    if(!f.turn&&f.df!==wantF)f.turn={from:f.df,to:wantF,t:0};
    if(f.turn&&f.turn.to!==wantF)f.turn={from:f.turn.to,to:f.turn.from,t:Math.max(0,T-f.turn.t)};   /* reverses smoothly */
    if(f.turn){f.turn.t+=dt;tu={u:clamp(f.turn.t/T,0,1),from:f.turn.from,to:f.turn.to};if(f.turn.t>=T){f.df=f.turn.to;f.turn=null;tu=null;}}
   }
  }
  const setSign=sg=>{if(m)el.style.setProperty('transform',tr.replace(/scaleX\([^)]*\)/,'scaleX('+sg+')'),'important');};   /* no flat squash */
  const rot=/rotate\(([-\d.e]+)deg\)/.exec(tr),tilt=rot?Math.abs(+rot[1]):0;
  if(!tu||tu.from===tu.to||tilt>10){setSign(tu&&tilt>10?(tu.u<.5?tu.from:tu.to):f.df);oldDraw(tank,el,f);return;}   /* 3D U-turn only when level on the sand */
  /* V17.94 walking U-turn: the fish curves away into the tank along a semicircle (radius 39 px at scale 1) and comes back
     facing the other way; the photo drawing walks the same path while it cross-fades (first/last 15 %) */
  const u=tu.u,kf=24*u,k=Math.min(24,Math.floor(kf)),k2=Math.min(24,k+1),mix=kf-k,a3=u<.15?u/.15:u>.85?(1-u)/.15:1,sg=u<.5?tu.from:tu.to;
  /* the forward part of the walk fits the free space ahead (a wall or the cave is usually why it turns) */
  if(!f.tr94||f.tr94.key!==tu.from+'|'+tu.to+'|'+(s&&s.turn?1:0)){
   const sn=x+56*scl*tu.from,W=tank.clientWidth||960;let room=tu.from>0?W-14-sn:sn-14;
   if(cave){const L=parseFloat(cave.style.left)||0;if(tu.from>0&&L+8>sn)room=Math.min(room,L+8-sn);if(tu.from<0&&L+156<sn)room=Math.min(room,sn-(L+156));}
   f.tr94={key:tu.from+'|'+tu.to+'|'+(s&&s.turn?1:0),R:clamp(room-6,0,39*scl)};}
  const hd94=Math.PI*(u-Math.sin(2*Math.PI*u)/(2*Math.PI)),dx94=f.tr94.R*Math.sin(hd94)*tu.from;
  setSign(sg);el.style.setProperty('clip-path','none','important');el.classList.add('anc90');fade(tank,el,1-a3);
  el.style.setProperty('translate',dx94.toFixed(2)+'px 0px','important');f.tx94=1;   /* the photo moves with the 3D fish */
  const c=turnCanvas(el,sex),g=c.getContext('2d');c.style.display='block';g.clearRect(0,0,480,220);
  c.style.translate='none';                                   /* the element's shift carries the walk for both */
  const mir=(tu.from<0)!==(sg<0);blit(g,ATL.T,sex+'_turn'+String(k).padStart(2,'0'),mir,a3,220);if(mix>.02&&k2!==k)blit(g,ATL.T,sex+'_turn'+String(k2).padStart(2,'0'),mir,a3*mix,220);   /* right->left as rendered, left->right mirrored */
 }

 const prev=window.ancPostV1789;
 window.ancPostV1789=function(tank,el,s,fish,dt,sc,blocked,via,cave){
  if(prev)prev.apply(this,arguments);
  try{drawFish(tank,el,s,fish,dt,sc,blocked,via,cave||(tank&&tank.querySelector('.ancBreedingCave')));}catch(e){console.error('AFNICA V17.90 anc 3D',e);}
 };
 /* ================= V17.91 BRISTLENOSE LIFE 2 (owner: "do all - make it more realistic") =================
    Drives the old animated drawing (V17.42 fin canvas, hook ancCanvasV1791) from what the fish is doing:
    - dorsal folds back flat at rest (DFOLD), raised when it moves, swims, fans, courts or another bristlenose comes close
    - crawling: snout pressed down, tail sways gently; it goes in bouts of 1.6-3.4 s with short stops (sand speed gate)
    - rasping on the sand: the head grips and releases (nose dip pulses ~1.5 Hz), the tail sways a little
    - swimming (long trips, crossing the cave): stronger, faster tail beat, dorsal up
    - male bristles sway a little even at rest; breathing slower at rest with a clearly visible low gill slit (old code)
    - on the glass: the oral disc grips and releases (old code) and the head turns a few degrees side to side */
 const Q91=new WeakMap();
 function life91(tank,el,s,mode,now){
  if(s&&!/^(cave|fanning)/.test(mode))s.p91done=0;
  const mb=s&&s.bg;el.dataset.swim91=(mb&&mb.swim&&(mode==='move'||mode==='toWall'))||(s&&s.ovl89>2)?'1':'';
  /* alert: another bristlenose within ~75 px */
  const x=+el.dataset.ancX,y=+el.dataset.ancY;let near=false;
  if(Number.isFinite(x))tank.querySelectorAll('.modelFish[data-anc-mode]').forEach(o=>{if(o!==el){const d=Math.hypot(+o.dataset.ancX-x,+o.dataset.ancY-y);if(d<75)near=true;}});
  el.dataset.alert91=near?'1':'';
  /* glass rasping: small side-to-side head turns while gripping */
  if(el.dataset.ancSurface==='glass'&&mode==='graze'&&el.dataset.ancStroke!=='0'){
   const tr=el.style.transform||'',m=/rotate\(([-\d.e]+)deg\)/.exec(tr);
   if(m){const w=3.5*Math.sin(now/1000*1.15+(el.dataset.fishId||'').length);el.style.setProperty('transform',tr.replace(m[0],'rotate('+(+m[1]+w).toFixed(2)+'deg)'),'important');}
  }
 }
 window.ancCanvasV1791=function(s,dt,sp,move,fan){
  const fe=s.fe;if(!fe)return null;let q=Q91.get(fe);if(!q){q={fold:.6,rp:Math.random()*6.283,idle:Math.random()*6.283};Q91.set(fe,q);}
  const mode=fe.dataset.ancMode||'',surf=fe.dataset.ancSurface,swim=fe.dataset.swim91==='1',male=!!fe.querySelector('.ancMale');
  const rasp=(mode==='graze'||mode==='forage'||mode==='wafer')&&surf!=='glass';
  const alert=swim||fan||move>.15||fe.dataset.alert91==='1'||/^(cave|courtship|spawn|breeding)/.test(mode);
  const want=alert?0:(rasp?.45:.8);
  q.fold+=(want-q.fold)*Math.min(1,dt*(want<q.fold?2.5:.7));
  q.rp+=dt*2*Math.PI*1.5;q.idle+=dt;
  const grip=rasp?Math.pow(Math.max(0,Math.sin(q.rp)),.7):0;
  return {fold:q.fold,nose:swim?0:rasp?.014+.016*grip:.01*move,sway:swim?1:rasp?.25+.25*grip:.45*move,dors:swim?1:(fan?.8:Math.max(move,.15)),
   amp:swim?2.4:1,ph:swim?2*Math.PI*1.7:0,tentMin:male?.2+.1*Math.sin(q.idle*.9):0};
 };
 /* crawling in bouts: 1.6-3.4 s of walking, 0.35-0.95 s stops (not for swims or the last few px) */
 const sand91=window.ancSandSpeedV1789;
 if(sand91)window.ancSandSpeedV1789=function(s,d,thrust,dt,scale,key){
  const v=sand91.apply(this,arguments),b=s&&s.bg;if(s&&s.p91until&&performance.now()<s.p91until)return 0;
  if(!b||b.swim||!(dt>0)||s.young||!(s.mode==='move'||s.mode==='graze'))return v;   /* bouts only for ordinary crawling */
  let q=s.sg91;if(!q||q.key!==key){q=s.sg91={on:true,t:0,d:1.6+Math.random()*1.8,f:1,key};}   /* a new trip starts walking */
  q.t+=dt;if(q.t>q.d){q.on=!q.on;q.t=0;q.d=q.on?1.6+Math.random()*1.8:.35+Math.random()*.6;}
  q.f+=((q.on||d<6?1:0)-q.f)*Math.min(1,dt*5);return v*q.f;
 };
 window.anc90Debug=()=>({ATL,ST,TK,Q91});
})();
