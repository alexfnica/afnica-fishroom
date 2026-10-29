/* V17.122 player character + illustrated fishroom Home. Needs block V17.121 (screen system) before it. The Gemini characters are embedded by
   install122.py as window.AV122 = {front:{id:dataURI}, walk:{id:dataURI}}. Switch off with window.UI122=false before the page loads. */
(function(){
if(window.UI122===false||!window.AV122||!window.u121api)return;
const $=id=>document.getElementById(id);
const AV=window.AV122,api=window.u121api;
/* id, name, level needed */
const CH=[['05','Luna',1],['01','Mia',1],['11','Leo',1],['10','Rosa',1],['08','Dev',1],['07','Zora',1],['02','Omar',1],['03','Anna',1],
 ['21','Finn',2],['04','Gus',2],['09','Amira',2],['06','Rex',3],['14','Yuki',3],['12','Kit',4],['13','Marcus',4],['19','Jay',5],['20','Hana',5],
 ['15','Paul',6],['16','Dr. Eva',6],['17','Chef Gino',7]].filter(c=>AV.front[c[0]]);
const byId=Object.create(null);CH.forEach(c=>{byId[c[0]]={id:c[0],name:c[1],lvl:c[2]}});
const OUTFITS=['#e8b83a','#2872d7','#d0463e','#2f9d8f','#6b4aa5','#e8e8e8','#2b2d33','#e8739a'];
const safe=(fn,tag)=>{try{return fn()}catch(e){console.error('AFNICA ui122 '+(tag||''),e)}};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let gen=0,sayN=0,rosterScroll=0;

/* ---------- save defaults ---------- */
const oldEnsure=window.ensureHealthState;
window.ensureHealthState=function(){
 const r=oldEnsure.apply(this,arguments);
 try{
  let a=st.avatar122;if(!a||typeof a!=='object')a=st.avatar122={id:'05',name:'',chosen:false,outfit:null};
  if(typeof a.id!=='string'||!byId[a.id])a.id='05';if(typeof a.name!=='string')a.name='';a.name=a.name.slice(0,14);
  if(typeof a.chosen!=='boolean')a.chosen=false;if(typeof a.outfit!=='string'||!/^#[0-9a-f]{6}$/i.test(a.outfit))a.outfit=null;
 }catch(e){console.error('AFNICA ui122 defaults',e);}
 return r;
};
const me=()=>{ensureHealthState();const a=st.avatar122,c=byId[a.id]||byId['05'];return {id:c.id,name:a.name||c.name,outfit:a.outfit,chosen:a.chosen,lvl:c.lvl}};

/* ---------- outfit recolour (canvas) ---------- */
const loadImg=u=>new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=rej;i.src=u});
function rgb2hsv(r,g,b){r/=255;g/=255;b/=255;const m=Math.max(r,g,b),n=Math.min(r,g,b),d=m-n;let h=0;if(d){if(m===r)h=((g-b)/d)%6;else if(m===g)h=(b-r)/d+2;else h=(r-g)/d+4;h/=6;if(h<0)h+=1}return[h,m?d/m:0,m]}
function hsv2rgb(h,s,v){const i=Math.floor(h*6)%6,f=h*6-Math.floor(h*6),p=v*(1-s),q=v*(1-f*s),t=v*(1-(1-f)*s);return[[v,t,p],[q,v,p],[p,v,t],[p,q,v],[t,p,v],[v,p,q]][i].map(x=>Math.round(x*255))}
function hex2rgb(h){const n=parseInt(h.slice(1),16);return[n>>16,(n>>8)&255,n&255]}
/* the outfit colour is sampled from the torso; pixels of that colour between the shoulders and the hips get the new hue, brightness is kept */
function recolor(c,hex){
 const x=c.getContext('2d',{willReadFrequently:true}),W=c.width,H=c.height,id=x.getImageData(0,0,W,H),d=id.data;
 let sr=0,sg=0,sb=0,n=0;
 for(let yy=Math.floor(H*.30);yy<H*.42;yy+=2)for(let xx=Math.floor(W*.40);xx<W*.60;xx+=2){const i=(yy*W+xx)*4;if(d[i+3]>230){sr+=d[i];sg+=d[i+1];sb+=d[i+2];n++}}
 if(!n)return c;
 sr/=n;sg/=n;sb/=n;const [h0,s0]=rgb2hsv(sr,sg,sb),[th,ts]=rgb2hsv(...hex2rgb(hex)),gate=s0>.2;
 const y0=Math.floor(H*.24),y1=Math.floor(H*.5);
 for(let y=y0;y<y1;y++)for(let xx=0;xx<W;xx++){
  const i=(y*W+xx)*4;if(d[i+3]<8)continue;
  const [h,s,v]=rgb2hsv(d[i],d[i+1],d[i+2]);let w=0;
  if(gate){const dh=Math.min(Math.abs(h-h0),1-Math.abs(h-h0));if(dh<.05&&s>s0*.6)w=1;else if(dh<.075&&s>s0*.7)w=.5}
  else{const dist=Math.abs(d[i]-sr)+Math.abs(d[i+1]-sg)+Math.abs(d[i+2]-sb);if(dist<70)w=1-dist/70*.45}
  if(!w)continue;
  const ns=s0<.12?ts*.85:Math.min(1,ts*s/Math.max(.05,s0)),o=hsv2rgb(th,ns,v);
  d[i]+=(o[0]-d[i])*w;d[i+1]+=(o[1]-d[i+1])*w;d[i+2]+=(o[2]-d[i+2])*w;
 }
 x.putImageData(id,0,0);return c;
}
const cache=new Map();
/* returns the picture for a pose ('front' | 'walk') in the chosen outfit colour; a character with no walking picture falls back to the front one */
async function sprite(id,pose,outfit){
 const base=(pose==='walk'&&AV.walk[id])?AV.walk[id]:AV.front[id];
 if(!outfit||!base)return base;
 const key=id+'|'+(pose==='walk'&&AV.walk[id]?'w':'f')+'|'+outfit;
 if(cache.has(key))return cache.get(key);
 const img=await loadImg(base),c=document.createElement('canvas');c.width=img.naturalWidth;c.height=img.naturalHeight;c.getContext('2d').drawImage(img,0,0);
 const url=recolor(c,outfit).toDataURL('image/webp',.9);
 if(cache.size>40)cache.clear();cache.set(key,url);return url;
}

/* ---------- Home ---------- */
const isNight=()=>{let h=new Date().getHours();try{if(window.__afHourOverride!=null&&!isNaN(+window.__afHourOverride))h=+window.__afHourOverride}catch(e){}return h<6||h>=20};
function tankWin(k,nm){
 const open=k==='breeder'&&!api.breederOpen();
 const a=(api.arrFor(k)||[]).filter(f=>f&&!f.dead),ns=api.notices().filter(n=>n.go===k);
 let badge='';
 if(open)badge='<span class="u122Bub">🔒</span>';
 else if(ns.length)badge=`<span class="u122Bub warn">${ns[0].ic}${ns.length>1?' '+ns.length:''}</span>`;
 else if(k==='fry'&&a.length)badge=`<span class="u122Bub ok">🐣 ${a.length}</span>`;
 else badge='<span class="u122Bub ok">✓</span>';
 const fish=open?'':a.slice(0,3).map((f,i)=>`<div class="u122F" style="top:${8+i*24}%;--d:${12+i*8}px;animation-duration:${7+i*2.3}s;animation-delay:${-i*2.1}s">${safe(()=>dexAvatarHTML(f,52,30),'fish')||''}</div>`).join('');
 const fn=open?'unlockTank3V9()':k==='breeder'?"u121tank('breeder')":`switchTankV8('${k}')`;
 return `<div class="u122Tk" onclick="${fn}" role="button" aria-label="${nm}">${badge}<div class="u122Wtr">${fish}</div><i class="u122Sand"></i></div>`;
}
function sayText(m){
 const ns=api.notices(),list=[];
 if(!m.chosen)list.push(`Hi! I'm ${m.name}. Tap 🎨 below to choose who I am.`);
 ns.slice(0,3).forEach(n=>list.push(n.go==='progress'?'You have a reward to claim! Tap 🏆 PROGRESS.':n.tx+(/^(main|fry|breeder)$/.test(n.go)?' Tap that tank!':'')));
 const dm=dailyFor('main'),done=[dm.feed,dm.water,dm.clean].filter(Boolean).length;
 list.push(done<3?`Chores today: ${done}/3 done. Feed, change water, clean the glass.`:`All chores done! Press NEXT DAY when you're ready.`);
 list.push('Your fishroom looks great, boss!');
 return list[sayN++%list.length];
}
function showSay(text){
 const b=$('u122Say');if(!b)return;b.textContent=text;b.classList.add('on');
 clearTimeout(showSay.t);showSay.t=setTimeout(()=>{const x=$('u122Say');if(x)x.classList.remove('on')},6500);
}
window.u122Tap=function(){const m=me();showSay(sayText(m))};
window.u122Door=function(){u121go('store')};
window.u122Home=function(){
 if(!AV.front||!CH.length)return false;
 setAfnicaScreenV104('home');ensureHealthState();
 const m=me(),need=xpNeededV9(st.playerLevel),pct=Math.min(100,st.xp/need*100);
 const dm=dailyFor('main'),df=dailyFor('fry'),done=[dm.feed,dm.water,dm.clean].filter(Boolean).length,ns=api.notices().slice(0,2);
 const g=++gen;
 $('screen').innerHTML=`<div class="u122Room ${isNight()?'night':''}" id="u122Room">
  <div class="u122Win"></div><div class="u122Sign">AFNICA<small>FISHROOM</small></div>
  <div class="u122Shelf">${tankWin('main','Main tank')}${tankWin('fry','Fry tank')}${tankWin('breeder','Breeder tank')}</div>
  <div class="u122Plank"></div><div class="u122Lbl"><span>MAIN</span><span>FRY</span><span>BREEDER</span></div>
  <div class="u122Door" onclick="u122Door()" role="button" aria-label="My store"><i>🏪</i><b>MY STORE</b></div>
  <div class="u122Floor"></div>
  <div class="u122Me idle" id="u122Me" style="left:50%" onclick="u122Tap()" role="button" aria-label="${esc(m.name)}"><div class="u122Say" id="u122Say"></div><img id="u122Img" alt="${esc(m.name)}" style="opacity:0"></div>
 </div>
 <div class="u122Strip"><div class="u122Chip"><b>⭐ LEVEL ${st.playerLevel}</b><div class="u122Xp"><i style="width:${pct}%"></i></div><small>${st.xp}/${need} XP · DAY ${st.day}</small></div>
  <div class="u122Chip"><b>✅ TODAY ${done}/3</b><small>Main ${done}/3 · Fry ${[df.feed,df.water,df.clean].filter(Boolean).length}/3</small></div></div>
 ${ns.length?ns.map(n=>api.noticeRow(n)).join(''):''}
 <div class="u122Btns"><button class="go" onclick="u121nextDay()">NEXT DAY →</button><button class="alt ${m.chosen?'':'pulse'}" onclick="u121go('avatar')">🎨 CHARACTER</button></div>
 <div class="u122Quick"><button onclick="u121go('dex')"><em>🐟</em>FISHDEX</button><button onclick="u121go('shop')"><em>🛒</em>SUPPLIES</button><button onclick="u121go('store')"><em>🏪</em>MY STORE</button><button onclick="u121go('progress')"><em>🏆</em>PROGRESS</button></div>`;
 api.deco('home');
 safe(()=>startCharacter(g,m),'character');
 return true;
};
/* the character: stands facing the player, now and then walks to another spot (side-view picture, flipped when going left), then turns back */
const SPOTS=[27,50,73];
async function startCharacter(g,m){
 /* a picture that cannot be loaded or recoloured falls back to the original, so the character never disappears */
 const [front,walk]=await Promise.all([sprite(m.id,'front',m.outfit).catch(()=>AV.front[m.id]),sprite(m.id,'walk',m.outfit).catch(()=>AV.walk[m.id]||AV.front[m.id])]);
 const img=$('u122Img'),el=$('u122Me');if(g!==gen||!img||!el)return;
 img.src=front;img.onload=()=>{img.style.opacity='1'};if(img.complete)img.style.opacity='1';
 setTimeout(()=>{if(g===gen)showSay(sayText(m))},500);
 const hasWalk=!!AV.walk[m.id];let x=50;
 const step=()=>{
  if(g!==gen||!$('u122Me'))return;
  const opts=SPOTS.filter(s=>Math.abs(s-x)>5),to=opts[Math.floor(Math.random()*opts.length)],dur=Math.abs(to-x)*95;   /* ms: 2.1 s for a 23 % hop, 4.4 s for the longest */
  if(hasWalk){img.src=walk;img.style.transform=to<x?'scaleX(-1)':'none';el.classList.remove('idle');el.classList.add('walk');}
  el.style.transitionDuration=dur+'ms';el.style.left=to+'%';x=to;
  setTimeout(()=>{if(g!==gen||!$('u122Me'))return;img.src=front;img.style.transform='none';el.classList.remove('walk');el.classList.add('idle');el.style.transitionDuration='0ms';
   setTimeout(step,5500+Math.random()*6000);},dur+60);
 };
 setTimeout(step,3500+Math.random()*3000);
}

/* ---------- picker ---------- */
function rosterHTML(m){
 return `<div class="u122Roster" id="u122Roster">${CH.map(c=>{const open=st.playerLevel>=c[2];return `<div class="${c[0]===m.id?'on':''} ${open?'':'lock'}" onclick="u122Pick('${c[0]}')" role="button" aria-label="${esc(c[1])}"><img src="${AV.front[c[0]]}" alt="">${open?'':`<span>L${c[2]}</span>`}</div>`}).join('')}</div>`;
}
window.u122Pick=function(id){
 safe(()=>{
  ensureHealthState();const c=byId[id];if(!c)return;
  if(st.playerLevel<c.lvl){toast('🔒 '+c.name+' unlocks at level '+c.lvl);return;}
  const a=st.avatar122,old=byId[a.id];
  if(!a.name||(old&&a.name===old.name))a.name='';       /* keep a custom name, otherwise follow the character's name */
  a.id=id;a.chosen=true;save();rosterScroll=($('u122Roster')||{}).scrollLeft||0;window.u122Picker(true);
 },'pick');
};
window.u122Outfit=function(hex){safe(()=>{ensureHealthState();st.avatar122.outfit=hex||null;st.avatar122.chosen=true;save();rosterScroll=($('u122Roster')||{}).scrollLeft||0;window.u122Picker(true);},'outfit')};
window.u122Name=function(v){safe(()=>{ensureHealthState();const nm=Array.from(String(v||'').replace(/[<>]/g,'').trim()).slice(0,14).join(''),was=st.avatar122.name||byId[st.avatar122.id].name;
  if(nm===was)return;                                    /* focusing / leaving the field without a change does nothing */
  st.avatar122.name=nm;st.avatar122.chosen=true;save();const l=$('u122StName');if(l)l.textContent=me().name.toUpperCase();},'name')};
window.u122Picker=function(keep){
 if(!AV.front||!CH.length)return;
 setAfnicaScreenV104('avatar');ensureHealthState();gen++;
 const m=me();
 $('screen').innerHTML=`<div class="u122Stage"><span class="u122StName" id="u122StName">${esc(m.name.toUpperCase())}</span><span class="u122StLv">⭐ L${st.playerLevel}</span><img id="u122StImg" alt="${esc(m.name)}" style="opacity:0"></div>
  ${rosterHTML(m)}
  <div class="u122Opt"><b>OUTFIT COLOUR</b><div class="u122Sw"><i class="orig ${m.outfit?'':'on'}" onclick="u122Outfit(null)" title="Original">⟲</i>${OUTFITS.map(c=>`<i class="${m.outfit&&m.outfit.toLowerCase()===c?'on':''}" style="background:${c}" onclick="u122Outfit('${c}')"></i>`).join('')}</div></div>
  <div class="u122Opt"><b>NAME</b><input class="u122Name" maxlength="14" value="${esc(m.name)}" onchange="u122Name(this.value)" onblur="u122Name(this.value)" aria-label="Character name"></div>
  <button class="btn green wide" style="margin-top:12px" onclick="u121back()">DONE</button>`;
 api.deco('avatar');
 const r=$('u122Roster');if(r&&keep)r.scrollLeft=rosterScroll;
 else if(r){const on=r.querySelector('.on');if(on)r.scrollLeft=Math.max(0,on.offsetLeft-r.clientWidth/2+on.clientWidth/2);}
 const g=gen;   /* a slower earlier colour must not overwrite a later one */
 sprite(m.id,'front',m.outfit).catch(()=>AV.front[m.id]).then(u=>{const i=$('u122StImg');if(g!==gen||!i)return;i.src=u;i.onload=()=>{i.style.opacity='1'};if(i.complete)i.style.opacity='1';});
};
window.u122Debug=()=>({gen,me:me(),chars:CH.length,cache:cache.size});
})();
