# V17.92 (owner: "how they turn and how the male enters the cave - make it look more natural"): one-off patch of block90.js.
#  turn: 13 U-turn frames (head swings toward the viewer, body curled, tail follows) driven by the old turn's own timer
#        (s.turn) or the facing-follow; cross-fade photo <-> 3D at both ends, the old shadow fades with the photo.
#  cave: tube drawn alone; the male as two layers (in front of / behind the mouth plane) at the exact sub-pixel position;
#        hand-over with a cross-fade at d -64..-48 (in) and 108..124 (out).
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'block90.js'); s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:90]; s = s.replace(a, b)
def cut(start, end, new):
    global s; i0 = s.index(start); i1 = s.index(end); s = s[:i0] + new + s[i1:]

rep("const ATL={M:{src:'@@ATLAS_M@@',idx:@@INDEX_M@@},F:{src:'@@ATLAS_F@@',idx:@@INDEX_F@@},C:{src:'@@ATLAS_C@@',idx:@@INDEX_C@@},JO:{src:'@@ATLAS_JO@@',idx:@@INDEX_JO@@},JB:{src:'@@ATLAS_JB@@',idx:@@INDEX_JB@@}};   /* JO/JB: juvenile turn frames (V17.91) */",
    "const ATL={T:{src:'@@ATLAS_T@@',idx:@@INDEX_T@@},C2:{src:'@@ATLAS_C2@@',idx:@@INDEX_C2@@}};   /* V17.92: T = U-turn frames (M, F, JO, JB), C2 = tube + the male's cave layers */")
rep("  '.modelFish.anc90 .ancArt{opacity:0!important}.modelFish.anc90.anc90hid{opacity:0!important}'+", "")

cut(" /* ---------- the cave: tube + (male) drawn together ---------- */", " /* ---------- one fish ----------", r''' /* ---------- the cave (V17.92): tube alone + the male in two layers ----------
    _in  = his part behind the mouth plane, shown only through the mouth opening (ellipse 7 x 22.6 at 173.8,72);
    _out = his part in front of it, never hidden by the clay (the camera is on the mouth side). Drawn at the exact
    sub-pixel position (frames every 4 px + the remainder as a shift), so he moves smoothly and never overlaps the clay. */
 const MX=173.8*2,MY=72*2,MRX=7*2,MRY=22.6*2;
 function caveState(el,cave,face,sc,mode){
  const L=parseFloat(cave.style.left)||0,mouth=L+13.8,x=+el.dataset.ancX;
  if(!Number.isFinite(x))return null;
  if(mode==='cave-flip')return {hide:1};                     /* turning round deep inside: nothing shows */
  if(mode==='fanning'){const ph=+el.dataset.fanPh89||0;return {name:'C2_f'+String(((Math.round(ph/(2*Math.PI)*12)%12)+12)%12).padStart(2,'0'),shift:0,a:1};}
  if(face>0){
   const d=(x+56*sc-mouth)/sc;if(d<-64)return null;if(d>146)return {hide:1};
   const q=clamp(Math.round(d/4)*4,-64,144);return {name:'C2_i'+(q<0?'-':'+')+String(Math.abs(q)).padStart(3,'0'),shift:(d-q)*2,a:sm((d+64)/16)};
  }
  const d=(mouth-(x-56*sc))/sc;if(d>124)return null;if(d<-54)return {hide:1};
  const q=clamp(Math.round(d/4)*4,-52,124);return {name:'C2_o'+(q<0?'-':'+')+String(Math.abs(q)).padStart(3,'0'),shift:-(d-q)*2,a:1-sm((d-108)/16)};
 }
 function drawCave(tank,cave,m){
  let t=TK.get(tank);if(!t){t={};TK.set(tank,t);}
  let cv=tank.querySelector('canvas.anc90cv');
  if(!cv){cv=document.createElement('canvas');cv.className='anc90cv';cv.width=680;cv.height=220;tank.insertBefore(cv,tank.querySelector('.modelFish')||null);t.last='';}
  cv.style.left=((parseFloat(cave.style.left)||0)-160)+'px';cv.style.top=((parseFloat(cave.style.top)||0)-30)+'px';
  if(!ready(ATL.C2))return;
  const sig=m&&m.name?m.name+'|'+m.shift.toFixed(2)+'|'+m.a.toFixed(2):'tube';if(t.last===sig)return;
  const g=cv.getContext('2d');g.clearRect(0,0,680,220);
  if(!blit(g,ATL.C2,'C_tube00',false,1))return;t.last=sig;tank.classList.add('anc90cave');   /* old cave hidden once the new one is drawn */
  if(m&&m.name){
   g.save();g.beginPath();g.ellipse(MX,MY,MRX,MRY,0,0,7);g.clip();g.translate(m.shift,0);blit(g,ATL.C2,m.name+'_in',false,m.a);g.restore();
   g.save();g.translate(m.shift,0);blit(g,ATL.C2,m.name+'_out',false,m.a);g.restore();
  }
 }
 function caveLoop(){
  try{
   if(window.ANC90)document.querySelectorAll('.tank').forEach(tank=>{
    const cave=tank.querySelector('.ancBreedingCave');const t=TK.get(tank)||{};
    if(!cave||spawning()&&tank.id==='tank-breeder'){const cv=tank.querySelector('canvas.anc90cv');if(cv){cv.remove();tank.classList.remove('anc90cave');}return;}
    drawCave(tank,cave,t.m&&performance.now()-t.at<250?t.m:null);
   });
   if(!window.ANC90)document.querySelectorAll('canvas.anc90cv').forEach(c=>{c.parentElement&&c.parentElement.classList.remove('anc90cave');c.remove();});
  }catch(e){console.error('AFNICA V17.92 cave',e);}
  requestAnimationFrame(caveLoop);
 }
 requestAnimationFrame(caveLoop);

''')

rep(""" function oldDraw(tank,el,f){
  el.classList.remove('anc90','anc90hid');if(f&&f.hid){f.hid=0;el.style.setProperty('opacity','1','important');}
  const c=el.querySelector(':scope>canvas.anc90c');if(c)c.style.display='none';
  const sh=shadowOf(tank,el);if(sh&&sh.dataset.h90){sh.style.removeProperty('visibility');delete sh.dataset.h90;}
 }""",
""" function fade(tank,el,o){                                  /* the old drawing + its shadow at opacity o */
  const art=el.querySelector('.ancArt');if(art){if(o>=1)art.style.removeProperty('opacity');else art.style.setProperty('opacity',o.toFixed(3),'important');}
  const sh=shadowOf(tank,el);if(sh){if(o>=1)sh.style.removeProperty('opacity');else sh.style.setProperty('opacity',o.toFixed(3),'important');}
 }
 function oldDraw(tank,el,f){
  el.classList.remove('anc90','anc90hid');if(f&&f.hid){f.hid=0;el.style.setProperty('opacity','1','important');}
  const c=el.querySelector(':scope>canvas.anc90c');if(c)c.style.display='none';
  fade(tank,el,1);
 }""")

cut("  /* cave: the male is drawn inside the tube frame */", " const prev=window.ancPostV1789;", r'''  /* cave (adult male): drawn by the cave canvas; his own element fades out as the cave layers fade in */
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
  if(!tu||tu.from===tu.to){setSign(f.df);oldDraw(tank,el,f);return;}
  /* the U-turn: 3D frames, cross-faded with the photo drawing at both ends */
  const u=tu.u,k=Math.round(12*u),a3=u<.12?u/.12:u>.88?(1-u)/.12:1,sg=u<.5?tu.from:tu.to;
  setSign(sg);el.style.setProperty('clip-path','none','important');el.classList.add('anc90');fade(tank,el,1-a3);
  const c=canvasFor(el,sex),g=c.getContext('2d');c.style.display='block';g.clearRect(0,0,320,180);
  blit(g,ATL.T,sex+'_turn'+String(k).padStart(2,'0'),(tu.from<0)!==(sg<0),a3);   /* right->left as rendered, left->right mirrored; undo the parent's mirror */
 }

''')
rep("  const sex=stg91==='juv'?(art91.dataset.col91==='b'?'JB':'JO'):(fish&&fish.sex==='F'?'F':'M'),atl=ATL[sex];if(!ready(atl)){oldDraw(tank,el,f);return;}",
    "  const sex=stg91==='juv'?(art91.dataset.col91==='b'?'JB':'JO'):(fish&&fish.sex==='F'?'F':'M');if(!ready(ATL.T)){oldDraw(tank,el,f);return;}")
rep("  if(!f){f={a:face>0?0:-180,turn:null};ST.set(el,f);}", "  if(!f){f={df:face,turn:null};ST.set(el,f);}")
open(p, 'w', encoding='utf-8').write(s); print('patched')
