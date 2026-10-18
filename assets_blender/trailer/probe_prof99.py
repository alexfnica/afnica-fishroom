# CPU profile of a slow frame window (2026-10-18): run the mixed tank to frame A, profile frames A..B, print the functions
# with the most self time. Run: python probe_prof99.py A B
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
A, B = int(sys.argv[1]), int(sys.argv[2])
FISH = os.environ.get('FISH') or "[T.fish('anc','M',40),T.fish('anc','M',38),T.fish('anc','M',36),T.fish('anc','F',36)]"
c = anc_game(tank='main', fish=FISH, warm=1, pre=SEED % 7)
try:
    for i in range(A): c.js('__afStep(%f, 2)' % (1000 / 30))
    c.cmd('Profiler.enable'); c.cmd('Profiler.setSamplingInterval', interval=200); c.cmd('Profiler.start')
    for i in range(A, B): c.js('__afStep(%f, 2)' % (1000 / 30))
    prof = c.cmd('Profiler.stop')['profile']
    nodes = {n['id']: n for n in prof['nodes']}; cnt = collections.Counter(prof['samples']); dts = prof['timeDeltas']
    selft = collections.Counter()
    for sid, dt in zip(prof['samples'], dts): n = nodes[sid]['callFrame']; selft[(n['functionName'] or '(anon)', n['lineNumber'] + 1)] += dt / 1000
    for (fn, ln), ms in selft.most_common(12): print('%8.1f ms  %s  line %d' % (ms, fn, ln))
    par = {}
    for n in prof['nodes']:
        for ch in n.get('children', []): par[ch] = n['id']
    pc = collections.Counter()
    for sid, dt in zip(prof['samples'], dts):
        if nodes[sid]['callFrame']['functionName'] == 'restore':
            q = par.get(sid); chain = []
            while q and len(chain) < 3: cf = nodes[q]['callFrame']; chain.append('%s:%d' % (cf['functionName'] or 'anon', cf['lineNumber'] + 1)); q = par.get(q)
            pc[' <- '.join(chain)] += dt / 1000
    for k, ms in pc.most_common(4): print('restore %6.1f ms from %s' % (ms, k))
finally: c.close()
