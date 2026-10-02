# Preview single trailer frames (half size) at given times: python compose_test.py 4.9,26.9 [take_to_replace ...]
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome
import timeline
HERE = os.path.dirname(os.path.abspath(__file__))
TL = dict(timeline.TL); TL['shots'] = [dict(s) for s in TL['shots']]
for s in TL['shots']:
    if not os.path.exists(os.path.join(HERE, 'raw', s['take'], 'cam.json')) or s['take'] in sys.argv[2:]: s['take'] = 'guppy_court'
    s['len'] = len([f for f in os.listdir(os.path.join(HERE, 'raw', s['take'])) if f.endswith('.jpg')])
times = [float(x) for x in sys.argv[1].split(',')]
c = Chrome(1080, 1920, 1, port=9556)
try:
    c.cmd('Page.navigate', url='file:///' + os.path.join(HERE, 'compose.html').replace(os.sep, '/')); c.wait_event('Page.loadEventFired', 30)
    c.js('ready'); c.js('window.TL=' + json.dumps(TL) + ';1')
    for t in times:
        fi = int(round(t * 30)); c.js('renderFrame(%d)' % fi)
        p = os.path.join(HERE, 'test', 'comp_%05d.jpg' % fi); c.shot(p, clip=dict(x=0, y=0, width=1080, height=1920, scale=.5), q=88); print(p)
finally: c.close()
