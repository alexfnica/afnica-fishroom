import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
from scene import open_game, record, advance, HERE
c = open_game(540, 960, 4)
try:
    c.js(r'''(()=>{
     T.tank('main',[T.fish('xipho','M',30),T.fish('xipho','M',28),T.fish('xipho','F',30),T.fish('guppy','M',20),T.fish('guppy','F',20),T.fish('cory','M',30),T.fish('anc','M',40)]);
     T.show('main'); T.clean();
     const s=document.createElement('style');s.textContent='#tank-main{position:fixed!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;z-index:9000!important;border-radius:0!important;margin:0!important;aspect-ratio:auto!important;max-width:none!important;max-height:none!important}body{overflow:hidden!important}';document.head.appendChild(s);
     window.dispatchEvent(new Event('resize'));
     return 1;})()''')
    advance(c, 6)
    print(c.js("JSON.stringify(T.rect('#tank-main'))"))
    t = time.time(); c.shot(os.path.join(HERE, 'test', 'bleed.jpg'), clip=dict(x=0, y=0, width=540, height=960, scale=.5)); print('full', round(time.time() - t, 2))
    t = time.time(); c.shot(os.path.join(HERE, 'test', 'zoom.jpg'), clip=dict(x=135, y=240, width=270, height=480, scale=1)); print('zoom', round(time.time() - t, 2))
finally:
    c.close()
