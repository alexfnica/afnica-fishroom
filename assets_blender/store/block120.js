/* ===== V17.120 FISH STORE (MVP) =====
   A shop screen: stock your adult fish in 3 display tanks, NPC customers walk in, browse, queue, the clerk nets and bags the fish,
   they pay and leave. Fish live in st.storeFish (never in st.fish/fry), settings in st.store (defaults in ensureStoreV120, called from
   the wrapped ensureHealthState). Switch: window.STORE120=false. Debug: window.storeDebugV120(). Design: docs/STORE_DESIGN.md */
(function(){
'use strict';
if(window.STORE120===undefined)window.STORE120=true;
const W=760,H=480,TX=[110,280,450,620],TW=156,TY=62,TH=104,SPT=4;
const DOOR={x:48,y:352},PAY={x:722,y:392};
const QS=[{x:654,y:406},{x:598,y:416},{x:542,y:426},{x:486,y:436}];
const FCOL={guppy:'#ff9a3c',molly:'#2b2b3a',platy:'#ffb830',xipho:'#ff6a3c',neon:'#4fb4ff',cory:'#c9a46a',anc:'#6b5a3a'};
const PALS=[
 {shirt:'#e8576a',pants:'#33405a',shoe:'#222',skin:'#e8b48a',hair:'#c76b2a',style:'long'},
 {shirt:'#4aa860',pants:'#2b2b3a',shoe:'#f2f2f2',skin:'#d9a07a',hair:'#2a2a2a',style:'short'},
 {shirt:'#e8b83a',pants:'#5a3a6a',shoe:'#333',skin:'#f3d0b0',hair:'#8a5a2a',style:'bun'},
 {shirt:'#6a7de0',pants:'#444',shoe:'#222',skin:'#a8714a',hair:'#1a1a1a',style:'short'},
 {shirt:'#d96ad0',pants:'#2f3f5f',shoe:'#fff',skin:'#8d5a3a',hair:'#111',style:'long'},
 {shirt:'#52b8c9',pants:'#3a3a3a',shoe:'#222',skin:'#f1c9a0',hair:'#d8c06a',style:'short'}];

const PH=[['greet',1.0],['net',1.4],['bag',1.4],['hand',1.8],['pay',1.1]];
const ST={cust:[],queue:[],pay:null,clerk:{c:null,ph:'idle',t:0,part:null},next:0,last:0,uid:0,sec:0,saveT:0,gen:0,slots:[],els:new Map(),door:false};
const $=id=>document.getElementById(id);

/* ---------- save defaults ---------- */
function ensureStoreV120(){
 if(!st.store||typeof st.store!=='object')st.store={};
 const s=st.store,d={unlocked:true,tanks:3,slotsPerTank:SPT,rep:0,markupPct:115,decor:[],clerks:1,lastSimAt:0,dayNo:0,totalSales:0,totalRevenue:0,sale:null};
 for(const k in d)if(s[k]===undefined)s[k]=d[k];
 if(!s.day||typeof s.day!=='object')s.day={customers:0,sales:0,revenue:0,upkeep:0,walkouts:0,best:0,rep0:s.rep};
 if(!Array.isArray(st.storeFish))st.storeFish=[];
 placeFishV120();
}
/* each store fish has its own place (f.storeSlot); old saves and stocking get the first free one, so a sale never moves the others */
function placeFishV120(){
 const s=st.store,n=s.tanks*s.slotsPerTank,used=new Set();
 st.storeFish.forEach(f=>{if(Number.isInteger(f.storeSlot)&&f.storeSlot>=0&&f.storeSlot<n&&!used.has(f.storeSlot))used.add(f.storeSlot);else f.storeSlot=null;});
 st.storeFish.forEach(f=>{if(f.storeSlot==null){let k=0;while(used.has(k)&&k<n)k++;f.storeSlot=k<n?k:n-1;used.add(f.storeSlot);}});
}
const tankFishV120=ti=>st.storeFish.filter(f=>Math.floor(f.storeSlot/st.store.slotsPerTank)===ti);
const oldEnsure=window.ensureHealthState;
window.ensureHealthState=function(){const r=oldEnsure.apply(this,arguments);try{ensureStoreV120();}catch(e){console.error('AFNICA store defaults',e);}return r;};

/* ---------- nav tab ---------- */
const oldNav=window.v8Nav;
window.v8Nav=function(a){
 let h=oldNav.apply(this,arguments);
 if(window.STORE120===false)return h;
 try{h=h.replace('repeat(6,1fr)','repeat(7,1fr)').replace(/<\/div>\s*$/,`<button class="${a==='store'?'active':''}" onclick="renderStoreV120()">🏪<span>MY STORE</span></button></div>`);}catch(e){console.error('AFNICA store nav',e);}
 return h;
};

/* ---------- prices and eligibility ---------- */
function fairV120(f){
 if(typeof f.health!=='number'||!isFinite(f.health))f.health=100;
 let v=sellValueV9(f);if(!isFinite(v))v=1;
 const gm=(window.fullGrownV1763&&fullGrownV1763(f))?1.2:1,fm=Math.max(.7,1-.06*(f.finTorn||0));
 return Math.max(1,Math.round(v*gm*fm));
}
/* species on sale today (-20%): picked each game day from what is on display (the most stocked species), the player can change it */
function saleV120(){
 const s=st.store;
 if(!s.sale||typeof s.sale!=='object'||s.sale.day!==st.day){
  const n={};st.storeFish.forEach(f=>{n[f.species]=(n[f.species]||0)+1;});
  const sp=Object.keys(n).sort((a,b)=>n[b]-n[a])[0]||null;s.sale={day:st.day,species:sp,pct:20};
 }
 return s.sale;
}
const onSaleV120=f=>{const sa=saleV120();return !!sa.species&&sa.species===f.species;};
function priceV120(f){return Math.max(1,Math.round(fairV120(f)*(f.storePct||115)/100*(onSaleV120(f)?1-saleV120().pct/100:1)));}
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
  const sc=(p.type==='collector'?g.rank*10+fair/price:fair/price+Math.random()*.3)+(onSaleV120(f)?.6:0);   /* the sale draws buyers */
  if(sc>bs){bs=sc;best=f;}
 }
 let dear=null,dl=1e9;if(!best&&saw)for(const f of st.storeFish){if(f._res120)continue;const lim=Math.min(p.budget,fairV120(f)*p.sense*(1+.15*lvl)),o=priceV120(f)/lim;if(o<dl){dl=o;dear=f;}}
 return {fish:best,dear,reason:best?'':(saw?'expensive':'nomatch')};
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
/* a speech bubble; '§' in the text is replaced by a small picture of fish f (the player sees which fish is meant) */
function bubble(c,txt,sec,f){const b=c.parts.bub;b.textContent='';const im=f&&txt.indexOf('§')>=0?fishImgV120(f):null;
 txt.split('§').forEach((s,i)=>{if(i&&im){const e=document.createElement('img');e.className='bfi';e.src=im.src;e.alt='';b.appendChild(e);}b.appendChild(document.createTextNode(s));});
 b.classList.add('on');c.bubT=sec||2.2;}
/* realistic customers: a rendered full-body cut-out (assets_blender/store/people, made with cut_people.py), walked with a bob / rock / squash instead of limbs */
/* walk rigs (walk120.js), one per sprite image, built once the image has decoded; pairs / failures keep the bob */
const RIG=new Map();
function rigFor(src,pair,noArms){let e=RIG.get(src);if(!e){e={R:null,pair:!!pair};RIG.set(src,e);const im=new Image();im.onload=()=>{try{e.R=e.pair?(window.rigPairV120?window.rigPairV120(im):null):(window.rigSpriteV120?window.rigSpriteV120(im,{noArms:!!noArms}):null);if(e.R&&!e.pair)e.R.ax=hipX(im);}catch(er){console.error('AFNICA store walk rig',er);}};im.src=src;}return e;}
/* x of the body at hip height (48-58% of the height): lines up the walk picture and the pointing picture, whose arm sticks out */
function hipX(im){const w=im.naturalWidth,h=im.naturalHeight,c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.drawImage(im,0,0);
 const D=g.getImageData(0,Math.round(h*.48),w,Math.round(h*.1)).data;let sx=0,n=0;for(let i=0;i<D.length;i+=4)if(D[i+3]>110){sx+=(i/4)%w;n++;}return n?sx/n:w/2;}
const PTI=new Map();
function pointFor(src){let e=PTI.get(src);if(!e){e={im:null};PTI.set(src,e);const im=new Image();im.onload=()=>{try{
 const w=im.naturalWidth,h=im.naturalHeight,c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.drawImage(im,0,0);const D=g.getImageData(0,0,w,h).data;
 let gr=h-1;for(;gr>0;gr--){let f=false;for(let x=0;x<w;x++)if(D[(gr*w+x)*4+3]>110){f=true;break;}if(f)break;}e.ground=gr;e.ax=hipX(im);e.im=im;}catch(er){console.error('AFNICA store point pose',er);}};im.src=src;}return e;}
function mkSprite(src,asp,pose){
 const wide=asp>.62;
 const d=document.createElement('div');d.className='st120p sp'+(wide?' wide':'');
 d.innerHTML=`<div class="sprw"><img src="${src}" alt=""><canvas class="wk${wide?' wkw':''}" width="${wide?480:200}" height="320"></canvas><svg class="bagh" width="22" height="28" viewBox="0 0 22 28"><path d="M3 4 q-3 8 1 18 q7 5 14 0 q4 -10 1 -18z" fill="#9ee2f7" fill-opacity=".65" stroke="#e8fbff" stroke-width="1.2"/><path d="M4 4 q7 -8 13 0" stroke="#e8fbff" stroke-width="1.6" fill="none"/><path class="bf" d="M6 15 q5 -5 10 0 q-5 5 -10 0z" fill="#ff9a3c"/></svg></div><div class="bub"></div>`;
 const w=d.querySelector('.sprw'),bag=d.querySelector('.bagh');
 if(wide){bag.style.left='96px';bag.style.top='96px';}
 return {spr:true,wide,rad:wide?60:40,rig:rigFor(src,wide),bagRig:pose&&pose.bag?rigFor(pose.bag,false,true):null,bagFish:pose&&pose.fish||null,ptP:pose&&pose.point?pointFor(pose.point):null,cv:d.querySelector('.wk'),el:d,svg:w,img:w.firstChild,bagEl:bag,bag:{setAttribute(a,v){bag.style.display=v==='visible'?'block':'none';}},bf:d.querySelector('.bf'),bub:d.querySelector('.bub')};
}
function poseP(c,t){
 const P=c.parts,mv=Math.min(1,c.speed/30),sw=Math.sin(c.phase)*mv,sd=c.seed;
 if(P.spr){
  const bob=-Math.abs(Math.sin(c.phase))*2.6*mv+Math.sin(t*2+sd)*.5*(1-mv);
  let rock=Math.sin(c.phase)*2.4*mv,sq=1+Math.abs(Math.sin(c.phase))*.012*mv+Math.sin(t*1.6+sd)*.004*(1-mv);
  if(c.state==='look'){rock=-3+Math.sin(t*3+sd)*(c.pointing?3:1);}
  const RB=c.bagged&&P.bagRig&&P.bagRig.R,R=RB||(P.rig&&P.rig.R);   /* with a bag pose the bag is really in the hand */
  if(R){
   /* real walk: legs swing from the hip, distance-driven so the planted foot does not slide */
   if(P.img.style.display!=='none'){P.img.style.display='none';P.cv.style.display='block';}
   const g=P.cv.getContext('2d'),k=150/R.h,m=Math.min(1,c.speed/25),cw=P.wide?240:100,bag=c.bagged&&!RB?{col:c.bagCol,img:c.bagImg}:null;
   g.setTransform(2,0,0,2,0,0);g.clearRect(0,0,cw,160);g.translate(cw/2,156);
   const pdt=Math.min(.1,Math.max(0,t-(c.plt||t)));c.plt=t;
   /* pointing = the person's own 'point' picture (pose sheet), crossfaded in while they stand at a tank they like */
   const PT=P.ptP&&P.ptP.im?P.ptP:null,ptT=PT&&!R.pair&&c.state==='look'&&c.pointing&&m<.2?1:0;c.pt=(c.pt||0)+(ptT-(c.pt||0))*Math.min(1,pdt*5);
   if(bag){const cyc=(c.dist||0)/(window.cycleLenV120(R.pair?R.parts[0].R:R)*k),tgt=.16*m*Math.sin(2*Math.PI*cyc-1.3);
    c.bagV=(c.bagV||0)+((tgt-(c.bagA||0))*30-(c.bagV||0)*7)*pdt;c.bagA=(c.bagA||0)+c.bagV*pdt;bag.ang=c.bagA;}
   if(R.pair)window.drawPairV120(g,R,c.dist||0,m,k,bag,0);
   else{const FB=RB&&P.bagFish,over=FB&&c.bagImg&&c.bagImg.complete&&c.bagImg.naturalWidth?(x=>{const im=c.bagImg,w=Math.max(FB[2],FB[3]*1.8)*1.35,h=w*im.naturalHeight/im.naturalWidth;x.drawImage(im,FB[0]+FB[2]/2-w/2,FB[1]+FB[3]/2-h/2,w,h);}):null;
    if(c.pt<.99){g.globalAlpha=1-c.pt;window.drawWalkV120(g,R,(c.dist||0)/(window.cycleLenV120(R)*k),m,k,bag,0,over);}
    if(c.pt>.01){g.globalAlpha=c.pt;const kp=150/PT.im.naturalHeight;g.save();g.scale(kp,kp);g.translate(-PT.ax+((R.ax||R.w/2)-R.w/2)*k/kp,-PT.ground);g.drawImage(PT.im,0,0);g.restore();}
    g.globalAlpha=1;}
   const lean=c.state==='look'&&c.pt<.5?-2+Math.sin(t*3+sd)*(c.pointing?1.5:.5):0;
   P.cv.style.transform=`rotate(${lean.toFixed(2)}deg)`;
  }else P.img.style.transform=`translateX(-50%) translateY(${bob.toFixed(2)}px) rotate(${rock.toFixed(2)}deg) scaleY(${sq.toFixed(4)})`;
  P.bag.setAttribute('visibility',c.bagged&&!R?'visible':'hidden');if(c.bagged&&!R)P.bagEl.style.transform=`translateY(${bob.toFixed(2)}px)`;
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
/* the owner at the counter: four Gemini poses of him (idle = hands on the counter, greet = open hand, bag = holding the bag up,
   give = holding it out to the viewer's right), cut with one crop box so they line up, crossfaded per serving phase */
function fishImgV120(f){
 try{let u=realAssetV154(f);if(!u){const set=REAL_FISH_ASSETS_V154[assetSpeciesKeyV154(f)]||{};u=set.adult_m||set.adult_f||set.juvenile||set.fry;}
  if(!u)return null;const im=new Image();im.src=u;return im;}catch(e){return null;}
}
const OWN_K=.107,OWN_X=600,OWN_Y=188,GIVE_BAG={x:OWN_X+810*OWN_K,y:OWN_Y+450*OWN_K};   /* crop px -> stage units; the bag's middle in the 'give' pose */
function mkOwner(){
 const PO=(window.ST120_LOGO||{}).poses||{};
 const d=document.createElement('div');d.className='own';
 const BF=window.ST120_BAGFISH||{},S=95.2/356;
 /* the painted fish was taken out of the bag pictures: the fish being sold is drawn there instead (box from fix_bag_fish.py) */
 const fishEl=k=>{const b=BF['owner_'+k];if(!b)return '';const cx=(b[0]+b[2]/2)*S,cy=(b[1]+b[3]/2)*S,w=Math.max(b[2],b[3]*1.8)*S*1.25;
  return `<img class="ofish" data-k="${k}" alt="" style="left:${(cx-w/2).toFixed(1)}px;top:${(cy-w*.3).toFixed(1)}px;width:${w.toFixed(1)}px;opacity:0">`;};
 d.innerHTML=['idle','greet','bag','give'].map(k=>`<img class="op" data-k="${k}" src="${PO[k]||''}" alt="" style="opacity:${k==='idle'?1:0}">`).join('')+fishEl('bag')+fishEl('give')+'<div class="bub"></div>';
 const im={},fi={};d.querySelectorAll('img.op').forEach(e=>im[e.dataset.k]=e);d.querySelectorAll('img.ofish').forEach(e=>fi[e.dataset.k]=e);
 return {el:d,im,fi,fishFor:null,op:{idle:1,greet:0,bag:0,give:0},lt:0,bub:d.querySelector('.bub')};
}
function custHandV120(c){return {x:c.x+(c.faceT>0?11:-11),y:c.y-74};}
function poseClerk(t){
 const K=ST.clerk,P=K.parts;if(!P)return;
 const pp=K.part||0;let want='idle',rate=7;
 if(K.c){if(K.ph==='greet'||K.ph==='pay')want='greet';else if(K.ph==='bag')want='bag';else if(K.ph==='hand'){want=pp<.55?'give':'idle';rate=14;}}
 const dt=Math.min(.1,Math.max(0,t-(P.lt||t)));P.lt=t;
 const f=K.c&&K.c.want;
 if(f&&P.fishFor!==f){P.fishFor=f;const im=fishImgV120(f);for(const k in P.fi)if(im)P.fi[k].src=im.src;}
 for(const k in P.op){P.op[k]+=((k===want?1:0)-P.op[k])*Math.min(1,dt*rate);P.im[k].style.opacity=P.op[k].toFixed(3);if(P.fi[k])P.fi[k].style.opacity=(f?P.op[k]:0).toFixed(3);}
 /* life: breathing and a very slow sway */
 P.el.style.transform=`translateY(${(Math.sin(t*1.7)*.35).toFixed(2)}px) scaleY(${(1+.006*Math.sin(t*1.7)).toFixed(4)}) rotate(${(Math.sin(t*.5)*.4).toFixed(2)}deg)`;
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

 </svg>
 <div class="dr" id="st120door"></div>
 <div class="board" id="st120board"></div>
 ${tanks}
 <div class="clk" id="st120clerk"></div>
 <div class="cnt"><svg viewBox="0 0 192 100" width="192" height="100"><rect x="0" y="0" width="192" height="14" rx="5" fill="#e8bd7c"/><rect x="4" y="14" width="184" height="86" fill="#9a6538"/><rect x="14" y="26" width="164" height="64" rx="4" fill="#6b4526" opacity=".6"/><text x="96" y="56" text-anchor="middle" font-size="16" font-weight="900" fill="#ffd9a0" opacity=".85" font-family="Inter,system-ui,Arial,sans-serif">PAY HERE</text></svg></div>
 <div class="reg" id="st120reg">🪙 ${st.store.day.revenue||0}</div>
 <div class="cbag" id="st120cbag"></div>
 <div class="qm" style="left:${PAY.x-30}px;top:${PAY.y-6}px"></div>
 </div></div>`;
}
const SWIM=[{x:14,y:14},{x:88,y:20},{x:34,y:40},{x:104,y:44}],FLOOR=[{x:10,y:70},{x:62,y:72},{x:108,y:70},{x:36,y:72}];
const isBottom=f=>f.species==='cory'||f.species==='anc';
function syncFish(){
 const s=st.store,list=st.storeFish,seen=new Set();
 list.forEach((f,idx)=>{
  if(!Number.isInteger(f.storeSlot))placeFishV120();
  const ti=Math.floor(f.storeSlot/s.slotsPerTank),si=f.storeSlot%s.slotsPerTank,fb=$('st120fb'+ti);if(!fb)return;
  const bot=isBottom(f),k=si;   /* its own place: bottom fish on the sand, the others in the water */
  let el=ST.els.get(f.id);
  if(!el){el=document.createElement('div');el.className='sf'+(isBottom(f)?' bt':'');el.innerHTML=`<div class="d" style="animation-duration:${(isBottom(f)?9:5)+Math.random()*4}s;animation-delay:-${(Math.random()*6).toFixed(1)}s">${dexAvatarHTML(f,32,19)}</div>`;ST.els.set(f.id,el);}
  if(el.parentNode!==fb)fb.appendChild(el);
  const p=(bot?FLOOR:SWIM)[k%4];el.style.left=p.x+'px';el.style.top=p.y+'px';
  el.classList.toggle('gone',!!f._net120);seen.add(f.id);
 });
 for(const [id,el] of ST.els)if(!seen.has(id)){el.remove();ST.els.delete(id);}
 for(let i=0;i<s.tanks;i++){
  const tg=$('st120tg'+i);if(!tg)continue;
  const fs=tankFishV120(i).filter(f=>!f._net120);
  if(!fs.length)tg.innerHTML='<b>empty</b>';
  else{const pr=fs.map(priceV120),a=Math.min(...pr),b=Math.max(...pr);tg.innerHTML=`${fs.some(onSaleV120)?'<span class="sl">SALE</span> ':''}${fs.length} fish<br><b>🪙 ${a===b?a:a+'–'+b}</b>`;}
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
/* the sale sign on the wall: which species is on sale today and how much off */
function boardUI(){
 const b=$('st120board');if(!b)return;const sa=saleV120(),f=sa.species&&st.storeFish.find(x=>x.species===sa.species);
 const h=f?`<b>SALE</b><div class="ss">${dexAvatarHTML(f,52,30)}</div><div class="sn">${sname(f)}</div><em>−${sa.pct}% today</em>`:`<b class="off">SALE</b><div class="sn">coming soon</div>`;
 if(b.__h!==h){b.innerHTML=h;b.__h=h;}
}
window.stSale120=function(){
 try{const sp=[...new Set(st.storeFish.map(f=>f.species))];const sa=saleV120();const i=sp.indexOf(sa.species);
  sa.species=sp.length?(i<0||i===sp.length-1?(i<0?sp[0]:null):sp[i+1]):null;save();boardUI();syncFish();panel();}catch(e){console.error('AFNICA store sale',e);}
};
function panel(){
 boardUI();
 const el=$('st120panel');if(!el)return;
 const s=st.store,d=s.day,lvl=repLevel();
 const elig=[];
 st.fish.forEach(f=>{if(eligibleV120(f))elig.push([f,'main']);});
 st.fry.forEach(f=>{if(eligibleV120(f))elig.push([f,'fry']);});
 el.innerHTML=`<div class="v8panel"><div class="v8head"><b>🏪 YOUR FISH STORE</b><span>★ LEVEL ${lvl}</span></div>
  <div class="meta">On sale today: <b style="color:#ff6b5a">${(()=>{const sa=saleV120(),f=sa.species&&st.storeFish.find(x=>x.species===sa.species);return f?sname(f)+' −'+sa.pct+'%':'nothing'})()}</b> <button class="btn small blue" style="padding:4px 8px;min-height:24px;font-size:10px" onclick="stSale120()">CHANGE</button></div>
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
  src.splice(i,1);f.storeSlot=null;f.storeFrom=key;f.storePct=st.store.markupPct;f.storeSince=st.day;delete f._res120;delete f._net120;delete f._from;
  st.storeFish.push(f);placeFishV120();save();syncFish();panel();
 }catch(e){console.error('AFNICA store stock',e);}
};
window.stReturn120=function(id){
 try{
  const i=st.storeFish.findIndex(f=>f.id===id);if(i<0)return;const f=st.storeFish[i];
  if(f._res120)return toast('That fish is being sold right now');
  const order=f.storeFrom==='fry'?[st.fry,st.fish]:[st.fish,st.fry];
  const dst=order.find(a=>a.length<7);if(!dst)return toast('Your tanks are full (7 fish each)');
  st.storeFish.splice(i,1);delete f.storeFrom;delete f.storePct;delete f.storeSince;delete f.storeSlot;
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
 if(d<(c.path.length===1?4:8)){c.path.shift();return c.path.length===0;}   /* close enough: others nudging must not stop an arrival */
 const last=c.path.length===1;
 let want=last?Math.min(c.maxSp,d*3+8):c.maxSp;
 c.hx+=(dx/d-c.hx)*Math.min(1,dt*6);c.hy+=(dy/d-c.hy)*Math.min(1,dt*6);
 const hl=Math.hypot(c.hx,c.hy)||1;const ux=c.hx/hl,uy=c.hy/hl;
 const inDoor=q=>q.state==='exit'&&q.x<125,x0=c.x,y0=c.y;
 if(c.ghost>0)c.ghost-=dt;
 for(const o of ST.cust){
  if(o===c||inDoor(c)||inDoor(o)||c.ghost>0)continue;   /* 'excuse me': a blocked walker slips past for a moment */const ox=o.x-c.x,oy=o.y-c.y,od=Math.hypot(ox,oy);
  const R=Math.max(c.parts.rad||40,o.parts.rad||40);if(od<R){if(ox*ux+oy*uy>0&&od<R-4)want*=.5;const pu=Math.min((R-od)*3.2,40)*dt;c.x-=ox/(od||1)*pu;c.y-=oy/(od||1)*pu;}
 }
 c.speed+=(want-c.speed)*Math.min(1,dt*5);
 const step=Math.min(d,c.speed*dt);
 c.x+=ux*step;c.y+=uy*step;
 /* blocked = hardly any real progress (pushes included) while trying to walk */
 if(Math.hypot(c.x-x0,c.y-y0)<dt*8){c.stk=(c.stk||0)+dt;if(c.stk>1.2){c.ghost=1.5;c.stk=0;}}else c.stk=Math.max(0,(c.stk||0)-dt);c.phase+=step*.09;c.dist=(c.dist||0)+step;
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
/* a person who is not in the shop right now (each picture is one real person); the one who left last is avoided too */
function pickPersonV120(PP){
 if(!PP||!PP.length)return -1;
 const busy=new Set(ST.cust.map(c=>c.pi));if(ST.lastPi!=null&&PP.length>ST.cust.length+1)busy.add(ST.lastPi);
 const free=[];for(let i=0;i<PP.length;i++)if(!busy.has(i))free.push(i);
 return free.length?free[Math.floor(Math.random()*free.length)]:-1;
}
function spawn(){
 if(window.ST120_PEOPLE&&window.ST120_PEOPLE.length&&pickPersonV120(window.ST120_PEOPLE)<0)return;   /* everyone is already inside */
 const p=newProfile(),pal=PALS[Math.floor(Math.random()*PALS.length)],PP=window.ST120_PEOPLE,pi=pickPersonV120(PP),parts=pi>=0?mkSprite(PP[pi],(window.ST120_PEOPLE_ASPECT||[])[pi],(window.ST120_POSES||[])[pi]):mkPerson(pal);
 const c=Object.assign(p,{pi,id:++ST.uid,sz:parts.spr?1:.8,parts,x:DOOR.x,y:DOOR.y,hx:1,hy:.3,speed:0,maxSp:52+Math.random()*16,phase:Math.random()*6,face:1,faceT:1,alpha:0,state:'enter',path:[],seed:Math.random()*6,visits:[],slot:null,want:null,t:0,wait:0,bagged:false,pointing:false,bubT:0,leaving:false});
 $('st120stage').appendChild(parts.el);ST.cust.push(c);st.store.day.customers++;
 const avail=[];for(let i=0;i<st.store.tanks;i++)if(tankFishV120(i).some(f=>!f._res120))avail.push(i);
 avail.sort(()=>Math.random()-.5);c.visits=avail.slice(0,1+Math.floor(Math.random()*Math.min(3,avail.length)));
 const col=FCOL.guppy;parts.bf.setAttribute('fill',col);
 route(c,[{x:110,y:372}]);
}
/* what a customer thinks of the fish in one display tank: 'good' (something they like at a price they accept), 'pricey' (they like it, too dear), 'meh' */
/* what a customer thinks of one display tank, and WHICH fish it is about (so the player knows which price to change):
   'cheap' = a fish they like priced well under its value, 'good' = one they would buy, 'pricey' = one they like but find too dear */
function tankOpinion(c,ti){
 const lvl=repLevel(),fs=tankFishV120(ti).filter(f=>!f._res120&&!f._net120);
 let good=null,gs=-1,dear=null,ds=1e9;
 for(const f of fs){const g=gradeV10(f),rar=rarityV9(f.species);const match=c.type==='beginner'?true:c.type==='collector'?(rar!=='common'||g.rank>=3):false;
  if(!match)continue;const price=priceV120(f),fair=fairV120(f),lim=Math.min(c.budget,fair*c.sense*(1+.15*lvl));
  if(price<=lim){const sc=fair/price;if(sc>gs){gs=sc;good=f;}}else{const over=price/lim;if(over<ds){ds=over;dear=f;}}}
 if(good)return {op:gs>=1.35?'cheap':'good',f:good};
 if(dear)return {op:'pricey',f:dear};
 return {op:'meh',f:null};
}
const pickV120=a=>a[Math.floor(Math.random()*a.length)];
/* customers talk to each other now and then (one short exchange every 5-9 s at most): two at the same tank, a happy customer on
   the way out recommending the fish they bought to someone coming in, and people waiting in the queue. They turn to each other. */
function sayLater(c,txt,at,sec,f){ST.says.push({c,txt,at,sec:sec||2.4,f});}
function talkPair(a,b,t){a.talkTo=b;b.talkTo=a;a.talkUntil=b.talkUntil=t+3.4;a.chatT=b.chatT=t;}
function socialTick(t){
 for(let i=ST.says.length-1;i>=0;i--){const q=ST.says[i];if(t>=q.at){if(!q.c.dead&&q.c.alpha>.5)bubble(q.c,q.txt,q.sec,q.f);ST.says.splice(i,1);}}
 if(t<(ST.chatNext||0))return;
 const C=ST.cust.filter(c=>!c.dead&&c.alpha>.9&&c.bubT<=0&&t-(c.chatT||-99)>14);
 const near=(a,b,d)=>Math.hypot(a.x-b.x,(a.y-b.y)*1.4)<d;
 let done=false;
 for(let i=0;i<C.length&&!done;i++)for(let j=0;j<C.length&&!done;j++){if(i===j)continue;const a=C[i],b=C[j];
  /* at the same tank */
  if(a.state==='look'&&b.state==='look'&&a.slot&&b.slot&&a.slot.tank===b.slot.tank&&!a.parts.wide&&tankOpinion(a,a.slot.tank).f){
   const O=tankOpinion(a,a.slot.tank),nm=O.f?'§':'fish',F=O.f;
   bubble(a,O.op==='pricey'?pickV120(['Pricey '+nm+' , right? 😬','Look at that '+nm+' … 💸']):pickV120(['Nice '+nm+' , huh? 😍','Have you seen this? '+nm,'I like this one '+nm+' 👍']),2.4,F);
   sayLater(b,O.op==='pricey'?pickV120(['Yeah, a bit much 😅','Maybe on sale later 🤞']):pickV120(['Beautiful! 😍','I might get one too 🙂','Good choice! 👍']),t+1.3);
   talkPair(a,b,t);done=true;}
  /* leaving with a bag, passing someone who is coming in or walking to a tank */
  else if(a.state==='exit'&&a.happy&&a.boughtFish&&(b.state==='enter'||b.state==='goto')&&near(a,b,95)){
   bubble(a,pickV120(['Try one of these! §','Great § here! 😊','Get a § , they’re lovely 😍']),2.4,a.boughtFish);
   sayLater(b,pickV120(['Thanks, I will! 😊','Ooh, nice! 👀','Good tip! 👍']),t+1.3);talkPair(a,b,t);done=true;}
  /* in the queue */
  else if(a.state==='wait'&&(b.state==='wait'||b.state==='atpay'||b.state==='toPay')&&near(a,b,90)&&!a.parts.wide){
   bubble(a,pickV120(['Busy shop today! 😄','What did you pick? 🐟','Worth the wait 🙂']),2.4);
   sayLater(b,b.want?pickV120(['This one! §','A § 😍']):pickV120(['It’s great here 🙂','Yes! 😄']),t+1.3,2.4,b.want);
   talkPair(a,b,t);done=true;}
 }
 if(done)ST.chatNext=t+5+Math.random()*4;
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
  if(c.type!=='shopper'){bubble(c,r.reason==='expensive'?(r.dear?pickV120(['§ too expensive… 💸','§ ? Out of my budget 😬']):'Too expensive… 💸'):pickV120(['Nothing for me 😕','Not what I wanted 😕','Hmm, no 🤷']),2.6,r.dear);walkout(c,r.reason);}
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
  case 'goto':if(arrived){c.state='look';c.t=3+Math.random()*3;c.faceT=(TX[c.slot.tank]+TW/2-c.x)>=0?1:-1;
   /* react to the prices in this tank; point at it when interested (the child of a pair points when it sees something) */
   const O=tankOpinion(c,c.slot.tank),op=O.op,nm='§',F=O.f;c.pointing=op==='good'||op==='cheap'||(c.parts.wide&&op!=='meh')||(op==='pricey'&&Math.random()<.4);
   if(c.parts.wide&&op!=='meh')bubble(c,pickV120(['That '+nm+'! 😍','Look! '+nm,'Can we get one? '+nm+' 🥺']),2.8,F);
   else if(op==='cheap')bubble(c,pickV120(['Wow, so cheap! '+nm+' 😮',nm+' is a steal! 🤑']),2.8,F);
   else if(op==='good')bubble(c,pickV120(['Good price! '+nm+' 👍','Nice '+nm+' 😍','Fair price '+nm+' 🙂']),2.8,F);
   else if(op==='pricey')bubble(c,pickV120([nm+' too pricey… 💸',nm+' ? Too much 😬']),2.8,F);
   else bubble(c,pickV120(['👀','🙂']),1.6);}break;
  case 'look':c.t-=dt;c.speed=0;if(c.t<=0){releaseSlot(c);c.pointing=false;c.state='gone1';nextStep(c);}break;
  case 'toQueue':if(arrived){c.state='wait';c.faceT=1;if(!ST.pay&&!ST.clerk.c&&ST.queue[0]===c){ST.queue.shift();ST.pay=c;c.state='toPay';route(c,[PAY]);reQueue();}}break;
  case 'wait':c.wait+=dt;if(c.wait>45){const f=c.want;if(f)delete f._res120;c.want=null;ST.queue.splice(ST.queue.indexOf(c),1);bubble(c,pickV120(['Too slow! 😠','I can’t wait any longer 😤']),2.6);walkout(c,'queue');leave(c);reQueue();}break;
  case 'toPay':if(arrived){c.state='atpay';c.faceT=-1;   /* turned toward the owner, who stands to their left */ST.clerk.c=c;ST.clerk.t=0;ST.clerk.ph='';}break;
  case 'exit':if(c.happy&&!c.bye&&c.x<170&&c.bubT<=0){c.bye=true;bubble(c,pickV120(['Bye! 👋','See you! 👋']),1.4);}
   if(arrived||(c.leaving!==undefined&&c.x<70&&c.path.length<=1)){c.alpha=Math.max(0,c.alpha-dt*3);if(c.alpha<=0)c.dead=true;}else if(c.x<120)c.alpha=Math.max(0,Math.min(c.alpha,(c.x-DOOR.x)/70+.3));break;
 }
 if(c.talkTo&&t<c.talkUntil){if(c.state==='look'||c.state==='wait')c.faceT=c.talkTo.x>=c.x?1:-1;}else if(c.talkTo){c.talkTo=null;if(c.state==='look'&&c.slot)c.faceT=(TX[c.slot.tank]+TW/2-c.x)>=0?1:-1;else if(c.state==='wait')c.faceT=1;}
 c.face+=(c.faceT-c.face)*Math.min(1,dt*16);
 const P=c.parts;
 P.el.style.transform=`translate(${(c.x-40).toFixed(1)}px,${(c.y-130).toFixed(1)}px) scale(${c.sz})`;P.el.style.zIndex=Math.round(c.y);P.el.style.opacity=c.alpha;
 P.svg.style.transform=`scaleX(${c.face.toFixed(3)})`;poseP(c,t);
}
/* the owner's speech bubble above him at the counter */
function ownerSay(txt,sec){const K=ST.clerk;if(!K.parts||!K.parts.bub)return;K.parts.bub.textContent=txt;K.parts.bub.classList.add('on');K.bubT=sec||1.6;}
function clerkTick(dt,t){
 const K=ST.clerk,P=K.parts;
 if(!K.c){K.ph='idle';K.part=0;poseClerk(t);return;}
 K.t+=dt;let acc=0,cur=null,dur=1,ph0=0;
 for(const [n,d] of PH){if(K.t<acc+d){cur=n;dur=d;ph0=K.t-acc;break;}acc+=d;}
 const c=K.c,f=c.want,cb=$('st120cbag'),reg=$('st120reg');
 if(!cur){
  cb.classList.remove('on');cb.style.transform='';if(!c.bagged){c.bagImg=f?fishImgV120(f):null;}c.bagged=true;c.bagCol=f?FCOL[f.species]||'#ff9a3c':'#ff9a3c';if(f)P&&c.parts.bf.setAttribute('fill',FCOL[f.species]||'#ff9a3c');
  c.boughtFish=f||null;K.c=null;K.ph='idle';ST.pay=null;c.state='exit';c.leaving=false;c.want=null;c.happy=true;
  bubble(c,c.parts.wide?pickV120(['Yay, our fish! 🎉','Thank you! 😊','Look, a fish! 🐟']):pickV120(['Thanks! 😊','Love it! 🐟','Perfect for my tank 😍','Great shop! ⭐']),2.4);
  route(c,[{x:c.x-8,y:Math.max(c.y+30,440)},{x:140,y:440},{x:70,y:372},{x:DOOR.x,y:DOOR.y}]);c.faceT=-1;
  const h=ST.queue[0];if(h&&(h.state==='wait'||h.state==='toQueue')){ST.queue.shift();ST.pay=h;h.state='toPay';route(h,[PAY]);reQueue();}
  poseClerk(t);return;
 }
 K.part=ph0/dur;
 if(K.ph==='hand'&&cur==='hand'){
  const u=K.part,sm=v=>{v=Math.max(0,Math.min(1,v));return v*v*(3-2*v);},p1=GIVE_BAG,p2=custHandV120(c);
  if(u>=.55&&!cb.classList.contains('on'))cb.classList.add('on');
  if(u>=.55){const e=sm((u-.55)/.33),q={x:p1.x+(p2.x-p1.x)*e,y:p1.y+(p2.y-p1.y)*e};cb.style.transform=`translate(${(q.x-25-648).toFixed(1)}px,${(q.y-8-222).toFixed(1)}px) scale(.32)`;}
  if(u>=.9&&!c.bagged){cb.classList.remove('on');c.bagImg=f?fishImgV120(f):null;c.bagged=true;c.bagCol=f?FCOL[f.species]||'#ff9a3c':'#ff9a3c';}}
 if(cur!==K.ph){
  K.ph=cur;
  if(cur==='greet'){bubble(c,c.parts.wide?pickV120(['Hello! 👋','Hi! 😊']):pickV120(['This one, please 🐟','I’ll take it! 😊','Hi! 👋']),1.6);ownerSay(pickV120(['Welcome! 😊','Hi there! 👋','Great choice! 👍','Good eye! 🐟']),1.4);}
  if(cur==='net')ownerSay(pickV120(['Let me catch it 🎣','Coming right up! 🐟','One moment… 🎣']),1.4);
  if(cur==='bag')ownerSay(pickV120(['Bagging it 💧','Fresh water for you 💧','Nice and safe 💧']),1.4);
  if(cur==='hand')ownerSay(pickV120(['Here you go! 🐟','All yours! 😊','Enjoy! 🐠']),1.8);
  if(cur==='pay')ownerSay(pickV120(['Thank you! 🙏','Come back soon! 👋','Happy fishkeeping! 🐟']),1.6);
  if(cur==='net'&&f){f._net120=true;syncFish();}
  if(cur==='bag'&&f){cb.classList.remove('on');cb.innerHTML=`<div class="bw"></div><div class="bfish">${dexAvatarHTML(f,44,26)}</div>`;}   /* he holds it in the 'bag' picture */
  if(cur==='hand'){cb.style.transition='none';}
  if(cur==='pay'&&f){
   const pr=sellV120(f,false);reg.textContent='🪙 '+(st.store.day.revenue||0);coinsUI();   /* the till shows today's total */
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
   if(hf>0&&st.storeFish.length&&ST.cust.length<5&&!ST.cust.some(o=>Math.hypot(o.x-DOOR.x,o.y-DOOR.y)<(o.parts.rad||40)+50)){spawn();ST.next=(18+Math.random()*20)/((1+.15*repLevel())*Math.max(.3,hf||.3));}
   else ST.next=hf>0&&st.storeFish.length&&ST.cust.length<5?1.5:(18+Math.random()*20)/((1+.15*repLevel())*Math.max(.3,hf||.3));   /* doorway busy: try again shortly */
  }
  for(const c of ST.cust)custTick(c,dt,t);
  try{socialTick(t);}catch(e){console.error('AFNICA store social',e);}
  for(let i=ST.cust.length-1;i>=0;i--)if(ST.cust[i].dead){ST.lastPi=ST.cust[i].pi;ST.cust[i].parts.el.remove();ST.cust.splice(i,1);}
  /* clerk faces left, customers' bag fish colour */
  clerkTick(dt,t);
  /* door */
  const open=ST.cust.some(c=>c.x<120&&c.y<400);
  if(open!==ST.door){ST.door=open;$('st120door').classList.toggle('open',open);}
  /* bookkeeping */
  ST.sec+=dt;if(ST.sec>=1){ST.sec=0;st.store.lastSimAt=Date.now();dayCheck();boardUI();}
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
  ST.cust=[];ST.queue=[];ST.pay=null;ST.says=[];ST.chatNext=0;ST.els=new Map();ST.door=false;ST.next=2.5;ST.sec=0;ST.saveT=0;ST.last=performance.now();
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

/* ===== V17.120 store music: a light bossa loop (F major, 100 bpm) only while MY FISH STORE is open; the aquarium music
   (V17.49) steps aside (its wanted() checks for the store stage) and is re-synced on every switch. Same 🎵 / 🔊 switches. */
(function(){
'use strict';
const hz=m=>440*Math.pow(2,(m-69)/12),B=60/100;
const PROG=[[53,57,60,64],[50,53,57,60],[55,58,62,65],[48,52,55,58],[53,57,60,64],[50,53,57,60],[46,50,53,57],[48,52,55,58]];   /* Fmaj7 Dm7 Gm7 C7 Fmaj7 Dm7 Bbmaj7 C7 */
const ROOT=[41,38,43,36,41,38,34,36];
const MEL=[65,67,69,72,74,77,79,81,84];   /* F major pentatonic */
let ctx=null,bus=null,on=false,timer=null,nextBar=0,bar=0,mi=3,noise=null;
function build(){
 ctx=typeof audioReadyV141==='function'?audioReadyV141():null;if(!ctx)return false;if(bus)return true;
 bus=ctx.createGain();bus.gain.value=0;
 const len=Math.floor(ctx.sampleRate*1.8),ir=ctx.createBuffer(2,len,ctx.sampleRate);
 for(let ch=0;ch<2;ch++){const d=ir.getChannelData(ch);for(let i=0;i<len;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/len,3);}
 const rv=ctx.createConvolver();rv.buffer=ir;const dry=ctx.createGain(),wet=ctx.createGain();dry.gain.value=.8;wet.gain.value=.28;
 bus.connect(dry);dry.connect(ctx.destination);bus.connect(rv);rv.connect(wet);wet.connect(ctx.destination);
 noise=ctx.createBuffer(1,Math.floor(ctx.sampleRate*.08),ctx.sampleRate);const nd=noise.getChannelData(0);for(let i=0;i<nd.length;i++)nd[i]=(Math.random()*2-1)*(1-i/nd.length);
 return true;
}
function env(g,t,v,a,d){g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(v,t+a);g.gain.exponentialRampToValueAtTime(.0001,t+a+d);}
function ep(t,m,v,d){   /* electric-piano-ish chord voice */
 const o=ctx.createOscillator(),o2=ctx.createOscillator(),g=ctx.createGain(),g2=ctx.createGain(),lp=ctx.createBiquadFilter();
 o.type='sine';o2.type='sine';o.frequency.value=hz(m);o2.frequency.value=hz(m)*2.003;g2.gain.value=.18;lp.type='lowpass';lp.frequency.value=2400;
 o2.connect(g2);g2.connect(g);o.connect(g);env(g,t,v,.008,d);g.connect(lp);lp.connect(bus);o.start(t);o2.start(t);o.stop(t+d+.05);o2.stop(t+d+.05);
}
function bass(t,m,d){
 const o=ctx.createOscillator(),g=ctx.createGain(),lp=ctx.createBiquadFilter();o.type='triangle';o.frequency.value=hz(m);lp.type='lowpass';lp.frequency.value=420;
 env(g,t,.11,.015,d);o.connect(lp);lp.connect(g);g.connect(bus);o.start(t);o.stop(t+d+.05);
}
function shaker(t,v){
 const s=ctx.createBufferSource(),hp=ctx.createBiquadFilter(),g=ctx.createGain();s.buffer=noise;hp.type='highpass';hp.frequency.value=6500;g.gain.value=v;
 s.connect(hp);hp.connect(g);g.connect(bus);s.start(t);
}
function marimba(t,m,v){
 const o=ctx.createOscillator(),o2=ctx.createOscillator(),g=ctx.createGain(),g2=ctx.createGain();o.type='sine';o2.type='sine';o.frequency.value=hz(m);o2.frequency.value=hz(m)*3.98;g2.gain.value=.08;
 o2.connect(g2);g2.connect(g);o.connect(g);env(g,t,v,.005,.55);g.connect(bus);o.start(t);o2.start(t);o.stop(t+.65);o2.stop(t+.65);
}
function scheduleBar(t,i){
 const k=i%PROG.length,ch=PROG[k],r=ROOT[k];
 bass(t,r,.85*B);bass(t+1.5*B,r+7,.4*B);bass(t+2*B,r,.85*B);bass(t+3.5*B,r+7,.4*B);   /* bossa bass: root and fifth */
 [[0,.8],[1.5,.45],[2.5,.4],[3.5,.6]].forEach(([o,d])=>ch.forEach(m=>ep(t+o*B,m+12,.012,d*B*1.8)));
 for(let s=0;s<8;s++)shaker(t+s*B/2,s%2?.018:.03);
 if(i%2===1||Math.random()<.35){   /* a short, happy melody phrase */
  const slots=[0,.5,1,1.5,2,2.5,3,3.5].filter(()=>Math.random()<.45).slice(0,5);
  slots.forEach(o=>{mi=Math.max(0,Math.min(MEL.length-1,mi+[-2,-1,-1,1,1,2][Math.floor(Math.random()*6)]));marimba(t+o*B,MEL[mi],.05);});
 }
}
function schedule(){if(!on||!ctx)return;const ahead=ctx.currentTime+1.5;while(nextBar<ahead){scheduleBar(nextBar,bar);bar++;nextBar+=4*B;}}
const wanted=()=>{try{return !!(st&&st.soundOn&&st.musicOn&&!document.hidden&&window.STORE120!==false&&document.getElementById('st120stage'));}catch(e){return false;}};
function start(){
 if(on||!build())return;on=true;const t=ctx.currentTime;nextBar=t+.15;bar=0;
 bus.gain.cancelScheduledValues(t);bus.gain.setValueAtTime(bus.gain.value,t);bus.gain.linearRampToValueAtTime(.9,t+1.5);
 schedule();timer=setInterval(schedule,300);
}
function stop(){
 if(!on)return;on=false;clearInterval(timer);
 if(ctx&&bus){const t=ctx.currentTime;bus.gain.cancelScheduledValues(t);bus.gain.setValueAtTime(bus.gain.value,t);bus.gain.linearRampToValueAtTime(0,t+1);}
 const b=bus;setTimeout(()=>{if(!on&&bus===b){try{b.disconnect();}catch(e){}bus=null;}},1300);
}
let last=null;
setInterval(()=>{try{const w=wanted();if(w!==last){last=w;w?start():stop();if(typeof window.musicSyncV1749==='function')window.musicSyncV1749();}}catch(e){console.error('AFNICA store music',e);}},400);
document.addEventListener('pointerdown',()=>setTimeout(()=>{if(wanted()&&!on){start();}},60));   /* the first tap unlocks audio */
window.storeMusicStateV120=()=>({on,ctx:ctx&&ctx.state,bar});
})();
