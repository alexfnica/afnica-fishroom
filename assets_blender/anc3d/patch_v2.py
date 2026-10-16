# One-off patch of block90.js for v2 (owner: keep the old animated drawing; 3D only for turns and the cave).
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'block90.js'); s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
i0 = s.index(' /* ---------- one fish ---------- */'); i1 = s.index(' const prev=window.ancPostV1789;')
s = s[:i0] + r''' /* ---------- one fish ----------
    Owner (v2): the old animated drawing must stay (fins stepping, body flex, breathing, mouth rasping on the glass) - it now
    runs on the owner's photos (SHEET). V17.90 draws only what the old system did badly: the TURN (3D yaw frames instead
    of a flat squash) and the CAVE (tube + male rendered together). */
 function shadowOf(tank,el){return tank.querySelector('[data-anc-shadow="'+el.dataset.fishId+'"]');}
 function oldDraw(tank,el,f){
  el.classList.remove('anc90','anc90hid');if(f&&f.hid){f.hid=0;el.style.setProperty('opacity','1','important');}
  const c=el.querySelector(':scope>canvas.anc90c');if(c)c.style.display='none';
  const sh=shadowOf(tank,el);if(sh&&sh.dataset.h90){sh.style.removeProperty('visibility');delete sh.dataset.h90;}
 }
 function drawFish(tank,el,s,fish,dt,sc,blocked,via,cave){
  let f=ST.get(el);
  if(!window.ANC90||(spawning()&&tank.id==='tank-breeder')){oldDraw(tank,el,f);return;}
  const sex=fish&&fish.sex==='F'?'F':'M',atl=ATL[sex];if(!ready(atl)){oldDraw(tank,el,f);return;}
  const tr=el.style.transform||'',m=/scaleX\(([-\d.e]+)\)/.exec(tr),face=s&&s.face!=null?(s.face<0?-1:1):(m&&+m[1]<0?-1:1);
  const scm=/scale\(([-\d.e]+)\)/.exec(tr),scl=scm?+scm[1]:(sc||1),now=performance.now(),mode=el.dataset.ancMode||'';
  if(!f){f={a:face>0?0:-180,turn:null};ST.set(el,f);}
  /* cave: the male is drawn inside the tube frame */
  if(cave&&CAVEMODES[mode]&&!spawning()&&fish&&fish.sex==='M'){
   const name=caveFrame(el,cave,face,scl,mode);
   if(name){let t=TK.get(tank);if(!t){t={};TK.set(tank,t);}t.want=name;t.at=now;el.classList.add('anc90hid');el.style.setProperty('opacity','0','important');f.hid=1;f.a=face>0?0:-180;f.turn=null;return;}
  }
  if(f.hid){f.hid=0;el.classList.remove('anc90hid');el.style.setProperty('opacity','1','important');}
  /* a turn on the sand: yaw 0 = facing right, -180 = facing left, always through -90 (head toward the viewer) */
  const glass=clamp(parseFloat(el.style.getPropertyValue('--anc-glass'))||(s&&s.glass)||0,0,1);
  const target=face>0?0:-180,T=Math.max(.5,window.ancTurnSecV1789||1);
  if(glass>.3){f.a=target;f.turn=null;}
  else{
   if(!f.turn&&f.a!==target)f.turn={from:f.a,to:target,t:0};
   if(f.turn&&f.turn.to!==target)f.turn={from:f.a,to:target,t:0};
   if(f.turn){f.turn.t+=dt;f.a=f.turn.from+(f.turn.to-f.turn.from)*sm(f.turn.t/T);if(f.turn.t>=T){f.a=target;f.turn=null;}}
  }
  if(!f.turn&&!(s&&s.turn&&glass<=.3)){oldDraw(tank,el,f);return;}
  /* the 3D turn frame; the old drawing (and its flat squash) is hidden meanwhile */
  el.classList.add('anc90');
  if(m)el.style.setProperty('transform',tr.replace(/scaleX\([^)]*\)/,'scaleX(1)'),'important');
  el.style.setProperty('clip-path','none','important');
  const sh=shadowOf(tank,el);if(sh&&!sh.dataset.h90){sh.style.setProperty('visibility','hidden');sh.dataset.h90='1';}
  const c=canvasFor(el,sex),g=c.getContext('2d');c.style.display='block';g.clearRect(0,0,320,180);
  const a=-f.a;let name,mirror;
  if(a<=90){name=sex+'_yaw'+String(Math.round(a/15)*15).padStart(2,'0');mirror=false;}
  else{name=sex+'_yaw'+String(Math.round((180-a)/15)*15).padStart(2,'0');mirror=true;}
  blit(g,atl,name,mirror,1);
 }

''' + s[i1:]
rep("css.textContent='.modelFish.anc90 .ancArt{opacity:0!important}.modelFish.anc90.anc90hid{opacity:0!important}.tank.anc90on [data-anc-shadow]{display:none!important}'+",
    "css.textContent='html .ancArt i{background-image:url('+SHEET+')}'+   /* the old animated drawing runs on the owner's photos */\n  '.modelFish.anc90 .ancArt{opacity:0!important}.modelFish.anc90.anc90hid{opacity:0!important}'+")
rep("""   if(window.ANC90)document.querySelectorAll('.tank').forEach(tank=>tank.classList.toggle('anc90on',!!tank.querySelector('.modelFish.anc90')));   /* old shadows back when no fish is drawn by V17.90 */
   else document.querySelectorAll('canvas.anc90cv').forEach(c=>{c.parentElement&&c.parentElement.classList.remove('anc90cave','anc90on');c.remove();});""",
    """   if(!window.ANC90)document.querySelectorAll('canvas.anc90cv').forEach(c=>{c.parentElement&&c.parentElement.classList.remove('anc90cave');c.remove();});""")
rep(" window.ANC90=true;", """ window.ANC90=true;
 window.ANC3D_V1789=false;                                  /* the V17.89 shader path drew the sprite without the stepping fins; turns are 3D frames now */
 const SHEET='@@SHEET@@';
 try{const P=window.ancDebugV1789&&ancDebugV1789().PFIN,N=@@PFIN_F@@;if(P)for(const k in N)P[k]=N[k];}catch(e){console.error('AFNICA V17.90 fins',e);}   /* the female's fins sit elsewhere on her photo */""")
open(p, 'w', encoding='utf-8').write(s); print('ok')
