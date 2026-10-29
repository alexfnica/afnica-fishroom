# V17.121 functional test on a throw-away headless Chrome (save blocked). Output goes to a file (C: can be full, pipes fail):
# D:/Blender/5.2/python/bin/python.exe test_ui121.py D:/ClaudeWork/ui121_test.txt [width height]
import os, sys, time, json
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome
OUTF = sys.argv[1] if len(sys.argv) > 1 else 'D:/ClaudeWork/ui121_test.txt'
W = int(sys.argv[2]) if len(sys.argv) > 2 else 375
H = int(sys.argv[3]) if len(sys.argv) > 3 else 812
GAME = 'http://127.0.0.1:8791/AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html'
lines = []
def log(*a):
    s = ' '.join(str(x) for x in a); lines.append(s); open(OUTF, 'w', encoding='utf-8').write('\n'.join(lines))
def ok(name, cond, extra=''):
    log(('PASS ' if cond else 'FAIL ') + name + (' | ' + str(extra) if extra != '' else ''))
c = Chrome(W, H, 1, port=9366)
try:
    # count timers and rAF callbacks from the very start
    c.cmd('Page.addScriptToEvaluateOnNewDocument', source="""window.__iv=0;window.__raf=0;const _si=window.setInterval;window.setInterval=function(){window.__iv++;return _si.apply(this,arguments)};
const _r=window.requestAnimationFrame;window.requestAnimationFrame=function(f){window.__raf++;return _r.call(window,f)};""")
    c.cmd('Page.navigate', url=GAME); c.wait_event('Page.loadEventFired', 120)
    c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,220));_ce.apply(console,arguments)};window.addEventListener('error',e=>window.__err.push('ERR '+e.message));1")
    for _ in range(80):
        if c.js("typeof calibV1773!=='undefined'"): break
        time.sleep(.5)
    time.sleep(3.5)
    c.js("window.save=()=>{};window.__afHourOverride=12;1")
    ok('boot opens Home', c.js("ui121Debug().cur")=='home', c.js("ui121Debug().cur"))
    c.js("""(()=>{const mk=(sp,sex,age,id,fins)=>({id,name:id,species:sp,sex,age,genes:{color:92,pattern:82,fins,vitality:90,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0});
const a=tankArrayV14('main');a.length=0;a.push(mk('guppy','M',20,'g1',90),mk('guppy','F',20,'g2',80),mk('molly','M',30,'m1',90),mk('platy','F',24,'p1',85),mk('cory','M',30,'c1',90),mk('cory','M',30,'c2',90),mk('cory','F',30,'c3',90));
st.coins=1240;return 1})()""")
    # ---- timers / loops: baseline on the Tank screen
    c.js("switchTankV8('main');u121go('tank')"); time.sleep(2)
    iv0 = c.js("window.__iv"); wr0 = c.js("window._afnicaWaterRuntime")
    c.js("window.__fr=0;(function f(){window.__fr++;requestAnimationFrame(f)})()")
    def rafrate():
        a = c.js("window.__raf"); f0 = c.js("window.__fr"); time.sleep(3); b = c.js("window.__raf"); f1 = c.js("window.__fr"); return round((b - a - (f1 - f0)) / max(1, f1 - f0), 2)
    base = rafrate(); log('rAF callbacks per frame (baseline)', base)
    # ---- rapid switching: 240 navigations
    import random
    random.seed(7)
    targets = ["u121go('home')", "u121go('tank')", "u121go('breed')", "u121go('market')", "u121go('dex')", "u121go('shop')", "u121go('store')", "u121go('progress')", "u121go('settings')",
               "u121breedTab('fry')", "u121breedTab('info')", "u121breedTab('breeder')", "u121cycle(1)", "u121cycle(-1)", "u121back()", "u121nav('more')", "u121layer('notes')", "u121layer(false)"]
    for i in range(240):
        c.js(random.choice(targets)); time.sleep(0.03)
    time.sleep(1.5)
    ok('no JS errors after 240 rapid switches', c.js("window.__err.length")==0, c.js("JSON.stringify(window.__err.slice(0,4))"))
    c.js("u121layer(false);switchTankV8('main')"); time.sleep(2.5)
    after = rafrate(); log('rAF callbacks per frame (after switching)', after)
    ok('rAF callbacks per frame not multiplied (<= 1.3x baseline)', after <= base * 1.3 + 0.5, '%s vs %s' % (after, base))
    ok('water runtime interval is the same one', c.js("window._afnicaWaterRuntime")==wr0, wr0)
    ok('few new setIntervals created (<= 12 over 240 switches)', c.js("window.__iv") - iv0 <= 12, c.js("window.__iv") - iv0)
    # ---- tank screen has no scroll
    ok('tank screen: no scroll', c.js("(()=>{const s=document.getElementById('screen');return s.scrollHeight-s.clientHeight<=1&&document.documentElement.scrollWidth<=innerWidth})()"))
    # ---- feed through the real dock button
    f0 = c.js("st.food")
    c.js("document.querySelector('.v8dock button').click()"); time.sleep(.8)
    ok('FEED button works (food -1, daily.feed)', c.js("st.food")==f0-1 and c.js("dailyFor('main').feed")==True, (f0, c.js("st.food")))
    ok('still on Tank after feed', c.js("ui121Debug().cur")=='tank')
    # ---- water change
    c.js("[...document.querySelectorAll('.v8dock button')][1].click()"); time.sleep(1.2)
    ok('WATER change started', c.js("waterChangeInfo('main').active")==True)
    # water clock keeps running while the player is on other screens
    p0 = c.js("JSON.stringify(waterChangeInfo('main'))")
    c.js("u121go('market')"); time.sleep(4); c.js("u121go('progress')"); time.sleep(3)
    p1 = c.js("JSON.stringify(waterChangeInfo('main'))")
    ok('water clock advances while on other screens', p0 != p1, p0[:80] + ' -> ' + p1[:80])
    # ---- quests show on Progress
    c.js("u121go('progress')"); time.sleep(.8)
    ok('Progress shows quest done for feed', c.js("document.getElementById('screen').innerText.includes('1/1')"))
    # ---- clean + treat panel
    c.js("u121go('tank')"); time.sleep(1.2)
    c.js("[...document.querySelectorAll('.v8dock button')][2].click()"); time.sleep(.6)
    ok('CLEAN works', c.js("dailyFor('main').clean")==True)
    c.js("(()=>{const f=st.fish.find(x=>x.id==='g1');f.disease='ich';f.sickDays=1;return 1})()"); c.js("u121go('tank')"); time.sleep(1.5)
    ok('sick fish -> notice in bell', c.js("ui121Debug().notices.some(n=>/sick/.test(n.tx))"))
    c.js("u121go('home')"); time.sleep(.5)
    ok('Home lists the sick notice', c.js("document.getElementById('screen').innerText.includes('sick')"))
    c.js("u121go('tank')"); time.sleep(1.2)
    c.js("[...document.querySelectorAll('.v8dock button')][3].click()"); time.sleep(.8)
    ok('TREAT button opens the medicine chooser', c.js("!!document.getElementById('treat71')"))
    c.js("document.querySelector('#treat71 button[data-a=gen]').click()"); time.sleep(.8)
    ok('General Treatment starts from the chooser', c.js("!!st.generalTreatment"))

    # ---- details sheet (moved panels) holds the fish strip and quests
    c.js("u121sheet(true)"); time.sleep(.4)
    ok('sheet contains YOUR FISH + quests', c.js("(()=>{const t=document.getElementById('u121Sheet').innerText;return t.includes('YOUR FISH')&&t.includes('DAILY QUESTS')})()"))
    ok('sheet SELL buttons exist', c.js("document.querySelectorAll('#u121Sheet .v9SellBtn').length")>=1, c.js("document.querySelectorAll('#u121Sheet .v9SellBtn').length"))
    c.js("u121sheet(false)")
    # ---- move corydoras: panel in Breeding > FRY tab, move into the breeder tank
    c.js("u121breedTab('fry')"); time.sleep(.6)
    ok('Fry tab has Move Corydoras panel', c.js("document.getElementById('screen').innerText.includes('MOVE CORYDORAS')"))
    c.js("moveToBreederV103('c1')"); time.sleep(.6)
    c.js("moveToBreederV103('c3')"); time.sleep(.6)
    ok('cory moved to breeder tank', c.js("st.breederTank.filter(f=>f.species==='cory').length")>=1, c.js("st.breederTank.length"))
    c.js("u121go('breed')"); time.sleep(1.2)
    ok('Breeder tab renders with seg bar', c.js("!!document.getElementById('u121Seg')&&ui121Debug().cur==='breed'"))
    # ---- shop buy
    cc = c.js("st.coins"); fd = c.js("st.food")
    c.js("u121go('shop')"); time.sleep(.8)
    c.js("[...document.querySelectorAll('#screen .btn')].find(b=>/BUY 10 FOOD/.test(b.textContent)).click()"); time.sleep(.6)
    ok('SHOP buy food works', c.js("st.food")==fd+10 and c.js("st.coins")<cc, (fd, c.js("st.food"), cc, c.js("st.coins")))
    ok('still on Shop after buying', c.js("ui121Debug().cur")=='shop')
    # ---- market
    c.js("u121go('market')"); time.sleep(.8)
    ok('Market renders orders', c.js("document.getElementById('screen').innerText.includes('FISH MARKET')"))
    # ---- achievements claim
    c.js("st.totalSold=12;1"); c.js("u121go('progress')"); time.sleep(.6)
    c0 = c.js("st.coins"); c.js("u121claim('seller')"); time.sleep(.5)
    ok('achievement claim pays coins once', c.js("st.coins")==c0+100, (c0, c.js("st.coins")))
    c.js("u121claim('seller')"); ok('no double claim', c.js("st.coins")==c0+100)
    # ---- NEXT DAY from Home keeps Home
    d0 = c.js("st.day"); c.js("u121go('home')"); time.sleep(.5); c.js("u121nextDay()"); time.sleep(1.5)
    ok('NEXT DAY advanced the day and stayed on Home', c.js("st.day")==d0+1 and c.js("ui121Debug().cur")=='home', (d0, c.js("st.day"), c.js("ui121Debug().cur")))
    # ---- back stack
    c.js("u121go('home');u121go('shop');u121go('progress')"); c.js("u121back()"); a1 = c.js("ui121Debug().cur"); c.js("u121back()"); a2 = c.js("ui121Debug().cur")
    ok('Back goes progress -> shop -> home', a1=='shop' and a2=='home', (a1, a2))
    # ---- store opens and stops its loop when leaving
    c.js("u121go('store')"); time.sleep(1.5)
    ok('Store screen renders', c.js("!!document.getElementById('st120stage')"))
    c.js("u121go('home')"); time.sleep(.5)
    ok('Store stage gone after leaving', c.js("!document.getElementById('st120stage')"))
    # ---- ensure save defaults
    ok('st.ach121 default present', c.js("typeof st.ach121==='object'&&typeof st.ach121.claimed==='object'"))
    # ---- no page scroll anywhere
    bad = []
    for n in ['home', 'tank', 'breed', 'market', 'dex', 'shop', 'store', 'progress', 'settings']:
        c.js("u121go('%s')" % n); time.sleep(.9)
        if c.js("document.documentElement.scrollWidth>innerWidth||document.documentElement.scrollHeight>innerHeight+1||document.getElementById('screen').scrollWidth>document.getElementById('screen').clientWidth+1"): bad.append(n)
    ok('no horizontal overflow / page scroll on any screen', not bad, bad)
    ok('final error count', c.js("window.__err.length")==0, c.js("JSON.stringify(window.__err.slice(0,5))"))
finally:
    c.close()
    log('DONE')
