# V17.120 phase 4: ONE full purchase (enter -> browse -> queue -> greet/net/bag/hand/pay -> leave with the bag) on the fake clock;
# saves the stage frame at each stage and a 3x3 grid -> docs/store120_purchase_grid.jpg
import os, sys, json, time, base64, shutil
sys.path.insert(0, os.path.dirname(__file__))
from scene import open_game
from cdp import Chrome
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs'); W = r'D:\ClaudeWork\outro'
c = open_game(1100, 800, 1, port=int(os.environ.get('AF_PORT', '9333')))
frames = []
try:
    c.js("""window.save=()=>{};window.dispatchEvent(new Event('pointerdown'));window.__afHourOverride=12;window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};(()=>{const mk=(sp,sex,age,id,g)=>({id,name:id,species:sp,sex,age,genes:{color:g,pattern:g,fins:g,vitality:g,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0});
const a=tankArrayV14('main');a.length=0;a.push(mk('guppy','M',40,'g1',70),mk('molly','F',60,'m1',88),mk('platy','M',50,'p1',95),mk('neon','F',40,'n1',80),mk('cory','F',60,'c1',90),mk('anc','M',60,'a1',85));
ensureHealthState();['g1','m1','p1','n1','c1','a1'].forEach(id=>{stStock120(id);stPrice120(id,-30)});window.scrollTo(0,0);renderStoreV120();
const d=storeDebugV120();d.S.next=1e9;d.spawn();const c=d.S.cust[0];c.type='beginner';c.budget=900;c.sense=1.4;window.__c=c;window.__c0=st.coins;return 1})()""")
    w = json.loads(c.js("JSON.stringify((()=>{const b=document.getElementById('st120wrap').getBoundingClientRect();return {x:b.x,y:b.y,width:b.width,height:b.height,scale:.5}})())"))
    want = ['enter', 'look', 'toPay', 'atpay:greet', 'atpay:net', 'atpay:bag', 'atpay:hand', 'atpay:pay', 'exit']; got = {}
    log = []
    for i in range(40 * 60):
        c.js('__afStep(25,1)')
        k = json.loads(c.js("JSON.stringify([__c.state,storeDebugV120().S.clerk.ph,Math.round(__c.x),Math.round(__c.y)])"))
        key = k[0] + (':' + k[1] if k[0] == 'atpay' else '')
        if key in want and key not in got and not (key == 'exit' and not json.loads(c.js('JSON.stringify(!!__c.bagged)'))):
            if key == 'look': 
                for _ in range(40): c.js('__afStep(25,1)')
            if key in ('atpay:net',):
                for _ in range(20): c.js('__afStep(25,1)')
            if key in ('atpay:bag', 'atpay:hand', 'atpay:pay'):
                for _ in range(12): c.js('__afStep(25,1)')
            p = os.path.join(W, 'g%d.png' % len(got)); c.shot(p, clip=w, fmt='png'); got[key] = p; log.append((round(i * .025, 1), key))
        if json.loads(c.js('JSON.stringify(!!__c.dead)')): break
    print(log)
    print(c.js("JSON.stringify({coins:st.coins-__c0,sales:st.store.day.sales,err:__err,left:st.storeFish.length})"))
finally:
    c.close()
order = [got[k] for k in want if k in got]
open(os.path.join(W, 'grid.html'), 'w').write('<body style="margin:0;background:#041019;display:grid;grid-template-columns:repeat(3,526px);gap:4px">' + ''.join('<div style="position:relative"><img src="%s" width="526"><b style="position:absolute;left:8px;top:6px;color:#fff;font:700 15px Arial;text-shadow:0 1px 3px #000">%d. %s</b></div>' % (os.path.basename(p), i + 1, k) for i, (p, k) in enumerate(zip(order, [k for k in want if k in got]))) + '</body>')
g = Chrome(1590, 1010, 1, port=9556)
try:
    g.cmd('Page.navigate', url='http://127.0.0.1:8792/grid.html'); g.wait_event('Page.loadEventFired', 20); time.sleep(1)
    g.shot(os.path.join(D, 'store120_purchase_grid.jpg'), q=88)
finally:
    g.close()
