/* Temporary in-memory mockup: Home room with a real character + character picker with working outfit/hair recolour. Nothing touches the game file or the save. */
const GAME='../AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html';
const CUT='http://127.0.0.1:8791/assets_blender/avatar/cut/';
const CH=[
 ['walk_01_girl_pink_hoodie_bob','Mia'],['walk_02_man_curly_beard','Omar'],['walk_03_woman_blonde_ponytail','Anna'],['walk_04_man_bald_beard_vest','Gus'],
 ['walk_05_girl_braids_raincoat','Luna'],['walk_06_teen_mohawk_leather','Rex'],['walk_07_woman_afro_purple','Zora'],['walk_08_man_bun_glasses','Dev'],
 ['walk_09_woman_hijab','Amira'],['walk_10_grandma_wateringcan','Rosa'],['walk_11_boy_backpack_wateringcan','Leo'],['walk_12_woman_pink_pixie','Kit']];
/* where to sample the outfit / hair colour (fractions of the cut-out) */
const SAMPLE={walk_05_girl_braids_raincoat:{top:[.47,.45],hair:[.47,.09]}};
const loadImg=u=>new Promise((res,rej)=>{const i=new Image();i.crossOrigin='anonymous';i.onload=()=>res(i);i.onerror=rej;i.src=u});
function rgb2hsv(r,g,b){r/=255;g/=255;b/=255;const m=Math.max(r,g,b),n=Math.min(r,g,b),d=m-n;let h=0;if(d){if(m==r)h=((g-b)/d)%6;else if(m==g)h=(b-r)/d+2;else h=(r-g)/d+4;h/=6;if(h<0)h+=1}return[h,m?d/m:0,m]}
function hsv2rgb(h,s,v){const i=Math.floor(h*6),f=h*6-i,p=v*(1-s),q=v*(1-f*s),t=v*(1-(1-f)*s);const m=[[v,t,p],[q,v,p],[p,v,t],[p,q,v],[t,p,v],[v,p,q]][i%6];return m.map(x=>Math.round(x*255))}
/* recolour on a canvas: pixels close to the sampled colour (RGB distance, inside the box) get the target hue/saturation, brightness is kept */
function recolor(c,pt,target,tol,box){
 const x=c.getContext('2d',{willReadFrequently:true}),W=c.width,H=c.height,id=x.getImageData(0,0,W,H),d=id.data;
 const px=Math.round(pt[0]*W),py=Math.round(pt[1]*H);let sr=0,sg=0,sb=0,n=0;
 for(let dy=-4;dy<=4;dy++)for(let dx=-4;dx<=4;dx++){const i=((py+dy)*W+px+dx)*4;sr+=d[i];sg+=d[i+1];sb+=d[i+2];n++}
 sr/=n;sg/=n;sb/=n;const [h0,s0]=rgb2hsv(sr,sg,sb),[th,ts]=rgb2hsv(...target);
 const hueGate=s0>.2;
 for(let y=Math.floor(box[1]*H);y<Math.min(H,box[3]*H);y++)for(let xx=Math.floor(box[0]*W);xx<Math.min(W,box[2]*W);xx++){
  const i=(y*W+xx)*4;if(d[i+3]<8)continue;
  const [h,s,v]=rgb2hsv(d[i],d[i+1],d[i+2]);let w=0;
  if(hueGate){const dh=Math.min(Math.abs(h-h0),1-Math.abs(h-h0));if(dh<.05&&s>s0*.6)w=1;else if(dh<.075&&s>s0*.7)w=.5}
  else{const dist=Math.abs(d[i]-sr)+Math.abs(d[i+1]-sg)+Math.abs(d[i+2]-sb);if(dist<tol)w=1-dist/tol*.45}
  if(!w)continue;
  const ns=s0<.12?ts*.85:Math.min(1,ts*s/Math.max(.05,s0)),o=hsv2rgb(th,ns,v);
  d[i]+=(o[0]-d[i])*w;d[i+1]+=(o[1]-d[i+1])*w;d[i+2]+=(o[2]-d[i+2])*w;
 }
 x.putImageData(id,0,0);return c;
}
const CSS=`
.v8nav,.v8top{display:none!important}
#screen{padding:0!important;overflow:hidden!important}
.room{position:relative;height:470px;overflow:hidden;background:linear-gradient(#1b5a73 0%,#1a4c63 58%,#143a4d 58%)}
.room .floor{position:absolute;left:0;right:0;bottom:0;height:150px;background:linear-gradient(#8a5a33,#6a4326);border-top:5px solid #4a2d17}
.room .floor:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,#0000 0 118px,#0003 118px 120px)}
.room .win{position:absolute;left:14px;top:10px;width:70px;height:78px;border:5px solid #5b3a1e;border-radius:8px;background:linear-gradient(#bfe9ff,#7cc7ee);box-shadow:inset 0 0 14px #fff8}
.room .sign{position:absolute;left:50%;top:10px;transform:translateX(-50%);background:#fff;border:3px solid #43b7e6;border-radius:12px;padding:4px 14px;font:900 15px Georgia,serif;letter-spacing:.3em;color:#111}
.room .sign small{display:block;font:700 8px Inter,system-ui,sans-serif;letter-spacing:.4em;text-align:center}
.shelf{position:absolute;left:8px;right:84px;top:100px;height:92px;display:flex;gap:8px}
.shelf .t{flex:1;position:relative;border:4px solid #0b2531;border-radius:8px;background:linear-gradient(#7cd0ec,#2f9fc5 70%,#d7c08a 70%);overflow:hidden}
.shelf .t .f{position:absolute;transform:scale(.55);transform-origin:left top}
.plank{position:absolute;left:4px;right:80px;top:196px;height:10px;background:#5a3a1c;border-radius:4px}
.tl{position:absolute;top:208px;font:900 10px Inter,system-ui,sans-serif;letter-spacing:.06em;text-align:center}
.bub{position:absolute;top:2px;right:2px;z-index:3;background:#fff;color:#07212e;border-radius:11px;padding:2px 6px;font:900 11px Inter,system-ui,sans-serif;box-shadow:0 2px 6px #0007}
.bub.ok{background:#3ad07a}
.door{position:absolute;right:6px;top:92px;width:66px;height:300px;background:linear-gradient(#5a371c,#3a2210);border:4px solid #2a180a;border-radius:6px}
.door b{position:absolute;left:8px;right:8px;top:56px;background:#e0483f;color:#fff;font:900 11px Inter,system-ui,sans-serif;text-align:center;border-radius:5px;padding:3px}
.door i{position:absolute;left:0;right:0;top:20px;text-align:center;font-style:normal;font-size:20px}
.me{position:absolute;left:156px;bottom:-4px;height:300px;filter:drop-shadow(0 6px 5px #0008)}
.me canvas,.stage canvas{height:100%;width:auto;display:block}
.speech{position:absolute;left:10px;top:236px;width:140px;background:#fff;color:#08222f;border-radius:16px;padding:8px 11px;font:800 12px Inter,system-ui,sans-serif;box-shadow:0 4px 12px #0007;z-index:6}
.speech:after{content:"";position:absolute;right:-9px;top:44px;border:9px solid #0000;border-left-color:#fff;border-right:0}
.strip{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px}
.chip{background:#09232e;border:1px solid #ffffff15;border-radius:14px;padding:9px 10px;font-size:12px}
.chip b{display:block;font-size:12px}.chip small{opacity:.75}
.btnrow{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:0 10px}
.btnrow button{border:0;border-radius:13px;padding:12px;font:900 12px Inter,system-ui,sans-serif;color:#fff;background:linear-gradient(#2f9d57,#1f6d3f)}
.btnrow button.alt{background:#0d2b38;border:1px solid #f2b33d66}
.xp{height:7px;background:#061923;border-radius:5px;margin-top:5px}.xp i{display:block;height:100%;width:70%;background:linear-gradient(90deg,#3fc1ff,#6ee28c);border-radius:5px}
.ed{padding:8px 10px}
.stage{height:290px;border-radius:18px;position:relative;overflow:hidden;background:radial-gradient(circle at 50% 30%,#2b7a99,#12394c 70%);display:flex;justify-content:center;align-items:flex-end;padding-top:14px;box-sizing:border-box}
.stage .name{position:absolute;top:10px;left:12px;font:900 13px Inter,system-ui,sans-serif;letter-spacing:.08em}
.stage .lv{position:absolute;top:8px;right:10px;background:#0d2b38;border-radius:12px;padding:5px 9px;font:900 11px Inter,system-ui,sans-serif}
.roster{display:flex;gap:6px;overflow:hidden;margin-top:8px}
.roster div{flex:none;width:50px;height:74px;border-radius:12px;background:#09232e;border:2px solid #25404c;display:flex;align-items:flex-end;justify-content:center;overflow:hidden;position:relative}
.roster div.on{border-color:#f2b33d;box-shadow:0 0 0 2px #f2b33d55}
.roster div img{height:96%;width:auto}.roster div.lock img{filter:brightness(.25)}.roster div.lock:after{content:"🔒";position:absolute;top:22px;left:15px;font-size:18px}
.opt{margin-top:8px}.opt>b{display:block;font:900 11px Inter,system-ui,sans-serif;letter-spacing:.1em;opacity:.8;margin-bottom:5px}
.sw{display:flex;gap:7px;flex-wrap:wrap}.sw i{width:28px;height:28px;border-radius:50%;border:2px solid #ffffff30;display:block}.sw i.on{border-color:#f2b33d;box-shadow:0 0 0 2px #f2b33d55}
.nm{background:#09232e;border:1px solid #25404c;border-radius:12px;padding:9px 12px;font:800 13px Inter,system-ui,sans-serif;display:flex;justify-content:space-between}
.save{margin:9px 0 0;width:100%;border:0;border-radius:14px;padding:12px;font:900 13px Inter,system-ui,sans-serif;color:#fff;background:linear-gradient(#6fdc4a,#3f9d28)}
`;
async function setup(w,k){
 w.save=()=>{};w.__afHourOverride=12;
 const d=w.document,s=d.createElement('style');s.textContent=CSS;d.head.appendChild(s);
 const mk=(sp,sex,age,id)=>({id,name:id,species:sp,sex,age,genes:{color:92,pattern:82,fins:90,vitality:90,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0});
 const S=w.eval('st');S.coins=1240;S.playerLevel=4;S.xp=180;
 const a=w.tankArrayV14('main');a.length=0;a.push(mk('guppy','M',20,'g1'),mk('molly','M',30,'m1'),mk('platy','F',24,'p1'),mk('xipho','M',36,'x1'));
 w.u121go('home');
 const scr=d.getElementById('screen');
 const fish=(sp,x,y,wd)=>`<div class="f" style="left:${x}px;top:${y}px">${w.dexAvatarHTML({species:sp,sex:'M',age:w.eval('S')[sp].adult+6,health:100,disease:null,dead:false},wd||80,46)}</div>`;
 /* the character: Luna with the raincoat recoloured yellow -> blue, to show the recolour */
 const id='walk_05_girl_braids_raincoat',img=await loadImg(CUT+id+'.png');
 const cv=document.createElement('canvas');cv.width=img.naturalWidth;cv.height=img.naturalHeight;cv.getContext('2d').drawImage(img,0,0);
 recolor(cv,SAMPLE[id].top,[40,110,215],150,[0,.24,1,.7]);
 if(k==='home'){
  scr.innerHTML=`<div class="room">
   <div class="win"></div><div class="sign">AFNICA<small>FISHROOM</small></div>
   <div class="shelf">
     <div class="t"><span class="bub">🍽️</span>${fish('guppy',2,4,70)}${fish('molly',14,30,70)}${fish('platy',-4,50,60)}</div>
     <div class="t"><span class="bub ok">🐣 3</span>${fish('cory',4,34,70)}</div>
     <div class="t"><span class="bub ok">❤️</span>${fish('xipho',8,14,70)}</div>
   </div><div class="plank"></div>
   <div class="tl" style="left:12px;width:84px">MAIN</div><div class="tl" style="left:102px;width:84px">FRY</div><div class="tl" style="left:192px;width:84px">BREEDER</div>
   <div class="door"><i>🏪</i><b>STORE</b></div>
   <div class="floor"></div>
   <div class="speech">Hi boss! The Main Tank is hungry 🍽️ and 3 new fry are in the Fry Tank.</div>
   <div class="me"></div>
  </div>
  <div class="strip"><div class="chip"><b>⭐ LEVEL 4</b><div class="xp"><i></i></div><small>180/260 XP</small></div><div class="chip"><b>✅ TODAY 1/3</b><small>Feed · Water · Clean</small></div></div>
  <div class="btnrow"><button>NEXT DAY →</button><button class="alt">🎨 CHANGE CHARACTER</button></div>`;
  scr.querySelector('.me').appendChild(cv);
 }else{
  const sw=(cols,on)=>`<div class="sw">${cols.map(c=>`<i class="${c===on?'on':''}" style="background:${c}"></i>`).join('')}</div>`;
  scr.innerHTML=`<div class="ed"><div class="stage"><span class="name">LUNA</span><span class="lv">⭐ L4</span></div>
  <div class="roster">${CH.map((c,i)=>`<div class="${c[0]===id?'on':''} ${i>7?'lock':''}"><img src="${CUT+c[0]}.png"></div>`).join('')}</div>
  <div class="opt"><b>OUTFIT COLOUR</b>${sw(['#e8b83a','#2872d7','#d0463e','#2f9d8f','#6b4aa5','#e8e8e8'],'#2872d7')}</div>
  <div class="opt"><b>HAIR COLOUR</b>${sw(['#1d1410','#5a3220','#8a4b1f','#c08a3a','#d8d3c8','#2f6fb0'],'#1d1410')}</div>
  <div class="opt"><b>NAME</b><div class="nm"><span>Luna</span><span>✏️</span></div></div>
  <button class="save">SAVE CHARACTER</button></div>`;
  scr.querySelector('.stage').appendChild(cv);
 }
}
document.querySelectorAll('iframe').forEach(f=>{
 f.src=GAME;
 f.onload=async()=>{const w=f.contentWindow;for(let i=0;i<80&&typeof w.calibV1773==='undefined';i++)await new Promise(r=>setTimeout(r,500));
  await new Promise(r=>setTimeout(r,2500));
  try{await setup(w,f.dataset.k)}catch(e){console.error('mock',f.dataset.k,e)}};
});
