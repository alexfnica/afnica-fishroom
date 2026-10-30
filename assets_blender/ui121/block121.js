/* V17.121 screen system. One screen at a time inside #screen, a persistent top bar and bottom nav. Existing renderers are wrapped (they
   still build their own HTML); panels are moved, never rewritten. Switch off with window.UI121=false before the page loads. */
(function(){
if(window.UI121===false)return;
const $=id=>document.getElementById(id);
const NAVMAP={home:'home',tank:'tank',breed:'breed',market:'market'};
const TITLES={home:'FISHROOM',breed:'BREEDING',market:'ORDERS',dex:'FISHDEX',shop:'SUPPLIES',store:'MY FISH STORE',progress:'PROGRESS',settings:'SETTINGS',avatar:'CHARACTER'};
let cur='home',hist=[],breedTab='info',onBreeder=false,onQuar=false,guard=0,unread=0,badgeAt=0,explicitTank=false,tapped=false,sheetOpen=false,sheetScroll=0;
window.addEventListener('pointerdown',()=>{tapped=true},{once:true,capture:true});
const events=[];
const arrFor=k=>k==='fry'?st.fry:k==='breeder'?st.breederTank:st.fish;
const alive=a=>(a||[]).filter(f=>f&&!f.dead).length;
const tankName=k=>k==='fry'?'FRY TANK':k==='breeder'?'BREEDER TANK':k==='quar'?'QUARANTINE TANK':'MAIN TANK';
/* V17.120: the quarantine tank (bought in the store) is the last tank of the Tank tab */
const quarOpen=()=>!!(window.quarOwnedV120&&window.quarOwnedV120());
const tankList=()=>['main','fry'].concat(breederOpen()?['breeder']:[],quarOpen()?['quar']:[]);
const breederOpen=()=>!!(st.unlockedTanks&&st.unlockedTanks.tank3);
/* the tank the Tank tab is showing: main / fry from v8Tank, or the Breeder Tank (its own renderer) */
const curTank=()=>onQuar?'quar':onBreeder?'breeder':(typeof v8Tank==='string'&&v8Tank!=='breeder'?v8Tank:'main');
const openTank=k=>{if(k==='quar'&&window.renderQuarV120){window.renderQuarV120();return;}onQuar=false;if(k==='breeder')renderV103Breeder();else{onBreeder=false;switchTankV8(k);}};
const safe=(fn,tag)=>{try{return fn()}catch(e){console.error('AFNICA ui121 '+(tag||''),e)}};

/* ---------- save defaults ---------- */
const oldEnsure=window.ensureHealthState;
window.ensureHealthState=function(){
 const r=oldEnsure.apply(this,arguments);
 try{const a=st.ach121;if(!a||typeof a!=='object')st.ach121={claimed:{},fryPeak:0};else{if(!a.claimed||typeof a.claimed!=='object')a.claimed={};if(typeof a.fryPeak!=='number')a.fryPeak=0;}}
 catch(e){console.error('AFNICA ui121 defaults',e);}
 return r;
};

/* ---------- notices: state-derived list + recent events (toasts) ---------- */
function notices(){
 const out=[];
 [['main','Main Tank'],['fry','Fry Tank'],['breeder','Breeder Tank']].forEach(([k,nm])=>{
  if(k==='breeder'&&!breederOpen())return;
  const a=arrFor(k)||[];if(!alive(a)&&!(a||[]).length)return;
  safe(()=>{const d=tankFoodStreak(k);if(d>=3&&alive(a))out.push({ic:d>=5?'🔴':'⚠️',tx:nm+': '+(d>=5?'starving':'hungry')+' · '+d+' days without food',go:k});},'food');
  safe(()=>{const s=diseaseSummaryFor(a);if(s.sick.length)out.push({ic:'🚨',tx:nm+': '+s.sick.length+' sick fish',go:k});},'sick');
  safe(()=>{const n=deadFishCountV122(k);if(n>0)out.push({ic:'☠️',tx:nm+': '+n+' dead fish to remove',go:k});},'dead');
 });
 safe(()=>{if(st.generalTreatment)out.push({ic:'💊',tx:'General treatment · day '+st.generalTreatment.day+'/3',go:'main'});},'treat');
 safe(()=>{if(coryAdultReadinessV172().ready&&!st.corySpawn)out.push({ic:'🐟',tx:'Corydoras are adults and ready to spawn',go:'breed'});},'cory');
 safe(()=>{if(st.corySpawn)out.push({ic:'🥚',tx:'Corydoras eggs will hatch next day',go:'breed'});},'spawn');
 safe(()=>{if(window.importNoticesV120)window.importNoticesV120().forEach(n=>out.push(n));},'import');
 safe(()=>{const n=achList().filter(x=>x.done&&!x.claimed).length;if(n)out.push({ic:'🏆',tx:n+' achievement reward'+(n>1?'s':'')+' ready to claim',go:'progress'});},'ach');
 return out;
}
function badgeCount(){return notices().length+unread}
function refreshHead(force){
 const now=performance.now();if(!force&&now-badgeAt<400)return;badgeAt=now;
 safe(()=>{
  const n=(st.fry||[]).filter(f=>f&&!f.dead).length;if(st.ach121&&n>st.ach121.fryPeak)st.ach121.fryPeak=n;
  const c=$('u121Coins');if(!c)return;
  c.textContent='🪙 '+st.coins;$('u121Lvl').textContent='⭐ L'+st.playerLevel;$('u121Food').textContent='🍽️ '+st.food;
  const b=badgeCount();$('u121Badge').textContent=b?String(b):'';$('u121Badge').dataset.n=b;
 },'head');
}
const oldUi=window.ui;
window.ui=function(){const r=oldUi.apply(this,arguments);refreshHead();return r;};
const oldToast=window.toast;
window.toast=function(t){
 try{if(/fry|born|hatch|spawn|sick|dead|died|disease|hungry|starv|treat|egg|level|order|achiev|sold|reward/i.test(String(t))){events.unshift({t:String(t),at:Date.now()});if(events.length>20)events.length=20;unread++;refreshHead(true);}}catch(e){}
 return oldToast.apply(this,arguments);
};

/* ---------- shell ---------- */
function buildShell(){
 if($('u121Head'))return;
 const app=document.querySelector('.app'),scr=$('screen');if(!app||!scr)return;
 const head=document.createElement('div');head.id='u121Head';head.className='u121Head';
 head.innerHTML='<button class="u121Back" id="u121Back" onclick="u121back()" aria-label="Back">←</button><b id="u121Title">FISHROOM</b><button class="u121Pill" id="u121Lvl" onclick="u121go(\'progress\')"></button><button class="u121Pill" id="u121Coins" onclick="u121go(\'shop\')"></button><button class="u121Pill" id="u121Food" onclick="u121go(\'shop\')"></button><button class="u121Bell" id="u121Bell" onclick="u121layer(\'notes\')" aria-label="Notifications">🔔<i id="u121Badge" data-n="0"></i></button>';
 app.insertBefore(head,scr);
 const nav=document.createElement('div');nav.id='u121Nav';nav.className='u121Nav';
 nav.innerHTML=[['home','🏠','HOME'],['tank','🐠','TANK'],['breed','❤️','BREEDING'],['market','📦','ORDERS'],['more','☰','MORE']].map(n=>`<button data-k="${n[0]}" onclick="u121nav('${n[0]}')"><em>${n[1]}</em>${n[2]}</button>`).join('');
 app.insertBefore(nav,scr.nextSibling);
 const lay=document.createElement('div');lay.id='u121Layer';lay.className='u121Layer';lay.onclick=e=>{if(e.target===lay)u121layer(false)};
 lay.innerHTML='<div class="u121Panel" id="u121LayerBody"></div>';
 app.appendChild(lay);
}
function setNav(name){
 const slot=NAVMAP[name]||'more';
 document.querySelectorAll('#u121Nav button').forEach(b=>b.classList.toggle('on',b.dataset.k===slot));
}
function titleFor(name){return name==='tank'?'TANK':(TITLES[name]||'AFNICA');}

/* called after every screen render: bookkeeping, header, nav, transition */
function deco(name,opts){
 if(guard)return;
 const scr=$('screen');if(!scr)return;
 buildShell();
 document.body.classList.add('ui121');
 const same=name===cur,saved=same?scr.scrollTop:0;
 let dir='fwd';
 if(!same){if(opts&&opts.back)dir='back';else{hist.push(cur);if(hist.length>12)hist.shift();}cur=name;sheetOpen=false;sheetScroll=0;}
 document.body.classList.toggle('u121tank',name==='tank');document.body.classList.toggle('u121shop',name==='shop');
 $('u121Title').textContent=titleFor(name);
 $('u121Back').style.visibility=name==='home'?'hidden':'visible';
 setNav(name);layer(false);
 if(!same){
  scr.classList.remove('u121In','u121InBack','u121Fade');void scr.offsetWidth;
  scr.classList.add(name==='tank'||name==='breed'?'u121Fade':dir==='back'?'u121InBack':'u121In');
  setTimeout(()=>scr.classList.remove('u121In','u121InBack','u121Fade'),260);
 }else if(saved)scr.scrollTop=saved;
 refreshHead(true);
}

/* ---------- navigation ---------- */
function go(name,opts){
 safe(()=>{
  setAfnicaScreenV104(name);
  if(name==='home')showHome();
  else if(name==='tank'){if(onQuar&&quarOpen()&&window.renderQuarV120){window.renderQuarV120();return;}if(onBreeder&&breederOpen()){renderV103Breeder();return;}explicitTank=true;try{renderV8('home')}finally{explicitTank=false}}
  else if(name==='breed')showBreed(breedTab);
  else if(name==='market')renderV10Market();
  else if(name==='dex')renderV8('dex');
  else if(name==='shop')renderV8('shop');
  else if(name==='store')showStore();
  else if(name==='progress')showProgress();
  else if(name==='settings')showSettings();
  else if(name==='avatar'&&typeof window.u122Picker==='function')window.u122Picker();
 },'go '+name);
}
window.u121go=go;
window.u121nav=function(k){if(k==='more'){layer('more');return;}layer(false);go(k);};
window.u121back=function(){layer(false);const p=hist.pop();const t=p&&p!==cur?p:'home';const prev=cur;go(t);/* go() recorded the jump as forward: drop it */if(hist[hist.length-1]===prev)hist.pop();};
window.u121tank=function(k){layer(false);openTank(k);};
window.u121cycle=function(dir){
 const list=tankList(),i=Math.max(0,list.indexOf(curTank())),n=list[(i+dir+list.length)%list.length];
 openTank(n);
};
function layer(kind){
 const L=$('u121Layer');if(!L)return;
 if(!kind){L.classList.remove('open');return;}
 const body=$('u121LayerBody');
 if(kind==='more'){
  body.innerHTML='<div class="u121Grid"><button onclick="u121go(\'dex\')"><em>🐟</em>FISHDEX</button><button onclick="u121go(\'shop\')"><em>🛒</em>SUPPLIES</button><button onclick="u121go(\'store\')"><em>🏪</em>MY STORE</button><button onclick="u121go(\'progress\')"><em>🏆</em>PROGRESS</button><button onclick="u121go(\'settings\')"><em>⚙️</em>SETTINGS</button></div>';
 }else{
  unread=0;refreshHead(true);
  const ns=notices();
  body.innerHTML='<div class="u121Sub"><b>NOTIFICATIONS</b><span>'+ns.length+'</span></div>'+(ns.length?ns.map(noticeRow).join(''):'<div class="u121Card"><div class="ic">✅</div><div class="tx"><b>All quiet</b><small>Nothing needs your attention.</small></div></div>')
   +(events.length?'<div class="u121Sub"><b>RECENT</b></div>'+events.map(e=>`<div class="u121Card"><div class="tx"><b>${e.t.replace(/</g,'&lt;')}</b><small>${new Date(e.at).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</small></div></div>`).join(''):'');
 }
 L.classList.add('open');
}
window.u121layer=layer;
function noticeRow(n){return `<div class="u121Card warn"><div class="ic" style="font-size:22px">${n.ic}</div><div class="tx"><b>${n.tx}</b></div><button class="go" onclick="u121notice('${n.go}')">GO</button></div>`}
window.u121notice=function(g){layer(false);if(g==='import'&&window.stImport120){window.stImport120();return;}if(g==='breed'){go('breed');}else if(g==='progress')go('progress');else openTank(g);};

/* ---------- wrap existing renderers ---------- */
const oldRenderV8=window.renderV8;
window.renderV8=function(s){
 if(s==='breed'&&!guard){showBreed(breedTab);return;}
 /* at load, bootAfnica and later blocks re-render the tank by themselves: until the first tap those calls open Home instead */
 if(s==='home'&&!guard&&!explicitTank&&!tapped&&performance.now()<9000){showHome();return;}
 const sb=$('u121Sheet')&&$('u121Sheet').lastElementChild;if(sb)sheetScroll=sb.scrollTop;   /* the tank screen is rebuilt by every action: keep the sheet as it was */
 if(s==='home'){onBreeder=false;onQuar=false;}
 const r=oldRenderV8.apply(this,arguments);
 if(!guard)safe(()=>{
  if(s==='dex'){deco('dex');}
  else if(s==='shop'){deco('shop');}
  else{deco('tank');decoTank();}
 },'renderV8 '+s);
 return r;
};
const oldMarket=window.renderV10Market;
window.renderV10Market=function(){const r=oldMarket.apply(this,arguments);safe(()=>deco('market'),'market');return r;};
const oldRoom=window.renderV9Fishroom;
window.renderV9Fishroom=function(){if(guard)return oldRoom.apply(this,arguments);showHome();};
const oldBreeder=window.renderV103Breeder;
window.renderV103Breeder=function(){
 const r=oldBreeder.apply(this,arguments);
 onBreeder=true;onQuar=false;
 if(!guard)safe(()=>{deco('tank');document.body.classList.remove('u121tank');   /* the Tank tab, but the breeder page keeps its own tall layout */
  const sc=$('screen');tankBar(sc,'breeder',sc.firstElementChild);},'breeder');
 return r;
};
if(typeof window.renderQuarV120==='function'){
 const oldQuar=window.renderQuarV120;
 window.renderQuarV120=function(){const r=oldQuar.apply(this,arguments);onQuar=true;onBreeder=false;
  if(!guard)safe(()=>{deco('tank');document.body.classList.remove('u121tank');const sc=$('screen');tankBar(sc,'quar',sc.firstElementChild);},'quar');return r;};
}
if(typeof window.renderStoreV120==='function'){
 const oldStore=window.renderStoreV120;
 window.renderStoreV120=function(){const r=oldStore.apply(this,arguments);if(!guard)safe(()=>deco('store'),'store');return r;};
}
const oldRender=window.render;
window.render=function(s){
 if(s==='start')document.body.classList.remove('ui121','u121tank');
 return oldRender.apply(this,arguments);
};

/* ---------- Home ---------- */
function showHome(){
 /* V17.122 draws the illustrated fishroom with the player's character; the card Home below is the fallback */
 if(typeof window.u122Home==='function'){let ok=false;try{ok=window.u122Home()}catch(e){console.error('AFNICA ui121 home122',e)}if(ok)return;}
 setAfnicaScreenV104('home');ensureHealthState();
 const need=xpNeededV9(st.playerLevel),pct=Math.min(100,st.xp/need*100);
 const dm=dailyFor('main'),df=dailyFor('fry'),done=[dm.feed,dm.water,dm.clean].filter(Boolean).length;
 const card=(k,ic,nm,open,locked)=>{
  if(locked)return `<div class="u121Card"><div class="ic">${ic}</div><div class="tx"><b>${nm}</b><small>🔒 Locked</small></div><button class="go" onclick="unlockTank3V9()">UNLOCK</button></div>`;
  const a=arrFor(k)||[],issues=[];
  safe(()=>{const d=tankFoodStreak(k);if(d>=5)issues.push('Starving');else if(d>=3)issues.push('Hungry')},'f');
  safe(()=>{const s=diseaseSummaryFor(a);if(s.sick.length)issues.push(s.sick.length+' sick')},'s');
  safe(()=>{const n=deadFishCountV122(k);if(n>0)issues.push(n+' dead')},'d');
  let h=100;safe(()=>{h=tankHealthFor(k)},'h');
  return `<div class="u121Card ${issues.length?'warn':''}"><div class="ic">${ic}</div><div class="tx"><b>${nm}</b><small><span class="u121Dot ${issues.length?'':'ok'}"></span>${issues.length?issues.join(' · '):'All good'} · ${alive(a)} fish · ${h}%</small></div><button class="go" onclick="${open}">OPEN</button></div>`;
 };
 const ns=notices().slice(0,3);
 $('screen').innerHTML=`<div class="u121Card" style="margin-bottom:10px"><div class="v9LevelOrb" style="flex:none">${st.playerLevel}</div><div class="tx"><b>FISHROOM LEVEL ${st.playerLevel}</b><div class="v9XP" style="margin-top:5px"><i style="width:${pct}%"></i></div><small>${st.xp}/${need} XP · DAY ${st.day}</small></div></div>
 <div class="u121Sub"><b>YOUR TANKS</b><span>${[st.unlockedTanks&&st.unlockedTanks.main,st.unlockedTanks&&st.unlockedTanks.fry,breederOpen()].filter(Boolean).length}/3</span></div>
 ${card('main','🐠','Main Tank',"switchTankV8('main')")}${card('fry','🐣','Fry Tank',"switchTankV8('fry')")}${card('breeder','🧬','Breeder Tank',"u121tank('breeder')",!breederOpen())}
 ${ns.length?'<div class="u121Sub"><b>NEEDS ATTENTION</b><span onclick="u121layer(\'notes\')" style="cursor:pointer">SEE ALL ›</span></div>'+ns.map(noticeRow).join(''):''}
 <div class="u121Card" style="margin-top:10px"><div class="ic">✅</div><div class="tx"><b>TODAY · ${done}/3 DONE (MAIN)</b><small>Fry Tank: ${[df.feed,df.water,df.clean].filter(Boolean).length}/3 · feed · water · clean</small></div><button class="go" onclick="u121nextDay()">NEXT DAY →</button></div>
 <div class="u121Quick"><button onclick="u121go('dex')">🐟 FISHDEX</button><button onclick="u121go('shop')">🛒 SUPPLIES</button><button onclick="u121go('store')">🏪 MY STORE</button><button onclick="u121go('progress')">🏆 PROGRESS</button></div>`;
 deco('home');
}
/* every NEXT DAY (Home, Progress, the sheet's old button, the breeder button) runs under the guard so its own re-render does not
   change the screen or the history; the screen is rebuilt afterwards */
const oldNextDay=window.nextDay;
window.nextDay=function(){
 if(guard||!document.body.classList.contains('ui121'))return oldNextDay.apply(this,arguments);
 const keep=cur;let r;
 guard++;try{r=oldNextDay.apply(this,arguments);}catch(e){console.error('AFNICA ui121 nextDay',e);}finally{guard--;}
 go(keep);return r;
};
window.u121nextDay=function(){window.nextDay();};

/* ---------- Tank screen ---------- */
/* the tank bar (arrows + one dot per tank + name) shared by Main, Fry and the Breeder Tank */
function tankBar(scr,k,before){
 const list=tankList();
 const bar=document.createElement('div');bar.className='u121TankBar';
 bar.innerHTML=`<button onclick="u121cycle(-1)" aria-label="Previous tank">◀</button><div>${list.map(x=>`<i class="${x===k?'on':''}"></i>`).join('')}<span>${tankName(k)}</span></div><button onclick="u121cycle(1)" aria-label="Next tank">▶</button>`;
 if(before&&before.parentNode===scr)scr.insertBefore(bar,before);else scr.prepend(bar);
 return bar;
}
function decoTank(){
 const scr=$('screen'),hero=scr.querySelector('.v8hero');if(!hero)return;
 const k=curTank();
 const bar=tankBar(scr,k,hero);



 /* details sheet: every panel that used to sit under the tank, moved as is */
 const sheet=document.createElement('div');sheet.className='u121Sheet';sheet.id='u121Sheet';
 sheet.innerHTML='<div class="u121SheetHead"><b>FISH & TANK DETAILS</b><button onclick="u121sheet(false)" aria-label="Close">✕</button></div><div class="u121SheetBody"></div>';
 const body=sheet.lastElementChild;
 [...scr.children].forEach(n=>{if(n!==hero&&n!==bar&&n!==sheet&&(n.classList.contains('v8panel')||n.classList.contains('v8quests')||n.classList.contains('diseaseAlert')))body.appendChild(n);});
 scr.appendChild(sheet);
 if(sheetOpen){sheet.classList.add('open');body.scrollTop=sheetScroll;}
 /* the sick/dead panels are inside the sheet now: show a warning on the tank bar */
 const w=notices().filter(n=>n.go===k).length;
 if(w){const lab=bar.children[1];lab.insertAdjacentHTML('beforeend',`<b style="color:#ffb347;cursor:pointer" onclick="u121sheet(true)">⚠ ${w}</b>`);}
 /* the dock's FISH button opened the dex; it now opens the details sheet (the dex is under MORE) */
 hero.querySelectorAll('.v8dock button').forEach(b=>{if(/renderV8\('dex'\)/.test(b.getAttribute('onclick')||'')){b.setAttribute('onclick','u121sheet(true)');const s=b.querySelector('small');if(s)s.textContent='FISH';}});
}
window.u121sheet=function(open){sheetOpen=!!open;const s=$('u121Sheet');if(s)s.classList.toggle('open',sheetOpen);};

/* ---------- Breeding ---------- */
/* Breeding = the breeding guide and status only; the Breeder Tank and the Fry Tank are tanks (Tank tab) */
window.u121breedTab=function(){showBreed();};
function showBreed(){
 breedTab='info';
 setAfnicaScreenV104('breed');ensureHealthState();
 const scr=$('screen');
 const broods=Array.isArray(st.broods45)?st.broods45.length:0;
 scr.innerHTML=`<div class="u121Card"><div class="ic">🧬</div><div class="tx"><b>Breeder Tank</b><small>${breederOpen()?alive(st.breederTank)+' fish · pair them up there':'locked'}</small></div>${breederOpen()?`<button class="go" onclick="u121tank('breeder')">OPEN</button>`:''}</div>
 <div class="u121Card"><div class="ic">🤰</div><div class="tx"><b>Broods expected</b><small>${broods} female${broods===1?'':'s'} carrying fry in your tanks</small></div></div>
 ${st.corySpawn?'<div class="u121Card"><div class="ic">🥚</div><div class="tx"><b>Corydoras spawn</b><small>Eggs hatch next day. Open the Fry Tank to see the fry.</small></div></div>':''}
 ${breedHTML()}${coryReadinessPanelV172()}`;
 deco('breed');
}
function decoBreed(){}

/* ---------- Store / Settings ---------- */
function showStore(){
 if(typeof window.renderStoreV120==='function'&&window.STORE120!==false){window.renderStoreV120();return;}
 setAfnicaScreenV104('store');
 $('screen').innerHTML='<div class="u121Card" style="margin-top:20px;flex-direction:column;text-align:center;padding:30px 16px"><div style="font-size:54px">🏪</div><b style="font-size:16px">FISH STORE</b><small style="margin-top:6px">Coming soon: open your own fish store and serve customers.</small></div>';
 deco('store');
}
function showSettings(){
 setAfnicaScreenV104('settings');ensureHealthState();
 $('screen').innerHTML=`<div class="u121Sub"><b>SOUND</b></div>
 <div class="u121Card"><div class="ic">${st.soundOn?'🔊':'🔇'}</div><div class="tx"><b>Sound & ambience</b><small>${st.soundOn?'On':'Off'}</small></div><button class="go" onclick="toggleSoundV141();u121go('settings')">${st.soundOn?'TURN OFF':'TURN ON'}</button></div>
 <div class="u121Sub"><b>SAVE</b></div>
 <div class="u121Card"><div class="ic">💾</div><div class="tx"><b>Export save file</b><small>Download a backup of your game as a JSON file.</small></div><button class="go" onclick="exportSaveV17()">EXPORT</button></div>
 <div class="u121Sub"><b>ABOUT</b></div>
 <div class="u121Card"><div class="ic">🐠</div><div class="tx"><b>AFNICA Aquarium</b><small>Day ${st.day} · screens V17.121</small></div></div>`;
 deco('settings');
}

/* ---------- Progress + achievements ---------- */
function achList(){
 const claimed=(st.ach121&&st.ach121.claimed)||{},fp=(st.ach121&&st.ach121.fryPeak)||0;
 let dex=0;safe(()=>{dex=discoveredV8().size},'dex');
 const total=Object.keys(S).length,sold=st.totalSold||0,ord=st.ordersCompleted||0,bg=st.bestGrade||0,day=st.day||1,lv=st.playerLevel||1,alv=alive(st.fish);
 const stSales=(st.store&&st.store.totalSales)||0;
 const hasSp=sp=>{let r=0;safe(()=>{r=discoveredV8().has(sp)?1:0},'sp');return r};
 const D=[
  ['first_birth','🐣','First birth','Get your first fry',fp,1,50,20],
  ['nursery','👶','Nursery','Have 10 fry at once',fp,10,100,40],
  ['seller','💰','Fish seller','Sell 10 fish',sold,10,100,30],
  ['dealer','💰','Fish dealer','Sell 50 fish',sold,50,300,80],
  ['order1','📦','First contract','Complete 1 market order',ord,1,50,20],
  ['order5','📦','Contract master','Complete 5 market orders',ord,5,150,50],
  ['order20','📦','Market regular','Complete 20 market orders',ord,20,400,120],
  ['dex4','🐟','Collector','Discover 4 species',dex,4,100,40],
  ['dexall','📖','Complete dex','Discover every species',dex,total,400,150],
  ['neon','🔹','Neon school','Discover the neon tetra',hasSp('neon'),1,60,20],
  ['cory','🐟','Cory keeper','Discover the corydoras',hasSp('cory'),1,60,20],
  ['anc','🦈','Bristlenose keeper','Discover the bristlenose',hasSp('anc'),1,100,40],
  ['lv5','⭐','Level 5','Reach fishroom level 5',lv,5,100,0],
  ['lv10','🌟','Level 10','Reach fishroom level 10',lv,10,300,0],
  ['gradeA','🏅','A-grade bloodline','Raise an A-grade fish',bg,3,150,50],
  ['gradeS','🥇','S-grade bloodline','Raise an S-grade fish',bg,4,300,100],
  ['gradeSp','👑','S+ bloodline','Raise an S+ grade fish',bg,5,500,150],
  ['day10','📅','Settled in','Reach day 10',day,10,50,20],
  ['day30','📅','Veteran','Reach day 30',day,30,150,50],
  ['full','🐠','Full tank','Keep 7 fish in the main tank',alv,7,50,20],
  ['rich','🪙','Saver','Hold 1000 coins',st.coins||0,1000,100,30],
  ['shop1','🏪','Shopkeeper','Make your first store sale',stSales,1,100,40],
  ['shop50','🏪','Store star','Make 50 store sales',stSales,50,400,120]
 ];
 return D.map(d=>({id:d[0],ic:d[1],name:d[2],desc:d[3],val:Math.min(d[4],d[5]),max:d[5],coins:d[6],xp:d[7],done:d[4]>=d[5],claimed:!!claimed[d[0]]}));
}
window.u121claim=function(id){
 safe(()=>{
  ensureHealthState();const a=achList().find(x=>x.id===id);if(!a||!a.done||a.claimed)return;
  st.ach121.claimed[id]=1;st.coins+=a.coins;if(a.xp)addXPV9(a.xp);save();
  toast('🏆 '+a.name+' · +'+a.coins+' coins');
  showProgress();
 },'claim');
};
function showProgress(){
 setAfnicaScreenV104('progress');ensureHealthState();
 const need=xpNeededV9(st.playerLevel),pct=Math.min(100,st.xp/need*100),k=(typeof v8Tank==='string'&&v8Tank==='fry')?'fry':'main',d=dailyFor(k);
 const q=[['🍽️','Feed the tank',d.feed],['💧','Change water',d.water],['🧽','Clean the glass',d.clean]];
 const A=achList(),dn=A.filter(x=>x.done).length;
 $('screen').innerHTML=`<div class="u121Card"><div class="v9LevelOrb" style="flex:none">${st.playerLevel}</div><div class="tx"><b>FISHROOM LEVEL ${st.playerLevel}</b><div class="v9XP" style="margin-top:5px"><i style="width:${pct}%"></i></div><small>${st.xp}/${need} XP</small></div></div>
 <div class="u121Sub"><b>DAILY QUESTS · ${tankName(k)}</b><span>${q.filter(x=>x[2]).length}/3</span></div>
 ${q.map(x=>`<div class="u121Ach ${x[2]?'done':''}"><span class="ic">${x[0]}</span><div class="tx"><b>${x[1]}</b></div><span class="rw">${x[2]?'1/1 ✓':'0/1'}</span></div>`).join('')}
 <button class="btn green wide" style="margin:6px 0" onclick="u121nextDay()">NEXT DAY →</button>
 <div class="u121Sub"><b>STATS</b></div>
 <div class="u121Ach"><span class="ic">📦</span><div class="tx"><b>${st.ordersCompleted||0} orders · ${st.totalSold||0} fish sold</b><small>Best bloodline: ${['No graded adults yet','C Grade','B Grade','A Grade','S Grade','S+ Grade'][st.bestGrade]||'Developing'} · ${st.breedingCount||0} breeds</small></div></div>
 <div class="u121Sub"><b>ACHIEVEMENTS</b><span>${dn}/${A.length}</span></div>
 ${A.map(a=>`<div class="u121Ach ${a.done?'done':''} ${a.claimed?'claimed':''}"><span class="ic">${a.ic}</span><div class="tx"><b>${a.name}</b><small>${a.desc}</small><div class="bar2"><i style="width:${a.val/a.max*100}%"></i></div></div><span class="rw">${a.claimed?'✓':a.done?`<button onclick="u121claim('${a.id}')">CLAIM</button>`:''}<div>+${a.coins}🪙${a.xp?' +'+a.xp+'XP':''}</div></span></div>`).join('')}`;
 deco('progress');
}

/* ---------- boot ---------- */
function start(){
 if(!st.started)return;   /* fresh save: the title screen stays shell-free; the first deco() after START builds the shell */
 safe(()=>{buildShell();document.body.classList.add('ui121');
  /* bootAfnica and later blocks re-render the tank a few times at load: open Home once they are done, unless the player already tapped */
  setTimeout(()=>{if(st.started&&!tapped&&cur!=='home')go('home');},900);
 },'start');
}
window.addEventListener('resize',()=>{const s=$('screen');if(s&&cur==='tank')s.scrollTop=0;});
window.u121api={deco:(n)=>deco(n),notices:()=>notices(),noticeRow:(n)=>noticeRow(n),tankName:(k)=>tankName(k),cur:()=>cur,breederOpen:()=>breederOpen(),arrFor:(k)=>arrFor(k)};
window.ui121Debug=()=>({cur,hist:hist.slice(),breedTab,guard,unread,events:events.slice(),notices:notices(),ach:achList()});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
