# V17.120: stills of the store (full scene, clerk close-up, sign) on the fake clock. Output: docs/store120_*.png
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from scene import open_game
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs')
c = open_game(1100, 800, 1, port=int(os.environ.get('AF_PORT', '9333')))
try:
    c.js("""window.save=()=>{};window.dispatchEvent(new Event('pointerdown'));window.__afHourOverride=12;(()=>{const mk=(sp,sex,age,id,g)=>({id,name:id,species:sp,sex,age,genes:{color:g,pattern:g,fins:g,vitality:g,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0});
const a=tankArrayV14('main');a.length=0;a.push(mk('guppy','M',40,'g1',70),mk('molly','F',60,'m1',88),mk('platy','M',50,'p1',95),mk('neon','F',40,'n1',80),mk('cory','F',60,'c1',90),mk('anc','M',60,'a1',85));
ensureHealthState();['g1','m1','p1','n1','c1','a1'].forEach(id=>stStock120(id));renderStoreV120();window.scrollTo(0,0);return 1})()""")
    for i in range(30): c.js('__afStep(40,1)')
    r = json.loads(c.js("JSON.stringify((()=>{const g=id=>{const b=document.getElementById(id).getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height}};return {wrap:g('st120wrap'),clerk:g('st120clerk')}})())"))
    print(r)
    w = r['wrap']; c.shot(os.path.join(D, 'store120_full.png'), clip={'x': w['x'], 'y': w['y'], 'width': w['w'], 'height': w['h'], 'scale': 1}, fmt='png')
    k = w['w'] / 760
    c.shot(os.path.join(D, 'store120_clerk.png'), clip={'x': w['x'] + 590 * k, 'y': w['y'] + 140 * k, 'width': 170 * k, 'height': 200 * k, 'scale': 3}, fmt='png')
    c.shot(os.path.join(D, 'store120_sign.png'), clip={'x': w['x'] + 240 * k, 'y': w['y'], 'width': 280 * k, 'height': 66 * k, 'scale': 3}, fmt='png')
finally:
    c.close()
