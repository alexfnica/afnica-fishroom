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
 window.ancTurnSecV1789=2;                                   /* V17.95: a slow, even pivot (ref. B7RksQ1xU18 0:25.4-0:27.8, ~2.4 s) */
 window.ANC3D_V1789=false;                                  /* the V17.89 shader path drew the sprite without the stepping fins; turns are 3D frames now */
 const SHEET='@@SHEET@@';
 try{const P=window.ancDebugV1789&&ancDebugV1789().PFIN;if(P)for(const k of Object.keys(P))P[k]=[];}catch(e){console.error('AFNICA V17.93 fins',e);}   /* the photos already show the fins as they lie: no erase-and-redraw (it cut them) */
 const ATL={T:{src:'@@ATLAS_T@@',idx:@@INDEX_T@@},C2:{src:'@@ATLAS_C2@@',idx:@@INDEX_C2@@},P:{src:'@@ATLAS_P@@',idx:@@INDEX_P@@}};   /* V17.96: P = the two-male fight */   /* V17.92: T = U-turn frames (M, F, JO, JB), C2 = tube + the male's cave layers */
 for(const k in ATL){const a=ATL[k];a.img=new Image();a.img.src=a.src;a.pos={};a.idx.names.forEach((n,i)=>a.pos[n]=a.idx.pos[i]);}
 const ready=a=>a.rc97||a.img.complete&&a.img.naturalWidth>0;   /* a broken image is 'complete' too; rc97 = a recoloured canvas copy */
 /* V17.97 colour for life: every non-fry fish keeps one colour from its id (olive-brown 'o' or black 'b'); adults whose
    colour differs from their photo (black male, brown female) use two extra sheet columns (recolor_sheet.py) and, for the
    3D frames, a copy of the atlas recoloured here once (MAPS97 from make_maps97.py: brightness LUT + tint). */
 const MAPS97=@@MAPS97@@;
 function recol97(atl,key){                                /* per frame on demand: small canvases (Safari/iOS canvas limit, memory, no hitch) */
  if(!key||!ready(atl)||!MAPS97[key])return atl;atl.rc=atl.rc||{};
  return atl.rc[key]||(atl.rc[key]={img:atl.img,idx:atl.idx,pos:atl.pos,rc97:1,cells:new Map(),cell(name){
   let c=this.cells.get(name);if(c!==undefined)return c;const p=atl.pos[name],w=atl.idx.w,h=atl.idx.h;c=null;
   try{c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d',{willReadFrequently:true});g.drawImage(atl.img,p[0],p[1],w,h,0,0,w,h);
    const d=g.getImageData(0,0,w,h),q=d.data,M=MAPS97[key],L=M.lut,T=M.tint;
    for(let k=0;k<q.length;k+=4){if(q[k+3]<10)continue;const y=(q[k]*.299+q[k+1]*.587+q[k+2]*.114)|0,yt=L[y>255?255:y],t=T[Math.min(23,(yt*24/256)|0)];q[k]=yt*t[0];q[k+1]=yt*t[1];q[k+2]=yt*t[2];}
    g.putImageData(d,0,0);}catch(e){console.error('AFNICA V17.97 recolour',e);c=null;}
   this.cells.set(name,c);return c;}});
 }
 function rc97(el){                                          /* '' (as photographed), 'MB' black adult male, 'FO' brown adult female */
  const a=el&&el.querySelector('.ancArt');if(!a||a.dataset.stage91)return '';
  const F=a.classList.contains('ancFemale'),c=a.dataset.col91;return !F&&c==='b'?'MB':F&&c==='o'?'FO':'';
 }
 const clamp=(v,a,b)=>v<a?a:v>b?b:v,sm=q=>{q=clamp(q,0,1);return q*q*(3-2*q);};
 const PIVX=155.4,PIVY=96.8;                                 /* frame px of the mid-body ground point (2x) */
 const TRANS97={attach:1,detach:1,wallHold:1,toEdgeG:1};   /* glass transitions */
 const CAVEMODES={'fanning':1,'cave-in':1,'cave-flip':1,'cave-peek':1,'cave-guard':1,'cave-exit':1,'cave-enter':1,'cave-turn':1};   /* V17.97: cave-turn too (the photo popped up for half a second at the mouth) */
 const ST=new WeakMap(),TK=new WeakMap();
 const css=document.createElement('style');
 css.textContent='html .ancArt i{background-image:url('+SHEET+');background-size:480px 620px}'+   /* V17.97: 4 columns (male, female, black male, brown female) */
  'html .ancArt:not([data-stage91]):not(.ancFemale)[data-col91=b] .ancSide{background-position:-240px -38px}html .ancArt:not([data-stage91]):not(.ancFemale)[data-col91=b] .ancGlass{background-position:-240px -138px}'+
  'html .ancArt:not([data-stage91]).ancFemale[data-col91=o] .ancSide{background-position:-360px -38px}html .ancArt:not([data-stage91]).ancFemale[data-col91=o] .ancGlass{background-position:-360px -138px}'+
  'html .ancArt .ancSide{transform:none!important;filter:none!important}'+   /* no squash, no washed-out colours on the photos */
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
  const w=atl.idx.w,h=atl.idx.h,cel=atl.cell?atl.cell(name):null;g.save();g.globalAlpha=alpha;
  if(mirror){g.translate(2*(piv||PIVX),0);g.scale(-1,1);}
  if(cel)g.drawImage(cel,0,0,w,h,0,0,w,h);else g.drawImage(atl.img,p[0],p[1],w,h,0,0,w,h);g.restore();return true;   /* V17.97: a recoloured cell (or the photo colour if that failed) */
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
   g.save();g.beginPath();g.ellipse(MX,MY,MRX,MRY,0,0,7);g.clip();g.translate(m.shift,m.dy||0);blit(g,recol97(ATL.C2,m.rc),m.name+'_in',false,m.a);if(m.name2&&m.mix>.02)blit(g,recol97(ATL.C2,m.rc),m.name2+'_in',false,m.a*m.mix);g.restore();
   gf.save();gf.translate(m.shift,m.dy||0);blit(gf,recol97(ATL.C2,m.rc),m.name+'_out',false,m.a);if(m.name2&&m.mix>.02)blit(gf,recol97(ATL.C2,m.rc),m.name2+'_out',false,m.a*m.mix);gf.restore();
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
  const col=stg==='fry'?'':(h&1?'b':'o');   /* V17.97: the same colour as a juvenile and as an adult */
  if((art.dataset.stage91||'')===stg&&(art.dataset.col91||'')===col)return;
  if(stg)art.dataset.stage91=stg;else delete art.dataset.stage91;
  if(col)art.dataset.col91=col;else delete art.dataset.col91;
  /* the old articulated body/tail pieces keep the cell they were made with: point them at the new one */
  const isF97=art.classList.contains('ancFemale'),px=stg==='juv'?(col==='o'?0:-120):stg==='fry'?(isF97?-120:0):isF97?(col==='o'?-360:-120):(col==='b'?-240:0),py=stg==='fry'?-238:stg==='juv'?-438:-38;
  art.querySelectorAll('.ancBodyPiece,.ancTailPiece').forEach(p=>p.style.backgroundPosition=px+'px '+py+'px');
  const side=art.querySelector('.ancSide');if(side){side.querySelectorAll(':scope>canvas').forEach(c=>c.remove());side.classList.remove('finWarp');delete side.dataset.finSkip;}
  const gl=art.querySelector('.ancGlass');if(gl){gl.querySelectorAll(':scope>canvas').forEach(c=>c.remove());gl.classList.remove('finWarpG','gOn');}
 }
 /* V17.99 (owner: "the male teleports a little going into the cave"): the photo -> cave-frame hand-over lasted ~3 frames
    (16 depth units of walking) and the cave frame sat ~4 px off the photo (a pop). At the first frame of the fade the cave
    frame is moved onto the photo (alpha centroids); that correction eases out as the fade completes. */
 const CC99=new Map();
 function cen99(name){if(CC99.has(name))return CC99.get(name);const A=ATL.C2;let r=null;
  try{if(ready(A)){const w=A.idx.w,h=A.idx.h,c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d',{willReadFrequently:true});let sx=0,sy=0,sw=0;
   for(const n of [name+'_in',name+'_out']){const p=A.pos[n];if(!p)continue;g.clearRect(0,0,w,h);g.drawImage(A.img,p[0],p[1],w,h,0,0,w,h);const d=g.getImageData(0,0,w,h).data;
    for(let y=0;y<h;y+=2)for(let x=0;x<w;x+=2){const q=d[(y*w+x)*4+3];if(q>40){sx+=x*q;sy+=y*q;sw+=q;}}}
   if(sw)r=[sx/sw,sy/sw];}}catch(e){console.error('AFNICA V17.99 cave centroid',e);}
  if(r||ready(A))CC99.set(name,r);return r;}
 function photo99(tank,el){const c=el.querySelector('.ancSide>canvas');if(!c||!c.width||c.style.visibility==='hidden')return null;
  const T=tank.getBoundingClientRect(),r=c.getBoundingClientRect();if(!r.width)return null;const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let sx=0,sy=0,sw=0;
  for(let y=0;y<c.height;y+=2)for(let x=0;x<c.width;x+=2){const q=d[(y*c.width+x)*4+3];if(q>40){sx+=x*q;sy+=y*q;sw+=q;}}if(!sw)return null;
  const mir=/scaleX\(-/.test(el.style.transform||''),u=sx/sw/c.width,v=sy/sw/c.height,k=T.width/(tank.clientWidth||T.width)||1;
  return [(r.left-T.left+(mir?1-u:u)*r.width)/k,(r.top-T.top+v*r.height)/k];}
 function xfade99(tank,el,f,cs,dt){
  if(cs.hide||!cs.name||cs.name2){f.x99=null;return;}                    /* fanning (two frames blended) or hidden: nothing to hand over */
  const fading=cs.a>0&&cs.a<1;
  if(!fading&&!f.x99)return;
  if(!f.x99){f.x99={a:cs.a>=.5?1:0,dx:0,dy:0};                           /* coming from the cave side (walking out): fade the photo in */
   let pc=null,cc=null;try{pc=photo99(tank,el);cc=cen99(cs.name);}catch(e){console.error('AFNICA V17.99 cave hand-over',e);}const cv=tank.querySelector('canvas.anc90cv.front');
   if(pc&&cc&&cv){const L=parseFloat(cv.style.left)||0,Tp=parseFloat(cv.style.top)||0,mx=L+(cc[0]+cs.shift)/2,my=Tp+(cc[1]+(cs.dy||0))/2;
    const dx=pc[0]-mx,dy=pc[1]-my;if(Math.abs(dx)<14&&Math.abs(dy)<14){f.x99.dx=dx;f.x99.dy=dy;}}}
  const X=f.x99;X.a=cs.a;   /* no time lag: a slower fade would leave the photo over the clay at the mouth */
  const k=1-sm(X.a);cs.shift+=2*X.dx*k;cs.dy=(cs.dy||0)+2*X.dy*k;
  if(!fading&&(X.a<=0||X.a>=1))f.x99=null;
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
   const cs=caveState(el,cave,face,scl,mode);if(cs)xfade99(tank,el,f,cs,dt);   /* V17.99 */
   if(cs){let t=TK.get(tank);if(!t){t={};TK.set(tank,t);}t.m=cs.hide?null:cs;if(cs)cs.rc=rc97(el);t.at=now;
    const a=cs.hide?1:cs.a;el.style.setProperty('opacity',(1-a).toFixed(3),'important');f.hid=1;f.df=face;f.turn=null;f.x=+el.dataset.ancX;f.vx=0;f.mv=0;
    const c=el.querySelector(':scope>canvas.anc90c');if(c)c.style.display='none';fade(tank,el,1);return;}
  }
  f.x99=null;   /* V17.99: outside the cave drawing - the next hand-over measures afresh */
  if(f.hid){f.hid=0;el.classList.remove('anc90hid');el.style.setProperty('opacity','1','important');}
  const glass=clamp(parseFloat(el.style.getPropertyValue('--anc-glass'))||(s&&s.glass)||0,0,1);
  /* never drawn crawling backwards: on the sand a clear, sustained movement decides the facing (head first) */
  const x=+el.dataset.ancX,dx=Number.isFinite(x)&&Number.isFinite(f.x)&&dt>0&&dt<.2?x-f.x:0;f.x=x;   /* no velocity across a gap */
  f.vx=(f.vx||0)+((dt>0?dx/dt:0)-(f.vx||0))*Math.min(1,dt*6);
  const th=Math.max(2,9*scl),opp=glass<.3&&!blocked&&!TRANS97[mode]&&Math.abs(f.vx)>th&&Math.sign(f.vx)!==face;f.ot=opp?(f.ot||0)+dt:0;   /* thresholds scale with the fish: young hop slowly */
  if(glass<.3&&!blocked&&!TRANS97[mode]){if(f.ot>(scl<.8?.3:.6))f.mv=Math.sign(f.vx);   /* young react quicker (short hops) */else if(Math.abs(f.vx)<th/3)f.mv=0;else if(f.mv&&Math.sign(f.vx)!==f.mv)f.mv=0;}else f.mv=0;   /* V17.99 (owner: turns flat): the corner moves of attach/detach slide the body, they are not walking - they flipped him flat */
  /* V17.92 turn: the old turn's own timer (s.turn, during which the fish stays put) or a facing-follow turn of our own */
  const T=Math.max(.5,window.ancTurnSecV1789||1),TF=Math.min(T,1);let tu=null;   /* V17.95: TF = facing-follow turns (the fish keeps moving) stay short */
  if(f.df==null)f.df=face;
  const tr97=glass>.02||TRANS97[mode];                      /* V17.98: no 3D turn while going onto / off the glass (it was cut after a few frames: the fish vanished, side frames over the belly view) */
  if(f.wf!==(f.mv||face)){f.wf=f.mv||face;f.wt=0;}else f.wt=(f.wt||0)+dt;   /* how long the wanted facing has held */
  if(s&&s.turn&&!tr97){tu={u:clamp(s.turn.t/T,0,1),from:s.turn.from<0?-1:1,to:s.turn.to<0?-1:1};f.df=tu.to;f.turn=null;}
  else{
   const wantF=f.mv||face;
   if(tr97){f.df=wantF;f.turn=null;}
   else{
    if(!f.turn&&f.df!==wantF&&f.wt>.25)f.turn={from:f.df,to:wantF,t:0};
    if(f.turn&&f.turn.to!==wantF&&f.wt>.25)f.turn={from:f.turn.to,to:f.turn.from,t:Math.max(0,TF-f.turn.t)};   /* reverses smoothly */
    if(f.turn){f.turn.t+=dt;tu={u:clamp(f.turn.t/TF,0,1),from:f.turn.from,to:f.turn.to};if(f.turn.t>=TF){f.df=f.turn.to;f.turn=null;tu=null;}}
   }
  }
  const setSign=sg=>{if(m)el.style.setProperty('transform',tr.replace(/scaleX\([^)]*\)/,'scaleX('+sg+')'),'important');};   /* no flat squash */
  const rot=/rotate\(([-\d.e]+)deg\)/.exec(tr),tilt=rot?Math.abs(+rot[1]):0;
  if(!tu||tu.from===tu.to||tilt>10){setSign(tu&&tilt>10?(tu.u<.5?tu.from:tu.to):f.df);oldDraw(tank,el,f);return;}   /* 3D U-turn only when level on the sand */
  /* V17.95 pivot turn (replaces the V17.94 walking U-turn, which walked 39 px out and back = 6.2 px/frame): the fish turns
     almost on the spot (render_turn3.py: belly down, pectorals spread, gentle curve, head away, tail sweeping toward the
     viewer); the photo drawing cross-fades in place over the first/last 15 % */
  const u=tu.u,kf=24*u,k=Math.min(24,Math.floor(kf)),k2=Math.min(24,k+1),mix=kf-k,a3=u<.15?u/.15:u>.85?(1-u)/.15:1,sg=u<.5?tu.from:tu.to;
  setSign(sg);el.style.setProperty('clip-path','none','important');el.classList.add('anc90');fade(tank,el,1-a3);
  if(f.tx94){f.tx94=0;el.style.removeProperty('translate');}
  const c=turnCanvas(el,sex),g=c.getContext('2d');c.style.display='block';g.clearRect(0,0,480,220);
  c.style.translate='none';
  const AT97=recol97(ATL.T,rc97(el)),mir=(tu.from<0)!==(sg<0);blit(g,AT97,sex+'_turn'+String(k).padStart(2,'0'),mir,a3,220);if(mix>.02&&k2!==k)blit(g,AT97,sex+'_turn'+String(k2).padStart(2,'0'),mir,a3*mix,220);   /* right->left as rendered, left->right mirrored */
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
   if(m){const w=1.5*Math.sin(now/1000*1.15+(el.dataset.fishId||'').length);   /* V17.99: was 3.5 deg - the whole body rocked; the jaws do the rasping now */el.style.setProperty('transform',tr.replace(m[0],'rotate('+(+m[1]+w).toFixed(2)+'deg)'),'important');}
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
 /* ================= V17.95 BRISTLENOSE MOVEMENT (owner picked 1-3; ref. youtube B7RksQ1xU18) =================
    1. DARTS (0:22.3): now and then an adult on the sand bursts forward off the bottom - ~0.18 s to a peak of 1.8 body
       lengths/s, then a decaying glide (lifted, tail beating, via the V17.89 swim flags) and it settles. One roll per trip
       (25 %; a wander trip is set to 1-1.4 body lengths, a walk to the glass keeps its target; the burst lasts <= 1.6 s,
       then the old crawl takes over) + a timer every ~1-2.5 min from grazing/resting (pivots first if the room is behind), only straight
       ahead with room (never across the cave, never into a wall). Intended exception to 3 px/frame.
    2. LONG FLAT RESTS (0:09-0:14, 1:04-1:08, 1:28-1:32): after a trip an adult rests more often (30 % of grazes become
       rests) and longer (6-15 s x day/night activity), dorsal folded flat, no tail sway.
    3. HEAD-DOWN RASPING (0:43-1:02): grazing sessions last 10-20 s, rasp phases 3-6 s, the creep is slower; while rasping
       (or on a wafer) the body tilts head-down up to 4 deg (owner: 11 lifted the tail far too high) around the snout (the snout stays on the sand, the tail rises).
    Switch: window.ANC95=false. */
 const ACT95=()=>typeof ancActivityScaleV17==='function'?ancActivityScaleV17():1;
 const FAN95={'fanning':1,'cave-in':1,'cave-flip':1,'cave-peek':1,'cave-guard':1,'cave-exit':1,'cave-enter':1,'cave-approach':1,'breeding-display':1};
 const sandOk95=s=>s&&s.surface==='substrate'&&!s.atWall&&!s.transition&&!(s.glass>.02)&&!FAN95[s.mode];
 const adult95=s=>sandOk95(s)&&!s.young&&!s.cavePhase&&!s.fight96;
 function room95(s,fc){                                    /* free sand in direction fc (walls 70 px, the cave 10 px) */
  fc=fc||(s.face<0?-1:1);const tk=document.getElementById(s.tankId),W=tk&&tk.clientWidth||960,cv=s.cave89;
  let room=fc>0?W-70-s.x:s.x-70;
  if(cv){if(s.x>=cv[0]-10&&s.x<=cv[1]+10)room=0;else if(fc>0&&s.x<cv[0])room=Math.min(room,cv[0]-10-s.x);else if(fc<0&&s.x>cv[1])room=Math.min(room,s.x-cv[1]-10);}
  return room;
 }
 const sand95=window.ancSandSpeedV1789,D95={roll:0,dart:0,noroom:0,trips:0};
 if(sand95)window.ancSandSpeedV1789=function(s,d,thrust,dt,scale,key){
  if(key==null)key=s.tx;
  const trip=s.mode==='move'||s.mode==='toWall';            /* toWall: the walk to the glass, most of the long trips */
  if(window.ANC95!==false&&trip&&adult95(s)&&!s.turn&&thrust>0&&s.dk95!==key&&!(s.dart95&&s.dart95.key===key)&&(key-s.x)*(s.face<0?-1:1)>0){   /* rolled once it faces the target (after any turn) */
   s.dk95=key;D95.trips++;                                  /* one roll per trip (or a dart the timer below asked for) */
   if(s.force95===key||Math.random()<.25){D95.roll++;
    const BL=Math.max(12,112*scale),fc=s.face<0?-1:1,room=room95(s);
    if(s.mode==='toWall'){if(d>1.6*BL&&(key-s.x)*fc>0&&Math.abs(key-s.x)<=room+70){s.dart95={key,t:0,BL};D95.dart++;}else D95.noroom++;}
    else if(room>1.6*BL&&(key-s.x)*fc>0){key=s.x+fc*Math.min(room,(1+Math.random()*.4)*BL);s.tx=key;d=Math.abs(key-s.x);s.dk95=key;s.dart95={key,t:0,BL};D95.dart++;}else D95.noroom++;
   }
  }
  const v=sand95.call(this,s,d,thrust,dt,scale,key),q=s.dart95;
  if(!q)return v;
  if(q.key!==key||!trip){s.dart95=null;return v;}
  if(q.t>1.6){if(s.bg&&q.sw0!=null)s.bg.swim=q.sw0;s.dart95=null;return v;}   /* burst over: an ordinary crawl again */
  if(s.bg){if(q.sw0==null)q.sw0=!!s.bg.swim;s.bg.swim=true;}                                  /* lifted, tail beating (V17.89 / V17.91), no crawl bouts */
  if(s.turn||!(thrust>0))return v;
  q.t+=dt;const t=q.t,env=t<.18?sm(t/.18):Math.max(.1,Math.exp(-(t-.18)/.45)),brake=Math.min(1,d/(.35*q.BL)+.08);
  return Math.min(1.8*q.BL*env*brake,d/Math.max(dt,.001))*thrust;
 };
 /* rests and grazing sessions: adjusted once, right after the old code ends a trip */
 function life95(tank,el,s,sc,dt,via){
  if(!s)return;
  if(via==='breed'){s.r95=0;s.dart95=null;s.pm95=s.mode;return;}   /* breeder choreography (display, spawning) owns the fish */
  const p=s.pm95;s.pm95=s.mode;
  if(s.dart95&&s.mode!=='move'&&s.mode!=='toWall')s.dart95=null;   /* the trip is over */
  if(window.ANC95===false)return;
  if(p==='move'&&s.mode!=='move'&&adult95(s)){
   if(s.mode==='graze'&&Math.random()<.3){s.mode='rest';s.pm95='rest';}
   if(s.mode==='rest')s.wait=(6+Math.random()*9)*ACT95();
   else if(s.mode==='graze')s.wait=(10+Math.random()*10)*ACT95();
  }
  /* a dart now and then even without a trip: every ~1-2.5 min (slower by day/night activity), from grazing or resting */
  if(adult95(s)&&(s.mode==='graze'||s.mode==='rest')&&!s.turn&&Number.isFinite(s.time)){
   if(s.nd95==null||s.nd95>s.time+400)s.nd95=s.time+(30+Math.random()*60)*ACT95();
   else if(s.time>=s.nd95){
    const BL=112*(sc||1),fc=s.face<0?-1:1,room=room95(s);
    const back=room95(s,-fc),dir=room>1.6*BL?fc:back>1.6*BL?-fc:0,rm=dir===fc?room:back;   /* behind: it pivots first */
    if(dir){s.mode='move';s.pm95='move';s.tx=s.x+dir*Math.min(rm,(1+Math.random()*.4)*BL);s.ty=s.y;s.force95=s.tx;s.wait=0;s.fg=null;s.nudgeV=0;s.raspV=0;s.nd95=s.time+(60+Math.random()*90)*ACT95();}   /* activity is low at night: shorter waits, more darts */
    else s.nd95=s.time+8;                                   /* no room ahead: try again a little later */
   }
  }
  if(s.mode==='graze'&&adult95(s)&&s.fg&&s.fg!==s.fg95){s.fg95=s.fg;const g=s.fg;   /* a new foraging phase from the old code */
   if(g.k==='rasp')g.d=3+Math.random()*3;else if(g.k==='mow')g.v*=.4;else g.v*=.7;}
  /* head-down rasping pose: rotate around the snout (positive = head down, as in V17.89) */
  const on=false;   /* owner 2026-10-17: rasping must not lift the body or tail at all - pose switched off (kept for reference) */
  s.r95=(s.r95||0)+((on&&window.ANC95!==false?1:0)-(s.r95||0))*Math.min(1,(dt||0)*(on?1.1:2));
  if(s.r95<.005||!sandOk95(s)){if(!sandOk95(s))s.r95=0;return;}
  if(s.w95&&el.style.rotate===s.w95)return;               /* V17.89 did not redraw this frame: never add the tilt twice */
  const th=4*s.r95,f=s.face<0?-1:1,rm=/(-?[\d.e]+)deg/.exec(el.style.rotate||''),tm=/^\s*(-?[\d.e]+)px\s+(-?[\d.e]+)px/.exec(el.style.translate||'');
  const r0=rm?+rm[1]:0,tx0=tm?+tm[1]:0,ty0=tm?+tm[2]:0,lift=56*(sc||1)*Math.sin(th*Math.PI/180);
  el.style.setProperty('rotate',(r0+f*th).toFixed(2)+'deg','important');
  el.style.setProperty('translate',tx0.toFixed(2)+'px '+(ty0-lift).toFixed(2)+'px','important');s.w95=el.style.rotate;
 }
 const prev95=window.ancPostV1789;
 window.ancPostV1789=function(tank,el,s,fish,dt,sc,blocked,via){
  prev95.apply(this,arguments);
  try{life95(tank,el,s,sc,dt,via);}catch(e){console.error('AFNICA V17.95 anc movement',e);}
 };
 /* rest: dorsal folded flat, tail still */
 const can95=window.ancCanvasV1791,R95=new WeakMap();
 window.ancCanvasV1791=function(s,dt,sp,move,fan){
  const r=can95.apply(this,arguments);if(!r||!s.fe||window.ANC95===false)return r;
  const fe=s.fe,rest=fe.dataset.ancMode==='rest'&&fe.dataset.ancSurface!=='glass'&&fe.dataset.alert91!=='1';
  let k=R95.get(fe)||0;k+=((rest?1:0)-k)*Math.min(1,dt*(rest?.6:3));R95.set(fe,k);
  if(k>.01){r.fold=r.fold+(1-r.fold)*k;r.sway*=1-k;}
  return r;
 };
 /* ================= V17.96 BRISTLENOSE MALE FIGHTS (owner OK'd plan + still; ref. youtube shorts R6KUQ73HhlI) =================
    Two adult males on the sand of the same tank (not the breeder) may fight: about once per 20 s of being within 2.5
    body lengths, once per 60 s when farther apart (one goes looking for the other) (x4 if one of them held the cave in the last 2 min or a female is near, more at night), one fight
    per tank, 3 min cooldown per pair. The attacker (the cave holder if there is one) walks to the rival - round the rival's
    head first if it came from behind, so it always ends head-to-tail facing the other way; the rival stops once it is
    close. Then both photos fade out and the 3D pair (render_fight.py, both fish in one frame) plays: settle, 3-6 tail
    sweeps, a head shove (1 s, always moving), spine strikes (V17.98, was half a circle); 30 % play it twice. The winner (cave holder > size > health +
    luck) stays and rests, the loser darts away (V17.95 dart). Visual only: health stays with ancTerritorialClashCheck40.
    The pair canvas hangs on the right-facing fish (its scale, never mirrored); fish state only in memory (s.fight96).
    Switch: window.ANC96=false; debug: anc90Debug().F96 */
 const F96={},CD96={},R96={},C96={calls:0,ticks:0,males:0,close:0,starts:0};let N96=0;
 const SEQ96=n=>{const q=[['A',12]];for(let i=0;i<n;i++)q.push(['B',12]);q.push(['C',15],['D',21]);return q;};
 function free96(e){const s=e.s;return e.fish&&e.fish.sex==='M'&&!s.young&&sandOk95(s)&&!s.cavePhase&&!s.turn&&(s.mode==='graze'||s.mode==='rest'||s.mode==='move'||s.fight96);}
 function hold96(s){return s.cave96&&performance.now()-s.cave96<120000;}
 function release96(F,why){
  for(const e of [F.a,F.b]){const s=e.s;s.fight96=null;if(s.wait>100)s.wait=1+Math.random()*2;fade(e.tank,e.el,1);}
  const m=R96[F.tid]||{};for(const e of [F.a,F.b]){const n=m[e.fish.id];if(n&&n.el!==e.el)fade(n.tank,n.el,1);}   /* the tank was redrawn: new elements */
  if(F.cv)F.cv.remove();delete F96[F.tid];CD96[F.key]=performance.now()+(why==='done'?180000:30000);F.end=why;window.__f96last=F;
 }
 function go96(e,tx){const s=e.s;s.mode='move';s.tx=clamp(tx,70,(e.tank.clientWidth||960)-70);s.ty=s.y;s.wait=0;s.dk95=s.tx;s.force95=null;s.fg=null;}
 function stop96(e){const s=e.s;if(s.mode!=='rest'||s.wait<100){s.mode='rest';s.wait=999;s.tx=s.x;s.ty=s.y;s.fg=null;s.nudgeV=0;s.raspV=0;}}
 function start96(tid,a,b,now){
  const BL=112*(a.sc||1),rf=b.s.face<0?-1:1,W=a.tank.clientWidth||960,behind=(a.s.x-b.s.x)*rf<0;
  const F={tid,a,b,key:[a.fish.id,b.fish.id].sort().join('|'),ph:'walk',t:0,leg:2,rf,BL,n:++N96,tmax:10+Math.abs(a.s.x-b.s.x)/20};
  /* V17.99 (owner: "they spin against each other"): no walk round the rival's head and U-turn back (that was the circling).
     If both face the same way and the intruder is behind, the territorial male turns to face him (one pivot), then the
     intruder slides in alongside; otherwise the intruder comes straight in (turning once himself if he must). */
  const fa=a.s.face<0?-1:1;
  if(fa===rf&&behind){F.leg=3;stop96(a);go96(b,b.s.x-rf*6);}else{F.leg=2;go96(a,b.s.x-rf*4);}
  a.s.fight96=b.s.fight96=F;F96[tid]=F;if(F.leg!==3)stop96(b);   /* V17.99: unless he first turns to face the intruder */           /* the rival lies still, as in the clip */
 }
 function step96(F,dt,now){
  const a=F.a,b=F.b,A=a.s,Bs=b.s;F.t+=dt;
  if(!a.el.isConnected||!b.el.isConnected||F.cv&&F.cv.parentElement!==F.R.el||!free96(a)&&!A.turn||!free96(b)&&!Bs.turn){release96(F,'abort');return;}
  if(F.ph==='walk'){if(F.leg===3){if(F.t>F.tmax){release96(F,'timeout');return;}if(Bs.mode==='move'||Bs.turn)return;F.rf=Bs.face<0?-1:1;if(F.rf===(A.face<0?-1:1)){release96(F,'misaligned');return;}F.leg=2;F.t=0;F.tmax=10+Math.abs(A.x-Bs.x)/20;stop96(b);go96(a,Bs.x-F.rf*4);return;}   /* reviewer: no turn happened (wall) -> no pointless walk; fresh walk timer */   /* V17.99: the rival has turned to face him */
   if(Math.abs(A.x-Bs.x)<1.8*F.BL)stop96(b);
   if(F.t>F.tmax){release96(F,'timeout');return;}
   if(A.mode==='move'||A.turn)return;
   const fa=A.face<0?-1:1,fb=Bs.face<0?-1:1;
   if(fa===fb||Math.abs(A.x-Bs.x)>12){release96(F,'misaligned');return;}
   stop96(a);stop96(b);
   const R=fa>0?a:b,O=R===a?b:a,tw=Math.random()<.3;
   F.ph='fight';F.t=0;F.R=R;F.O=O;F.q=SEQ96(3+Math.floor(Math.random()*4)).concat(tw?SEQ96(2+Math.floor(Math.random()*3)).slice(1):[]);
   F.T=F.q.reduce((t,x)=>t+x[1],0)/15;F.nD=0;   /* V17.98: D = spine strikes, nobody changes sides (was a half circle) */F.k1=rc97(R.el);F.k2=rc97(O.el);   /* V17.97: each male in his own colour (fish 1 = the right-facing one) */
   const sc=e=>(hold96(e.s)?2:0)+(+e.fish.age||0)/40+(+e.fish.health||0)/100+Math.random();F.win=sc(a)>=sc(b)?a:b;
   const c=document.createElement('canvas');c.className='anc96p';c.width=600;c.height=260;R.el.appendChild(c);F.cv=c;
   return;
  }
  if(F.ph==='fight'){
   stop96(a);stop96(b);
   const t=Math.min(F.t,F.T),al=Math.min(1,t/.3,(F.T-t)/.3);
   let f=t*15,k=0;while(k<F.q.length-1&&f>=F.q[k][1]){f-=F.q[k][1];k++;}
   const [ph,n]=F.q[k],i=Math.min(n-1,Math.floor(f));F.cur=ph+i;
   F.al=al;for(const e of [a,b])fade(e.tank,e.el,1-al);
   if(F.nD%2&&!F.flipped&&F.t>=F.T-.3){                    /* odd number of half circles: the two swapped sides - the photos fade back in turned round */
    F.flipped=1;for(const e of [a,b]){const q=e.s;q.face=q.face<0?1:-1;q.fv=q.face;q.turn=null;const f=ST.get(e.el);if(f){f.df=q.face;f.turn=null;}}
    const t=F.R;F.R=F.O;F.O=t;F.R.el.appendChild(F.cv);      /* the canvas always hangs on the right-facing fish (never mirrored) */
   }
   const c=F.cv,R=F.R,O=F.O,s=R.sc||1,dx=(O.s.x-R.s.x)/2/s;
   c.style.left=(57.7-150+dx).toFixed(2)+'px';c.style.top=(38.4-84)+'px';
   const g=c.getContext('2d');g.clearRect(0,0,600,260);const nm=ph+String(i).padStart(2,'0');blit(g,recol97(ATL.P,F.k1),'P1_'+nm,false,al);blit(g,recol97(ATL.P,F.k2),'P2_'+nm,false,al);
   if(F.t>=F.T){
    const L=F.win===a?b:a,W2=F.win,fl=L.s.face<0?-1:1,BL=F.BL;release96(F,'done');
    W2.s.mode='rest';W2.s.wait=3+Math.random()*3;
    const ahead=room95(L.s,fl),back=room95(L.s,-fl),dir=ahead>BL?fl:back>BL?-fl:0;
    if(dir){L.s.mode='move';L.s.tx=L.s.x+dir*Math.min(dir===fl?ahead:back,1.4*BL);L.s.ty=L.s.y;L.s.wait=0;L.s.force95=L.s.tx;L.s.dk95=null;}
    else{L.s.mode='rest';L.s.wait=4;}
   }
  }
 }
 function tank96(tid,now,dt){
  const list=Object.values(R96[tid]||{});
  const F=F96[tid];if(F){step96(F,dt,now);return;}
  if(window.ANC96===false||!ready(ATL.P))return;
  C96.ticks++;const males=list.filter(free96);if(males.length>1)C96.males++;const fem=list.filter(e=>e.fish&&e.fish.sex==='F'&&!e.s.young);
  for(let i=0;i<males.length;i++)for(let j=i+1;j<males.length;j++){
   const p=males[i],q=males[j],BL=112*(p.sc||1);
   const far=Math.abs(p.s.x-q.s.x)>2.5*BL;if(!far)C96.close++;   /* far apart: now and then one goes looking for the other */
   const key=[p.fish.id,q.fish.id].sort().join('|');if(CD96[key]&&now<CD96[key])continue;
   const hp=hold96(p.s),hq=hold96(q.s),boost=hp||hq||fem.some(f=>Math.abs(f.s.x-p.s.x)<2.5*BL)?4:1;
   if(window.anc96Force||Math.random()<dt*boost/(far?60:20)*ACT96()){window.anc96Force=0;   /* anc96Force=1: the next free pair fights (tests) */const att=hp?p:hq?q:Math.random()<.5?p:q;C96.starts++;start96(tid,att,att===p?q:p,now);return;}
  }
 }
 const ACT96=()=>{const a=ACT95();return a>0?1/a:1;};   /* night (low activity scale) = more fights */
 function life96(tank,el,s,fish,dt,sc,blocked,via){
  C96.calls++;if(!s||!fish||via!=='main'||!tank||!tank.id||tank.id==='tank-breeder')return;
  if(s.cavePhase||CAVEMODES[s.mode]||s.mode==='cave-approach')s.cave96=performance.now();
  const now=performance.now(),m=R96[tank.id]||(R96[tank.id]={});
  m[fish.id]={tank,el,s,fish,sc,seen:now};
  if(s.fight96&&s.fight96.ph==='fight'&&s.fight96.al!=null)fade(tank,el,1-s.fight96.al);   /* after this fish's own drawing pass */
  if(blocked)return;
  for(const k in m)if(now-m[k].seen>1500)delete m[k];
  if(Object.keys(m)[0]!==String(fish.id))return;            /* once per frame per tank: on the first fish still there */
  tank96(tank.id,now,Math.min(.1,dt||0));
 }
 /* V17.97 glass gait (owner: "it looks like it swims on the glass, not the ancistrus movement"): the V17.89 glide went at a
    steady 12 px/s. A bristlenose on glass inches along: a short push (~0.4-0.8 s, eased), then it grips and rasps
    (~0.5-1.2 s), and again - about 40 % of the old average speed, never a steady slide. Switch: window.ANC97GAIT=false. */
 const glide97=window.ancGlideV1789;
 if(glide97)window.ancGlideV1789=function(s,thrust,gate){
  const v=glide97.apply(this,arguments);if(!(v>0)||window.ANC97GAIT===false){if(s.h97)s.h97.mv0=0;return v;}
  const h=s.h97||(s.h97={t:9,T:1,mv:.5,last:s.time}),dt=Math.max(0,Math.min(.1,(s.time||0)-h.last));h.last=s.time;h.t+=dt;
  if(h.t>=h.T){h.t=0;h.mv=.4+Math.random()*.4;h.T=h.mv+.5+Math.random()*.7;}
  const u=h.t/h.mv,env=u<1?Math.sin(Math.PI*u):0;h.mv0=env;
  return v*env*(h.T/h.mv)*.64;                              /* peak ~18 px/s (0.6 px/frame), average ~5 px/s */
 };
 css.textContent+='html .ancArt .ancSide{opacity:var(--anc-sop,var(--anc-side,1))!important}html .ancArt .ancGlass{opacity:var(--anc-gop,var(--anc-glass,0))!important}';
 const FREE97={graze:1,rest:1,move:1,toWall:1,attach:1,detach:1,wallHold:1,toEdgeG:1,wafer:1};
 const prev96=window.ancPostV1789;
 window.ancPostV1789=function(tank,el,s,fish,dt,sc,blocked,via){
  prev96.apply(this,arguments);
  try{life96(tank,el,s,fish,dt,sc,blocked,via);}catch(e){console.error('AFNICA V17.96 anc fight',e);}
  /* V17.97: the V17.89 cave mask (clip-path polygon) stayed on after the cave cycle - the fish walked around cut off */
  if(s&&FREE97[s.mode]&&el.style.clipPath&&el.style.clipPath!=='none')el.style.removeProperty('clip-path');
  /* V17.97: side <-> belly view: a quick swap in the middle of the glass transition instead of a long double image */
  /* V17.99 (owner: "teleports going onto the glass"): with both fin canvases set up, the side canvas draws the whole roll
     (drawRoll ends on the belly view, pixel-identical) and the belly canvas only shows from .999 - the mid swap hid the side
     drawing at .58 and the fish was invisible for ~1.5 s, then popped in. Now the swap happens at .999, where both match. */
  {const g=parseFloat(el.style.getPropertyValue('--anc-glass'))||0,sc=el.querySelector('.ancSide.finWarp>canvas'),gc=el.querySelector('.ancGlass.finWarpG>canvas');
   /* reviewer: follow what the fin canvases actually show (the side canvas only draws the roll once the belly record is cached) */
   const rl=sc&&gc&&(g>=.999?gc.style.visibility==='visible':sc.style.visibility==='visible');
   const q=clamp((g-.42)/.16,0,1),o=rl?(g>=.999?1:0):q*q*(3-2*q);el.style.setProperty('--anc-gop',o.toFixed(3));el.style.setProperty('--anc-sop',(1-o).toFixed(3));}
 };
 css.textContent+='html .ancArt .ancGlass::after{clip-path:circle(8.6px at 102.4px 35.6px)!important;transform-origin:102.4px 35.6px!important;transform:scale(calc(1.33 - .33*var(--anc-mouth,1)))!important}'+
  'html .ancArt.ancFemale .ancGlass::after{clip-path:circle(6.4px at 104.9px 37.1px)!important;transform-origin:104.9px 37.1px!important;transform:scale(calc(1.17 - .17*var(--anc-mouth,1)))!important}';   /* females: a smaller, milder pulse inside the disc (the faint second ring around it is left alone) */   /* V17.97 rasping on the glass: the oral disc swells up to 10 % (a copy, clipped to the disc, always covering the original); the old squashed oval smeared the tentacles */
 css.textContent+='html .ancArt:not([data-stage91]):not(.ancFemale) .ancGlass::after{clip-path:circle(8.6px at 97.4px 35.6px)!important;transform-origin:97.4px 35.6px!important}'+   /* V17.99: the adult belly cells moved inside the cell (make_sheet.py MDX/FDY); fry/juvenile rows did not */
   'html .ancArt.ancFemale:not([data-stage91]) .ancGlass::after{clip-path:circle(6.4px at 104.9px 35.1px)!important;transform-origin:104.9px 35.1px!important}';
  css.textContent+='canvas.anc96p{position:absolute;width:300px;height:130px;pointer-events:none;transform:none!important}';
 window.anc90Debug=()=>({ATL,ST,TK,Q91,D95,F96,CD96,C96,R96,recol97});
})();
