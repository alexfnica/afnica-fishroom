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
/* one game day of store numbers; per species: sold, 'too pricey' reactions, 'too cheap' reactions, missed requests; add-ons sold */
function newDayV120(rep){return {customers:0,sales:0,revenue:0,upkeep:0,walkouts:0,best:0,rep0:rep||0,sold:{},pricey:{},cheap:{},reqMiss:{},addon:{}};}
const bumpV120=(k,sp)=>{try{const o=st.store.day[k]||(st.store.day[k]={});o[sp]=(o[sp]||0)+1;}catch(e){}};
function ensureStoreV120(){
 if(!st.store||typeof st.store!=='object')st.store={};
 const s=st.store,d={unlocked:true,tanks:3,slotsPerTank:SPT,rep:0,markupPct:115,decor:[],clerks:1,lastSimAt:0,dayNo:0,totalSales:0,totalRevenue:0,sale:null,regulars:{},owned:{},name:null};
 for(const k in d)if(s[k]===undefined)s[k]=d[k];
 if(!s.day||typeof s.day!=='object')s.day=newDayV120(s.rep);
 for(const k of ['sold','pricey','cheap','reqMiss','addon'])if(!s.day[k]||typeof s.day[k]!=='object')s.day[k]={};
 if(!Array.isArray(s.hist))s.hist=[];
 if(!s.regulars||typeof s.regulars!=='object')s.regulars={};
 if(!st.imp120||typeof st.imp120!=='object')st.imp120={week:-1,offers:[],shown:false};if(!Array.isArray(st.quar120))st.quar120=[];if(!Array.isArray(st.ord120))st.ord120=[];if(!s.owned||typeof s.owned!=='object')s.owned={};
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
/* the player's name (V17.122 avatar) and the store's name on the sign (renamable; default "<NAME>'S FISH STORE") */
function playerNameV120(){try{const a=st.avatar122;if(a&&a.name)return a.name;if(window.u122Debug)return u122Debug().me.name||'';}catch(e){}return '';}
function storeNameV120(){const n=st.store&&st.store.name;if(n)return n;const p=playerNameV120().trim();if(!p)return 'MY FISH STORE';const P=p.toUpperCase();return (/S$/.test(P)?P+"'":P+"'S")+' FISH STORE';}
window.stRename120=function(){try{const i=$('st120name');if(!i)return;const v=i.value.replace(/[<>&"]/g,'').trim().slice(0,22);st.store.name=v||null;save();toast('🏪 '+storeNameV120());renderStoreV120(true);}catch(e){console.error('AFNICA store rename',e);}};
/* store upgrades (st.store.owned): the plant tank and the freezer sell add-ons, the rug and poster make customers accept a little more */
const UPG=[{k:'plants',name:'Plant tank',ic:'🌿',cost:400,txt:'Customers can add aquarium plants (🪙 15) to their fish.'},
 {k:'freezer',name:'Frozen food freezer',ic:'🧊',cost:500,txt:'Customers can add frozen food (🪙 10) to their fish.'},
 {k:'qt',name:'Quarantine tank',ic:'🧪',cost:350,txt:'A separate tank for new fish: 7 days apart, sick ones are treated there. Shows in the TANK tab.'},
 {k:'rug',name:'Cosy rug',ic:'🟫',cost:200,txt:'+3% on the prices customers accept.'},
 {k:'poster',name:'Fish poster',ic:'🖼️',cost:150,txt:'+2% on the prices customers accept.'}];
const ADDON={plants:{price:15,ic:'🌿',name:'plants'},frozen:{price:10,ic:'🧊',name:'frozen food'}};
const owns=k=>!!(st.store&&st.store.owned&&st.store.owned[k]);
const QCAP=12;   /* fish the quarantine tank holds */
window.quarOwnedV120=()=>{try{return owns('qt');}catch(e){return false;}};
const decorV120=()=>1+(owns('rug')?.03:0)+(owns('poster')?.02:0)+(owns('plants')?.02:0);
/* time of day on the shop: daylight / evening glow / night (dimmer, CLOSED sign); uses the same hour as the arrivals */
function todV120(){try{const h=window.__afHourOverride!=null?+window.__afHourOverride:new Date().getHours(),tod=h<8||h>=22?'night':h>=18?'eve':'day',sg=$('st120stage');
 if(sg&&sg.dataset.tod!==tod){sg.dataset.tod=tod;const d=$('st120door');if(d)d.classList.toggle('closed',tod==='night');}}catch(e){}}
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
  const match=p.req?(f.species===p.req.sp&&g.rank>=p.req.minRank):p.type==='beginner'?true:p.type==='collector'?(rar!=='common'||g.rank>=3):false;
  if(!match)continue;saw=true;
  const price=priceV120(f),fair=fairV120(f);
  if(p.req){if(price>p.budget*1.4||price>fair*(p.sense+.2)*(1+.15*lvl)*decorV120())continue;const sc=g.rank*10+fair/price;if(sc>bs){bs=sc;best=f;}continue;}   /* they came for it */
  if(price>p.budget||price>fair*p.sense*(1+.15*lvl)*decorV120())continue;
  const sc=(p.type==='collector'?g.rank*10+fair/price:fair/price+Math.random()*.3)+(onSaleV120(f)?.6:0);   /* the sale draws buyers */
  if(sc>bs){bs=sc;best=f;}
 }
 let dear=null,dl=1e9;if(!best&&saw)for(const f of st.storeFish){if(f._res120)continue;const lim=Math.min(p.budget,fairV120(f)*p.sense*(1+.15*lvl)*decorV120()),o=priceV120(f)/lim;if(o<dl){dl=o;dear=f;}}
 return {fish:best,dear,reason:best?'':(saw?'expensive':p.req?'reqmiss':'nomatch')};
}
function sellV120(f,silent,c){
 const i=st.storeFish.indexOf(f);if(i<0)return 0;
 const s=st.store,g=gradeV10(f),nm=sname(f);let price=c&&c.offer&&c.offerOk?c.offer:priceV120(f);
 let extra=0,note='';
 if(c&&c.req&&c.req.sp===f.species){extra+=Math.round(price*.25);note+=' · request tip +'+Math.round(price*.25);s.rep=Math.min(100,s.rep+2);}
 if(c&&c.addon&&owns(c.addon==='plants'?'plants':'freezer')){const a=ADDON[c.addon];extra+=a.price;note+=' · '+a.ic+' +'+a.price;bumpV120('addon',c.addon);}
 if(c&&c.pi!=null&&c.pi>=0){const R=s.regulars||(s.regulars={});R[c.pi]=Math.min(6,(R[c.pi]||0)+1);}
 bumpV120('sold',f.species);price+=extra;
 st.storeFish.splice(i,1);
 st.coins+=price;st.totalSold=(st.totalSold||0)+1;
 s.totalSales++;s.totalRevenue+=price;s.day.sales++;s.day.revenue+=price;s.day.best=Math.max(s.day.best,price);
 s.rep=Math.min(100,s.rep+2);
 try{addXPV9(8+g.rank*3);}catch(e){}
 if(!silent){sndV120('till');toast(`🪙 Sold ${g.name} ${nm} for ${price}${note} · rep +2`);}
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
  (s.hist||(s.hist=[])).push({day:s.dayNo,revenue:dd.revenue||0,sales:dd.sales||0,customers:dd.customers||0});if(s.hist.length>14)s.hist.splice(0,s.hist.length-14);
  s.dayNo++;s.day=newDayV120(s.rep);n++;
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
 const sp=new Set([...Object.keys(m.sold||{}),...Object.keys(m.pricey||{}),...Object.keys(m.cheap||{}),...Object.keys(m.reqMiss||{})]);
 const nm=k=>S[k]&&S[k].name?S[k].name:k,rows=[...sp].map(k=>{const so=(m.sold||{})[k]||0,pr=(m.pricey||{})[k]||0,ch=(m.cheap||{})[k]||0,rq=(m.reqMiss||{})[k]||0;
  const tip=rq&&!st.storeFish.some(f=>f.species===k)?'stock some — customers asked':pr>=3&&pr>so*2?'lower −10%':ch>=3?'raise +10%':so?'price looks right':'—';
  return `<tr><td>${nm(k)}</td><td>${so}</td><td>${pr}</td><td>${ch}</td><td>${rq}</td><td><b>${tip}</b></td></tr>`;}).join('');
 const ad=m.addon||{},adds=(ad.plants?`🌿 plants ×${ad.plants} `:'')+(ad.frozen?`🧊 frozen food ×${ad.frozen}`:'');
 const table=rows?`<table class="rep120"><tr><th>Species</th><th>Sold</th><th>Too pricey</th><th>Too cheap</th><th>Asked, none</th><th>Suggestion</th></tr>${rows}</table>`:'';
 return table+(adds?`<div style="text-align:left;margin:6px 0">Add-ons: ${adds}</div>`:'')+`<div style="text-align:left;line-height:1.7">Customers: <b>${m.customers}</b><br>Sales: <b>${m.sales}</b> · 🪙 <b>${m.revenue}</b><br>Upkeep paid: 🪙 ${m.upkeep}<br>Walked out: ${m.walkouts}<br>Best sale: 🪙 ${m.best}<br>Reputation: ${m.rep0} → ${m.rep1}</div>`;
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
function bubble(c,txt,sec,f){const b=c.parts.bub;b.textContent='';b.classList.toggle('lft',c.x>560);const im=f&&txt.indexOf('§')>=0?fishImgV120(f):null;
 txt.split('§').forEach((s,i)=>{if(i&&im){const e=document.createElement('img');e.className='bfi';e.alt='';if(im.src)e.src=im.src;else im.addEventListener('load',()=>{e.src=im.src;},{once:true});b.appendChild(e);}b.appendChild(document.createTextNode(s));});
 b.classList.add('on');c.bubT=sec||2.2;}
/* realistic customers: a rendered full-body cut-out (assets_blender/store/people, made with cut_people.py), walked with a bob / rock / squash instead of limbs */
/* walk rigs (walk120.js), one per sprite image, built once the image has decoded; pairs / failures keep the bob */
const RIG=new Map();
/* people further back (higher on the floor) are drawn a little smaller */
const depthV120=y=>.9+.15*Math.max(0,Math.min(1,(y-340)/130));
/* shop sounds (respect the sound switch): door bell, footsteps, bag rustle, till; crowd murmur in murmurV120 */
let lastStepV120=0;
function sndV120(kind){try{if(!st.soundOn)return;
 if(kind==='bell'){toneV141(1318,.9,'sine',.009);toneV141(988,1.2,'sine',.007,.17);}
 else if(kind==='step'){const now=performance.now();if(now-lastStepV120<110)return;lastStepV120=now;toneV141(80+Math.random()*30,.05,'sine',.01);noiseV141(.02,.0025);}
 else if(kind==='rustle'){for(let i=0;i<7;i++)noiseV141(.025+Math.random()*.035,.006+Math.random()*.006,i*.08+Math.random()*.05);}
 else if(kind==='till'){toneV141(150,.12,'triangle',.025);noiseV141(.05,.01,.02);toneV141(2093,.45,'triangle',.016,.13);toneV141(2637,.55,'triangle',.013,.21);}
}catch(e){}}
let MUR=null;
function murmurV120(n){try{
 const want=st.soundOn&&!document.hidden&&n>=3?Math.min(.03,.012+.004*(n-3)):0;
 if(!MUR){if(!want)return;const ctx=typeof audioReadyV141==='function'?audioReadyV141():null;if(!ctx)return;
  const len=ctx.sampleRate*3,b=ctx.createBuffer(1,len,ctx.sampleRate),d=b.getChannelData(0);let l=0;for(let i=0;i<len;i++){l=(l+.05*(Math.random()*2-1))/1.05;d[i]=l*4;}
  const s=ctx.createBufferSource();s.buffer=b;s.loop=true;const bp=ctx.createBiquadFilter();bp.type='bandpass';bp.frequency.value=430;bp.Q.value=1.3;const g=ctx.createGain();g.gain.value=0;
  const lfo=ctx.createOscillator(),lg=ctx.createGain();lfo.frequency.value=3.2;lg.gain.value=170;lfo.connect(lg);lg.connect(bp.frequency);   /* syllable-like wobble */
  s.connect(bp);bp.connect(g);g.connect(ctx.destination);s.start();lfo.start();MUR={ctx,g};}
 const t=MUR.ctx.currentTime;MUR.g.gain.cancelScheduledValues(t);MUR.g.gain.setTargetAtTime(want,t,.8);}catch(e){}}
function rigFor(src,pair,noArms){let e=RIG.get(src);if(!e){e={R:null,pair:!!pair};RIG.set(src,e);const im=new Image();im.onload=()=>{try{e.R=e.pair?(window.rigPairV120?window.rigPairV120(im):null):(window.rigSpriteV120?window.rigSpriteV120(im,{noArms:!!noArms}):null);if(e.R&&!e.pair)e.R.ax=hipX(im);}catch(er){console.error('AFNICA store walk rig',er);}};im.src=src;}return e;}
/* x of the body at hip height (48-58% of the height): lines up the walk picture and the pointing picture, whose arm sticks out */
function hipX(im){const w=im.naturalWidth,h=im.naturalHeight,c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.drawImage(im,0,0);
 const D=g.getImageData(0,Math.round(h*.48),w,Math.round(h*.1)).data;let sx=0,n=0;for(let i=0;i<D.length;i+=4)if(D[i+3]>110){sx+=(i/4)%w;n++;}return n?sx/n:w/2;}
const PTI=new Map();
function pointFor(src){let e=PTI.get(src);if(!e){e={im:null};PTI.set(src,e);const im=new Image();im.onload=()=>{try{
 const w=im.naturalWidth,h=im.naturalHeight,c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.drawImage(im,0,0);const D=g.getImageData(0,0,w,h).data;
 let gr=h-1;for(;gr>0;gr--){let f=false;for(let x=0;x<w;x++)if(D[(gr*w+x)*4+3]>110){f=true;break;}if(f)break;}e.ground=gr;e.ax=hipX(im);e.im=im;}catch(er){console.error('AFNICA store point pose',er);}};im.src=src;}return e;}
function mkSprite(src,asp,pose){
 const wide=asp>.5;   /* pairs are ~0.55-0.8 wide for their height, single people ~0.41-0.47 */
 const d=document.createElement('div');d.className='st120p sp'+(wide?' wide':'');
 d.innerHTML=`<div class="shd${wide?' w':''}"></div><div class="sprw"><img src="${src}" alt=""><canvas class="wk${wide?' wkw':''}" width="${wide?480:200}" height="320"></canvas><svg class="bagh" width="22" height="28" viewBox="0 0 22 28"><path d="M3 4 q-3 8 1 18 q7 5 14 0 q4 -10 1 -18z" fill="#9ee2f7" fill-opacity=".65" stroke="#e8fbff" stroke-width="1.2"/><path d="M4 4 q7 -8 13 0" stroke="#e8fbff" stroke-width="1.6" fill="none"/><path class="bf" d="M6 15 q5 -5 10 0 q-5 5 -10 0z" fill="#ff9a3c"/></svg></div><div class="bub"></div>`;
 const w=d.querySelector('.sprw'),bag=d.querySelector('.bagh');
 if(wide){bag.style.left='96px';bag.style.top='96px';}
 return {spr:true,wide,rad:wide?60:40,rig:rigFor(src,wide),bagRig:pose&&pose.bag?rigFor(pose.bag,wide,true):null,bagFish:pose&&pose.fish||null,ptP:pose&&pose.point?pointFor(pose.point):null,cv:d.querySelector('.wk'),shd:d.querySelector('.shd'),el:d,svg:w,img:w.firstChild,bagEl:bag,bag:{setAttribute(a,v){bag.style.display=v==='visible'?'block':'none';}},bf:d.querySelector('.bf'),bub:d.querySelector('.bub')};
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
   const PT=P.ptP&&P.ptP.im?P.ptP:null,ptT=PT&&c.state==='look'&&c.pointing&&m<.2?1:0;c.pt=(c.pt||0)+(ptT-(c.pt||0))*Math.min(1,pdt*5);
   if(bag){const cyc=(c.dist||0)/(window.cycleLenV120(R.pair?R.parts[0].R:R)*k),tgt=.16*m*Math.sin(2*Math.PI*cyc-1.3);
    c.bagV=(c.bagV||0)+((tgt-(c.bagA||0))*30-(c.bagV||0)*7)*pdt;c.bagA=(c.bagA||0)+c.bagV*pdt;bag.ang=c.bagA;}
   if(R.pair){
    if(c.pt<.99){g.globalAlpha=1-c.pt;window.drawPairV120(g,R,c.dist||0,m,k,bag,0);
     /* the bought fish in the parent's bag (bag pose): the painted fish was taken out, the real one is drawn at its box */
     const FB=RB&&P.bagFish,im=c.bagImg;if(FB&&im&&im.complete&&im.naturalWidth){const gr=R.parts[0].R.ground,w=Math.max(FB[2]*1.35,FB[3]*2.4,FB[5]*.085),h=w*im.naturalHeight/im.naturalWidth;
      g.save();g.scale(k,k);g.translate(-R.w/2,-gr);g.drawImage(im,FB[0]+FB[2]/2-w/2,FB[1]+FB[3]/2-h/2,w,h);g.restore();}}
    if(c.pt>.01){g.globalAlpha=c.pt;const kp=150/PT.im.naturalHeight;g.save();g.scale(kp,kp);g.translate(-PT.im.naturalWidth/2,-PT.ground);g.drawImage(PT.im,0,0);g.restore();}
    g.globalAlpha=1;}
   else{const FB=RB&&P.bagFish,over=FB&&c.bagImg&&c.bagImg.complete&&c.bagImg.naturalWidth?(x=>{const im=c.bagImg,w=Math.max(FB[2]*1.35,FB[3]*2.4,FB[5]*.085),h=w*im.naturalHeight/im.naturalWidth;   /* never smaller than ~8.5% of the person's height */x.drawImage(im,FB[0]+FB[2]/2-w/2,FB[1]+FB[3]/2-h/2,w,h);}):null;
    if(c.pt<.99){g.globalAlpha=1-c.pt;window.drawWalkV120(g,R,(c.dist||0)/(window.cycleLenV120(R)*k),m,k,bag,0,over);}
    if(c.pt>.01){g.globalAlpha=c.pt;const kp=150/PT.im.naturalHeight;g.save();g.scale(kp,kp);g.translate(-PT.ax+((R.ax||R.w/2)-R.w/2)*k/kp,-PT.ground);g.drawImage(PT.im,0,0);g.restore();}
    g.globalAlpha=1;}
   {const cyc=(c.dist||0)/(window.cycleLenV120(R.pair?R.parts[0].R:R)*k),st2=Math.floor(cyc*2);
    if(P.shd)P.shd.style.transform=`scaleX(${(1+.14*m*Math.abs(Math.sin(cyc*2*Math.PI))).toFixed(3)})`;
    if(c.stepIx!==undefined&&st2!==c.stepIx&&m>.6&&c.alpha>.8)sndV120('step');c.stepIx=st2;}
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
const ANCIMG=new Map();
function ancImgV120(f){
 const d=document.createElement('div');d.style.cssText='position:fixed;left:-9999px;top:0';d.innerHTML=ancGraphicV1719(f);document.body.appendChild(d);
 try{const a=d.firstElementChild,e=d.querySelector('.ancSide');if(!e)return null;const cs=getComputedStyle(e),pf=getComputedStyle(a).filter,ef=cs.filter;
  const key=a.className+'|'+cs.backgroundPosition+'|'+pf+'|'+ef;let res=ANCIMG.get(key);if(res)return res;
  const m=/url\("?(.*?)"?\)/.exec(cs.backgroundImage);if(!m)return null;
  const bs=cs.backgroundSize.split(' ').map(parseFloat),bp=cs.backgroundPosition.split(' ').map(parseFloat),w=parseFloat(cs.width),h=parseFloat(cs.height);
  res=new Image();ANCIMG.set(key,res);const sh=new Image();
  sh.onload=()=>{const k=sh.naturalWidth/bs[0],c=document.createElement('canvas');c.width=Math.round(w*k);c.height=Math.round(h*k);const g=c.getContext('2d');
   const fl=[pf,ef].filter(x=>x&&x!=='none').join(' ');if(fl)g.filter=fl;g.drawImage(sh,-bp[0]*k,-bp[1]*k,w*k,h*k,0,0,c.width,c.height);res.src=c.toDataURL('image/png');};
  sh.src=m[1];return res;}catch(er){return null;}finally{d.remove();}
}
/* the bristlenose's small pictures (tanks, sale board, lists): the dex avatar scales its 2500 px sprite sheet down in CSS and looks blocky,
   so it is cut from the sheet once (ancImgV120) and shrunk in halving steps to 3x the shown size, then drawn as a plain <img> */
const ANCSM=new Map();let ancN120=0;
function ancSmallV120(im,w){const key=im.src.length+'|'+im.src.slice(-40)+'|'+w;let u=ANCSM.get(key);if(u)return u;
 let c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;c.getContext('2d').drawImage(im,0,0);const W=Math.max(8,Math.round(w*3));
 while(c.width/2>=W){const n=document.createElement('canvas');n.width=Math.round(c.width/2);n.height=Math.round(c.height/2);const g=n.getContext('2d');g.imageSmoothingQuality='high';g.drawImage(c,0,0,n.width,n.height);c=n;}
 u=c.toDataURL('image/png');ANCSM.set(key,u);return u;}
function avV120(f,w,h){
 if(f&&f.species==='anc'&&typeof ancGraphicV1719==='function'){try{const im=ancImgV120(f);if(im){
  if(im.complete&&im.naturalWidth)return `<img class="anc120" alt="" src="${ancSmallV120(im,w)}" style="width:${w}px;height:${h}px">`;
  const id='anc120_'+(++ancN120);im.addEventListener('load',()=>{const e=document.getElementById(id);if(e)e.src=ancSmallV120(im,w);},{once:true});
  return `<img class="anc120" id="${id}" alt="" style="width:${w}px;height:${h}px">`;}}catch(e){console.error('AFNICA store anc picture',e);}}
 return dexAvatarHTML(f,w,h);
}
window.fishAvV120=avV120;   /* also used by the V17.122 fishroom Home */
function fishImgV120(f){
 try{if(f.species==='anc'&&typeof ancGraphicV1719==='function'){const a=ancImgV120(f);if(a)return a;}let u=realAssetV154(f);if(!u){const set=REAL_FISH_ASSETS_V154[assetSpeciesKeyV154(f)]||{};u=set.adult_m||set.adult_f||set.juvenile||set.fry;}
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
 d.innerHTML='<div class="obody">'+['idle','greet','bag','give'].map(k=>`<img class="op" data-k="${k}" src="${PO[k]||''}" alt="" style="opacity:${k==='idle'?1:0}">`).join('')+fishEl('bag')+fishEl('give')+'</div><div class="bub"></div>';   /* the bubble stays outside the breathing body */
 const im={},fi={};d.querySelectorAll('img.op').forEach(e=>im[e.dataset.k]=e);d.querySelectorAll('img.ofish').forEach(e=>fi[e.dataset.k]=e);
 return {el:d,body:d.querySelector('.obody'),im,fi,fishFor:null,op:{idle:1,greet:0,bag:0,give:0},lt:0,bub:d.querySelector('.bub')};
}
function custHandV120(c){return {x:c.x+(c.faceT>0?11:-11),y:c.y-74};}
function poseClerk(t){
 const K=ST.clerk,P=K.parts;if(!P)return;
 const pp=K.part||0;let want='idle',rate=7;
 if(K.c){if(K.ph==='greet'||K.ph==='pay')want='greet';else if(K.ph==='bag')want='bag';else if(K.ph==='hand'){want=pp<.55?'give':'idle';rate=14;}}
 const dt=Math.min(.1,Math.max(0,t-(P.lt||t)));P.lt=t;
 const f=K.c&&K.c.want;
 if(f&&P.fishFor!==f){P.fishFor=f;const im=fishImgV120(f);for(const k in P.fi)if(im){if(im.src)P.fi[k].src=im.src;else{const el=P.fi[k];im.addEventListener('load',()=>{el.src=im.src;},{once:true});}}}
 for(const k in P.op){P.op[k]+=((k===want?1:0)-P.op[k])*Math.min(1,dt*rate);P.im[k].style.opacity=P.op[k].toFixed(3);if(P.fi[k])P.fi[k].style.opacity=(f?P.op[k]:0).toFixed(3);}
 /* life: breathing and a very slow sway */
 P.body.style.transform=`translateY(${(Math.sin(t*1.7)*.35).toFixed(2)}px) scaleY(${(1+.006*Math.sin(t*1.7)).toFixed(4)}) rotate(${(Math.sin(t*.5)*.4).toFixed(2)}deg)`;
}

/* ---------- scene ---------- */
/* the plant tank (on a stand) and the chest freezer stand on the floor against the wall, between the display tanks' viewing spots */
function extrasHTML(){
 let h='';
 if(owns('plants'))h+=`<div class="ptk120"><div class="pw"></div><div class="ps"></div>
  <svg viewBox="0 0 100 44" preserveAspectRatio="none"><path d="M8 44 Q4 26 10 6 Q14 26 14 44Z M16 44 Q20 22 30 10 Q24 30 22 44Z M34 44 Q30 20 38 4 Q42 24 40 44Z M46 44 Q52 26 60 14 Q56 32 52 44Z M64 44 Q62 22 70 6 Q74 26 70 44Z M76 44 Q82 24 92 12 Q86 32 82 44Z" fill="#3f9f3a"/><path d="M26 44 Q26 30 32 22 Q30 34 30 44Z M58 44 Q56 32 62 26 Q62 36 62 44Z M88 44 Q88 30 94 24 Q92 36 92 44Z" fill="#6cc24a"/></svg>
  <div class="pg"></div><i class="lg l"></i><i class="lg r"></i><div class="lb">🌿 PLANTS 🪙 15</div></div>`;
 if(owns('freezer'))h+=`<div class="frz120"><div class="fl"><i style="background:#c0392b"></i><i style="background:#8e44ad"></i><i style="background:#c0392b"></i><i style="background:#e67e22"></i><i style="background:#8e44ad"></i><i style="background:#c0392b"></i></div><div class="lb">🧊 FROZEN FOOD 🪙 10</div></div>`;
 return h;
}
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
  ${(()=>{const nm=storeNameV120(),fs=nm.length>18?13:nm.length>14?15:17,ic=window.ST120_LOGO&&window.ST120_LOGO.icon;   /* the player's shop name; the small AFNICA fish stays as the shop's mark */
   return (ic?`<image href="${ic}" x="258" y="9" width="44" height="44"/>`:'')+`<text x="${ic?405:380}" y="38" text-anchor="middle" font-size="${fs}" font-weight="900" fill="#092638" letter-spacing="1.5" font-family="Inter,system-ui,Arial,sans-serif" ${nm.length>16?'textLength="196" lengthAdjust="spacingAndGlyphs"':''}>${nm.replace(/&/g,'&amp;').replace(/</g,'&lt;')}</text>`;})()}
  <rect x="6" y="96" width="86" height="250" rx="5" fill="#2a1a0c"/><rect x="14" y="104" width="70" height="234" fill="#bdeaff" opacity=".9"/><path d="M14 104L84 104L14 220Z" fill="#fff" opacity=".4"/>
  <rect x="2" y="344" width="94" height="8" rx="3" fill="#3a2a14"/>
  ${owns('rug')?'<ellipse cx="380" cy="430" rx="200" ry="34" fill="#8e3b2f" opacity=".9"/><ellipse cx="380" cy="430" rx="184" ry="28" fill="none" stroke="#e7b75f" stroke-width="3" opacity=".8"/><ellipse cx="380" cy="430" rx="150" ry="20" fill="none" stroke="#e7b75f" stroke-width="1.5" opacity=".6"/>':''}
  ${owns('poster')?'<g transform="translate(16 46) rotate(-2)"><rect width="66" height="44" rx="3" fill="#fffbe8" stroke="#7a5a30" stroke-width="3"/><path d="M14 22 q14 -12 30 0 q-14 12 -30 0z M44 22 l10 -7 v14z" fill="#ff8a2a"/><circle cx="20" cy="20" r="1.6" fill="#222"/><text x="33" y="40" text-anchor="middle" font-size="7" font-weight="900" fill="#2a1a0c" font-family="Inter,Arial">KEEP FISH HAPPY</text></g>':''}

 </svg>
 <div class="dr" id="st120door"><i class="pane"></i></div>
 <div class="board" id="st120board"></div>
 ${extrasHTML()}
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
/* each display fish wanders inside its tank: swimmers pick a new spot every few seconds (turning round through a short
   squeeze), bottom fish creep along the sand with pauses */
function swimTickV120(dt){
 for(const el of ST.els.values()){const q=el.sw;if(!q)continue;
  if(q.w>0)q.w-=dt;else{const dx=q.tx-q.x,dy=q.ty-q.y,d=Math.hypot(dx,dy);
   if(d<1.5){q.w=q.bot?1+Math.random()*3:Math.random()*1.2;q.tx=q.bot?6+Math.random()*112:4+Math.random()*116;q.ty=q.bot?68+Math.random()*6:6+Math.random()*44;}
   else{const sp=q.bot?5:11+3*Math.sin(performance.now()/700+q.x),st2=Math.min(d,sp*dt);q.x+=dx/d*st2;q.y+=dy/d*st2;if(Math.abs(dx)>2)q.f=dx>0?1:-1;}}
  q.fs+=(q.f-q.fs)*Math.min(1,dt*6);
  el.style.transform=`translate(${q.x.toFixed(1)}px,${q.y.toFixed(1)}px)`;el.firstChild.style.transform=`scaleX(${(FISHFACE*Math.sign(q.fs||1)*Math.max(.15,Math.abs(q.fs))).toFixed(3)})`;}
}
const FISHFACE=1;   /* the fish pictures face right: +1 = swimming right */
function syncFish(){
 const s=st.store,list=st.storeFish,seen=new Set();
 list.forEach((f,idx)=>{
  if(!Number.isInteger(f.storeSlot))placeFishV120();
  const ti=Math.floor(f.storeSlot/s.slotsPerTank),si=f.storeSlot%s.slotsPerTank,fb=$('st120fb'+ti);if(!fb)return;
  const bot=isBottom(f),k=si;   /* its own place: bottom fish on the sand, the others in the water */
  let el=ST.els.get(f.id);
  if(!el){el=document.createElement('div');el.className='sf'+(isBottom(f)?' bt':'');el.innerHTML=`<div class="d" style="animation-duration:${(isBottom(f)?9:5)+Math.random()*4}s;animation-delay:-${(Math.random()*6).toFixed(1)}s">${avV120(f,32,19)}</div>`;ST.els.set(f.id,el);}
  if(el.parentNode!==fb)fb.appendChild(el);
  const p=(bot?FLOOR:SWIM)[k%4];if(!el.sw){el.sw={x:p.x,y:p.y,tx:p.x,ty:p.y,f:Math.random()<.5?1:-1,fs:1,w:Math.random()*3,bot};el.style.left='0px';el.style.top='0px';el.firstChild.style.animation='none';}
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
 return `<div class="st120row"><div class="av">${avV120(f,56,34)}</div><div class="in"><b>${sicon(f)} ${sname(f)}${sx}</b> <span class="v10Grade ${g.cls}">${g.name}</span>
  <small>${mode==='shop'?`value 🪙 ${fair} · price <b>🪙 ${priceV120(f)}</b> (${f.storePct||115}%)`:`worth about 🪙 ${Math.round(fair*1.15)} in the store · health ${Math.round(f.health==null?100:f.health)}`}</small></div><div class="ctl">${btns}</div></div>`;
}
/* the sale sign on the wall: which species is on sale today and how much off */
function boardUI(){
 const b=$('st120board');if(!b)return;const sa=saleV120(),f=sa.species&&st.storeFish.find(x=>x.species===sa.species);
 const h=f?`<b>SALE</b><div class="ss">${avV120(f,52,30)}</div><div class="sn">${sname(f)}</div><em>−${sa.pct}% today</em>`:`<b class="off">SALE</b><div class="sn">coming soon</div>`;
 if(b.__h!==h){b.innerHTML=h;b.__h=h;}
}
window.stSale120=function(){
 try{const sp=[...new Set(st.storeFish.map(f=>f.species))];const sa=saleV120();const i=sp.indexOf(sa.species);
  sa.species=sp.length?(i<0||i===sp.length-1?(i<0?sp[0]:null):sp[i+1]):null;save();boardUI();syncFish();panel();}catch(e){console.error('AFNICA store sale',e);}
};
/* one row per species on display: change the price of all of them at once */
function speciesRowsV120(){
 const by={};st.storeFish.forEach(f=>{if(!f._res120)(by[f.species]=by[f.species]||[]).push(f);});
 const ks=Object.keys(by);if(!ks.length)return '';
 return `<div class="v8panel"><div class="v8head"><b>PRICE PER SPECIES</b><span>ALL AT ONCE</span></div>${ks.map(k=>{const fs=by[k],pr=fs.map(priceV120),a=Math.min(...pr),b=Math.max(...pr),pc=Math.round(fs.reduce((x,f)=>x+(f.storePct||115),0)/fs.length);
  return `<div class="st120row"><div class="av">${avV120(fs[0],56,34)}</div><div class="in"><b>${sname(fs[0])} ×${fs.length}</b><small>🪙 ${a===b?a:a+'–'+b} · ${pc}% of value</small></div><div class="ctl"><button class="btn small blue" onclick="stPriceSp120('${k}',-10)">−10%</button><button class="btn small blue" onclick="stPriceSp120('${k}',10)">+10%</button></div></div>`;}).join('')}</div>`;
}
window.stPriceSp120=function(sp,d){
 st.storeFish.forEach(f=>{if(f.species===sp&&!f._res120)f.storePct=Math.max(50,Math.min(200,(f.storePct||115)+d));});save();syncFish();panel();
};
window.stBuy120=function(k){
 try{const u=UPG.find(x=>x.k===k);if(!u||owns(k))return;if(st.coins<u.cost)return toast('Not enough coins for the '+u.name);
  st.coins-=u.cost;st.store.owned[k]=true;save();toast(u.ic+' '+u.name+' added to your store!');coinsUI();renderStoreV120(true);}catch(e){console.error('AFNICA store buy',e);}
};
/* the last 7 days (6 closed days + today so far): takings as bars, sales count on top */
function weekChartV120(){
 const s=st.store,d=(s.hist||[]).slice(-6).concat([{day:st.day,revenue:s.day.revenue||0,sales:s.day.sales||0,today:true}]),mx=Math.max(1,...d.map(x=>x.revenue));
 const bw=34,gap=8,H=70,W=d.length*(bw+gap);
 return `<div style="text-align:left;font-size:11px;opacity:.85;margin-bottom:2px">Takings, last ${d.length} days</div><svg viewBox="0 0 ${W} ${H+30}" width="100%" style="max-width:${W}px;display:block;margin:0 auto 8px">${d.map((x,i)=>{const h=Math.round(x.revenue/mx*H),X=i*(bw+gap);
  return `<rect x="${X}" y="${H-h+12}" width="${bw}" height="${Math.max(1,h)}" rx="4" fill="${x.today?'#ffd24b':'#3bc8f5'}"/><text x="${X+bw/2}" y="${H-h+8}" text-anchor="middle" font-size="9" fill="#fff" font-family="Inter,Arial">🪙${x.revenue}</text><text x="${X+bw/2}" y="${H+26}" text-anchor="middle" font-size="9" fill="#9bb6c4" font-family="Inter,Arial">${x.today?'today':'day '+x.day}</text>`;}).join('')}</svg>`;
}
window.stReport120=function(){try{const s=st.store;pop('📋 TODAY’S STORE REPORT',weekChartV120()+summaryHTML(Object.assign({},s.day,{rep1:s.rep,day:st.day})),'OK');}catch(e){console.error('AFNICA store report',e);}};
function panel(){
 boardUI();
 const el=$('st120panel');if(!el)return;
 const s=st.store,d=s.day,lvl=repLevel();
 const elig=[];
 st.fish.forEach(f=>{if(eligibleV120(f))elig.push([f,'main']);});
 st.fry.forEach(f=>{if(eligibleV120(f))elig.push([f,'fry']);});
 el.innerHTML=`<div class="v8panel"><div class="v8head"><b>🏪 ${storeNameV120()}</b><span>★ LEVEL ${lvl}</span></div>
  <div class="meta">On sale today: <b style="color:#ff6b5a">${(()=>{const sa=saleV120(),f=sa.species&&st.storeFish.find(x=>x.species===sa.species);return f?sname(f)+' −'+sa.pct+'%':'nothing'})()}</b> <button class="btn small blue" style="padding:4px 8px;min-height:24px;font-size:10px" onclick="stSale120()">CHANGE</button></div>
  <div class="st120rep"><i style="width:${s.rep}%"></i></div><div class="meta">Reputation ${s.rep}/100 · higher reputation = more customers and higher prices they accept.</div>
  <div class="meta">Today: <b>${d.customers}</b> customers · <b>${d.sales}</b> sales · 🪙 <b>${d.revenue}</b> · lifetime ${s.totalSales} sales, 🪙 ${s.totalRevenue}</div>
  <div class="meta">Upkeep: 🪙 2 per displayed fish per game day (counted while the store screen is open). Fish unsold for 7+ days get stressed.</div>
  ${st.storeFish.length?'':'<div class="meta" style="color:#ffd24b">Stock some fish below, customers only come when there is something to buy.</div>'}</div>
  <div class="v8panel"><div class="v8head"><b>🏪 STORE NAME</b><span>ON THE SIGN</span></div><div style="display:flex;gap:6px;margin-top:4px"><input id="st120name" maxlength="22" placeholder="${storeNameV120()}" value="${(st.store.name||'').replace(/"/g,'')}" style="flex:1;min-width:0;border-radius:8px;border:1px solid #18516a;background:#061923;color:#fff;padding:6px 8px;font:700 12px Inter,Arial"><button class="btn small blue" onclick="stRename120()">SAVE</button></div><div class="meta">Leave it empty to use your name. AFNICA runs the counter for you.</div></div>
  ${importPanelV120()}
  <div class="v8panel"><div class="v8head"><b>📋 TODAY</b><span>DAY ${st.day}</span></div><div class="meta">What customers said about your prices today, per species, with a suggestion.</div><button class="btn small blue wide" style="margin-top:6px" onclick="stReport120()">OPEN TODAY'S REPORT</button></div>
  ${speciesRowsV120()}
  <div class="v8panel"><div class="v8head"><b>ON DISPLAY</b><span>${st.storeFish.length}/${cap()}</span></div>${st.storeFish.map(f=>f._res120?`<div class="st120row"><div class="in"><b>${sname(f)}</b> <small>being sold…</small></div></div>`:rowHTML(f,'shop')).join('')||'<div class="meta">Nothing on display.</div>'}</div>
  <div class="v8panel"><div class="v8head"><b>🛠️ STORE UPGRADES</b><span>🪙 ${st.coins}</span></div>${UPG.map(u=>`<div class="st120row"><div class="av" style="font-size:24px;text-align:center">${u.ic}</div><div class="in"><b>${u.name}</b><small>${u.txt}</small></div><div class="ctl">${owns(u.k)?'<b style="color:#7fe08a;font-size:11px">OWNED ✓</b>':`<button class="btn small green" onclick="stBuy120('${u.k}')">🪙 ${u.cost}</button>`}</div></div>`).join('')}</div>
  <div class="v8panel"><div class="v8head"><b>STOCK FROM YOUR TANKS</b><span>${elig.length} ELIGIBLE</span></div><div class="meta">Healthy adult fish from the Main and Fry tanks (not pregnant).</div>${elig.length?`<div style="display:flex;gap:6px;margin:6px 0"><button class="btn small green" style="flex:1" onclick="stStockAll120('main')">STOCK ALL FROM MAIN</button><button class="btn small green" style="flex:1" onclick="stStockAll120('fry')">STOCK ALL FROM FRY</button></div>`:''}${elig.map(x=>rowHTML(x[0],'stock')).join('')||'<div class="meta">No eligible adult fish right now.</div>'}</div>`;
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
window.stStockAll120=function(key){
 try{const src=key==='fry'?st.fry:st.fish;let n=0;
  for(const f of src.slice()){if(st.storeFish.length>=cap())break;if(!eligibleV120(f))continue;const i=src.indexOf(f);src.splice(i,1);f.storeSlot=null;f.storeFrom=key;f.storePct=st.store.markupPct;f.storeSince=st.day;st.storeFish.push(f);n++;}
  placeFishV120();save();syncFish();panel();toast(n?`🏪 ${n} fish stocked from the ${key==='fry'?'Fry':'Main'} Tank`+(st.storeFish.length>=cap()?' · display full':''):'No eligible fish there (or the display is full)');
 }catch(e){console.error('AFNICA store stock all',e);}
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
 if(Math.abs(dx)>3&&d>10&&c.state!=='look')c.faceT=dx>0?1:-1;   /* short shuffles (and steps at a tank) do not turn them round */
 return false;
}
function route(c,pts){c.path=pts.slice();}
function viaRow(c,x,y){
 const p=[];if(c.y<380)p.push({x:c.x,y:385});p.push({x:x,y:385});if(y!==undefined)p.push({x:x,y:y});return p;
}
function buildSlots(){
 ST.slots=[];for(let i=0;i<st.store.tanks;i++){const cx=TX[i]+TW/2;ST.slots.push([{x:cx-34,y:374,by:null,tank:i},{x:cx+34,y:374,by:null,tank:i}]);}
}
/* the plant tank and the freezer each have one spot to stand at */
const XS={P:{x:282,y:378,fx:282,by:null,tank:'P'},F:{x:470,y:380,fx:470,by:null,tank:'F'}};
function freeSlot(ti,c){const L=ST.slots[ti];if(!L)return null;if(c&&c.parts.wide)return (!L[0].by&&!L[1].by)?{x:(L[0].x+L[1].x)/2,y:L[0].y,by:null,tank:ti,both:L}:null;return L.find(s=>!s.by);}
function releaseSlot(c){if(c.slot){c.slot.by=null;if(typeof c.slot.tank==='string'){c.slot=null;return;}if(c.slot.both)c.slot.both.forEach(s=>s.by=null);c.slot=null;}}

/* ---------- customer flow ---------- */
/* a person who is not in the shop right now (each picture is one real person); the one who left last is avoided too */
function pickPersonV120(PP){
 if(!PP||!PP.length)return -1;
 const busy=new Set(ST.cust.map(c=>c.pi));if(ST.lastPi!=null&&PP.length>ST.cust.length+1)busy.add(ST.lastPi);
 const free=[];for(let i=0;i<PP.length;i++)if(!busy.has(i))free.push(i);
 if(!free.length)return -1;
 const R=(st.store&&st.store.regulars)||{},w=free.map(i=>1+Math.min(4,R[i]||0)*.6),tot=w.reduce((a,b)=>a+b,0);   /* regulars come back more often */
 let x=Math.random()*tot;for(let k=0;k<free.length;k++){x-=w[k];if(x<=0)return free[k];}return free[free.length-1];
}
function spawn(){
 if(window.ST120_PEOPLE&&window.ST120_PEOPLE.length&&pickPersonV120(window.ST120_PEOPLE)<0)return;   /* everyone is already inside */
 const p=newProfile(),pal=PALS[Math.floor(Math.random()*PALS.length)],PP=window.ST120_PEOPLE,pi=pickPersonV120(PP),parts=pi>=0?mkSprite(PP[pi],(window.ST120_PEOPLE_ASPECT||[])[pi],(window.ST120_POSES||[])[pi]):mkPerson(pal);
 const c=Object.assign(p,{pi,id:++ST.uid,sz:parts.spr?1:.8,parts,x:DOOR.x,y:DOOR.y,hx:1,hy:.3,speed:0,maxSp:52+Math.random()*16,phase:Math.random()*6,face:1,faceT:1,alpha:0,state:'enter',path:[],seed:Math.random()*6,visits:[],slot:null,want:null,t:0,wait:0,bagged:false,pointing:false,bubT:0,leaving:false});
 $('st120stage').appendChild(parts.el);ST.cust.push(c);sndV120('bell');st.store.day.customers++;
 const avail=[];for(let i=0;i<st.store.tanks;i++)if(tankFishV120(i).some(f=>!f._res120))avail.push(i);
 avail.sort(()=>Math.random()-.5);c.visits=avail.slice(0,1+Math.floor(Math.random()*Math.min(3,avail.length)));
 const col=FCOL.guppy;parts.bf.setAttribute('fill',col);
 route(c,[{x:110,y:372}]);
 const t0=performance.now()/1000,reg=pi>=0?((st.store.regulars||{})[pi]||0):0;
 if(reg>=2){c.regular=true;c.sense+=.05*Math.min(4,reg);}
 if(ST.friendNext){ST.friendNext=false;c.friend=true;sayLater(c,pickV120(['My friend said this shop is great! ⭐','I heard about this place! 😊']),t0+1,2.8);}
 else if(c.type!=='shopper'&&Math.random()<.22){   /* a request: they come for one species (sometimes a top grade) */
  const sps=Object.keys(S).filter(k=>S[k]&&S[k].price&&FCOL[k]);const sp=pickV120(sps);c.req={sp,minRank:c.type==='collector'||Math.random()<.25?3:0};
  const has=[];for(let i=0;i<st.store.tanks;i++)if(tankFishV120(i).some(f=>f.species===sp&&!f._res120))has.push(i);
  c.visits=has.concat(c.visits.filter(i=>!has.includes(i))).slice(0,3);
  sayLater(c,c.req.minRank?'Looking for a top-grade § ✨':'Looking for a § 🔎',t0+.9,3,{id:'req'+sp,species:sp,sex:'M',age:200,genes:{color:80,pattern:80,fins:80,vitality:80}});}
 else if(c.regular)sayLater(c,pickV120(['Back again! 😄','Hello again! 👋','My favourite shop! ⭐']),t0+.9,2.4);
 if(c.regular&&Math.random()<.3){ST.friendNext=true;ST.next=Math.min(ST.next,2.5);}   /* sometimes brings a friend */
 if(Math.random()<.3){const L=[];if(owns('plants'))L.push('Nice plants in here! 🌿');if(owns('rug'))L.push('Love the rug 😊');if(owns('poster'))L.push('Cool poster 🖼️');if(owns('freezer'))L.push('Oh, frozen food too! 🧊');
  if(st.storeFish.length>=8)L.push('Great selection! 🐟');if(st.store.rep>=40)L.push('Everyone talks about this shop ⭐');L.push('Clean tanks here 👍','Cosy little shop 😊');sayLater(c,pickV120(L),t0+3.2,2.4);}
 /* with a plant tank / freezer some customers have a look there too */
 if(owns('plants')&&Math.random()<.25)c.visits.push('P');if(owns('freezer')&&Math.random()<.25)c.visits.push('F');
}
/* what a customer thinks of the fish in one display tank: 'good' (something they like at a price they accept), 'pricey' (they like it, too dear), 'meh' */
/* what a customer thinks of one display tank, and WHICH fish it is about (so the player knows which price to change):
   'cheap' = a fish they like priced well under its value, 'good' = one they would buy, 'pricey' = one they like but find too dear */
function tankOpinion(c,ti){
 const lvl=repLevel(),fs=tankFishV120(ti).filter(f=>!f._res120&&!f._net120);
 let good=null,gs=-1,dear=null,ds=1e9;
 for(const f of fs){const g=gradeV10(f),rar=rarityV9(f.species);const match=c.type==='beginner'?true:c.type==='collector'?(rar!=='common'||g.rank>=3):false;
  if(!match)continue;const price=priceV120(f),fair=fairV120(f),lim=Math.min(c.budget,fair*c.sense*(1+.15*lvl)*decorV120());
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
 const C=ST.cust.filter(c=>!c.marco&&!c.dead&&c.alpha>.9&&c.bubT<=0&&t-(c.chatT||-99)>14);
 const near=(a,b,d)=>Math.hypot(a.x-b.x,(a.y-b.y)*1.4)<d;
 let done=false;
 for(let i=0;i<C.length&&!done;i++)for(let j=0;j<C.length&&!done;j++){if(i===j)continue;const a=C[i],b=C[j];
  /* at the same tank */
  if(a.state==='look'&&b.state==='look'&&a.slot&&b.slot&&typeof a.slot.tank==='number'&&a.slot.tank===b.slot.tank&&!a.parts.wide&&tankOpinion(a,a.slot.tank).f){
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
  const ti=c.visits.shift(),sl=typeof ti==='string'?(XS[ti]&&!XS[ti].by?XS[ti]:null):freeSlot(ti,c);if(!sl)return nextStep(c);
  c.slot=sl;sl.by=c;if(sl.both)sl.both.forEach(s=>s.by=c);c.state='goto';route(c,viaRow(c,sl.x,sl.y));return;
 }
 decide(c);
}
function decide(c){
 const r=evaluate(c);
 /* haggling: a fish they like is a little too dear -> they offer what they would pay (the player accepts or refuses at the counter) */
 if(!r.fish&&r.reason==='expensive'&&r.dear&&c.type!=='shopper'&&Math.random()<.4){
  const f=r.dear,lim=Math.min(c.budget*(c.req?1.4:1),fairV120(f)*(c.sense+(c.req?.2:0))*(1+.15*repLevel())*decorV120()),pr=priceV120(f);
  if(pr<=lim*1.35&&!f._res120){r.fish=f;c.offer=Math.max(1,Math.round(lim/5)*5);bubble(c,'I’d give 🪙 '+c.offer+' for § 🤝',2.6,f);}
 }
 if(r.fish){
  r.fish._res120=c.id;c.want=r.fish;if(!c.offer)bubble(c,'😊',1.6);
  if(!c.addon&&Math.random()<.3){const ks=[];if(owns('plants'))ks.push('plants');if(owns('freezer'))ks.push('frozen');if(ks.length)c.addon=pickV120(ks);}
  if(!ST.pay&&!ST.queue.length&&!ST.clerk.c){ST.pay=c;c.state='toPay';route(c,[{x:c.x,y:Math.max(c.y,388)},PAY]);}
  else{ST.queue.push(c);c.state='toQueue';route(c,[{x:c.x,y:Math.max(c.y,388)},QS[Math.min(ST.queue.length-1,3)]]);}
 }else{
  if(r.reason==='reqmiss'&&Math.random()<.5)bossSay('Boss, people keep asking for that one 🔎');
  if(r.reason==='expensive'&&r.dear&&Math.random()<.3)bossSay('Maybe lower that price a bit, boss? 🤔');
  if(r.reason==='reqmiss'){bubble(c,pickV120(['No § today 😢','Hmm, no § … 😕']),2.8,{id:'req'+c.req.sp,species:c.req.sp,sex:'M',age:200,genes:{color:80,pattern:80,fins:80,vitality:80}});bumpV120('reqMiss',c.req.sp);walkout(c,'req');}
  else if(c.type!=='shopper'){if(r.dear)bumpV120('pricey',r.dear.species);bubble(c,r.reason==='expensive'?(r.dear?pickV120(['§ too expensive… 💸','§ ? Out of my budget 😬']):'Too expensive… 💸'):pickV120(['Nothing for me 😕','Not what I wanted 😕','Hmm, no 🤷']),2.6,r.dear);walkout(c,r.reason);}
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
 if(c.alpha<1&&!c.leaving&&c.state!=='marcoGo')c.alpha=Math.min(1,c.alpha+dt*2.5);
 if(c.bubT>0){c.bubT-=dt;if(c.bubT<=0)c.parts.bub.classList.remove('on');}
 const arrived=stepWalk(c,dt);
 switch(c.state){
  case 'enter':if(arrived)nextStep(c);break;
  case 'goto':if(arrived&&typeof c.slot.tank==='string'){c.state='look';c.t=2.5+Math.random()*2;c.lookT0=c.t;c.faceT=c.slot.fx>=c.x?1:-1;
   bubble(c,c.slot.tank==='P'?pickV120(['Fresh plants! 🌿','Nice java fern 🌿','My tank needs plants 🌱']):pickV120(['Frozen bloodworms! 🧊','Treats for my fish 🧊','Brine shrimp! 🦐']),2.4);break;}
   if(arrived){c.state='look';c.t=3+Math.random()*3;c.lookT0=c.t;c.faceT=(TX[c.slot.tank]+TW/2-c.x)>=0?1:-1;
   /* react to the prices in this tank; point at it when interested (the child of a pair points when it sees something) */
   const O=tankOpinion(c,c.slot.tank),op=O.op,nm='§',F=O.f;if(F&&op==='pricey')bumpV120('pricey',F.species);if(F&&op==='cheap')bumpV120('cheap',F.species);c.pointing=op==='good'||op==='cheap'||(c.parts.wide&&op!=='meh')||(op==='pricey'&&Math.random()<.4);
   if(c.parts.wide&&op!=='meh')bubble(c,pickV120(['That '+nm+'! 😍','Look! '+nm,'Can we get one? '+nm+' 🥺']),2.8,F);
   else if(op==='cheap')bubble(c,pickV120(['Wow, so cheap! '+nm+' 😮',nm+' is a steal! 🤑']),2.8,F);
   else if(op==='good')bubble(c,pickV120(['Good price! '+nm+' 👍','Nice '+nm+' 😍','Fair price '+nm+' 🙂']),2.8,F);
   else if(op==='pricey')bubble(c,pickV120([nm+' too pricey… 💸',nm+' ? Too much 😬']),2.8,F);
   else bubble(c,pickV120(['👀','🙂']),1.6);}break;
  case 'look':c.t-=dt;if(!c.path.length)c.speed=0;
   if(!c.idle&&c.lookT0&&c.t<c.lookT0-1.4&&c.t>1.2&&!c.talkTo){c.idle=true;   /* after a moment: a small step closer to the glass, or a glance at the next tank */
    if(Math.random()<.55)route(c,[{x:c.x,y:c.y-5}]);}   /* a small step closer to the glass, still facing the tank (no turning away: owner) */
   if(c.glanceT&&t>c.glanceT){c.glanceT=0;if(c.slot&&typeof c.slot.tank==='number')c.faceT=(TX[c.slot.tank]+TW/2-c.x)>=0?1:-1;}
   if(c.t<=0){c.idle=false;c.glanceT=0;releaseSlot(c);c.pointing=false;c.state='gone1';nextStep(c);}break;
  case 'toQueue':if(arrived){c.state='wait';c.faceT=1;if(!ST.pay&&!ST.clerk.c&&ST.queue[0]===c){ST.queue.shift();ST.pay=c;c.state='toPay';route(c,[PAY]);reQueue();}}break;
  case 'wait':c.wait+=dt;if(c.wait>45){const f=c.want;if(f)delete f._res120;c.want=null;ST.queue.splice(ST.queue.indexOf(c),1);bubble(c,pickV120(['Too slow! 😠','I can’t wait any longer 😤']),2.6);walkout(c,'queue');leave(c);reQueue();}break;
  case 'toPay':if(arrived){c.state='atpay';c.faceT=-1;   /* turned toward the owner, who stands to their left */ST.clerk.c=c;ST.clerk.t=0;ST.clerk.ph='';}break;
  case 'marco':if(arrived&&!c.arr){c.arr=true;const MP=window.ST120_MARCO||{};if(MP.thumbs)marcoStillV120(c,MP.thumbs);bubble(c,'Delivery for you, boss! 📦',2.4);setTimeout(()=>{try{deliveryPopV120();}catch(e){}},2200);}break;
  case 'marcoGo':c.t-=dt;if(c.t<=0){c.alpha=Math.max(0,c.alpha-dt*2);if(c.alpha<=0)c.dead=true;}break;
  case 'exit':if(c.happy&&!c.bye&&c.x<170&&c.bubT<=0){c.bye=true;bubble(c,pickV120(['Bye! 👋','See you! 👋']),1.4);}
   if(arrived||(c.leaving!==undefined&&c.x<70&&c.path.length<=1)){c.alpha=Math.max(0,c.alpha-dt*3);if(c.alpha<=0)c.dead=true;}else if(c.x<120)c.alpha=Math.max(0,Math.min(c.alpha,(c.x-DOOR.x)/70+.3));break;
 }
 if(c.talkTo&&t<c.talkUntil){if(c.state==='look'||c.state==='wait')c.faceT=c.talkTo.x>=c.x?1:-1;}else if(c.talkTo){c.talkTo=null;if(c.state==='look'&&c.slot&&typeof c.slot.tank==='number')c.faceT=(TX[c.slot.tank]+TW/2-c.x)>=0?1:-1;else if(c.state==='wait')c.faceT=1;}
 c.face+=(c.faceT-c.face)*Math.min(1,dt*11);c.turnDip=Math.abs(c.face)<.85?(1-Math.abs(c.face))*.035:0;   /* step-turn: a small dip while turning */
 const P=c.parts;
 const sc=c.sz*depthV120(c.y);P.el.style.transform=`translate(${(c.x-40).toFixed(1)}px,${(c.y-130).toFixed(1)}px) scale(${sc.toFixed(3)})`;P.el.style.setProperty('--bs',(1/sc).toFixed(3));   /* the bubble keeps one size whatever the depth */P.el.style.zIndex=Math.round(c.y);P.el.style.opacity=c.alpha;
 P.svg.style.transform=`translateY(${((c.turnDip||0)*40).toFixed(2)}px) scaleX(${(Math.sign(c.face||1)*Math.max(.12,Math.abs(c.face))).toFixed(3)})`;poseP(c,t);
}
/* the owner's speech bubble above him at the counter */
/* an offer card over the counter: the player accepts or refuses (refused after 15 s) */
function showOfferV120(c,t){
 const K=ST.clerk,f=c.want;if(!f)return;const d=document.createElement('div');d.className='offer120';
 const im=fishImgV120(f);d.innerHTML=`<div class="ot">Offer for <img alt=""></div><div class="op">price <s>🪙 ${priceV120(f)}</s> → <b>🪙 ${c.offer}</b></div><div class="ob"><button class="ok" onclick="stOffer120(true)">✔ ACCEPT</button><button class="no" onclick="stOffer120(false)">✖ NO</button></div>`;
 const ie=d.querySelector('img');if(im){if(im.src)ie.src=im.src;else im.addEventListener('load',()=>{ie.src=im.src;},{once:true});}
 $('st120stage').appendChild(d);K.offerEl=d;K.offerT=t;ownerSay('Hmm… 🤔',2);
}
window.stOffer120=function(yes){
 try{const K=ST.clerk,c=K.c;if(!c||!c.offer||c.offerDone)return;c.offerDone=true;if(K.offerEl){K.offerEl.remove();K.offerEl=null;}
  if(yes){c.offerOk=true;ownerSay('Deal! 🤝',1.6);bubble(c,'Thank you! 😊',1.6);K.t=0;K.ph='';return;}
  const f=c.want;if(f){delete f._res120;bumpV120('pricey',f.species);}c.want=null;K.c=null;ST.pay=null;ownerSay('Sorry, the price is fixed 🙂',1.8);bubble(c,pickV120(['Oh well… 😕','Maybe next time 😕']),2.2);leave(c);
  const h=ST.queue[0];if(h&&(h.state==='wait'||h.state==='toQueue')){ST.queue.shift();ST.pay=h;h.state='toPay';route(h,[PAY]);reQueue();}
 }catch(e){console.error('AFNICA store offer',e);}
};
let bossT=0;
function bossSay(txt,sec){const t=performance.now()/1000;if(t<bossT)return;bossT=t+12;setTimeout(()=>{if(!ST.clerk.c)ownerSay(txt,sec||2.4);},2600);}
function ownerSay(txt,sec){const K=ST.clerk;if(!K.parts||!K.parts.bub)return;K.parts.bub.textContent=txt;K.parts.bub.classList.add('on');K.bubT=sec||1.6;}
function clerkTick(dt,t){
 const K=ST.clerk,P=K.parts;
 if(!K.c){K.ph='idle';K.part=0;poseClerk(t);return;}
 K.t+=dt;let acc=0,cur=null,dur=1,ph0=0;
 for(const [n,d] of PH){if(K.t<acc+d){cur=n;dur=d;ph0=K.t-acc;break;}acc+=d;}
 const c=K.c,f=c.want,cb=$('st120cbag'),reg=$('st120reg');
 if(c.offer&&!c.offerDone){K.t=0;if(!K.offerEl)showOfferV120(c,t);else if(t-K.offerT>15)window.stOffer120(false);if(K.bubT>0){K.bubT-=dt;if(K.bubT<=0)K.parts.bub.classList.remove('on');}poseClerk(t);return;}
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
  if(cur==='greet'&&c.addon){sayLater(c,c.addon==='plants'?'And some plants, please 🌿':'And some frozen food 🧊',t+1.7,2);}
  if(cur==='greet'){bubble(c,c.parts.wide?pickV120(['Hello! 👋','Hi! 😊']):pickV120(['This one, please 🐟','I’ll take it! 😊','Hi! 👋']),1.6);ownerSay(pickV120(['Welcome! 😊','Hi there! 👋','Great choice! 👍','Good eye! 🐟']),1.4);}
  if(cur==='net')ownerSay(pickV120(['Let me catch it 🎣','Coming right up! 🐟','One moment… 🎣']),1.4);
  if(cur==='bag')ownerSay(pickV120(['Bagging it 💧','Fresh water for you 💧','Nice and safe 💧']),1.4);
  if(cur==='hand')ownerSay(pickV120(['Here you go! 🐟','All yours! 😊','Enjoy! 🐠']),1.8);
  if(cur==='pay')ownerSay(pickV120(['Thank you! 🙏','Come back soon! 👋','Happy fishkeeping! 🐟']),1.6);
  if(cur==='net'&&f){f._net120=true;syncFish();}
  if(cur==='bag')sndV120('rustle');
  if(cur==='bag'&&f){cb.classList.remove('on');cb.innerHTML=`<div class="bw"></div><div class="bfish">${avV120(f,44,26)}</div>`;}   /* he holds it in the 'bag' picture */
  if(cur==='hand'){cb.style.transition='none';}
  if(cur==='pay'&&f){
   const pr=sellV120(f,false,c);
   if(c.req&&c.req.sp===f.species)bossSay('They came just for that one, boss! ⭐');else if(c.offer)bossSay('A deal is a deal, boss 🤝');else if(Math.random()<.35)bossSay(pickV120(['Nice sale, boss! 👍','Another happy customer, boss 😊','The till likes that, boss 🪙']));reg.textContent='🪙 '+(st.store.day.revenue||0);coinsUI();   /* the till shows today's total */
   const cn=document.createElement('div');cn.className='coin';cn.textContent='+'+pr;$('st120stage').appendChild(cn);setTimeout(()=>cn.remove(),1300);
   syncFish();panel();save();
  }
 }
 if(K.bubT>0){K.bubT-=dt;if(K.bubT<=0)K.parts.bub.classList.remove('on');}
 poseClerk(t);
}
function loop(now,gen){
 if(gen!==ST.gen||!$("st120stage")){if(!$("st120stage"))murmurV120(0);return;}
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
  try{swimTickV120(dt);}catch(e){}
  for(const c of ST.cust)custTick(c,dt,t);
  try{socialTick(t);}catch(e){console.error('AFNICA store social',e);}
  for(let i=ST.cust.length-1;i>=0;i--)if(ST.cust[i].dead){if(!ST.cust[i].marco)ST.lastPi=ST.cust[i].pi;ST.cust[i].parts.el.remove();ST.cust.splice(i,1);}
  /* clerk faces left, customers' bag fish colour */
  clerkTick(dt,t);
  /* door */
  const open=ST.cust.some(c=>c.x<120&&c.y<400);
  if(open!==ST.door){ST.door=open;$('st120door').classList.toggle('open',open);}
  /* bookkeeping */
  ST.sec+=dt;if(ST.sec>=1){ST.sec=0;todV120();murmurV120(ST.cust.length);st.store.lastSimAt=Date.now();dayCheck();boardUI();}
  ST.saveT+=dt;if(ST.saveT>15){ST.saveT=0;save();}
 }catch(e){console.error('AFNICA store loop',e);}
}

/* ---------- weekly import: an importer offers 3 random species every game Monday; bought fish spend QDAYS (7) game days in quarantine ---------- */
const weekOf=d=>Math.floor((Math.max(1,d)-1)/7),isMonday=d=>(Math.max(1,d)-1)%7===0;
/* one imported fish of species sp around the offer's grade level gr (each fish its own genes), sex chosen by the player */
const IMPMAX=10;   /* the importer brings at most 10 fish of each species per week */
const QDAYS=7;   /* imported fish stay 7 game days in quarantine (owner) */
function impFishV120(sp,gr,sex,mut){
 const g=()=>Math.max(30,Math.min(99,Math.round(gr+(Math.random()*8-4))));
 const id='imp'+st.day+'_'+sp+'_'+Math.floor(Math.random()*1e7);
 const f={id,name:id,species:sp,sex:sex||(Math.random()<.5?'M':'F'),age:(S[sp].adult||10)+4,genes:{color:g(),pattern:g(),fins:g(),vitality:g(),mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0,imported:true};
 if(mut){const k={'Iridescent Color':'color','Wild Pattern':'pattern','Extended Fins':'fins','High Vitality':'vitality'}[mut];f.genes.mutation=mut;if(k)f.genes[k]=Math.min(99,f.genes[k]+14);}   /* same boost as a bred mutation */
 return f;
}
function makeOffersV120(){
 const sps=Object.keys(S).filter(k=>S[k]&&S[k].price&&S[k].adult&&FCOL[k]).sort(()=>Math.random()-.5).slice(0,3);
 st.imp120={week:weekOf(st.day),shown:false,offers:sps.map(sp=>{const r=Math.random(),gr=r<.1?88:r<.45?79:68,sample=impFishV120(sp,gr,'M');
  return {sp,gr,price:Math.round(sellValueV9(sample)*1.6/5)*5,left:IMPMAX,sample};})};
 if(Math.random()<.2&&st.imp120.offers.length){   /* 1 week in 5: a special edition (S grade with a mutation, only 3 fish) */
  const o=st.imp120.offers[Math.floor(Math.random()*st.imp120.offers.length)],mut=['Iridescent Color','Wild Pattern','Extended Fins','High Vitality'][Math.floor(Math.random()*4)];
  o.gr=90;o.mut=mut;o.sample=impFishV120(o.sp,90,'M',mut);o.left=3;o.max=3;o.price=Math.round(sellValueV9(o.sample)*2.2/5)*5;}
}
/* saves from before the 10-per-species offer: one fish per card -> a 10-fish card of the same species and level */
function fixOffersV120(){const o=st.imp120&&st.imp120.offers;if(!Array.isArray(o))return;
 o.forEach((x,i)=>{if(x.fish&&!x.sp){const f=x.fish,gr=Math.round((f.genes.color+f.genes.pattern+f.genes.fins+f.genes.vitality)/4);o[i]={sp:f.species,gr,price:x.price,left:x.bought?IMPMAX-1:IMPMAX,sample:f};}});}
function impCardsV120(){
 fixOffersV120();const o=st.imp120.offers||[];if(!o.length)return '<div class="meta">No shipment this week.</div>';
 return o.map((x,i)=>{const f=x.sample,g=gradeV10(f);return `<div class="st120row"><div class="av">${avV120(f,56,34)}</div><div class="in"><b>${sname(f)}</b> <span class="v10Grade ${g.cls}">${g.name}</span>${x.mut?`<span class="spc120">✨ SPECIAL · ${x.mut}</span>`:''}<small>🪙 ${x.price} each · <b>${x.left} / ${x.max||IMPMAX} left</b> · delivered tomorrow</small></div><div class="ctl">${x.left>0?`<button class="btn small green" onclick="stImportBuy120(${i},'M')">BUY ♂</button><button class="btn small green" onclick="stImportBuy120(${i},'F')">BUY ♀</button>`:'<b style="color:#ffb347;font-size:11px">SOLD OUT</b>'}</div></div>`;}).join('');
}
function quarHTMLV120(){
 const q=st.quar120||[];if(!q.length)return '';
 return `<div class="meta" style="margin-top:6px"><b>🧪 In quarantine</b></div>`+q.map(x=>`<div class="st120row"><div class="av">${avV120(x.fish,56,34)}</div><div class="in"><b>${sname(x.fish)} ${x.fish.sex==='M'?'♂':'♀'}</b><small>${x.until>st.day?'ready on day '+x.until:'waiting for room in your tanks (7 fish max)'}</small></div></div>`).join('');
}
function importPanelV120(){
 const left=7-((Math.max(1,st.day)-1)%7),ord=(st.ord120||[]).length?`<div class="meta" style="margin-top:6px"><b>🚚 On the way</b> · ${st.ord120.length} fish · Marco delivers on day ${Math.min(...st.ord120.map(o=>o.due))}</div>`:'';
 return `<div class="v8panel"><div class="v8head"><b>📦 WEEKLY IMPORT</b><span>${left===7?'NEW TODAY':'NEW IN '+left+' DAY'+(left>1?'S':'')}</span></div>${impCardsV120()}${ord}${quarHTMLV120()}</div>`;
}
window.importNoticesV120=function(){
 const out=[];ensureStoreV120();const o=(st.imp120&&st.imp120.week===weekOf(st.day))?st.imp120.offers||[]:[];
 const left=o.reduce((a,x)=>a+(x.left||0),0);
 if(left&&!st.imp120.ordered)out.push({ic:'📦',tx:`Marco has a new shipment: ${o.map(x=>S[x.sp]?S[x.sp].name:x.sp).join(', ')}${o.some(x=>x.mut)?' ✨':''}`,go:'import'});
 const ord=st.ord120||[];if(ord.length)out.push({ic:'🚚',tx:`Marco delivers ${ord.length} fish on day ${Math.min(...ord.map(x=>x.due))}`,go:'import'});
 const q=st.quar120||[];if(q.length)out.push({ic:'🧪',tx:`Quarantine: ${q.length} fish, next ready on day ${Math.min(...q.map(x=>x.until))}`,go:owns('qt')?'quar':'import'});
 return out;
};
window.stImport120=function(){try{ensureHealthState();ensureStoreV120();if(st.imp120.week!==weekOf(st.day))makeOffersV120();st.imp120.shown=true;save();
 const IM=window.ST120_IMPORTER;
 pop('📦 WEEKLY IMPORT',`<div class="imp120"><div class="who">${IM?`<img src="${IM}" alt="">`:'<span class="sil">🧔</span>'}<div><b>Marco, the fish importer</b><small>"Fresh shipment this week! Pick what you like 📦"</small></div></div>${impCardsV120()}<div class="tip"><b>AFNICA tip:</b> imported fish bring new genes for breeding. Marco delivers your order the next day; then put them in quarantine for 7 days: new fish can carry diseases.</div></div>`,'LATER');}catch(e){console.error('AFNICA store import',e);}};
/* ordering: the player pays now, Marco brings the fish the next game day (st.ord120); where they go is chosen at delivery */
window.stImportBuy120=function(i,sex){
 try{fixOffersV120();const x=st.imp120.offers[i];if(!x||x.left<=0)return toast('Sold out for this week');if(st.coins<x.price)return toast('Not enough coins');
  const f=impFishV120(x.sp,x.gr,sex==='F'?'F':'M',x.mut);st.coins-=x.price;x.left--;st.ord120.push({fish:f,due:st.day+1,sick:Math.random()<.15});save();
  st.imp120.ordered=true;toast(`📦 ${sname(f)} ${f.sex==='M'?'♂':'♀'} ordered (${x.left} left) · Marco delivers tomorrow`);try{coinsUI();}catch(e){}
  if(!owns('qt')&&!st.store.qtTip){qtTipV120(true);return;}
  if(document.querySelector('.imp120'))stImport120();if($('st120panel'))panel();}catch(e){console.error('AFNICA store import buy',e);}
};
/* the delivery: one choice for the whole box: 7 days of quarantine (recommended) or straight into the tanks at the player's risk */
let delivering=false;
function qFreeV120(){return Math.max(0,QCAP-(st.quar120||[]).length);}
function dueOrdersV120(){return (st.ord120||[]).filter(o=>o.due<=st.day);}
function afnicaFaceV120(){const F=window.ST120_AFNICA_FACE;return F?`<img src="${F}" alt="">`:'<span class="sil">🧑</span>';}   /* square crop centred on his head (cut_afnica_face.py) */
/* AFNICA suggests a quarantine tank (once, when the player orders without one) */
function qtTipV120(back){
 st.store.qtTip=true;save();
 pop('🧪 A TIP FROM AFNICA',`<div class="imp120"><div class="who"><span class="afc">${afnicaFaceV120()}</span><div><b>AFNICA</b><small>"Boss, before Marco brings the fish: get a quarantine tank."</small></div></div>
  <div class="tip" style="margin:0 0 8px">New fish can carry ich, fungus or bacteria without showing it. In a quarantine tank they stay apart for ${QDAYS} days: if one is sick, it is treated there and never touches your Main Tank. It's the best way to keep your fish safe.</div>
  <button class="btn green wide" style="margin-bottom:6px" onclick="stBuyQt120(${back?1:0})">🧪 BUY A QUARANTINE TANK · 🪙 350</button>
  <button class="btn wide" style="background:#2b4a5a" onclick="closePop();${back?'setTimeout(()=>stImport120(),60);':''}">MAYBE LATER</button></div>`,'OK');
 {const btn=document.querySelector('#popup > .btn:last-child');if(btn)btn.style.display='none';}
}
window.stBuyQt120=function(back){
 try{if(owns('qt'))return;if(st.coins<350)return toast('Not enough coins for the quarantine tank');st.coins-=350;st.store.owned.qt=true;save();try{coinsUI();}catch(e){}
  toast('🧪 Quarantine tank set up! You will find it in the TANK tab.');if(typeof closePop==='function')closePop();
  if(back===1)setTimeout(()=>stImport120(),60);else if(back===2)setTimeout(()=>deliveryPopV120(),60);if($('st120panel'))panel();}catch(e){console.error('AFNICA store qt',e);}
};
function deliveryPopV120(){
 const due=dueOrdersV120();if(!due.length){delivering=false;return;}delivering=true;
 const MP=window.ST120_MARCO||{},pic=MP.thumbs||window.ST120_IMPORTER;
 pop('📦 DELIVERY FROM MARCO',`<div class="imp120"><div class="who">${pic?`<img src="${pic}" alt="" style="object-position:50% 8%">`:'<span class="sil">🧔</span>'}<div><b>Marco</b><small>"Your fish are here, boss! ${due.length} fish, all in good shape… I think 😉 See you on Monday, day ${nextMondayV120()}!"</small></div></div>
  <div class="dlv">${due.map(o=>`<span>${avV120(o.fish,52,30)}<i>${sname(o.fish)} ${o.fish.sex==='M'?'♂':'♀'}</i></span>`).join('')}</div>
  <div class="tip" style="margin:6px 0 8px"><b>AFNICA:</b> new fish can carry ich, fungus or bacteria without showing it. A ${QDAYS}-day quarantine is the safe way, boss: a sick one is treated there and joins your tank healthy.</div>
  ${owns('qt')?`<button class="btn green wide" style="margin-bottom:6px" onclick="stDeliver120(true)">🧪 QUARANTINE ${QDAYS} DAYS (recommended)</button>${due.length>qFreeV120()?`<div class="meta" style="font-size:11px;color:#ffb347;margin:-2px 0 6px">The quarantine tank has room for ${qFreeV120()} more; the other ${due.length-qFreeV120()} would go straight into your tanks.</div>`:''}`:`<button class="btn green wide" style="margin-bottom:6px" onclick="stBuyQt120(2)">🧪 BUY A QUARANTINE TANK (🪙 350) · recommended</button>`}
  <button class="btn wide" style="background:#a34040;margin-bottom:4px" onclick="stDeliver120(false)">⚠️ STRAIGHT TO THE MAIN TANK</button>
  <div class="meta" style="font-size:11px;opacity:.85">At your own risk: a sick fish brings its disease into your tank, and it can spread.</div></div>`,'QUARANTINE');
 /* only the two choices: the pop-up's own bottom button is hidden (pop() rebuilds it for every other pop-up) */
 {const btn=document.querySelector('#popup > .btn:last-child');if(btn)btn.style.display='none';}
}
window.stDeliver120=function(q){
 try{const due=dueOrdersV120();if(!due.length){if(typeof closePop==='function')closePop();delivering=false;return;}
  st.ord120=st.ord120.filter(o=>o.due>st.day);let sickIn=[],inQ=0,inT=0;
  if(q&&!owns('qt'))q=false;let room=qFreeV120();
  due.forEach(o=>{const toQ=q&&room>0;if(toQ)room--;const f=o.fish,dst=!toQ?[st.fish,st.fry].find(a=>Array.isArray(a)&&a.length<7):null;
   if(toQ||!dst){st.quar120.push({fish:f,until:st.day+QDAYS,sick:o.sick});inQ++;}
   else{if(o.sick){const r=Math.random();f.disease=r<.6?'ich':r<.8?'fungus':'bacteria';f.sickDays=0;f.treatment=null;f.health=Math.max(10,(f.health||100)-15);sickIn.push(f);}dst.push(f);inT++;}});
  save();if(typeof closePop==='function')closePop();delivering=false;
  if(sickIn.length)toast(`⚠️ A new ${sname(sickIn[0])} brought ${sickIn[0].disease} into your tank! Treat it fast.`);
  else toast(inT?`✅ ${inT} new fish went straight into your tanks`+(inQ?` · ${inQ} in quarantine (tanks full)`:''):`🧪 ${inQ} new fish in quarantine for ${QDAYS} days`);
  marcoLeaveV120();setTimeout(()=>{try{toast(`📦 Marco will be back on day ${nextMondayV120()} with a new shipment`);}catch(e){}},2600);if($('st120panel'))panel();
 }catch(e){console.error('AFNICA store delivery',e);}
};
/* in the shop Marco walks in with the box, stops by the counter (thumbs up), then waves and leaves after the choice */
function marcoVisitV120(){
 const MP=window.ST120_MARCO;if(!MP||!MP.box||!$('st120stage')||ST.cust.some(c=>c.marco))return false;
 const parts=mkSprite(MP.box,.52,null);
 const c={marco:true,type:'shopper',budget:0,sense:1,pi:-1,id:++ST.uid,sz:1,parts,x:DOOR.x,y:DOOR.y,hx:1,hy:.3,speed:0,maxSp:50,phase:0,face:1,faceT:1,alpha:0,state:'marco',path:[],seed:1,visits:[],slot:null,want:null,t:0,wait:0,bagged:false,pointing:false,bubT:0,leaving:false};
 $('st120stage').appendChild(parts.el);ST.cust.push(c);sndV120('bell');route(c,[{x:110,y:372},{x:548,y:398}]);return true;
}
function marcoStillV120(c,src){const P=c.parts;P.rig={R:null};P.img.src=src;P.img.style.display='block';P.cv.style.display='none';c.face=c.faceT=1;}
const nextMondayV120=()=>(weekOf(st.day)+1)*7+1;
function marcoLeaveV120(){
 const c=ST.cust.find(x=>x.marco);if(!c)return;const MP=window.ST120_MARCO||{};
 if(MP.wave)marcoStillV120(c,MP.wave);bubble(c,'See you next week! 👋',1.8);c.state='marcoGo';c.t=2;
}
/* release from quarantine/* release from quarantine (any screen): sick ones were caught and treated there */
function quarTickV120(){
 const q=st.quar120;if(!q||!q.length)return;let changed=false;
 for(let i=0;i<q.length;i++){const x=q[i];if(x.until>st.day)continue;
  const dst=[st.fish,st.fry].find(a=>Array.isArray(a)&&a.length<7);if(!dst)continue;
  q.splice(i,1);i--;dst.push(x.fish);changed=true;
  if(x.sick){st.coins=Math.max(0,st.coins-20);toast(`🧪 ${sname(x.fish)} had white spot in quarantine: treated (🪙 20) and released healthy`);}
  else toast(`✅ ${sname(x.fish)} passed quarantine and joined your ${dst===st.fish?'Main':'Fry'} Tank`);}
 if(changed){save();try{if($('st120panel'))panel();}catch(e){}}
}
setInterval(()=>{try{if(typeof st==='undefined'||!st||!st.started)return;ensureStoreV120();
 if(st.imp120.week!==weekOf(st.day))makeOffersV120();
 if(isMonday(st.day)&&!st.imp120.shown){const ov=document.getElementById('overlay');if(!ov||!ov.classList.contains('show')){stImport120();}}
 quarTickV120();
 if(!delivering&&dueOrdersV120().length){const ov=document.getElementById('overlay');if(!ov||!ov.classList.contains('show')){delivering=true;if(!marcoVisitV120())deliveryPopV120();}}
}catch(e){console.error('AFNICA store weekly',e);}},2500);

/* ---------- the quarantine tank (TANK tab, once bought) ---------- */
let QG=0;
window.renderQuarV120=function(){
 try{ensureHealthState();ensureStoreV120();setAfnicaScreenV104('quar');const e=$('screen');if(!e)return;const q=st.quar120||[];
  const row=x=>{const start=x.until-QDAYS,d=Math.min(QDAYS,Math.max(0,st.day-start)),found=x.sick&&st.day>=start+2;
   return `<div class="st120row"><div class="av">${avV120(x.fish,56,34)}</div><div class="in"><b>${sname(x.fish)} ${x.fish.sex==='M'?'♂':'♀'}</b><small>${found?'💊 white spot found · being treated':'looks healthy'} · day ${d}/${QDAYS} · ${x.until>st.day?'ready on day '+x.until:'ready, waiting for room (7 fish per tank)'}</small></div></div>`;};
  e.innerHTML=v8Top()+`<div class="qt120" id="qt120"><div class="w"></div><div class="sd"></div><i class="ht"></i><i class="air"></i><div class="lbl">🧪 QUARANTINE · ${q.length}/${QCAP}</div><div class="fb" id="qt120fb"></div><div class="gl"></div></div>
   <div class="v8panel"><div class="v8head"><b>🧪 QUARANTINE TANK</b><span>${q.length}/${QCAP}</span></div><div class="meta">New fish from Marco stay here ${QDAYS} days before joining your tanks. A sick one is treated here (🪙 20) and leaves healthy.</div>${q.map(row).join('')||'<div class="meta">Empty. Fish you put in quarantine from Marco’s deliveries show up here.</div>'}</div>`+v8Nav('home');
  const fb=$('qt120fb'),els=q.map(x=>{const d=document.createElement('div');d.className='qf'+(isBottom(x.fish)?' bt':'');d.innerHTML=avV120(x.fish,44,26);fb.appendChild(d);
   const b=isBottom(x.fish);return {el:d,q:{x:20+Math.random()*240,y:b?150:20+Math.random()*100,tx:0,ty:0,w:Math.random()*2,f:1,fs:1,bot:b}};});
  const gen=++QG;let last=performance.now();
  const tick=now=>{if(gen!==QG||!document.getElementById('qt120'))return;requestAnimationFrame(tick);const dt=Math.min(.1,(now-last)/1000);last=now;const W2=fb.clientWidth||300;
   els.forEach(o=>{const q=o.q;if(q.w>0)q.w-=dt;else{const dx=q.tx-q.x,dy=q.ty-q.y,d=Math.hypot(dx,dy);if(d<2){q.w=q.bot?1+Math.random()*3:Math.random()*1.5;q.tx=10+Math.random()*(W2-60);q.ty=q.bot?146+Math.random()*6:14+Math.random()*110;}
    else{const sp=q.bot?6:14,st2=Math.min(d,sp*dt);q.x+=dx/d*st2;q.y+=dy/d*st2;if(Math.abs(dx)>2)q.f=dx>0?1:-1;}}q.fs+=(q.f-q.fs)*Math.min(1,dt*6);
    o.el.style.transform=`translate(${q.x.toFixed(1)}px,${q.y.toFixed(1)}px) scaleX(${(FISHFACE*Math.sign(q.fs||1)*Math.max(.15,Math.abs(q.fs))).toFixed(3)})`;});};
  requestAnimationFrame(tick);
 }catch(err){console.error('AFNICA quarantine tank',err);}
};

/* ---------- screen ---------- */
window.renderStoreV120=function(force){
 try{
  if(force!==true&&$('st120stage')&&ST.gen&&typeof afnicaActiveScreen!=='undefined'&&afnicaActiveScreen==='store'){syncFish();panel();return;}   /* already open: keep the shop as it is */
  ensureHealthState();ensureStoreV120();setAfnicaScreenV104('store');
  const e=$('screen');if(!e)return;
  dayCheck();
  st.storeFish.forEach(f=>{delete f._res120;delete f._net120;});st.fish.concat(st.fry).forEach(f=>{delete f._from;});
  const away=batchSim();
  e.innerHTML=v8Top()+sceneHTML()+'<div id="st120panel"></div>'+v8Nav('store');
  XS.P.by=XS.F.by=null;ST.friendNext=false;ST.cust=[];ST.queue=[];ST.pay=null;ST.says=[];ST.chatNext=0;ST.els=new Map();ST.door=false;ST.next=2.5;ST.sec=0;ST.saveT=0;ST.last=performance.now();
  ST.clerk={c:null,ph:'idle',t:0,part:0,parts:null,bubT:0,offerEl:null};
  buildSlots();
  const cl=mkOwner();$('st120clerk').appendChild(cl.el);ST.clerk.parts=cl;
  syncFish();panel();coinsUI();todV120();
  setTimeout(()=>{try{if(!ST.clerk.c)ownerSay(st.storeFish.length?pickV120(['Welcome back, boss! 😊','Morning, boss! ☕','All set, boss! 🐟']):'Boss, we need fish to sell! 🐟',2.6);}catch(e){}},900);
  const msgs=[],sm=st.store.lastSummary;
  if(away.n)msgs.push(`<div style="text-align:left;margin-bottom:10px"><b>While you were away</b><br>${away.n} customers visited · ${away.sales} sales · 🪙 ${away.revenue}</div>`);
  if(sm&&!sm.shown){sm.shown=true;msgs.push(`<b>Day ${sm.day} summary</b>`+summaryHTML(sm));}
  if(msgs.length){try{pop('🏪 STORE REPORT',msgs.join('<hr style="opacity:.2">'),'OK');save();}catch(er){}}
  const gen=++ST.gen;
  requestAnimationFrame(n=>loop(n,gen));
 }catch(err){console.error('AFNICA store render',err);}
};
window.storeDebugV120=function(){return {fishImg:fishImgV120,S:ST,st:st.store,fish:st.storeFish,spawn,evaluate,fairV120,priceV120,sellV120,dayCheck,batchSim,newProfile};};
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
