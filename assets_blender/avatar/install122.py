# V17.122: embeds the Gemini player characters (avatar/game_front/*.webp = standing, avatar/game_walk/*.webp = walking) and block122.css/js into the
# game between <!-- V17.122 BEGIN/END --> (right before </body></html>, after V17.121). Safe to re-run: it replaces its own block.
# Run: D:/Blender/5.2/python/bin/python.exe assets_blender/avatar/install122.py
import os, re, base64, json
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, '..', '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
def pack(folder, prefix):
    out = {}
    for f in sorted(os.listdir(os.path.join(HERE, folder))):
        m = re.match(r'%s_(\d\d)_.*\.webp$' % prefix, f)
        if m: out[m.group(1)] = 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(HERE, folder, f), 'rb').read()).decode()
    return out
data = 'window.AV122=' + json.dumps({'front': pack('game_front', 'front'), 'walk': pack('game_walk', 'walk')}, separators=(',', ':')) + ';\n'
block = '<!-- V17.122 BEGIN -->\n<style>\n' + rd('block122.css') + '</style>\n<script>\n' + data + rd('block122.js') + '\n</script>\n<!-- V17.122 END -->\n'
s = open(GAME, encoding='utf-8', newline='').read()
if '<!-- V17.122 BEGIN -->' in s:
    a = s.index('<!-- V17.122 BEGIN -->'); b = s.index('<!-- V17.122 END -->') + len('<!-- V17.122 END -->\n')
    s = s[:a] + block + s[b:]
else:
    t = '</body></html>'; assert s.count(t) == 1; s = s.replace(t, block + t)
tmp = GAME + '.tmp122'; open(tmp, 'w', encoding='utf-8', newline='').write(s); os.replace(tmp, GAME)   # write beside the game, swap only when complete
print('installed V17.122: %d front, %d walk, %d KB of block' % (len(json.loads(data[len('window.AV122='):-2])['front']), len(json.loads(data[len('window.AV122='):-2])['walk']), len(block) // 1024))
