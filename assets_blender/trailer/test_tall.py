import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from scene import open_game, record, advance, HERE
c = open_game()
try:
    print(c.js('''(()=>{
     T.tank('main',[T.fish('xipho','M',30),T.fish('xipho','M',28),T.fish('xipho','F',30),T.fish('xipho','F',26),T.fish('guppy','M',20),T.fish('guppy','F',20),T.fish('neon','M',20)]);
     T.show('main'); T.clean();
     const t=document.getElementById('tank-main'); t.style.setProperty('height','693px','important'); t.style.setProperty('aspect-ratio','auto','important');
     return JSON.stringify([T.rect('#tank-main'), document.querySelectorAll('#tank-main .modelFish').length]);})()'''))
    advance(c, 4)
    r = c.js("JSON.stringify(T.rect('#tank-main'))"); print(r)
    import json; r = json.loads(r)
    c.js("window.scrollTo(0,%d)" % int(r['y'] - 20)); advance(c, .2)
    c.shot(os.path.join(HERE, 'test', 'tall.jpg'))
finally:
    c.close()
