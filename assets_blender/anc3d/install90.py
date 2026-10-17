# Install / update the V17.90 block in the game HTML: block90.js with the three WebP sprite sheets embedded.
# The block sits between <!-- V17.90 BEGIN --> and <!-- V17.90 END --> just before </body>; re-running replaces it.
# Run: python install90.py
import os, json, base64, re
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
GAME = os.path.join(HERE, '..', '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
js = open(os.path.join(HERE, 'block90.js'), encoding='utf-8').read()
for key, pre in (('T', 'atlas95_T'), ('C2', 'atlas92_C2'), ('P', 'atlas96_P')):
    idx = json.load(open(os.path.join(OUT, pre + '.json')))
    url = 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(OUT, pre + '.webp'), 'rb').read()).decode()
    small = json.dumps(dict(w=idx['w'], h=idx['h'], names=idx['names'], pos=idx['pos']), separators=(',', ':'))
    assert js.count('@@ATLAS_%s@@' % key) == 1 and js.count('@@INDEX_%s@@' % key) == 1
    js = js.replace('@@ATLAS_%s@@' % key, url).replace('@@INDEX_%s@@' % key, small)
sheet = 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(OUT, 'sheet90.webp'), 'rb').read()).decode()
assert js.count('@@SHEET@@') == 1
js = js.replace('@@SHEET@@', sheet)
assert '//' not in re.sub(r"data:image/webp;base64,[A-Za-z0-9+/=]+", '', js).replace('http://', '').replace('https://', ''), 'no // comments in the block'
block = '<!-- V17.90 BEGIN -->\n<script>\n' + js + '</script>\n<!-- V17.90 END -->\n'
html = open(GAME, encoding='utf-8', newline='').read()
if '<!-- V17.90 BEGIN -->' in html:
    a = html.index('<!-- V17.90 BEGIN -->'); b = html.index('<!-- V17.90 END -->\n') + len('<!-- V17.90 END -->\n')
    html = html[:a] + block + html[b:]; print('replaced')
else:
    assert html.count('</body></html>') == 1
    html = html.replace('</body></html>', block + '</body></html>'); print('inserted')
import time
for _try in range(20):                                        # the file can be briefly locked by a reader (Windows)
    try: open(GAME, 'w', encoding='utf-8', newline='').write(html); break
    except OSError as e: print('retry', e); time.sleep(1)
else: raise SystemExit('could not write the game file')
print('block %.0f KB' % (len(block) / 1024))
