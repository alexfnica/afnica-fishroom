# Side-on frames straight from the owner's photos (owner: the 3D renders "look like a placeholder" next to the photos).
# Same frame contract as render_frames.py (320x180 = 2x of 160x90 game px, mid-body ground point at 155.4, 96.8) so the
# 3D turn frames (yaw15..90) and the cave frames still fit. A soft contact shadow is painted under the belly.
#   yaw00 = the photo; crawl00-07 = tiny alternating rock of the body as the fins step; rasp00-01 = head pressed down
#   (rotated about the mouth); swim00-05 = nose slightly up, gentle pitch.
# Run: python photo_frames.py <M|F> <out_dir>   (overwrites those frames in out_dir)
import sys, os, json, base64, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
SPEC = {'M': dict(img='anc_mfull_side_cut.png', S=1225, G=412, tip=5, L=3.39),
        'F': dict(img='anc_ffull_side_cut.png', S=1270, G=425, tip=5, L=3.30),
        'JO': dict(img='anc_juv_olive_side_cut.png', S=895, G=330, tip=5, L=3.39),
        'JB': dict(img='anc_juv_black_side_cut.png', S=902, G=330, tip=5, L=3.30)}
SEX, OUT = sys.argv[1], sys.argv[2]; sp = SPEC[SEX]
src = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'incoming', sp['img']), 'rb').read()).decode()
k = sp['L'] * 32.5 * 2 / (sp['S'] - sp['tip'])                       # photo px -> frame px
mid = (sp['S'] + sp['tip']) / 2                                         # mid-length (photo x) sits on the pivot
FR = [('yaw', 0, 0, 0, 0)]
import math
for i in range(8): FR.append(('crawl', i, .45 * math.sin(2 * math.pi * i / 8), .35 * math.sin(2 * math.pi * i / 8 + 1.2), 0))
for i in range(2): FR.append(('rasp', i, 3.2 + 1.2 * i, 0, 1))
for i in range(6): FR.append(('swim', i, -2.0 + .8 * math.sin(2 * math.pi * i / 6), -1.5 * math.sin(2 * math.pi * i / 6 + .7), 0))
JS = r"""(async (src,k,mid,S,G,FR)=>{const im=new Image();im.src=src;await im.decode();const out={};
for(const [kind,i,deg,dy,mouth] of FR){const c=document.createElement('canvas');c.width=320;c.height=180;const g=c.getContext('2d');
 /* contact shadow: soft dark ellipse under the belly */
 g.save();g.filter='blur(5px)';g.fillStyle='rgba(0,0,0,.32)';g.beginPath();g.ellipse(155.4+8,96.8+2,(S-mid)*k*.78,6.5,0,0,7);g.fill();g.restore();
 g.save();g.imageSmoothingQuality='high';
 const px=mouth?155.4+(S-mid)*k*.92:155.4,py=96.8;               /* rasp pivots about the mouth, the rest about mid-body */
 g.translate(px,py+dy);g.rotate(deg*Math.PI/180);g.translate(-px,-py);
 g.drawImage(im,155.4-mid*k,96.8-G*k,im.naturalWidth*k,im.naturalHeight*k);g.restore();
 out[kind+String(i).padStart(2,'0')]=c.toDataURL('image/png');}
return JSON.stringify(out);})"""
c = Chrome(400, 300, 1, port=int(os.environ.get('AF_PORT', '9491')))
try:
    r = json.loads(c.js(JS + '(%s,%f,%f,%f,%f,%s)' % (json.dumps(src), k, mid, sp['S'], sp['G'], json.dumps(FR))))
    for name, url in r.items():
        open(os.path.join(OUT, '%s_%s.png' % (SEX, name)), 'wb').write(base64.b64decode(url.split(',', 1)[1]))
    print('ok', len(r), 'frames', SEX)
finally: c.close()
