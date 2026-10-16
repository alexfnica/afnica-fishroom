# V17.91 clips (throw-away headless game): A = whole tank bottom 40 s (1 male + 2 females); B = cave close-up 30 s from the
# start (the male walks over, pauses at the mouth, wriggles in, fans tail-out, comes head-out).
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = os.environ.get('FISH') or "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30)]"
def enc(name, out, w, h):
    subprocess.run([r'D:\Blender\blender.exe', '-b', '-P', os.path.join(HERE, 'encode_plain.py'), '--', os.path.join(HERE, 'raw', name), out, str(w), str(h), '24'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('clip', out, os.path.exists(out), flush=True)
which = sys.argv[1]
c = anc_game(tank='main', fish=FISH, warm=1, dsf=2, pre=SEED % int(os.environ.get('SEED', '7')))
try:
    if which == 'A':
        film(c, os.environ.get('TAKE', 'a91_tank'), 40, fps=24, caption=lambda i: os.environ.get('CAP', 'Bristlenose: fins step, dorsal folds at rest, head down when rasping, crawl in bouts, visible breathing.') + '  %d s' % (i // 24), clip=dict(x=0, y=240, width=960, height=300, scale=1.0))
    else:
        b = json.loads(c.js("JSON.stringify((()=>{const r=document.querySelector('#tank-main .ancBreedingCave').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})())"))
        w, h = 480, 150; x = max(0, min(b['x'] + b['w'] / 2 - 260, VW - w)); y = min(VH - h, b['y'] - 50)
        film(c, 'a91_cave', 30, fps=24, caption=lambda i: 'Male at the cave: pause at the mouth, wriggles in, fans tail-out, comes head-out to invite.  %d s' % (i // 24), clip=dict(x=x, y=y, width=w, height=h, scale=2.0))
finally: c.close()
ROOT = os.path.join(HERE, '..', '..')
if which == 'A': enc(os.environ.get('TAKE', 'a91_tank'), os.path.join(ROOT, os.environ.get('OUTMP4', 'AFNICA_Anc91_tank.mp4')), 1920, 600)
else: enc('a91_cave', os.path.join(ROOT, 'AFNICA_Anc91_cave.mp4'), 1920, 600)
