# V17.120: writes the fish-store block (block120.css + block120.js) into the game between <!-- V17.120 BEGIN/END --> (right before </body></html>).
# Safe to re-run: it replaces its own block. Run: D:/Blender/5.2/python/bin/python.exe assets_blender/store/install120.py
import os
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, '..', '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
import base64
def uri(n): return 'data:image/png;base64,' + base64.b64encode(open(os.path.join(HERE, n), 'rb').read()).decode()
# the AFNICA FISHROOM logo (black on transparent, made from assets_blender/logo/afnica_fishroom_src.webp): shirt print + sign
logo = 'window.ST120_LOGO={' + ','.join('%s:"%s"' % (k, uri('logo_%s.png' % k)) for k in ('icon', 'word')) + ',owner:"%s"};\n' % uri('owner_cut.png')
import glob
pp = sorted(glob.glob(os.path.join(HERE, 'people', '*.png')))
if pp: logo += 'window.ST120_PEOPLE=[' + ','.join('"data:image/png;base64,%s"' % base64.b64encode(open(f, 'rb').read()).decode() for f in pp) + '];' + chr(10)
import struct
def asp(f):
    b = open(f, 'rb').read(24); w, h = struct.unpack('>II', b[16:24]); return round(w / h, 3)
if pp: logo += 'window.ST120_PEOPLE_ASPECT=[' + ','.join(str(asp(f)) for f in pp) + '];' + chr(10)
print('people sprites:', len(pp))
block = '<!-- V17.120 BEGIN -->\n<style>\n' + rd('block120.css') + '</style>\n<script>\n' + logo + rd('walk120.js') + rd('block120.js') + '\n</script>\n<!-- V17.120 END -->\n'
s = open(GAME, encoding='utf-8', newline='').read()
if '<!-- V17.120 BEGIN -->' in s:
    a = s.index('<!-- V17.120 BEGIN -->'); b = s.index('<!-- V17.120 END -->') + len('<!-- V17.120 END -->\n')
    s = s[:a] + block + s[b:]
else:
    t = '</body></html>'; assert s.count(t) == 1; s = s.replace(t, block + t)
open(GAME, 'w', encoding='utf-8', newline='').write(s)
print('installed V17.120')
