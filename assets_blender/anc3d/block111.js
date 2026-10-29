/* ===== V17.111 CAVE INSPECT: real footage instead of the vector drawing =====
   Owner: "we need a realistic animation, made with Gemini from the photo". The inspect popup of the breeding cave (V17.43
   `inspectHTML` canvas #ancInspect43) is replaced, while the clutch is in its yolk stage, by a looping video chosen by how much
   yolk is left (full < 1/3 of the stage gone, half < 2/3, low after that): window.ANC111_ASSETS = {poster, full, half, low}
   (data URIs written by anc3d/install111.py from assets_blender/incoming/anc_wriggler_scene_*.webp / anc_wriggler_heap_*.mp4).
   Without a video the still of that yolk stage (poster_full / poster_half / poster_low, else poster) is shown with slow dust drifting through the beam. Without any asset, or with
   eggs / two broods / no brood, the V17.43 canvas stays. Nothing is saved. Switch: window.ANC111=false. */
(function(){
 window.ANC111=true;
 const A=window.ANC111_ASSETS||{};
 const clamp=(v,a,b)=>v<a?a:v>b?b:v;
 const key=c=>{if(c&&c.stage==='eggs'){if(!A.poster_eggs)return null;const laid=Number.isFinite(c.laidDay)?c.laidDay:c.hatchDay-5,q=clamp((st.day-laid)/Math.max(1,c.hatchDay-laid),0,1);return q<.5&&A.poster_eggs_early?'eggs_early':'eggs';}   /* fresh bright orange eggs first, eyed eggs in the second half */
  if(!c||c.stage!=='yolk')return null;const p=clamp((st.day-c.hatchDay)/Math.max(1,c.releaseDay-c.hatchDay),0,1);return p<.34?'full':p<.67?'half':'low';};
 if(!document.getElementById('anc111css')){const s=document.createElement('style');s.id='anc111css';
  s.textContent='@keyframes anc111dust{0%{transform:translate(0,0);opacity:0}15%{opacity:.8}85%{opacity:.7}100%{transform:translate(26px,38px);opacity:0}}'+
   '@keyframes anc111breath{0%,100%{transform:scale(1.02)}50%{transform:scale(1.045)}}'+
   '.anc111box{position:relative;overflow:hidden;margin:auto;display:block;background:#120a05}'+
   '.anc111box>img,.anc111box>video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:35% 55%}'+
   '.anc111box>img{animation:anc111breath 9s ease-in-out infinite}'+
   '.anc111box>i{position:absolute;width:3px;height:3px;border-radius:50%;background:#ffe3b8;filter:blur(.6px);animation:anc111dust 7s linear infinite}'+
   '.anc111box>b{position:absolute;inset:0;background:radial-gradient(ellipse at 38% 52%,rgba(0,0,0,0) 38%,rgba(0,0,0,.55) 100%)}';
  document.head.appendChild(s);}
 /* larvae per stage still (1024x559 image px): [head x, head y, tail tip x, tail tip y]; floor larvae first, then the ones on the wall */
 const LARVAE={
  full:[[400,360,300,350],[400,398,300,405],[458,430,385,485],[445,292,400,272],[642,285,690,262],[668,320,765,305],[765,344,880,352],[675,383,765,430],[722,383,808,395],[843,415,945,447],[626,432,675,487],[283,445,305,497],[255,135,262,230],[308,142,318,235],[165,212,190,305],[222,207,230,298],[112,348,138,435]],
  half:[[405,360,300,350],[405,395,285,408],[462,428,385,487],[448,293,405,272],[640,285,690,262],[668,320,765,305],[758,343,880,350],[670,385,765,430],[712,380,808,395],[843,415,945,447],[622,430,680,490],[275,448,300,497],[255,125,260,235],[307,138,318,238],[163,205,190,305],[222,203,232,298],[110,345,135,438]],
  eggs:[],eggs_early:[],   /* the eggs have no twitching: dust and beam only */
  low:[[378,377,235,395],[425,397,285,418],[595,402,755,428],[705,375,815,388],[775,398,900,438],[188,122,192,250],[138,205,150,320],[166,246,180,330],[868,388,885,300]]
 };
 const IW=1024,IH=559,SC=.75;
 /* one twitching larva: an upright patch of its rear body + tail (axis along x), waved in strips, drawn back rotated with a soft mask */
 function mkLarva(img,l){
  const [hx,hy,tx,ty]=l,dx=tx-hx,dy=ty-hy,len=Math.hypot(dx,dy),th=Math.atan2(dy,dx),s0=.42,px=hx+dx*s0,py=hy+dy*s0,pw=Math.ceil(len*(1-s0)+len*.12),hw=Math.max(12,Math.round(len*.14));
  const p=document.createElement('canvas');p.width=pw;p.height=hw*2;const g=p.getContext('2d');g.translate(0,hw);g.rotate(-th);g.translate(-px,-py);g.drawImage(img,0,0);
  const t=document.createElement('canvas');t.width=pw;t.height=hw*2;
  return {p,t,pw,hw,px,py,th,len,t0:0,t1:0,next:1+Math.random()*7,amp:3,fr:14,ph:Math.random()*6.28};
 }
 function drawLarva(g,L,now){
  const a=(now-L.t0)/(L.t1-L.t0);if(a<0||a>=1)return;
  const env=Math.sin(Math.PI*a),q=L.t.getContext('2d');q.globalCompositeOperation='source-over';q.clearRect(0,0,L.pw,L.hw*2);
  for(let x=0;x<L.pw;x+=2){const u=x/L.pw,d=L.amp*env*Math.sin(L.ph+now*L.fr-u*5.5)*Math.pow(u,1.3);q.drawImage(L.p,x,0,3,L.hw*2,x,d,3,L.hw*2);}
  q.globalCompositeOperation='destination-in';const m=q.createLinearGradient(0,0,L.pw,0);m.addColorStop(0,'rgba(0,0,0,0)');m.addColorStop(.12,'rgba(0,0,0,1)');m.addColorStop(.9,'rgba(0,0,0,1)');m.addColorStop(1,'rgba(0,0,0,0)');q.fillStyle=m;q.fillRect(0,0,L.pw,L.hw*2);
  q.globalCompositeOperation='destination-in';const v=q.createLinearGradient(0,0,0,L.hw*2);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(.3,'rgba(0,0,0,1)');v.addColorStop(.7,'rgba(0,0,0,1)');v.addColorStop(1,'rgba(0,0,0,0)');q.fillStyle=v;q.fillRect(0,0,L.pw,L.hw*2);
  g.save();g.translate(L.px,L.py);g.rotate(L.th);g.drawImage(L.t,0,-L.hw);g.restore();
 }
 function living(canvas,src,key){
  const img=new Image();img.onload=()=>{
   const g=canvas.getContext('2d'),list=(LARVAE[key]||[]).map(l=>mkLarva(img,l)),dust=[];
   for(let i=0;i<70;i++)dust.push({x:180+Math.random()*560,y:20+Math.random()*340,v:3+Math.random()*7,r:.7+Math.random()*1.3,a:.25+Math.random()*.5,f:Math.random()*6});
   window.__L111=list;   /* test hook (never read by the game) */
   let last=performance.now();
   (function frame(){
    if(!canvas.isConnected)return;
    const now=performance.now()/1000,dt=Math.min(.1,(performance.now()-last)/1000);last=performance.now();
    g.setTransform(SC,0,0,SC,0,0);g.globalCompositeOperation='source-over';g.drawImage(img,0,0);
    for(const L of list){if(now>L.next&&now>L.t1){L.t0=now;L.t1=now+.5+Math.random()*.7;L.amp=5+Math.random()*5;L.fr=11+Math.random()*7;L.next=now+2.5+Math.random()*8;}drawLarva(g,L,now);}
    g.globalCompositeOperation='lighter';
    for(const d of dust){d.x+=d.v*.7*dt;d.y+=d.v*dt;d.f+=dt*(1+d.r);if(d.x>760||d.y>380){d.x=180+Math.random()*300;d.y=10+Math.random()*60;}
     g.fillStyle='rgba(255,226,180,'+(d.a*(.55+.45*Math.sin(d.f))).toFixed(3)+')';g.beginPath();g.arc(d.x,d.y,d.r,0,6.283);g.fill();}
    const fl=.035+.03*Math.sin(now*1.7)+.015*Math.sin(now*5.3);const bg=g.createRadialGradient(240,40,10,300,200,420);bg.addColorStop(0,'rgba(255,190,110,'+fl.toFixed(3)+')');bg.addColorStop(1,'rgba(255,190,110,0)');g.fillStyle=bg;g.fillRect(0,0,IW,IH);
    requestAnimationFrame(frame);
   })();
  };
  img.src=src;
 }
 function swap(){
  if(window.ANC111===false)return;
  const cv=document.getElementById('ancInspect43');if(!cv||st.ancClutch2&&['eggs','yolk'].includes(st.ancClutch2.stage))return;
  const k=key(st.ancClutch);if(!k)return;
  const src=A[k]||null,poster=A['poster_'+k]||A.poster||null;if(!src&&!poster)return;
  const box=document.createElement('div');box.className='anc111box';box.dataset.k=k;
  box.style.cssText='width:100%;max-width:420px;aspect-ratio:'+(cv.width&&cv.height?cv.width+'/'+cv.height:'4/3')+';border-radius:50% / 42%;box-shadow:0 0 0 6px #2b2116';
  if(src){const v=document.createElement('video');v.src=src;v.loop=true;v.muted=true;v.autoplay=true;v.playsInline=true;if(poster)v.poster=poster;box.appendChild(v);const p=v.play();if(p&&p.catch)p.catch(()=>{});}
  else{const cvs=document.createElement('canvas');cvs.width=Math.round(IW*SC);cvs.height=Math.round(IH*SC);cvs.style.cssText='position:absolute;inset:0;width:100%;height:100%;object-fit:cover';box.appendChild(cvs);living(cvs,poster,k);}
  const sh=document.createElement('b');box.appendChild(sh);
  cv.replaceWith(box);
 }
 const prev=window.inspectAncCave40;
 if(typeof prev==='function')window.inspectAncCave40=function(){
  const r=prev.apply(this,arguments);
  try{swap();}catch(e){window.ANC111=false;console.error('AFNICA V17.111 inspect',e);}
  return r;
 };
})();
