import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from scene import open_game, advance, HERE
c = open_game(540, 960, 1)
try:
    c.js("(()=>{T.tank('main',[T.fish('xipho','M',40),T.fish('xipho','F',36),T.fish('guppy','M',30),T.fish('guppy','F',30),T.fish('platy','F',30),T.fish('cory','M',30),T.fish('anc','M',60)]);st.coins=2450;T.show('main');return 1})()")
    advance(c, 2)
    for name, js in [('market', "renderV10Market()"), ('shop', "renderV8('shop')"), ('room', "(()=>{const b=[...document.querySelectorAll('button')].find(b=>/ROOM/.test(b.textContent));b&&b.click();return !!b})()")]:
        print(name, c.js(js + ";1") if 'click' not in js else c.js(js)); advance(c, 1)
        c.js("window.scrollTo(0,0)"); advance(c, .2)
        c.shot(os.path.join(HERE, 'test', 'scr_%s.jpg' % name))
        print(c.js("document.documentElement.scrollHeight"))
        c.js("window.scrollTo(0,700)"); advance(c, .2); c.shot(os.path.join(HERE, 'test', 'scr_%s2.jpg' % name))
finally:
    c.close()
