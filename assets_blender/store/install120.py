# V17.120: writes the fish-store block (block120.css + block120.js) into the game between <!-- V17.120 BEGIN/END --> (right before </body></html>).
# Safe to re-run: it replaces its own block. Run: D:/Blender/5.2/python/bin/python.exe assets_blender/store/install120.py
import os
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, '..', '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
import base64
def uri(n): return 'data:image/png;base64,' + base64.b64encode(open(os.path.join(HERE, n), 'rb').read()).decode()
# the AFNICA FISHROOM logo (black on transparent, made from assets_blender/logo/afnica_fishroom_src.webp): shirt print + sign
import json as _json
BF = _json.load(open(os.path.join(HERE, 'poses', 'bagfish.json'))) if os.path.exists(os.path.join(HERE, 'poses', 'bagfish.json')) else {}
def cleanp(n):   # the bag pictures with the painted fish taken out (fix_bag_fish.py), else the original
    c = os.path.join('poses', n + '_clean.png'); return c if os.path.exists(os.path.join(HERE, c)) else os.path.join('poses', n + '.png')
logo = 'window.ST120_LOGO={' + ','.join('%s:"%s"' % (k, uri('logo_%s.png' % k)) for k in ('icon', 'word')) + ',owner:"%s",poses:{' % uri('owner_cut.png') + ','.join('%s:"%s"' % (k, uri(cleanp('owner_%s' % k))) for k in ('idle', 'greet', 'bag', 'give')) + '}};' + chr(10)   # the owner's counter poses (Gemini, cut by cut_owner_poses.py)
import glob
pp = sorted(glob.glob(os.path.join(HERE, 'people', '*.png')))
# a pose sheet (poses/personNN_walk/bag/point.png, cut by cut_sheet.py) replaces person NN's old picture, so all its poses match
PZ = os.path.join(HERE, 'poses')
pp = [os.path.join(PZ, 'person%02d_walk.png' % (i + 1)) if os.path.exists(os.path.join(PZ, 'person%02d_walk.png' % (i + 1))) else f for i, f in enumerate(pp)]
def puri(f): return '"data:image/png;base64,%s"' % base64.b64encode(open(f, 'rb').read()).decode()
def poses(i):
    b, q = os.path.join(HERE, cleanp('person%02d_bag' % (i + 1))), os.path.join(PZ, 'person%02d_point.png' % (i + 1))
    fb = BF.get('person%02d_bag' % (i + 1)) if b.endswith('_clean.png') else None
    return '{bag:%s,point:%s,fish:%s}' % (puri(b) if os.path.exists(b) else 'null', puri(q) if os.path.exists(q) else 'null', _json.dumps(fb))
if pp: logo += 'window.ST120_POSES=[' + ','.join(poses(i) for i in range(len(pp))) + '];' + chr(10)
if pp: logo += 'window.ST120_PEOPLE=[' + ','.join('"data:image/png;base64,%s"' % base64.b64encode(open(f, 'rb').read()).decode() for f in pp) + '];' + chr(10)
import struct
def asp(f):
    b = open(f, 'rb').read(24); w, h = struct.unpack('>II', b[16:24]); return round(w / h, 3)
if pp: logo += 'window.ST120_PEOPLE_ASPECT=[' + ','.join(str(asp(f)) for f in pp) + '];' + chr(10)
logo += 'window.ST120_BAGFISH=' + _json.dumps({k: v for k, v in BF.items() if k.startswith('owner')}) + ';' + chr(10)
print('people sprites:', len(pp))
block = '<!-- V17.120 BEGIN -->\n<style>\n' + rd('block120.css') + '</style>\n<script>\n' + logo + rd('walk120.js') + rd('block120.js') + '\n</script>\n<!-- V17.120 END -->\n'
s = open(GAME, encoding='utf-8', newline='').read()
if '<!-- V17.120 BEGIN -->' in s:
    a = s.index('<!-- V17.120 BEGIN -->'); b = s.index('<!-- V17.120 END -->') + len('<!-- V17.120 END -->\n')
    s = s[:a] + block + s[b:]
else:
    t = '</body></html>'; assert s.count(t) == 1; s = s.replace(t, block + t)
import time
for _try in range(8):   # write beside the game, swap only when complete (another session / process may hold the file for a moment)
    try:
        tmp = GAME + '.tmp120'; open(tmp, 'w', encoding='utf-8', newline='').write(s); os.replace(tmp, GAME); break
    except OSError as e:
        print('retry write', e); time.sleep(1.5)
else: raise SystemExit('could not write the game file')
print('installed V17.120')
