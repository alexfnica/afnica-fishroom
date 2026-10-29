/* ===== V17.120 FISH STORE (MVP) =====
   A shop screen: stock your adult fish in 3 display tanks, NPC customers walk in, browse, queue, the clerk nets and bags the fish,
   they pay and leave. Fish live in st.storeFish (never in st.fish/fry), settings in st.store (defaults in ensureStoreV120, called from
   the wrapped ensureHealthState). Switch: window.STORE120=false. Debug: window.storeDebugV120(). Design: docs/STORE_DESIGN.md */
(function(){
'use strict';
if(window.STORE120===undefined)window.STORE120=true;
const W=760,H=480,TX=[110,280,450,620],TW=156,TY=62,TH=104,SPT=4;
const DOOR={x:48,y:352},PAY={x:596,y:384};
const QS=[{x:544,y:406},{x:488,y:418},{x:432,y:430},{x:376,y:442}];
const FCOL={guppy:'#ff9a3c',molly:'#2b2b3a',platy:'#ffb830',xipho:'#ff6a3c',neon:'#4fb4ff',cory:'#c9a46a',anc:'#6b5a3a'};
const PALS=[
 {shirt:'#e8576a',pants:'#33405a',shoe:'#222',skin:'#e8b48a',hair:'#c76b2a',style:'long'},
 {shirt:'#4aa860',pants:'#2b2b3a',shoe:'#f2f2f2',skin:'#d9a07a',hair:'#2a2a2a',style:'short'},
 {shirt:'#e8b83a',pants:'#5a3a6a',shoe:'#333',skin:'#f3d0b0',hair:'#8a5a2a',style:'bun'},
 {shirt:'#6a7de0',pants:'#444',shoe:'#222',skin:'#a8714a',hair:'#1a1a1a',style:'short'},
 {shirt:'#d96ad0',pants:'#2f3f5f',shoe:'#fff',skin:'#8d5a3a',hair:'#111',style:'long'},
 {shirt:'#52b8c9',pants:'#3a3a3a',shoe:'#222',skin:'#f1c9a0',hair:'#d8c06a',style:'short'}];

const PH=[['greet',.9],['net',1.5],['bag',1.5],['hand',.8],['pay',1.0]];
const ST={cust:[],queue:[],pay:null,clerk:{c:null,ph:'idle',t:0,part:null},next:0,last:0,uid:0,sec:0,saveT:0,gen:0,slots:[],els:new Map(),door:false};
const $=id=>document.getElementById(id);

/* ---------- save defaults ---------- */
function ensureStoreV120(){
 if(!st.store||typeof st.store!=='object')st.store={};
 const s=st.store,d={unlocked:true,tanks:3,slotsPerTank:SPT,rep:0,markupPct:115,decor:[],clerks:1,lastSimAt:0,dayNo:0,totalSales:0,totalRevenue:0};
 for(const k in d)if(s[k]===undefined)s[k]=d[k];
 if(!s.day||typeof s.day!=='object')s.day={customers:0,sales:0,revenue:0,upkeep:0,walkouts:0,best:0,rep0:s.rep};
 if(!Array.isArray(st.storeFish))st.storeFish=[];
}
const oldEnsure=window.ensureHealthState;
window.ensureHealthState=function(){const r=oldEnsure.apply(this,arguments);try{ensureStoreV120();}catch(e){console.error('AFNICA store defaults',e);}return r;};

/* ---------- nav tab ---------- */
const oldNav=window.v8Nav;
window.v8Nav=function(a){
 let h=oldNav.apply(this,arguments);
 if(window.STORE120===false)return h;
 try{h=h.replace('repeat(6,1fr)','repeat(7,1fr)').replace(/<\/div>\s*$/,`<button class="${a==='store'?'active':''}" onclick="renderStoreV120()">🏪<span>STORE</span></button></div>`);}catch(e){console.error('AFNICA store nav',e);}
 return h;
};

/* ---------- prices and eligibility ---------- */
function fairV120(f){
 if(typeof f.health!=='number'||!isFinite(f.health))f.health=100;
 let v=sellValueV9(f);if(!isFinite(v))v=1;
 const gm=(window.fullGrownV1763&&fullGrownV1763(f))?1.2:1,fm=Math.max(.7,1-.06*(f.finTorn||0));
 return Math.max(1,Math.round(v*gm*fm));
}
function priceV120(f){return Math.max(1,Math.round(fairV120(f)*(f.storePct||115)/100));}
function eligibleV120(f){return !f.dead&&!f.disease&&S[f.species]&&f.age>=S[f.species].adult&&(f.health==null||f.health>=50)&&!Number.isFinite(f.gestStart)&&!(f.spermBroods>0);}
const repLevel=()=>Math.floor((st.store.rep||0)/20);
function hourF(){const h=window.__afHourOverride!=null?+window.__afHourOverride:new Date().getHours();return h<8||h>=22?0:(h>=10&&h<19?1.3:.7);}
function cap(){return st.store.tanks*st.store.slotsPerTank;}
function sname(f){const sp=S[f.species];return sp?sp.name:f.species;}
function sicon(f){const sp=S[f.species];return sp&&sp.icon?sp.icon:'🐟';}

/* ---------- customers: profile, choice ---------- */
function newProfile(){
 const r=Math.random(),type=r<.5?'beginner':r<.7?'collector':'shopper';
 const budget=type==='beginner'?25+Math.random()*65:type==='collector'?150+Math.random()*550:0;
 return {type,budget:Math.round(budget),sense:.95+Math.random()*.45};
}
function evaluate(p){
 const lvl=repLevel();let best=null,bs=-1,saw=false;
 for(const f of st.storeFish){
  if(f._res120||(f.health!=null&&f.health<50))continue;
  const g=gradeV10(f),rar=rarityV9(f.species);
  const match=p.type==='beginner'?true:p.type==='collector'?(rar!=='common'||g.rank>=3):false;
  if(!match)continue;saw=true;
  const price=priceV120(f),fair=fairV120(f);
  if(price>p.budget||price>fair*p.sense*(1+.15*lvl))continue;
  const sc=p.type==='collector'?g.rank*10+fair/price:fair/price+Math.random()*.3;
  if(sc>bs){bs=sc;best=f;}
 }
 return {fish:best,reason:best?'':(saw?'expensive':'nomatch')};
}
function sellV120(f,silent){
 const i=st.storeFish.indexOf(f);if(i<0)return 0;
 const price=priceV120(f),g=gradeV10(f),nm=sname(f),s=st.store;
 st.storeFish.splice(i,1);
 st.coins+=price;st.totalSold=(st.totalSold||0)+1;
 s.totalSales++;s.totalRevenue+=price;s.day.sales++;s.day.revenue+=price;s.day.best=Math.max(s.day.best,price);
 s.rep=Math.min(100,s.rep+2);
 try{addXPV9(8+g.rank*3);}catch(e){}
 if(!silent){try{sfxV141('coin');}catch(e){}toast(`🪙 Sold ${g.name} ${nm} for ${price} · rep +2`);}
 return price;
}
function walkout(p,reason){
 const s=st.store;if(p.type==='shopper')return;
 s.day.walkouts++;s.rep=Math.max(0,s.rep-(reason==='queue'?3:1));
}

/* ---------- day rollover, upkeep, offline batch ---------- */
function dayCheck(){
 const s=st.store;
 if(!s.dayNo){s.dayNo=st.day;s.day.rep0=s.rep;return;}
 let n=0;
 while(s.dayNo<st.day&&n<10){
  const dd=s.day;
  if(st.storeFish.length){
   const cost=2*st.storeFish.length;
   if(st.coins>=cost){st.coins-=cost;dd.upkeep=cost;}else st.storeFish.forEach(f=>{f.health=Math.max(10,(f.health==null?100:f.health)-5);});
   st.storeFish.forEach(f=>{if(st.day-(f.storeSince||st.day)>=7)f.health=Math.max(10,(f.health==null?100:f.health)-3);});
  }
  s.lastSummary=Object.assign({},dd,{day:s.dayNo,rep1:s.rep,shown:false});
  s.dayNo++;s.day={customers:0,sales:0,revenue:0,upkeep:0,walkouts:0,best:0,rep0:s.rep};n++;
 }
 if(s.dayNo<st.day)s.dayNo=st.day;
}
function batchSim(){
 const s=st.store,now=Date.now(),out={n:0,sales:0,revenue:0};
 const el=s.lastSimAt?(now-s.lastSimAt)/1000:0;
 s.lastSimAt=now;
 if(el<60||!st.storeFish.length)return out;
 const n=Math.min(40,Math.floor(el/(30/(1+.15*repLevel()))*.58)),rep0=s.rep;
 for(let i=0;i<n&&st.storeFish.length;i++){
  const p=newProfile();s.day.customers++;out.n++;
  const r=evaluate(p);
  if(r.fish){out.revenue+=sellV120(r.fish,true);out.sales++;}else walkout(p,r.reason);
 }
 if(s.rep<rep0-5)s.rep=rep0-5;
 return out;
}
function summaryHTML(m){
 return `<div style="text-align:left;line-height:1.7">Customers: <b>${m.customers}</b><br>Sales: <b>${m.sales}</b> · 🪙 <b>${m.revenue}</b><br>Upkeep paid: 🪙 ${m.upkeep}<br>Walked out: ${m.walkouts}<br>Best sale: 🪙 ${m.best}<br>Reputation: ${m.rep0} → ${m.rep1}</div>`;
}

/* ---------- drawing a person ---------- */
function personSVG(p){
 const back=p.style==='long'?`<rect x="-18" y="-106" width="12" height="40" rx="6" fill="${p.hair}"/>`:'';
 const bun=p.style==='bun'?`<circle cx="-8" cy="-115" r="7" fill="${p.hair}"/>`:'';
 const arm=`<rect x="-4" y="-2" width="8" height="30" rx="4" fill="${p.skin}"/><rect x="-4.5" y="-3" width="9" height="15" rx="4" fill="${p.shirt}"/><circle cx="0" cy="28" r="4.5" fill="${p.skin}"/>`;
 const bag=`<g class="bag" visibility="hidden"><path d="M-9 30 q-3 14 2 24 q9 5 18 0 q5 -10 2 -24z" fill="#9ee2f7" fill-opacity=".6" stroke="#e8fbff" stroke-width="1.2"/><path d="M-8 40 q8 -3 16 0 l1 10 q-9 5 -18 0z" fill="#2fb5d6" fill-opacity=".5"/><path class="bf" d="M-5 46 q5 -5 11 0 q-5 5 -11 0z M6 46 l5 -3 v6z" fill="#ff9a3c"/></g>`;
 const net=`<g class="net" visibility="hidden"><line x1="0" y1="28" x2="0" y2="64" stroke="#c9d3d8" stroke-width="2.5"/><ellipse cx="0" cy="72" rx="11" ry="9" fill="#9ee2f7" fill-opacity=".25" stroke="#c9d3d8" stroke-width="2"/><path class="nf" visibility="hidden" d="M-6 72 q6 -6 12 0 q-6 6 -12 0z M6 72 l5 -3 v6z" fill="#ff9a3c"/></g>`;
 return `<svg viewBox="-40 -130 80 134" width="80" height="134" class="ps"><ellipse cx="0" cy="0" rx="21" ry="5" fill="#000" opacity=".25"/><g class="all">
 <g class="aL">${arm}</g>
 <g class="lL"><rect x="-4" y="-1" width="8" height="36" rx="4" fill="${p.pants}"/><ellipse cx="2" cy="36" rx="8" ry="4" fill="${p.shoe}"/></g>
 <g class="lR"><rect x="-4" y="-1" width="8" height="36" rx="4" fill="${p.pants}"/><ellipse cx="2" cy="36" rx="8" ry="4" fill="${p.shoe}"/></g>
 <rect x="-15" y="-82" width="30" height="48" rx="13" fill="${p.shirt}"/>${p.badge?'<rect x="-8" y="-66" width="16" height="9" rx="2" fill="#fff"/><rect x="-5" y="-63" width="10" height="2" fill="#2f9be0"/>':''}
 ${back}<g class="hd"><circle cx="0" cy="-96" r="15" fill="${p.skin}"/><path d="M-16 -96 Q-17 -115 0 -115 Q17 -115 16 -96 Q9 -106 0 -106 Q-9 -106 -16 -96Z" fill="${p.hair}"/>${bun}
  <circle cx="6" cy="-96" r="2.3" fill="#222"/><circle cx="12" cy="-96" r="2.3" fill="#222"/><path d="M7 -88 Q10 -85 13 -88" stroke="#a33" stroke-width="2" fill="none" stroke-linecap="round"/></g>
 <g class="aR">${arm}${bag}${net}</g></g></svg>`;
}
function mkPerson(p,z){
 const d=document.createElement('div');d.className='st120p';d.innerHTML=personSVG(p)+'<div class="bub"></div>';
 const q=c=>d.querySelector(c);
 return {el:d,svg:q('svg'),all:q('.all'),aL:q('.aL'),aR:q('.aR'),lL:q('.lL'),lR:q('.lR'),hd:q('.hd'),bag:q('.bag'),net:q('.net'),nf:q('.nf'),bf:q('.bf'),bub:q('.bub')};
}
function bubble(c,txt,sec){c.parts.bub.textContent=txt;c.parts.bub.classList.add('on');c.bubT=sec||2.2;}
/* realistic customers: a rendered full-body cut-out (assets_blender/store/people, made with cut_people.py), walked with a bob / rock / squash instead of limbs */
/* walk rigs (walk120.js), one per sprite image, built once the image has decoded; pairs / failures keep the bob */
const RIG=new Map();
function rigFor(src){let e=RIG.get(src);if(!e){e={R:null};RIG.set(src,e);const im=new Image();im.onload=()=>{try{e.R=window.rigSpriteV120?window.rigSpriteV120(im):null;}catch(er){console.error('AFNICA store walk rig',er);}};im.src=src;}return e;}
function mkSprite(src,asp){
 const wide=asp>.62;
 const d=document.createElement('div');d.className='st120p sp'+(wide?' wide':'');
 d.innerHTML=`<div class="sprw"><img src="${src}" alt=""><canvas class="wk" width="200" height="320"></canvas><svg class="bagh" width="22" height="28" viewBox="0 0 22 28"><path d="M3 4 q-3 8 1 18 q7 5 14 0 q4 -10 1 -18z" fill="#9ee2f7" fill-opacity=".65" stroke="#e8fbff" stroke-width="1.2"/><path d="M4 4 q7 -8 13 0" stroke="#e8fbff" stroke-width="1.6" fill="none"/><path class="bf" d="M6 15 q5 -5 10 0 q-5 5 -10 0z" fill="#ff9a3c"/></svg></div><div class="bub"></div>`;
 const w=d.querySelector('.sprw'),bag=d.querySelector('.bagh');
 if(wide){bag.style.left='96px';bag.style.top='96px';}
 return {spr:true,wide,rad:wide?95:40,rig:wide?null:rigFor(src),cv:d.querySelector('.wk'),el:d,svg:w,img:w.firstChild,bagEl:bag,bag:{setAttribute(a,v){bag.style.display=v==='visible'?'block':'none';}},bf:d.querySelector('.bf'),bub:d.querySelector('.bub')};
}
function poseP(c,t){
 const P=c.parts,mv=Math.min(1,c.speed/30),sw=Math.sin(c.phase)*mv,sd=c.seed;
 if(P.spr){
  const bob=-Math.abs(Math.sin(c.phase))*2.6*mv+Math.sin(t*2+sd)*.5*(1-mv);
  let rock=Math.sin(c.phase)*2.4*mv,sq=1+Math.abs(Math.sin(c.phase))*.012*mv+Math.sin(t*1.6+sd)*.004*(1-mv);
  if(c.state==='look'){rock=-3+Math.sin(t*3+sd)*(c.pointing?3:1);}
  const R=P.rig&&P.rig.R;
  if(R){
   /* real walk: legs swing from the hip, distance-driven so the planted foot does not slide */
   if(P.img.style.display!=='none'){P.img.style.display='none';P.cv.style.display='block';}
   const g=P.cv.getContext('2d'),k=150/R.h,m=Math.min(1,c.speed/25);
   g.setTransform(2,0,0,2,0,0);g.clearRect(0,0,100,160);g.translate(50,156);
   window.drawWalkV120(g,R,(c.dist||0)/(window.cycleLenV120(R)*k),m,k);
   const lean=c.state==='look'?-2+Math.sin(t*3+sd)*(c.pointing?1.5:.5):0;
   P.cv.style.transform=`rotate(${lean.toFixed(2)}deg)`;
  }else P.img.style.transform=`translateX(-50%) translateY(${bob.toFixed(2)}px) rotate(${rock.toFixed(2)}deg) scaleY(${sq.toFixed(4)})`;
  P.bag.setAttribute('visibility',c.bagged?'visible':'hidden');if(c.bagged)P.bagEl.style.transform=`translateY(${bob.toFixed(2)}px)`;
  return;
 }
 let lL=sw*26,lR=-sw*26,aL=-sw*20,aR=sw*20,hd=0;
 const bob=-Math.abs(Math.sin(c.phase))*2.4*mv+Math.sin(t*2+sd)*.7*(1-mv);
 if(!mv){aL=Math.sin(t*1.6+sd)*2+3;aR=Math.sin(t*1.6+sd+1)*2-3;}
 if(c.state==='look'){hd=-9;if(c.pointing)aR=-(108+Math.sin(t*4+sd)*5);}
 if(c.bagged){aR=-22+sw*6;P.bag.setAttribute('visibility','visible');}
 else P.bag.setAttribute('visibility','hidden');
 if(c.state==='wait'||c.state==='atpay')hd=Math.sin(t*1.3+sd)*3;
 P.lL.setAttribute('transform',`translate(-5 -38) rotate(${lL})`);P.lR.setAttribute('transform',`translate(5 -38) rotate(${lR})`);
 P.aL.setAttribute('transform',`translate(-15 -74) rotate(${aL})`);P.aR.setAttribute('transform',`translate(15 -74) rotate(${aR})`);
 P.hd.setAttribute('transform',`rotate(${hd} 0 -82)`);P.all.setAttribute('transform',`translate(0 ${bob})`);
}
/* the clerk is the owner's own character: a cut-out of his YouTube outro render (real shirt print), swayed / leaned per phase, net as an overlay */
function mkOwner(){
 const src=(window.ST120_LOGO||{}).owner||'';
 const d=document.createElement('div');d.className='own';
 d.innerHTML=`<div class="ob"><img src="${src}" alt=""></div><div class="oh"><img src="${src}" alt=""><i class="lid" style="left:31px;top:25.4px"></i><i class="lid" style="left:46px;top:25.4px"></i></div><svg class="onet" viewBox="0 0 60 80" width="60" height="80"><g class="ng"><line x1="30" y1="76" x2="30" y2="26" stroke="#c9d3d8" stroke-width="3"/><ellipse cx="30" cy="16" rx="13" ry="11" fill="#9ee2f7" fill-opacity=".3" stroke="#c9d3d8" stroke-width="2.5"/><path class="nf" visibility="hidden" d="M23 16 q7 -7 14 0 q-7 7 -14 0z M37 16 l6 -4 v8z" fill="#ff9a3c"/></g></svg><div class="bub"></div>`;
 return {el:d,ob:d.querySelector('.ob'),oh:d.querySelector('.oh'),lids:d.querySelectorAll('.lid'),net:d.querySelector('.onet'),ng:d.querySelector('.ng'),nf:d.querySelector('.nf'),bub:d.querySelector('.bub'),nextBlink:2,blinkT:-9};
}
function poseClerk(t){
 const K=ST.clerk,P=K.parts;if(!P)return;
 /* idle: breathing, a slow head sway, a blink every 2.5-6 s */
 let bx=0,by=0,br=0,bs=1+.007*Math.sin(t*1.6);
 let hr=Math.sin(t*.7)*1.4+Math.sin(t*1.9)*.5,hy=Math.sin(t*1.6)*.4,hx=0,net=false,nf=false,nr=0;
 const pp=K.part||0;
 if(K.c){
  if(K.ph==='greet'){by=-1.8*Math.abs(Math.sin(t*7));hr=5+Math.sin(t*8)*2;}
  else if(K.ph==='net'){net=true;bx=-3;br=-2.5;hr=-5;hy=1;nr=-40+Math.sin(pp*Math.PI*2)*18;nf=pp>.55;}
  else if(K.ph==='bag'){bs=1.02;hr=3;hy=1.6;}
  else if(K.ph==='hand'){bx=3*Math.sin(pp*Math.PI);br=2;hr=4;}
  else if(K.ph==='pay'){hr=Math.sin(t*10)*2;hy=Math.abs(Math.sin(t*10))*1.2;}
 }
 if(t>=P.nextBlink){P.blinkT=t;P.nextBlink=t+2.5+Math.random()*3.5;}
 const u=(t-P.blinkT)/.16,cl=u>=0&&u<1?Math.sin(u*Math.PI):0;
 P.lids.forEach(l=>{l.style.opacity=cl>0?1:0;l.style.transform=`scaleY(${cl.toFixed(2)})`;});
 P.ob.style.transform=`translate(${bx.toFixed(2)}px,${by.toFixed(2)}px) rotate(${br}deg) scaleY(${bs.toFixed(4)})`;
 P.oh.style.transform=`translate(${(bx+hx).toFixed(2)}px,${(by+hy).toFixed(2)}px) rotate(${hr.toFixed(2)}deg)`;
 P.net.style.opacity=net?1:0;P.ng.setAttribute('transform',`rotate(${nr} 30 76)`);P.nf.setAttribute('visibility',nf?'visible':'hidden');
}

/* ---------- scene ---------- */
function sceneHTML(){
 const s=st.store;let tanks='';
 for(let i=0;i<s.tanks;i++){
  tanks+=`<div class="tk" style="left:${TX[i]}px;top:${TY}px"><div class="wt"></div><div class="sd"></div>
   <svg class="pl" viewBox="0 0 40 40" style="left:6px"><path d="M20 40Q14 22 18 4Q26 20 22 40Z M24 40Q32 24 36 12Q34 30 28 40Z" fill="#3f9f3a"/></svg>
   <svg class="pl" viewBox="0 0 40 40" style="right:4px"><path d="M20 40Q12 24 14 8Q24 22 22 40Z M24 40Q34 28 34 16Q32 32 28 40Z" fill="#3f9f3a"/></svg>
   <div class="fb" id="st120fb${i}"></div><div class="gl"></div><div class="lt"></div></div><div class="tg" id="st120tg${i}" style="left:${TX[i]}px"></div>`;
 }
 const sx=TX[0]-10,sw=TX[s.tanks-1]+TW+10-sx;
 return `<div class="st120wrap" id="st120wrap"><div class="st120stage" id="st120stage">
 <svg class="bg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><defs>
  <linearGradient id="s120w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c4a5e"/><stop offset="1" stop-color="#13394b"/></linearGradient>
  <linearGradient id="s120f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a5a35"/><stop offset="1" stop-color="#5d3a20"/></linearGradient></defs>
  <rect width="${W}" height="312" fill="url(#s120w)"/><rect y="236" width="${W}" height="76" fill="#235d73"/><rect y="232" width="${W}" height="6" fill="#0f3344"/>
  <rect y="312" width="${W}" height="168" fill="url(#s120f)"/><rect y="308" width="${W}" height="6" fill="#2a1a0c"/>
  <g stroke="#3d2411" stroke-opacity=".5" stroke-width="2"><path d="M0 366H${W}M0 424H${W}"/><path d="M120 312V366M360 312V366M600 312V366M240 366V424M480 366V424M60 424V480M300 424V480M540 424V480"/></g>
  <rect x="${sx}" y="${TY+TH+4}" width="${sw}" height="12" rx="3" fill="#5a3a1d"/>
  <rect x="250" y="3" width="260" height="56" rx="10" fill="#fff" stroke="#3bc8f5" stroke-width="3"/>
  ${(window.ST120_LOGO&&window.ST120_LOGO.icon)?`<image href="${window.ST120_LOGO.icon}" x="258" y="6" width="50" height="50"/><image href="${window.ST120_LOGO.word}" x="313" y="8" width="190" height="46" preserveAspectRatio="xMidYMid meet"/>`:'<text x="380" y="38" text-anchor="middle" font-size="18" font-weight="900" fill="#092638" letter-spacing="2" font-family="Inter,system-ui,Arial,sans-serif">AFNICA FISHROOM</text>'}
  <rect x="6" y="96" width="86" height="250" rx="5" fill="#2a1a0c"/><rect x="14" y="104" width="70" height="234" fill="#bdeaff" opacity=".9"/><path d="M14 104L84 104L14 220Z" fill="#fff" opacity=".4"/>
  <rect x="2" y="344" width="94" height="8" rx="3" fill="#3a2a14"/>
  <rect x="640" y="56" width="92" height="76" rx="5" fill="#0c1e28" stroke="#7a5a30" stroke-width="3"/><rect x="646" y="62" width="80" height="64" fill="#0d7893"/><path d="M660 100 q14 -14 30 0 q-14 14 -30 0z M690 100 l12 -8 v16z" fill="#ffb830"/><text x="686" y="120" text-anchor="middle" font-size="8" font-weight="800" fill="#d9f6ff" font-family="Inter,system-ui,Arial,sans-serif">FISH CARE TIPS</text>
 </svg>
 <div class="dr" id="st120door"></div>
 ${tanks}
 <div class="clk" id="st120clerk"></div>
 <div class="cnt"><svg viewBox="0 0 164 100" width="164" height="100"><rect x="0" y="0" width="164" height="14" rx="5" fill="#e8bd7c"/><rect x="4" y="14" width="156" height="86" fill="#9a6538"/><rect x="14" y="26" width="136" height="64" rx="4" fill="#6b4526" opacity=".6"/><text x="82" y="66" text-anchor="middle" font-size="16" font-weight="900" fill="#ffd9a0" opacity=".85" font-family="Inter,system-ui,Arial,sans-serif">PAY HERE</text></svg></div>
 <div class="reg" id="st120reg">🪙 0</div>
 <div class="cbag" id="st120cbag"></div>
 <div class="qm" style="left:${PAY.x-30}px;top:${PAY.y-6}px"></div>
 </div></div>`;
}
const slotXY=i=>[{x:12,y:16},{x:88,y:12},{x:14,y:52},{x:86,y:50}][i];
function syncFish(){
 const s=st.store,list=st.storeFish,seen=new Set();
 list.forEach((f,idx)=>{
  const ti=Math.floor(idx/s.slotsPerTank),si=idx%s.slotsPerTank,fb=$('st120fb'+ti);if(!fb)return;
  let el=ST.els.get(f.id);
  if(!el){el=document.createElement('div');el.className='sf';el.innerHTML=`<div class="d" style="animation-duration:${(5+Math.random()*4).toFixed(1)}s;animation-delay:-${(Math.random()*6).toFixed(1)}s">${dexAvatarHTML(f,46,27)}</div>`;ST.els.set(f.id,el);}
  if(el.parentNode!==fb)fb.appendChild(el);
  const p=slotXY(si);el.style.left=p.x+'px';el.style.top=p.y+'px';
  el.classList.toggle('gone',!!f._net120);seen.add(f.id);
 });
 for(const [id,el] of ST.els)if(!seen.has(id)){el.remove();ST.els.delete(id);}
 for(let i=0;i<s.tanks;i++){
  const tg=$('st120tg'+i);if(!tg)continue;
  const fs=list.slice(i*s.slotsPerTank,(i+1)*s.slotsPerTank).filter(f=>!f._net120);
  if(!fs.length)tg.innerHTML='<b>empty</b>';
  else{const pr=fs.map(priceV120),a=Math.min(...pr),b=Math.max(...pr);tg.innerHTML=`${fs.length} fish<br><b>🪙 ${a===b?a:a+'–'+b}</b>`;}
 }
}

/* ---------- panel ---------- */
function rowHTML(f,mode){
 const g=gradeV10(f),fair=fairV120(f);
 const btns=mode==='shop'
  ?`<button class="btn small blue" onclick="stPrice120('${f.id}',-10)">−10%</button><button class="btn small blue" onclick="stPrice120('${f.id}',10)">+10%</button><button class="btn small" style="background:#8a3a3a" onclick="stReturn120('${f.id}')">RETURN</button>`
  :`<button class="btn small green" onclick="stStock120('${f.id}')">STOCK</button>`;
 const sx=knownSex(f)?(f.sex==='M'?' ♂':f.sex==='F'?' ♀':''):'';
 return `<div class="st120row"><div class="av">${dexAvatarHTML(f,56,34)}</div><div class="in"><b>${sicon(f)} ${sname(f)}${sx}</b> <span class="v10Grade ${g.cls}">${g.name}</span>
  <small>${mode==='shop'?`value 🪙 ${fair} · price <b>🪙 ${priceV120(f)}</b> (${f.storePct||115}%)`:`worth about 🪙 ${Math.round(fair*1.15)} in the store · health ${Math.round(f.health==null?100:f.health)}`}</small></div><div class="ctl">${btns}</div></div>`;
}
function panel(){
 const el=$('st120panel');if(!el)return;
 const s=st.store,d=s.day,lvl=repLevel();
 const elig=[];
 st.fish.forEach(f=>{if(eligibleV120(f))elig.push([f,'main']);});
 st.fry.forEach(f=>{if(eligibleV120(f))elig.push([f,'fry']);});
 el.innerHTML=`<div class="v8panel"><div class="v8head"><b>🏪 YOUR FISH STORE</b><span>★ LEVEL ${lvl}</span></div>
  <div class="st120rep"><i style="width:${s.rep}%"></i></div><div class="meta">Reputation ${s.rep}/100 · higher reputation = more customers and higher prices they accept.</div>
  <div class="meta">Today: <b>${d.customers}</b> customers · <b>${d.sales}</b> sales · 🪙 <b>${d.revenue}</b> · lifetime ${s.totalSales} sales, 🪙 ${s.totalRevenue}</div>
  <div class="meta">Upkeep: 🪙 2 per displayed fish per game day (counted while the store screen is open). Fish unsold for 7+ days get stressed.</div>
  ${st.storeFish.length?'':'<div class="meta" style="color:#ffd24b">Stock some fish below, customers only come when there is something to buy.</div>'}</div>
  <div class="v8panel"><div class="v8head"><b>ON DISPLAY</b><span>${st.storeFish.length}/${cap()}</span></div>${st.storeFish.map(f=>f._res120?`<div class="st120row"><div class="in"><b>${sname(f)}</b> <small>being sold…</small></div></div>`:rowHTML(f,'shop')).join('')||'<div class="meta">Nothing on display.</div>'}</div>
  <div class="v8panel"><div class="v8head"><b>STOCK FROM YOUR TANKS</b><span>${elig.length} ELIGIBLE</span></div><div class="meta">Healthy adult fish from the Main and Fry tanks (not pregnant).</div>${elig.map(x=>rowHTML(x[0],'stock')).join('')||'<div class="meta">No eligible adult fish right now.</div>'}</div>`;
}
function coinsUI(){document.querySelectorAll('.v8money .v8pill').forEach(p=>{if(p.textContent.indexOf('🪙')===0)p.textContent='🪙 '+st.coins;});}
window.stStock120=function(id){
 try{
  if(st.storeFish.length>=cap())return toast('Display tanks are full');
  let src=null,key='main',i=st.fish.findIndex(f=>f.id===id);
  if(i>=0)src=st.fish;else{i=st.fry.findIndex(f=>f.id===id);if(i>=0){src=st.fry;key='fry';}}
  if(!src)return;
  const f=src[i];if(!eligibleV120(f))return toast('Only healthy adult fish can be sold in the store');
  src.splice(i,1);f.storeFrom=key;f.storePct=st.store.markupPct;f.storeSince=st.day;delete f._res120;delete f._net120;delete f._from;
  st.storeFish.push(f);save();syncFish();panel();
 }catch(e){console.error('AFNICA store stock',e);}
};
window.stReturn120=function(id){
 try{
  const i=st.storeFish.findIndex(f=>f.id===id);if(i<0)return;const f=st.storeFish[i];
  if(f._res120)return toast('That fish is being sold right now');
  const order=f.storeFrom==='fry'?[st.fry,st.fish]:[st.fish,st.fry];
  const dst=order.find(a=>a.length<7);if(!dst)return toast('Your tanks are full (7 fish each)');
  st.storeFish.splice(i,1);delete f.storeFrom;delete f.storePct;delete f.storeSince;
  dst.push(f);save();syncFish();panel();
 }catch(e){console.error('AFNICA store return',e);}
};
window.stPrice120=function(id,d){
 const f=st.storeFish.find(x=>x.id===id);if(!f)return;
 f.storePct=Math.max(50,Math.min(200,(f.storePct||115)+d));st.store.markupPct=f.storePct;save();syncFish();panel();
};

/* ---------- movement ---------- */
function stepWalk(c,dt){
 const t=c.path[0];if(!t){c.speed+=(0-c.speed)*Math.min(1,dt*6);return true;}
 const dx=t.x-c.x,dy=t.y-c.y,d=Math.hypot(dx,dy);
 if(d<2){c.path.shift();return c.path.length===0;}
 const last=c.path.length===1;
 let want=last?Math.min(c.maxSp,d*3+8):c.maxSp;
 c.hx+=(dx/d-c.hx)*Math.min(1,dt*6);c.hy+=(dy/d-c.hy)*Math.min(1,dt*6);
 const hl=Math.hypot(c.hx,c.hy)||1;const ux=c.hx/hl,uy=c.hy/hl;
 for(const o of ST.cust){
  if(o===c)continue;const ox=o.x-c.x,oy=o.y-c.y,od=Math.hypot(ox,oy);
  const R=Math.max(c.parts.rad||40,o.parts.rad||40);if(od<R){if(ox*ux+oy*uy>0&&od<R-4)want*=.5;c.x-=ox/(od||1)*(R-od)*dt*3.2;c.y-=oy/(od||1)*(R-od)*dt*3.2;}
 }
 c.speed+=(want-c.speed)*Math.min(1,dt*5);
 const step=Math.min(d,c.speed*dt);
 c.x+=ux*step;c.y+=uy*step;c.phase+=step*.09;c.dist=(c.dist||0)+step;
 if(Math.abs(dx)>3)c.faceT=dx>0?1:-1;
 return false;
}
function route(c,pts){c.path=pts.slice();}
function viaRow(c,x,y){
 const p=[];if(c.y<380)p.push({x:c.x,y:385});p.push({x:x,y:385});if(y!==undefined)p.push({x:x,y:y});return p;
}
function buildSlots(){
 ST.slots=[];for(let i=0;i<st.store.tanks;i++){const cx=TX[i]+TW/2;ST.slots.push([{x:cx-34,y:374,by:null,tank:i},{x:cx+34,y:374,by:null,tank:i}]);}
}
function freeSlot(ti,c){const L=ST.slots[ti];if(!L)return null;if(c&&c.parts.wide)return (!L[0].by&&!L[1].by)?{x:(L[0].x+L[1].x)/2,y:L[0].y,by:null,tank:ti,both:L}:null;return L.find(s=>!s.by);}
function releaseSlot(c){if(c.slot){c.slot.by=null;if(c.slot.both)c.slot.both.forEach(s=>s.by=null);c.slot=null;}}

/* ---------- customer flow ---------- */
function spawn(){
 const p=newProfile(),pal=PALS[Math.floor(Math.random()*PALS.length)],PP=window.ST120_PEOPLE,pi=(PP&&PP.length)?Math.floor(Math.random()*PP.length):-1,parts=pi>=0?mkSprite(PP[pi],(window.ST120_PEOPLE_ASPECT||[])[pi]):mkPerson(pal);
 const c=Object.assign(p,{id:++ST.uid,sz:parts.spr?1:.8,parts,x:DOOR.x,y:DOOR.y,hx:1,hy:.3,speed:0,maxSp:52+Math.random()*16,phase:Math.random()*6,face:1,faceT:1,alpha:0,state:'enter',path:[],seed:Math.random()*6,visits:[],slot:null,want:null,t:0,wait:0,bagged:false,pointing:false,bubT:0,leaving:false});
 $('st120stage').appendChild(parts.el);ST.cust.push(c);st.store.day.customers++;
 const avail=[];for(let i=0;i<st.store.tanks;i++)if(st.storeFish.slice(i*st.store.slotsPerTank,(i+1)*st.store.slotsPerTank).some(f=>!f._res120))avail.push(i);
 avail.sort(()=>Math.random()-.5);c.visits=avail.slice(0,1+Math.floor(Math.random()*Math.min(3,avail.length)));
 const col=FCOL.guppy;parts.bf.setAttribute('fill',col);
 route(c,[{x:110,y:372}]);
}
function nextStep(c){
 if(c.visits.length){
  const ti=c.visits.shift(),sl=freeSlot(ti,c);if(!sl)return nextStep(c);
  c.slot=sl;sl.by=c;if(sl.both)sl.both.forEach(s=>s.by=c);c.state='goto';route(c,viaRow(c,sl.x,sl.y));return;
 }
 decide(c);
}
function decide(c){
 const r=evaluate(c);
 if(r.fish){
  r.fish._res120=c.id;c.want=r.fish;bubble(c,'😊',1.6);
  if(!ST.pay&&!ST.queue.length&&!ST.clerk.c){ST.pay=c;c.state='toPay';route(c,[{x:c.x,y:Math.max(c.y,388)},PAY]);}
  else{ST.queue.push(c);c.state='toQueue';route(c,[{x:c.x,y:Math.max(c.y,388)},QS[Math.min(ST.queue.length-1,3)]]);}
 }else{
  if(c.type!=='shopper'){bubble(c,r.reason==='expensive'?'💸':'😕',2.4);walkout(c,r.reason);}
  else bubble(c,'🙂',1.6);
  leave(c);
 }
}
function leave(c){
 releaseSlot(c);c.state='exit';c.leaving=true;
 route(c,[{x:c.x,y:Math.max(c.y,440)},{x:140,y:440},{x:70,y:372},{x:DOOR.x,y:DOOR.y}]);
}
function reQueue(){ST.queue.forEach((q,i)=>{if(q.state==='wait'||q.state==='toQueue'){q.state='toQueue';route(q,[QS[Math.min(i,3)]]);}});}
function custTick(c,dt,t){
 if(c.alpha<1&&!c.leaving)c.alpha=Math.min(1,c.alpha+dt*2.5);
 if(c.bubT>0){c.bubT-=dt;if(c.bubT<=0)c.parts.bub.classList.remove('on');}
 const arrived=stepWalk(c,dt);
 switch(c.state){
  case 'enter':if(arrived)nextStep(c);break;
  case 'goto':if(arrived){c.state='look';c.t=3+Math.random()*3;c.pointing=Math.random()<.6;c.faceT=(TX[c.slot.tank]+TW/2-c.x)>=0?1:-1;if(Math.random()<.6)bubble(c,'💙🐟',2);}break;
  case 'look':c.t-=dt;c.speed=0;if(c.t<=0){releaseSlot(c);c.pointing=false;c.state='gone1';nextStep(c);}break;
  case 'toQueue':if(arrived){c.state='wait';c.faceT=1;if(!ST.pay&&!ST.clerk.c&&ST.queue[0]===c){ST.queue.shift();ST.pay=c;c.state='toPay';route(c,[PAY]);reQueue();}}break;
  case 'wait':c.wait+=dt;if(c.wait>45){const f=c.want;if(f)delete f._res120;c.want=null;ST.queue.splice(ST.queue.indexOf(c),1);bubble(c,'😠',2.4);walkout(c,'queue');leave(c);reQueue();}break;
  case 'toPay':if(arrived){c.state='atpay';c.faceT=1;ST.clerk.c=c;ST.clerk.t=0;ST.clerk.ph='';}break;
  case 'exit':if(arrived){c.alpha=Math.max(0,c.alpha-dt*3);if(c.alpha<=0)c.dead=true;}else if(c.x<120)c.alpha=Math.max(0,Math.min(c.alpha,(c.x-DOOR.x)/70+.3));break;
 }
 c.face+=(c.faceT-c.face)*Math.min(1,dt*8);
 const P=c.parts;
 P.el.style.transform=`translate(${(c.x-40).toFixed(1)}px,${(c.y-130).toFixed(1)}px) scale(${c.sz})`;P.el.style.zIndex=Math.round(c.y);P.el.style.opacity=c.alpha;
 P.svg.style.transform=`scaleX(${c.face.toFixed(3)})`;poseP(c,t);
}
function clerkTick(dt,t){
 const K=ST.clerk,P=K.parts;
 if(!K.c){K.ph='idle';K.part=0;poseClerk(t);return;}
 K.t+=dt;let acc=0,cur=null,dur=1,ph0=0;
 for(const [n,d] of PH){if(K.t<acc+d){cur=n;dur=d;ph0=K.t-acc;break;}acc+=d;}
 const c=K.c,f=c.want,cb=$('st120cbag'),reg=$('st120reg');
 if(!cur){
  cb.classList.remove('on');cb.style.transform='';c.bagged=true;if(f)P&&c.parts.bf.setAttribute('fill',FCOL[f.species]||'#ff9a3c');
  K.c=null;K.ph='idle';ST.pay=null;c.state='exit';c.leaving=false;c.want=null;
  route(c,[{x:c.x-8,y:Math.max(c.y+30,440)},{x:140,y:440},{x:70,y:372},{x:DOOR.x,y:DOOR.y}]);c.faceT=-1;
  const h=ST.queue[0];if(h&&(h.state==='wait'||h.state==='toQueue')){ST.queue.shift();ST.pay=h;h.state='toPay';route(h,[PAY]);reQueue();}
  poseClerk(t);return;
 }
 K.part=ph0/dur;
 if(cur!==K.ph){
  K.ph=cur;
  if(cur==='greet'){bubble(c,'😊',1.2);K.parts.bub.textContent='👋';K.parts.bub.classList.add('on');K.bubT=1.2;}
  if(cur==='net'&&f){f._net120=true;syncFish();}
  if(cur==='bag'&&f){cb.innerHTML=`<div class="bw"></div><div class="bfish">${dexAvatarHTML(f,44,26)}</div>`;cb.classList.add('on');cb.style.transform='';}
  if(cur==='hand'){cb.style.transform=`translate(${(c.x+8)-648}px,${(c.y-70)-222}px)`;}
  if(cur==='pay'&&f){
   const pr=sellV120(f,false);reg.textContent='🪙 '+pr;coinsUI();
   const cn=document.createElement('div');cn.className='coin';cn.textContent='+'+pr;$('st120stage').appendChild(cn);setTimeout(()=>cn.remove(),1300);
   syncFish();panel();save();
  }
 }
 if(K.bubT>0){K.bubT-=dt;if(K.bubT<=0)K.parts.bub.classList.remove('on');}
 poseClerk(t);
}
function loop(now,gen){
 if(gen!==ST.gen||!$("st120stage")){return;}
 requestAnimationFrame(n=>loop(n,gen));
 try{
  const dt=Math.min(.1,(now-ST.last)/1000||0);ST.last=now;const t=now/1000;
  const wrap=$('st120wrap'),k=wrap.clientWidth/W;$('st120stage').style.transform=`scale(${k})`;
  /* arrivals */
  ST.next-=dt;
  if(ST.next<=0){
   const hf=hourF();
   if(hf>0&&st.storeFish.length&&ST.cust.length<5)spawn();
   ST.next=(18+Math.random()*20)/((1+.15*repLevel())*Math.max(.3,hf||.3));
  }
  for(const c of ST.cust)custTick(c,dt,t);
  for(let i=ST.cust.length-1;i>=0;i--)if(ST.cust[i].dead){ST.cust[i].parts.el.remove();ST.cust.splice(i,1);}
  /* clerk faces left, customers' bag fish colour */
  clerkTick(dt,t);
  /* door */
  const open=ST.cust.some(c=>c.x<120&&c.y<400);
  if(open!==ST.door){ST.door=open;$('st120door').classList.toggle('open',open);}
  /* bookkeeping */
  ST.sec+=dt;if(ST.sec>=1){ST.sec=0;st.store.lastSimAt=Date.now();dayCheck();}
  ST.saveT+=dt;if(ST.saveT>15){ST.saveT=0;save();}
 }catch(e){console.error('AFNICA store loop',e);}
}

/* ---------- screen ---------- */
window.renderStoreV120=function(){
 try{
  ensureHealthState();ensureStoreV120();setAfnicaScreenV104('store');
  const e=$('screen');if(!e)return;
  dayCheck();
  st.storeFish.forEach(f=>{delete f._res120;delete f._net120;});st.fish.concat(st.fry).forEach(f=>{delete f._from;});
  const away=batchSim();
  e.innerHTML=v8Top()+sceneHTML()+'<div id="st120panel"></div>'+v8Nav('store');
  ST.cust=[];ST.queue=[];ST.pay=null;ST.els=new Map();ST.door=false;ST.next=2.5;ST.sec=0;ST.saveT=0;ST.last=performance.now();
  ST.clerk={c:null,ph:'idle',t:0,part:0,parts:null,bubT:0};
  buildSlots();
  const cl=mkOwner();$('st120clerk').appendChild(cl.el);ST.clerk.parts=cl;
  syncFish();panel();coinsUI();
  const msgs=[],sm=st.store.lastSummary;
  if(away.n)msgs.push(`<div style="text-align:left;margin-bottom:10px"><b>While you were away</b><br>${away.n} customers visited · ${away.sales} sales · 🪙 ${away.revenue}</div>`);
  if(sm&&!sm.shown){sm.shown=true;msgs.push(`<b>Day ${sm.day} summary</b>`+summaryHTML(sm));}
  if(msgs.length){try{pop('🏪 STORE REPORT',msgs.join('<hr style="opacity:.2">'),'OK');save();}catch(er){}}
  const gen=++ST.gen;
  requestAnimationFrame(n=>loop(n,gen));
 }catch(err){console.error('AFNICA store render',err);}
};
window.storeDebugV120=function(){return {S:ST,st:st.store,fish:st.storeFish,spawn,evaluate,fairV120,priceV120,sellV120,dayCheck,batchSim,newProfile};};
})();
