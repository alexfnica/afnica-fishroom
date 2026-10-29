# Shrinks avatar/cut/*.png to game size (height 560, WebP with alpha) into avatar/game/*.webp + game/meta.json. Needs the local server on :8791.
# Run: D:/Blender/5.2/python/bin/python.exe assets_blender/avatar/prep_game.py
import sys, os, time, base64, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
SRC = os.path.join(HERE, os.environ.get('AV_SRC', 'cut')); OUT = os.path.join(HERE, os.environ.get('AV_OUT', 'game')); os.makedirs(OUT, exist_ok=True)
HEIGHT = int(os.environ.get('AV_H', '560'))
names = sorted(f[:-4] for f in os.listdir(SRC) if f.endswith('.png'))
c = Chrome(900, 900, 1, port=9433); meta = {}
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8791/assets_blender/avatar/resize.html'); time.sleep(1.5)
    for n in names:
        o = json.loads(c.js("shrink('http://127.0.0.1:8791/assets_blender/avatar/%s/%s.png',%d,.86).then(r=>JSON.stringify(r))" % (os.environ.get('AV_SRC', 'cut'), n, HEIGHT)))
        open(os.path.join(OUT, n + '.webp'), 'wb').write(base64.b64decode(o['webp'].split(',')[1]))
        meta[n] = {'w': o['w'], 'h': o['h'], 'kb': round(os.path.getsize(os.path.join(OUT, n + '.webp')) / 1024)}
        print(n, meta[n], flush=True)
finally:
    c.close()
json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), indent=1)
