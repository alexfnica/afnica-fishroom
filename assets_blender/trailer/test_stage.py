import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from takes import game, HERE
c = game("T.tank('main',[T.fish('xipho','M',40),T.fish('guppy','M',30),T.fish('platy','F',30),T.fish('anc','M',60),T.fish('guppy','F',30)])", warm=4, dof=4)
try:
    c.shot(os.path.join(HERE, 'test', 'stage_full.jpg'), clip=dict(x=0, y=0, width=540, height=960, scale=1080 / (540 * 6)), q=88)
    c.shot(os.path.join(HERE, 'test', 'stage_zoom.jpg'), clip=dict(x=100, y=300, width=200, height=355.5, scale=1080 / (200 * 6)), q=88)
finally: c.close()
