# V17.121: writes the screen-system block (block121.css + block121.js) into the game between <!-- V17.121 BEGIN/END --> (right before </body></html>).
# Safe to re-run: it replaces its own block. Run: D:/Blender/5.2/python/bin/python.exe assets_blender/ui121/install121.py
import os
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, '..', '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
block = '<!-- V17.121 BEGIN -->\n<style>\n' + rd('block121.css') + '</style>\n<script>\n' + rd('block121.js') + '\n</script>\n<!-- V17.121 END -->\n'
s = open(GAME, encoding='utf-8', newline='').read()
if '<!-- V17.121 BEGIN -->' in s:
    a = s.index('<!-- V17.121 BEGIN -->'); b = s.index('<!-- V17.121 END -->') + len('<!-- V17.121 END -->\n')
    s = s[:a] + block + s[b:]
else:
    t = '</body></html>'; assert s.count(t) == 1; s = s.replace(t, block + t)
tmp = GAME + '.tmp121'; open(tmp, 'w', encoding='utf-8', newline='').write(s); os.replace(tmp, GAME)   # write beside the game, swap only when complete
print('installed V17.121')
