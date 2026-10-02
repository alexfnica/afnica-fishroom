import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from takes import game, advance, HERE
for name, sc in [('A', dict(ground='amazonia', surface='redroot', substrate='vallisneria', epiphyte='javafern', wood='spider', rock='dragon')),
                 ('B', dict(ground='sand', surface='frogbit', substrate='crypt', epiphyte='anubias', wood='mopani', rock='slate'))]:
    c = game("st.scapes=st.scapes||{};st.scapes.main=Object.assign(st.scapes.main||{},%s);T.tank('main',[T.fish('xipho','M',40),T.fish('guppy','M',30),T.fish('platy','F',30),T.fish('anc','M',60)])" % json.dumps(sc), warm=3, dof=0)
    try:
        print(name, c.js("JSON.stringify(st.scapes.main)"))
        c.shot(os.path.join(HERE, 'test', 'scape_%s.jpg' % name), clip=dict(x=0, y=0, width=540, height=960, scale=1080 / (540 * 6)), q=88)
    finally: c.close()
