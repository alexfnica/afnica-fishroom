# V17.100 (owner: "match the colour"): colour-match the raw turn frames to the PHOTO the game shows before and after the
# turn (the side cell of the sheet), not to the older 3D frames (they came out lighter than the photo). Per fish type: a
# brightness LUT + tint table (recolor_sheet.hist_map) learnt from the fish pixels of turn frame 00 (side view) -> the
# fish pixels of its sheet cell, applied to every frame of that type.
# Run: python lut_match_photo100.py <raw_dir> <out_dir>
import sys, os, glob, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pngio
from recolor_sheet import hist_map, recolor, fishpx
RAW, OUT = sys.argv[1:3]; os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
# sheet cells (css px: x, y) of the side photo each turn type stands for
CELL = {'M': (0, 38), 'F': (120, 38), 'JO': (0, 438), 'JB': (120, 438)}
from cdp import Chrome
c = Chrome(400, 300, 1, port=int(os.environ.get('AF_PORT', '9476')))
try:
    src = 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(HERE, 'out', 'sheet97.webp'), 'rb').read()).decode()
    r = json.loads(c.js("(async s=>{const i=new Image();i.src=s;await i.decode();const c=document.createElement('canvas');c.width=i.naturalWidth;c.height=i.naturalHeight;"
                        "const g=c.getContext('2d');g.drawImage(i,0,0);const d=g.getImageData(0,0,c.width,c.height).data;let b='';for(let k=0;k<d.length;k+=32768)b+=String.fromCharCode.apply(null,d.subarray(k,k+32768));"
                        "return JSON.stringify({w:c.width,h:c.height,b:btoa(b)})})(%s)" % json.dumps(src)))
finally: c.close()
W, H = r['w'], r['h']; A = np.frombuffer(base64.b64decode(r['b']), np.uint8).reshape(H, W, 4); F = W / 480.
for S, (cx, cy) in CELL.items():
    files = sorted(glob.glob(os.path.join(RAW, S + '_turn*.png')))
    if not files: print('no frames', S); continue
    cell = A[int(cy * F):int((cy + 70) * F), int(cx * F):int((cx + 120) * F)]
    m = hist_map(fishpx(pngio.read(files[0])), fishpx(cell))
    for f in files:
        a = pngio.read(f); pngio.write(os.path.join(OUT, os.path.basename(f)), recolor(a, m))
    lum = lambda p: float((p[:, 0] * .299 + p[:, 1] * .587 + p[:, 2] * .114).mean())
    print(S, len(files), 'frames | mean brightness raw %.0f -> matched %.0f, photo %.0f' % (
        lum(fishpx(pngio.read(files[0]))), lum(fishpx(pngio.read(os.path.join(OUT, os.path.basename(files[0]))))), lum(fishpx(cell))))
