# V17.90 session clip: main tank, 1 ready male + 2 females, 40 s, bottom of the tank (throw-away headless game).
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
from takes_anc89 import SEED
FISH = "[T.fish('anc','M',40,{ancCaveCycleStart:st.day}),T.fish('anc','F',36),T.fish('anc','F',30)]"
c = anc_game(tank='main', fish=FISH, warm=1, dsf=2, pre=SEED % int(os.environ.get('SEED', '7')))
try:
    clip = dict(x=0, y=540 - 300, width=960, height=300, scale=1.0)
    cap = lambda i: 'Bristlenose session: 1 male + 2 females (your photos; 3D turns and cave). ' + ('%d s' % (i // 24))
    film(c, 'a90_session', 40, fps=24, caption=cap, clip=clip)
finally: c.close()
out = os.path.join(HERE, '..', '..', 'AFNICA_Anc90_session_v3.mp4')
subprocess.run([r'D:\Blender\blender.exe', '-b', '-P', os.path.join(HERE, 'encode_plain.py'), '--', os.path.join(HERE, 'raw', 'a90_session'), out, '1920', '600', '24'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('clip', out, os.path.exists(out))
