# V17.102 review clip of the arc turn: an adult black male and a brown female on the sand, each sent behind itself every
# 4 s (a turn each time), zoomed on the male. -> AFNICA_Anc102_turns.mp4 in the repo root (git-ignored).
# Run: D:/Blender/5.2/python/bin/python.exe film_turn102.py   (env ZOOM, SECS)
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anc_rig import *
from takes_anc89 import encode, ROOT
Z = float(os.environ.get('ZOOM', '2.4')); SECS = int(os.environ.get('SECS', '14')); NAME = 'turn102'
MK = lambda i, s: "{id:'%s',name:'%s',species:'anc',sex:'%s',age:36,genes:{color:92,pattern:82,fins:90,vitality:90,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0}" % (i, i, s)
HOOK = r"""window.__S=new WeakMap();setTimeout(()=>{const p=window.ancPostV1789;window.ancPostV1789=function(t,el,s){p.apply(this,arguments);__S.set(el,s);};},0);1;"""
c = anc_game(tank='main', fish='[%s,%s]' % (MK('a1', 'M'), MK('f2', 'F')), warm=1, pre=HOOK)
out = os.path.join(HERE, 'raw', 'a89_' + NAME); os.makedirs(out, exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out, f))
GO = r"""(()=>{const W=document.getElementById('tank-main').clientWidth;for(const e of document.querySelectorAll('#tank-main [data-fish-id]')){const s=__S.get(e);if(!s||s.turn)continue;
 let tx=s.x-(s.face<0?-1:1)*110;if(tx<90||tx>W-90)tx=s.x+(s.face<0?-1:1)*110;s.mode='move';s.tx=tx;s.ty=s.y;s.wait=0;s.dk95=tx;s.force95=null;s.fg=null;}return 1})()"""
try:
    for i in range(20): c.js('__afStep(%f, 2)' % (1000 / 30))
    b = json.loads(c.js("JSON.stringify((()=>{const r=document.querySelector('#tank-main [data-fish-id=\"a1\"]').getBoundingClientRect();return [r.x+60,r.y+35]})())"))
    w, h = VW / Z, VH / Z; clip = dict(x=min(max(b[0] - w / 2, 0), VW - w), y=min(max(b[1] - h * .7, 0), VH - h), width=w, height=h, scale=Z)
    for i in range(SECS * 30):
        if i % 120 == 10: c.js(GO)
        c.js('__afStep(%f, 2)' % (1000 / 30)); c.shot(os.path.join(out, '%05d.jpg' % i), clip=clip, q=90)
finally: c.close()
encode(NAME, int(w * Z) // 2 * 2, int(h * Z) // 2 * 2)
src = os.path.join(ROOT, 'AFNICA_Anc89_%s.mp4' % NAME); dst = os.path.join(ROOT, 'AFNICA_Anc102_turns.mp4')
if os.path.exists(src): shutil.move(src, dst); print('clip', dst)
