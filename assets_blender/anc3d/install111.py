# V17.111: writes the cave-inspect block (block111.js + the footage as data URIs) into the game between <!-- V17.111 BEGIN/END -->
# (right before </body></html>). Safe to re-run: it replaces its own block. Footage = assets_blender/incoming:
#   anc_wriggler_scene_full.webp (full-yolk scene, interim poster; older anc_wriggler_heap.webp as fallback), anc_wriggler_heap_full.mp4 / _half.mp4 / _low.mp4 (Gemini loops, optional).
# Run: D:/Blender/5.2/python/bin/python.exe anc3d/install111.py
import os, base64, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); INC = os.path.join(HERE, '..', 'incoming')
GAME = os.path.join(HERE, '..', '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
def uri(name, mime):
    p = os.path.join(INC, name)
    if not os.path.exists(p): return None
    sz = os.path.getsize(p)
    if sz > 3_000_000: print('WARNING', name, '%.1f MB - shrink it first (480p, ~1-2 MB)' % (sz / 1e6))
    return 'data:%s;base64,%s' % (mime, base64.b64encode(open(p, 'rb').read()).decode())
A = {'poster': uri('anc_wriggler_scene_full.webp', 'image/webp') or uri('anc_wriggler_heap.webp', 'image/webp')}   # newest stage image first
for k in ('full', 'half', 'low'): A[k] = uri('anc_wriggler_heap_%s.mp4' % k, 'video/mp4')
for k in ('full', 'half', 'low'): A['poster_' + k] = uri('anc_wriggler_scene_%s.webp' % k, 'image/webp')   # still of each yolk stage (poster while the video loads, or instead of it)
A = {k: v for k, v in A.items() if v}
IMG = {k: uri(n, 'image/png') for k, n in (('larva', 'anc_wriggler_side_cut.png'), ('free', 'anc_wriggler_free_cut.png'))}; IMG = {k: v for k, v in IMG.items() if v}   # V17.110: fry sprites (cut-outs of the Gemini larva / free-fry photos)
assets = 'window.ANC110_IMG={' + ','.join('%s:"%s"' % (k, v) for k, v in IMG.items()) + '};' + chr(10) + 'window.ANC111_ASSETS={' + ','.join('%s:"%s"' % (k, v) for k, v in A.items()) + '};\n'
block = '<!-- V17.111 BEGIN -->\n<script>\n' + assets + open(os.path.join(HERE, 'block111.js'), encoding='utf-8').read() + '</script>\n<!-- V17.111 END -->\n'
s = open(GAME, encoding='utf-8', newline='').read()
if '<!-- V17.111 BEGIN -->' in s:
    a = s.index('<!-- V17.111 BEGIN -->'); b = s.index('<!-- V17.111 END -->') + len('<!-- V17.111 END -->\n')
    s = s[:a] + block + s[b:]
else:
    t = '</body></html>'; assert s.count(t) == 1; s = s.replace(t, block + t)
open(GAME, 'w', encoding='utf-8', newline='').write(s)
print('installed V17.111 with', ', '.join(A.keys()))
