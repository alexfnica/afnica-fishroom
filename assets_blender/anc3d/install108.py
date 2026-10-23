# Install / update the V17.108 spawning block (block108.js) in the game HTML, between <!-- V17.108 BEGIN --> and
# <!-- V17.108 END -->, right after the V17.90 block (install90.py leaves it alone). Run: python install108.py
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, '..', '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
js = open(os.path.join(HERE, 'block108.js'), encoding='utf-8').read()
assert '//' not in js.replace('http://', '').replace('https://', ''), 'no // comments in the block'
block = '<!-- V17.108 BEGIN -->\n<script>\n' + js + '</script>\n<!-- V17.108 END -->\n'
html = open(GAME, encoding='utf-8', newline='').read()
if '<!-- V17.108 BEGIN -->' in html:
    a = html.index('<!-- V17.108 BEGIN -->'); b = html.index('<!-- V17.108 END -->\n') + len('<!-- V17.108 END -->\n')
    html = html[:a] + block + html[b:]; print('replaced')
else:
    k = html.index('<!-- V17.90 END -->\n') + len('<!-- V17.90 END -->\n')
    html = html[:k] + block + html[k:]; print('inserted')
import time
for _try in range(20):                                        # the file can be briefly locked by a reader (Windows)
    try: open(GAME, 'w', encoding='utf-8', newline='').write(html); break
    except OSError as e: print('retry', e); time.sleep(1)
