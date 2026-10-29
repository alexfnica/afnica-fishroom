# Cuts the green background off the Gemini character pictures (assets_blender/incoming/chars/variations -> avatar/cut/*.png). Needs the local server on :8791.
# Run: D:/Blender/5.2/python/bin/python.exe assets_blender/avatar/cut_run.py [name ...]
import sys, os, time, base64, json
sys.path.insert(0, 'D:/Retirement/assets_blender/trailer')
from cdp import Chrome
SRC = 'D:/Retirement/assets_blender/incoming/chars/variations'
OUT = 'D:/Retirement/assets_blender/avatar/cut'
os.makedirs(OUT, exist_ok=True)
names = sorted(f[:-5] for f in os.listdir(SRC) if f.endswith('.jpeg'))
only = sys.argv[1:]
c = Chrome(900, 900, 1, port=9422)
meta = {}
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8791/assets_blender/avatar/cut_green.html'); time.sleep(2)
    for n in names:
        if only and n not in only: continue
        r = c.js("cutOne('http://127.0.0.1:8791/assets_blender/incoming/chars/variations/%s.jpeg').then(r=>JSON.stringify(r))" % n)
        o = json.loads(r)
        open(os.path.join(OUT, n + '.png'), 'wb').write(base64.b64decode(o['png'].split(',')[1]))
        meta[n] = {'w': o['w'], 'h': o['h'], 'bbox': o['bbox']}
        print(n, o['w'], o['h'], flush=True)
finally:
    c.close()
json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), indent=1)
