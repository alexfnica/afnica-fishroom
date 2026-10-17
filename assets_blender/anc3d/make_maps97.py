# V17.97: colour maps for the 3D frames (turn, cave layers, fight), recoloured in the browser at load time:
# MB = olive male -> black (the black female's 3D colours), FO = black female -> brown (the olive male's 3D colours).
# Each map: brightness LUT (256) + tint table (24x3), see recolor_sheet.py. Built from the colour-matched turn frames.
# Run: python make_maps97.py   -> out/maps97.json
import os, sys, glob, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pngio
from recolor_sheet import hist_map, fishpx
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
px = lambda s: np.concatenate([fishpx(pngio.read(f)) for f in sorted(glob.glob(os.path.join(OUT, 'turn95', s + '_turn*.png')))[::3]])
M, F = px('M'), px('F')
mp = {}
for k, (a, b) in {'MB': (M, F), 'FO': (F, M)}.items():
    lut, tint = hist_map(a, b); mp[k] = dict(lut=[int(round(v)) for v in lut], tint=[[round(float(x), 3) for x in t] for t in tint])
json.dump(mp, open(os.path.join(OUT, 'maps97.json'), 'w'), separators=(',', ':'))
print('ok', {k: (v['lut'][40], v['lut'][128], v['lut'][220]) for k, v in mp.items()})
