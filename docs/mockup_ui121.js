/* Temporary in-memory mockup of the screen system (nothing here touches the game file or the save) */
const GAME='../AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html';
const CSS=`
.v8nav,.v8top,.v8switch,.title,header.top{display:none!important}
html,body{overflow:hidden!important;height:100%}
#screen{padding:0!important;height:100vh;overflow:hidden;position:relative}
.m121head{position:relative;display:flex;align-items:center;gap:8px;height:50px;padding:0 10px;background:linear-gradient(#061923,#0a2230);border-bottom:1px solid #25404c;flex:none}
.m121head b{font-size:15px;letter-spacing:.1em;flex:1}
.m121head .back{width:34px;height:34px;border-radius:12px;border:1px solid #f2b33d66;background:#0d2b38;color:#eaf7ff;font-size:17px;font-weight:900}
.m121head .pill{background:#0d2b38;border-radius:14px;padding:6px 8px;font-weight:900;font-size:11px;white-space:nowrap}
.m121head .bell{position:relative;width:34px;height:34px;border-radius:12px;border:1px solid #25404c;background:#0d2b38;color:#fff;font-size:16px}
.m121head .bell i{position:absolute;top:-5px;right:-5px;background:#e0483f;border-radius:9px;font:900 10px Inter;padding:2px 5px;font-style:normal}
.m121body{height:calc(100vh - 50px - 62px);overflow:hidden;padding:10px;box-sizing:border-box}
.m121nav{position:fixed;left:0;right:0;bottom:0;height:62px;display:grid;grid-template-columns:repeat(5,1fr);background:rgba(6,24,33,.98);border-top:1px solid #25404c;z-index:50}
.m121nav button{background:none;border:0;color:#9fb8c4;font:900 10px Inter;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;letter-spacing:.06em}
.m121nav button em{font-style:normal;font-size:20px}
.m121nav button.on{color:#f2b33d;box-shadow:inset 0 3px 0 #f2b33d;background:linear-gradient(#f2b33d1a,#0000)}
.m121nav button.lock{opacity:.9}
.toast121{position:absolute;left:10px;right:10px;bottom:72px;z-index:40;background:#10394a;border:1px solid #f2b33d88;border-radius:14px;padding:8px 10px;font-weight:800;font-size:12px;box-shadow:0 6px 18px #0009}
.tc{display:flex;gap:10px;align-items:center;background:#09232e;border:1px solid #ffffff15;border-radius:15px;padding:10px;margin-bottom:8px}
.tc .ic{font-size:30px;width:44px;text-align:center}
.tc div b{display:block;font-size:13px}.tc div small{opacity:.75}
.tc .go{margin-left:auto;background:linear-gradient(#2f9d57,#1f6d3f);border:0;border-radius:12px;color:#fff;font:900 11px Inter;padding:9px 12px}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#e0483f;margin-right:5px}
.dot.ok{background:#3ad07a}
.quick{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
.quick button{background:#0d2b38;border:1px solid #f2b33d55;border-radius:14px;color:#fff;font:900 12px Inter;padding:12px}
.seg{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;background:#061923;border-radius:14px;padding:4px;margin-bottom:8px}
.seg button{border:0;border-radius:11px;background:none;color:#9fb8c4;font:900 11px Inter;padding:9px}
.seg button.on{background:#f2b33d;color:#1a1200}
.ach{display:flex;gap:10px;align-items:center;background:#09232e;border-radius:13px;padding:8px 10px;margin-bottom:6px;font-size:12px}
.ach .ic{font-size:22px}.ach .bar2{height:6px;background:#061923;border-radius:4px;margin-top:5px}.ach .bar2 i{display:block;height:100%;background:#3ad07a;border-radius:4px}
.ach.done{border:1px solid #f2b33d77}.ach .rw{margin-left:auto;font-weight:900;color:#f2b33d;white-space:nowrap}
.sheet{position:absolute;left:0;right:0;bottom:62px;background:#0a2230;border-top:2px solid #f2b33d;border-radius:20px 20px 0 0;padding:12px;z-index:45;display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.sheet button{background:#0d2b38;border:1px solid #25404c;border-radius:14px;color:#fff;font:900 11px Inter;padding:12px 4px;display:flex;flex-direction:column;gap:4px;align-items:center}
.sheet button em{font-style:normal;font-size:22px}
`;
const NAV=[['home','🏠','HOME'],['tank','🐠','TANK'],['breed','❤️','BREEDING'],['market','📦','MARKET'],['more','☰','MORE']];
function nav(on,sheet){return `<div class="m121nav">${NAV.map(n=>`<button class="${n[0]===on?'on':''}"><em>${n[1]}</em>${n[2]}</button>`).join('')}</div>${sheet?`<div class="sheet"><button><em>🐟</em>FISHDEX</button><button><em>🛒</em>SHOP</button><button class="lock"><em>🏪</em>STORE 🔒</button><button><em>🏆</em>PROGRESS</button><button><em>⚙️</em>SETTINGS</button></div>`:''}`}
function head(w,title,back){const st=w.eval('st');return `<div class="m121head">${back?'<button class="back">←</button>':''}<b>${title}</b><span class="pill">⭐ L${st.playerLevel}</span><span class="pill">🪙 ${st.coins}</span><button class="bell">🔔<i>3</i></button></div>`}

function setup(w,k){
  w.save=()=>{};w.__afHourOverride=12;
  const d=w.document,s=d.createElement('style');s.textContent=CSS;d.head.appendChild(s);
  const mk=(sp,sex,age,id,fins)=>({id,name:id,species:sp,sex,age,genes:{color:92,pattern:82,fins,vitality:90,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0});
  try{const a=w.tankArrayV14('main');a.length=0;a.push(mk('guppy','M',20,'g1',90),mk('guppy','F',20,'g2',80),mk('molly','M',30,'m1',90),mk('platy','F',24,'p1',85),mk('xipho','M',36,'x1',98));const S=w.eval('st');S.coins=1240;S.playerLevel=4;S.xp=180;}catch(e){console.error(e)}
  const scr=d.getElementById('screen');
  const st=w.eval('st'),need=w.xpNeededV9(st.playerLevel),pct=Math.min(100,st.xp/need*100);
  const toast=t=>`<div class="toast121">${t}</div>`;
  if(k==='home'){
    w.switchTankV8('main');
    scr.innerHTML=head(w,'FISHROOM')+`<div class="m121body">
    <div class="tc" style="margin-bottom:10px"><div class="ic" style="font-size:22px">⭐</div><div style="flex:1"><b>FISHROOM LEVEL ${st.playerLevel}</b><div class="v9XP" style="margin-top:5px"><i style="width:${pct}%"></i></div><small>${st.xp}/${need} XP · DAY ${st.day}</small></div></div>
    <div class="tc"><div class="ic">🐠</div><div><b>Main Tank</b><small><span class="dot"></span>Hungry fish · 5 fish · 92%</small></div><button class="go">OPEN</button></div>
    <div class="tc"><div class="ic">🐣</div><div><b>Fry Tank</b><small><span class="dot ok"></span>3 fry · 100%</small></div><button class="go">OPEN</button></div>
    <div class="tc"><div class="ic">🧬</div><div><b>Breeder Tank</b><small><span class="dot ok"></span>Pair breeding · 100%</small></div><button class="go">OPEN</button></div>
    <div class="tc" style="margin-top:10px"><div class="ic">✅</div><div style="flex:1"><b>TODAY · 1/3 DONE</b><small>Feed · Water change · Clean glass</small></div><button class="go">NEXT DAY →</button></div>
    <div class="quick"><button>🐟 FISHDEX</button><button>🛒 SHOP</button></div></div>`+toast('🐣 3 new fry born in Main Tank')+nav('home');
  } else if(k==='tank'){
    w.switchTankV8('main');
    const hero=d.querySelector('.v8hero');
    const hh=hero.outerHTML;
    scr.innerHTML=head(w,'MAIN TANK',true)+`<div class="m121body" style="padding:6px"><div style="display:flex;gap:6px;margin-bottom:6px"><button class="back" style="width:44px;height:30px;border-radius:10px;background:#0d2b38;border:1px solid #f2b33d66;color:#fff">◀</button><div class="pill" style="flex:1;text-align:center;padding:6px;background:#0d2b38;border-radius:10px;font:900 11px Inter">MAIN · FRY · BREEDER</div><button class="back" style="width:44px;height:30px;border-radius:10px;background:#0d2b38;border:1px solid #f2b33d66;color:#fff">▶</button></div><div id="mhero">${hh}</div></div>`+toast('🍽️ Fish are hungry')+nav('tank');
    const h=d.getElementById('mhero').firstElementChild;h.style.cssText+=';height:calc(100vh - 50px - 62px - 58px);overflow:hidden;margin:0';
    const dock=h.querySelector('.v8dock');if(dock)dock.style.cssText+=';position:absolute;left:0;right:0;bottom:0';
  } else if(k==='breed'){
    w.eval("v8Tank='main'");
    w.renderV103Breeder();
    d.querySelectorAll('#screen button').forEach(b=>{if(/MODELS/i.test(b.textContent))b.remove()});
    const panels=[...d.querySelectorAll('#screen .v8panel')].slice(0,3).map(p=>p.outerHTML).join('');
    scr.innerHTML=head(w,'BREEDING',true)+`<div class="m121body" style="overflow-y:auto"><div class="seg"><button class="on">BREEDER</button><button>FRY TANK</button><button>INFO</button></div>${panels}</div>`+toast('❤️ Pair is courting in Breeder Tank')+nav('breed');
  } else if(k==='prog'){
    const A=[['🐣','First birth','Get fry in any tank',1,1,'+50🪙'],['💰','Fish seller','Sell 10 fish',6,10,'+100🪙'],['📦','Contract master','Complete 5 market orders',2,5,'+150🪙'],['🐟','Collector','Discover all 8 species',5,8,'+200🪙'],['🏅','Top bloodline','Raise an S-grade fish',0,1,'+300🪙'],['🧬','Cave keeper','Hatch bristlenose fry',0,1,'+200🪙']];
    scr.innerHTML=head(w,'PROGRESS',true)+`<div class="m121body" style="overflow:hidden"><div class="tc"><div class="v9LevelOrb" style="flex:none">${st.playerLevel}</div><div style="flex:1"><b>FISHROOM LEVEL ${st.playerLevel}</b><div class="v9XP" style="margin-top:5px"><i style="width:${pct}%"></i></div><small>${st.xp}/${need} XP</small></div></div>
    <div class="v8head" style="margin:8px 2px"><b>DAILY QUESTS</b><span>1/3</span></div>
    <div class="ach done"><span class="ic">🍽️</span><b>Feed the tank</b><span class="rw">1/1 ✓</span></div><div class="ach"><span class="ic">💧</span><b>Change water</b><span class="rw">0/1</span></div><div class="ach"><span class="ic">🧽</span><b>Clean the glass</b><span class="rw">0/1</span></div>
    <div class="v8head" style="margin:8px 2px"><b>ACHIEVEMENTS</b><span>1/${A.length}</span></div>
    ${A.map(a=>`<div class="ach ${a[3]>=a[4]?'done':''}"><span class="ic">${a[0]}</span><div style="flex:1"><b>${a[1]}</b><div style="opacity:.7">${a[2]}</div><div class="bar2"><i style="width:${a[3]/a[4]*100}%"></i></div></div><span class="rw">${a[5]}</span></div>`).join('')}</div>`+nav('more');
  }
}
document.querySelectorAll('iframe').forEach(f=>{
  f.src=GAME;
  f.onload=async()=>{const w=f.contentWindow;for(let i=0;i<80&&typeof w.calibV1773==='undefined';i++)await new Promise(r=>setTimeout(r,500));
    await new Promise(r=>setTimeout(r,1500));
    try{setup(w,f.dataset.k)}catch(e){console.error('mock',f.dataset.k,e)}};
});
