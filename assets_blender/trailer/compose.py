# Render the trailer: timeline -> frames (compose.html in headless Chrome) -> music with synced SFX -> MP4.
# Run: python compose.py [first_frame last_frame]   (a range renders only those frames, for previews)
import os, sys, json, time, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome
from timeline import TL, SFX, DURATION, MUSIC
HERE = os.path.dirname(os.path.abspath(__file__)); OUTF = os.path.join(HERE, 'out', 'frames'); os.makedirs(OUTF, exist_ok=True)
BL = r'D:\Blender\blender.exe'; FPS = 30
N = int(round(DURATION * FPS))
rng = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, N - 1)
# lengths of the takes
for s in TL['shots']:
    s['len'] = len([f for f in os.listdir(os.path.join(HERE, 'raw', s['take'])) if f.endswith('.jpg')])
c = Chrome(1080, 1920, 1, port=9555)
try:
    c.cmd('Page.navigate', url='file:///' + os.path.join(HERE, 'compose.html').replace('\\', '/')); c.wait_event('Page.loadEventFired', 30)
    c.js('ready'); c.js('window.TL=' + json.dumps(TL) + ';1')
    t0 = time.time()
    for i in range(rng[0], rng[1] + 1):
        c.js('renderFrame(%d)' % i)
        c.shot(os.path.join(OUTF, '%05d.jpg' % i), clip=dict(x=0, y=0, width=1080, height=1920, scale=1), q=95)
        if i % 60 == 0: print('frame', i, '/', N, round(time.time() - t0), 's', flush=True)
finally:
    c.close()
if rng == (0, N - 1):
    json.dump(SFX, open(os.path.join(HERE, 'out', 'sfx.json'), 'w'))
    wav = os.path.join(HERE, 'out', 'music_trailer.wav')
    subprocess.run([BL, '-b', '-P', os.path.join(HERE, 'music.py'), '--', 'A', wav, str(MUSIC['bars']), os.path.join(HERE, 'out', 'sfx.json'), str(MUSIC['drop']), str(MUSIC['end'])], capture_output=True)
    mp4 = os.path.join(HERE, 'out', 'AFNICA_trailer.mp4')
    r = subprocess.run([BL, '-b', '-P', os.path.join(HERE, 'encode.py'), '--', OUTF, wav, mp4], capture_output=True, text=True)
    print([l for l in r.stdout.splitlines() if 'ENCODED' in l or 'rror' in l][-3:])
