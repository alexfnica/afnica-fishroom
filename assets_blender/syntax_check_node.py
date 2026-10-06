# Syntax check without Chrome (for cloud / CI sessions): every inline <script> block of the game is written to a temp
# file and checked with `node --check`. Errors are reported with the line number in the game HTML.
# Run: python assets_blender/syntax_check_node.py   (needs Node.js on PATH; on the owner's laptop use syntax_check.py)
import os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
s = open(GAME, encoding='utf-8').read()
blocks = list(re.finditer(r'<script>(.*?)</script>', s, re.S))
bad = 0
with tempfile.TemporaryDirectory() as td:
    for i, m in enumerate(blocks):
        p = os.path.join(td, 'b%d.js' % i)
        open(p, 'w', encoding='utf-8').write(m.group(1))
        r = subprocess.run(['node', '--check', p], capture_output=True, text=True)
        if r.returncode:
            bad += 1
            err = r.stderr
            mm = re.search(r'b%d\.js:(\d+)' % i, err)
            line = s[:m.start(1)].count('\n') + (int(mm.group(1)) if mm else 1)
            msg = [l for l in err.splitlines() if 'Error' in l]
            print('block', i, 'file line', line, (msg[0] if msg else err.strip()[:160])[:160])
print('blocks', len(blocks), 'with syntax errors', bad)
sys.exit(1 if bad else 0)
