# V17.108 spawning still (2026-10-23): headless breeder, 1 male + 1 female + cave, daytime, the owner's save never touched.
# The clock is fake, so after the last step the fish can be posed by hand (element styles) and shot without the loops
# moving them. Poses = the spec in docs/ANCISTRUS_SPAWNING_SPEC.md (choreography B), stages 2-4; top row as the player
# sees it, bottom row with the tube rim made see-through.
# Run: D:/Blender/5.2/python/bin/python.exe still_spawn108.py <out.jpg> [probe]
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
OUT = sys.argv[1]; PROBE = len(sys.argv) > 2
c = anc_game(tank='breeder', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", warm=3, pre=SEED % 7)
try:
    INFO = r"""(()=>{const tk=document.getElementById('tank-breeder'),cave=tk.querySelector('.ancBreedingCave'),rim=tk.querySelector('.ancCaveRim');
 const E=[...tk.querySelectorAll('[data-fish-id]')].map(e=>({id:e.dataset.fishId,sex:(tankArrayV14('breeder').find(f=>String(f.id)===e.dataset.fishId)||{}).sex,
  tr:e.style.transform,l:e.style.left,t:e.style.top,op:e.style.opacity,m:e.dataset.ancMode,clip:(e.style.clipPath||'').slice(0,30),z:e.style.zIndex,
  kids:[...e.children].map(k=>k.tagName+'.'+k.className+(k.style.display==='none'?'(hid)':''))}));
 return JSON.stringify({cave:cave&&[cave.style.left,cave.style.top,cave.style.zIndex],rim:!!rim,E,cv:[...tk.querySelectorAll(':scope>canvas')].map(k=>k.className+':'+k.style.display)})})()"""
    print(c.js(INFO))
    if PROBE: raise SystemExit
    # pose (V17.89 place() maths) applied inside the post hook every frame, so the V17.90 canvas draws it like the game does
    c.js(r"""(()=>{const tk=document.getElementById('tank-breeder'),cave=tk.querySelector('.ancBreedingCave');
 const p0=window.ancPostV1789;window.ancPostV1789=function(t,el,s,fish){p0.apply(this,arguments);const P=window.__pose;if(!P||!fish||t!==tk)return;const p=P[fish.sex];if(!p)return;
  const L=parseFloat(cave.style.left)||0,T=parseFloat(cave.style.top)||0,Mx=L+13.8,sc=1,tip=56*sc,x=Mx+p.snout-p.face*tip,cy=T+61+(p.dy||0)-3*sc;
  s.x=x;s.y=cy;s.face=p.face;
  let clip='none';if(!window.__xray){const f=p.face,P2=[[L-400,cy-200],[L+8,cy-200],[L+8,T+18],[L+156,T+18],[L+156,T+70],[L+8,T+70],[L+8,cy+200],[L-400,cy+200]];   /* V17.89 place() clip */
   clip='polygon('+P2.map(([px,py])=>(((px-x)/(sc*f))+60).toFixed(1)+'px '+(((py-cy)/sc)+35).toFixed(1)+'px').join(',')+')';}
  const S={left:(x-60)+'px',top:(cy-35)+'px',transform:'scale('+sc+') scaleX('+p.face+')',opacity:'1','clip-path':clip,'z-index':String(p.z||44),rotate:'none',translate:'none'};
  for(const k in S)el.style.setProperty(k,S[k],'important');el.dataset.ancX=x;el.dataset.ancY=cy;};return 1})()""")
    # a real spawning clutch (trapped, never ends) so the game's own spawning layers (rim over the tube) are used
    c.js("(()=>{const a=tankArrayV14('breeder'),m=a.find(f=>f.sex==='M'),f=a.find(f=>f.sex==='F');st.ancClutch={id:'t108',stage:'spawning',phase:'trapped',trapDay:st.day,trapDays:999,seconds:0,mom:f.id,dad:m.id,count:30,attempt:1,lossRoll:1,lastDay:st.day};return 1})()")
    def pose(P, xray):
        c.js("window.__xray=%d;" % xray + "window.__pose=%s;(k=>{let e=document.getElementById('xr108');if(!e){e=document.createElement('style');e.id='xr108';document.head.appendChild(e);}e.textContent=k?'#tank-breeder .ancCaveRim{opacity:.3!important}':'';})(%d);1" % (json.dumps(P), xray))
        advance(c, 3)
    cave = json.loads(c.js("JSON.stringify((r=>[r.left,r.top,r.width,r.height])(document.querySelector('#tank-breeder .ancBreedingCave').getBoundingClientRect()))"))
    cl, ct, cw, ch = cave
    k = cw / 160.0                                   # tank css px -> screen px
    # snout = tank px from the mouth plane (+ = inside); body length 112 px at scale 1, tube inside ~136 px deep
    STAGES = [('2  He steps out and aside, she comes to the mouth', {'M': dict(snout=-150, face=1, dy=-18, z=43), 'F': dict(snout=-4, face=1, dy=1, z=44)}),
              ('3  She slides in head first, slowly', {'M': dict(snout=-80, face=1, dy=-2, z=44), 'F': dict(snout=45, face=1, dy=1, z=44)}),
              ('4  He lies over her, tail out, fanning', {'M': dict(snout=74, face=1, dy=-6, z=44), 'F': dict(snout=115, face=1, dy=2, z=43)})]
    tiles = []
    for xray in (0, 1):
        for cap, P in STAGES:
            pose(P, xray)
            if os.environ.get('DBG'): print(cap[:2], xray, c.js(r"""JSON.stringify([...document.querySelectorAll('#tank-breeder [data-fish-id], #tank-breeder .ancBreedingCave, #tank-breeder .ancCaveRim, #tank-breeder canvas')].map(e=>{const k=getComputedStyle(e);return [e.className.baseVal!=null?'svg':String(e.className).slice(0,30),e.dataset.fishId||'',k.visibility,k.display,k.opacity,k.zIndex,e.style.left,e.style.top,(e.dataset.ancMode||'')]}))"""))
            p = os.path.join(os.path.dirname(os.path.abspath(OUT)), '_s%d.jpg' % len(tiles))
            shot(c, p, clip={'x': cl - 230 * k, 'y': ct - 50 * k, 'width': 410 * k, 'height': 150 * k, 'scale': 2})
            tiles.append((p, cap + (' (x-ray)' if xray else '')))
    html = ''.join('<div style="display:inline-block;vertical-align:top;width:300px;margin:4px;text-align:center;font:600 12px system-ui;color:#fff"><img src="data:image/jpeg;base64,%s" style="width:300px;display:block">%s</div>'
                   % (base64.b64encode(open(p, 'rb').read()).decode(), t) for p, t in tiles)
    c.js("(h=>{document.body.innerHTML='<div id=g style=\"position:fixed;left:0;top:0;z-index:99999;background:#111;padding:6px;width:940px\">'+h+'</div>';return 1})(%s)" % json.dumps(html))
    r = json.loads(c.js("JSON.stringify((r=>[r.width,r.height])(document.getElementById('g').getBoundingClientRect()))"))
    shot(c, OUT, clip={'x': 0, 'y': 0, 'width': r[0], 'height': r[1], 'scale': 1})
    for p, _ in tiles: os.remove(p)
    print('still', OUT)
finally:
    c.close()
