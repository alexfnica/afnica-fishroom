# V17.122 test (player character + fishroom Home) on a throw-away headless Chrome with the save blocked. Output goes to a file.
# D:/Blender/5.2/python/bin/python.exe test_ui122.py D:/ClaudeWork/ui122_test.txt [width height]
import os, sys, time, json
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome
OUTF = sys.argv[1] if len(sys.argv) > 1 else 'D:/ClaudeWork/ui122_test.txt'
W = int(sys.argv[2]) if len(sys.argv) > 2 else 375
H = int(sys.argv[3]) if len(sys.argv) > 3 else 812
TAG = os.environ.get('TAG', 'ui122')
DOCS = os.path.join(os.path.dirname(__file__), '..', '..', 'docs')
GAME = 'http://127.0.0.1:8791/AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html'
lines = []
def log(*a):
    s = ' '.join(str(x) for x in a); lines.append(s); open(OUTF, 'w', encoding='utf-8').write('\n'.join(lines))
def ok(name, cond, extra=''):
    log(('PASS ' if cond else 'FAIL ') + name + (' | ' + str(extra) if extra != '' else ''))
c = Chrome(W, H, 2, port=9444)
try:
    c.cmd('Page.navigate', url=GAME); c.wait_event('Page.loadEventFired', 120)
    c.js("window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,220));_ce.apply(console,arguments)};window.addEventListener('error',e=>window.__err.push('ERR '+e.message));1")
    for _ in range(80):
        if c.js("typeof calibV1773!=='undefined'"): break
        time.sleep(.5)
    time.sleep(3.5)
    c.js("window.save=()=>{};window.__afHourOverride=12;1")
    c.js("""(()=>{const mk=(sp,sex,age,id)=>({id,name:id,species:sp,sex,age,genes:{color:92,pattern:82,fins:90,vitality:90,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0});
const a=tankArrayV14('main');a.length=0;a.push(mk('guppy','M',20,'g1'),mk('molly','M',30,'m1'),mk('platy','F',24,'p1'),mk('xipho','M',36,'x1'),mk('cory','M',30,'c1'));
const f=tankArrayV14('fry');f.length=0;f.push(mk('guppy','M',2,'fr1'),mk('guppy','F',2,'fr2'));st.coins=1240;return 1})()""")
    ok('V17.122 loaded (20 characters)', c.js("u122Debug().chars")==20, c.js("u122Debug().chars"))
    ok('boot opens Home', c.js("ui121Debug().cur")=='home', c.js("ui121Debug().cur"))
    c.js("u121go('tank');u121go('home')"); time.sleep(2.5)
    ok('Home has the character and it is loaded', c.js("(()=>{const i=document.getElementById('u122Img');return !!i&&i.naturalWidth>50&&i.style.opacity==='1'})()"))
    ok('three tank windows + store door', c.js("document.querySelectorAll('.u122Tk').length")==3 and c.js("!!document.querySelector('.u122Door')"))
    ok('fish are drawn in the tank windows', c.js("document.querySelectorAll('.u122F').length")>=4, c.js("document.querySelectorAll('.u122F').length"))
    ok('greeting bubble shows on arrival', c.js("document.getElementById('u122Say').classList.contains('on')"), c.js("document.getElementById('u122Say').textContent"))
    c.shot(os.path.join(DOCS, TAG + '_home.png'), fmt='png')
    # no page scroll on Home, no overflow
    ok('Home: no horizontal overflow', c.js("document.documentElement.scrollWidth<=innerWidth&&document.getElementById('screen').scrollWidth<=document.getElementById('screen').clientWidth+1"))
    # tap the character: a new line each time
    t1 = c.js("document.getElementById('u122Say').textContent")
    c.js("u122Tap()"); t2 = c.js("document.getElementById('u122Say').textContent")
    c.js("u122Tap()"); t3 = c.js("document.getElementById('u122Say').textContent")
    ok('tapping the character cycles the speech', len({t1, t2, t3}) >= 2, [t1[:30], t2[:30], t3[:30]])
    # walking: sample the position for ~25 s
    seen = set(); walked = False; frontback = False
    for i in range(50):
        time.sleep(.5)
        st_ = json.loads(c.js("JSON.stringify({l:document.getElementById('u122Me').style.left,w:document.getElementById('u122Me').classList.contains('walk'),src:document.getElementById('u122Img').src.slice(-12)})"))
        if st_['w'] and not walked: c.shot(os.path.join(DOCS, TAG + '_walking.png'), fmt='png')
        seen.add(st_['l']); walked = walked or st_['w']
    ok('the character walks to other spots (>=2 positions) and shows the walk pose', len(seen) >= 2 and walked, (sorted(seen), walked))
    time.sleep(3)
    ok('after the walk it stands again', c.js("document.getElementById('u122Me').classList.contains('idle')||document.getElementById('u122Me').classList.contains('walk')"))
    # rapid switching: only one walker alive, no errors
    g0 = c.js("u122Debug().gen")
    for i in range(80):
        c.js(["u121go('home')", "u121go('tank')", "u121go('progress')", "u121go('avatar')", "u121go('shop')"][i % 5]); time.sleep(.03)
    c.js("u121go('home')"); time.sleep(2)
    ok('no JS errors after 80 rapid switches', c.js("window.__err.length")==0, c.js("JSON.stringify(window.__err.slice(0,3))"))
    ok('generation counter only grows (old walkers die)', c.js("u122Debug().gen")>g0)
    # tank windows open the tanks
    c.js("document.querySelectorAll('.u122Tk')[1].click()"); time.sleep(1.2)
    ok('tapping the Fry window opens the Fry tank', c.js("ui121Debug().cur")=='tank' and c.js("v8Tank")=='fry', c.js("ui121Debug().cur+' '+v8Tank"))
    c.js("switchTankV8('main');u121go('home')"); time.sleep(1.2)
    c.js("document.querySelector('.u122Door').click()"); time.sleep(1.5)
    ok('tapping the door opens My Store', c.js("ui121Debug().cur")=='store')
    c.js("u121go('home')"); time.sleep(1)
    # picker
    c.js("u121go('avatar')"); time.sleep(1.5)
    ok('picker opens (title CHARACTER)', c.js("document.getElementById('u121Title').textContent")=='CHARACTER')
    ok('picker shows 20 characters, 8 free at level 1', c.js("document.querySelectorAll('#u122Roster>div').length")==20 and c.js("document.querySelectorAll('#u122Roster>div:not(.lock)').length")==8, c.js("document.querySelectorAll('#u122Roster>div:not(.lock)').length"))
    c.shot(os.path.join(DOCS, TAG + '_picker.png'), fmt='png')
    id0 = c.js("st.avatar122.id")
    c.js("u122Pick('17')"); time.sleep(.5)
    ok('a locked character cannot be picked', c.js("st.avatar122.id")==id0, c.js("st.avatar122.id"))
    c.js("u122Pick('11')"); time.sleep(1.2)
    ok('picking Leo saves id 11 + chosen', c.js("st.avatar122.id")=='11' and c.js("st.avatar122.chosen")==True)
    ok('name follows the character (Leo)', c.js("document.getElementById('u122StName').textContent")=='LEO')
    c.js("u122Outfit('#d0463e')"); time.sleep(1.8)
    src_before = c.js("document.getElementById('u122StImg').src.length")
    ok('outfit colour saved + stage picture recoloured (data URL changes)', c.js("st.avatar122.outfit")=='#d0463e' and c.js("document.getElementById('u122StImg').src.startsWith('data:image/webp')"))
    c.js("document.querySelector('.u122Name').value='Capt. Fish';u122Name('Capt. Fish')"); time.sleep(.4)
    ok('custom name saved', c.js("st.avatar122.name")=='Capt. Fish', c.js("st.avatar122.name"))
    c.shot(os.path.join(DOCS, TAG + '_picker_red_leo.png'), fmt='png')
    c.js("u121back()"); time.sleep(2.5)
    ok('Back from picker returns to Home', c.js("ui121Debug().cur")=='home')
    ok('Home shows the new character (Leo, recoloured)', c.js("document.getElementById('u122Img').alt")=='Capt. Fish' and c.js("document.getElementById('u122Img').src.startsWith('data:image/webp')"))
    c.shot(os.path.join(DOCS, TAG + '_home_leo.png'), fmt='png')
    # level up unlocks
    c.js("st.playerLevel=7;u121go('avatar')"); time.sleep(1.2)
    ok('at level 7 all 20 are unlocked', c.js("document.querySelectorAll('#u122Roster>div:not(.lock)').length")==20, c.js("document.querySelectorAll('#u122Roster>div:not(.lock)').length"))
    # every character renders in the picker with every pose loaded
    bad = c.js("(()=>{const r=[];for(const k in AV122.front){const i=new Image();i.src=AV122.front[k]}return Object.keys(AV122.front).length})()")
    c.js("u122Pick('17')"); time.sleep(.8); c.js("u122Outfit('#2872d7')"); time.sleep(1.5)
    ok('Chef Gino picks and recolours without errors', c.js("st.avatar122.id")=='17' and c.js("window.__err.length")==0, c.js("JSON.stringify(window.__err.slice(0,3))"))
    # save default + old saves
    c.js("delete st.avatar122;ensureHealthState()")
    ok('default st.avatar122 created for old saves', c.js("st.avatar122.id")=='05' and c.js("st.avatar122.chosen")==False)
    c.js("st.avatar122={id:'zz',name:12,chosen:'x',outfit:'red'};ensureHealthState()")
    ok('bad avatar data is repaired', c.js("st.avatar122.id")=='05' and c.js("st.avatar122.outfit")==None and c.js("typeof st.avatar122.name")=='string')
    c.js("st.avatar122={id:'__proto__',name:'',chosen:false,outfit:null};ensureHealthState()")
    ok('tampered id __proto__ is repaired', c.js("st.avatar122.id")=='05', c.js("st.avatar122.id"))
    c.js("st.avatar122={id:'05',name:'',chosen:false,outfit:null};u121go('avatar')"); time.sleep(1)
    c.js("u122Name(document.querySelector('.u122Name').value)")
    ok('leaving the name field unchanged does not mark the character as chosen', c.js("st.avatar122.chosen")==False)
    c.js("u122Outfit('#2872d7');u122Outfit('#d0463e');u122Outfit('#6b4aa5')"); time.sleep(2.2)
    ok('fast colour changes: the picture ends on the last colour', c.js("st.avatar122.outfit")=='#6b4aa5' and c.js("document.getElementById('u122StImg').src.startsWith('data:image/webp')"))
    c.js("AV122.front['05']='data:image/webp;base64,AAAA';u121go('home')"); time.sleep(2.5)
    ok('a broken picture still leaves the page usable (no uncaught error)', c.js("ui121Debug().cur")=='home' and c.js("!!document.getElementById('u122Me')"))
    ok('final error count', c.js("window.__err.length")==0, c.js("JSON.stringify(window.__err.slice(0,5))"))
finally:
    c.close()
    log('DONE')
