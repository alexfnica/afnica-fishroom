# The OLD bristlenose sprite sheet layout (1254x1254, shown 240x240: male side cell at 0,38; female side at 120,38; belly
# cells one row lower at y 138) rebuilt from the owner's photos, so the old animation (V17.42 fin canvas: fins stepping,
# body flex, breathing; V17.89 flat pectorals; glass mouth rasping) runs on the new fish. Owner: "these were functions that
# worked before - now it's a step back".
# Side cells: the photo scaled uniformly so snout, caudal tip and belly line sit where the old sprite had them.
# Belly cells: the 3D glass render (belly photo on the 3D body, whole tail), mouth on the old mouth spot (the ::after pulse).
# Also writes the female's flat-fin polygons (her fins sit elsewhere than the old female's) in record space (260 px wide).
# Run: python make_sheet.py   -> out/sheet90.webp, out/sheet90_pfin.json
import sys, os, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); INC = os.path.join(HERE, '..', 'incoming'); OUT = os.path.join(HERE, 'out')
u = lambda p: 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
F = 1254 / 240                                   # sheet natural px per css px
# side placement: (photo, snout x, tip x, ground y) -> (old snout x, old tip x, old ground y)
SIDE = {'M': ('anc_mfull_side_cut.png', 1225, 5, 412, 590, 14, 400, 0),
        'F': ('anc_ffull_side_cut.png', 1270, 5, 425, 1227, 643, 432, 627)}
# belly placement: render frame mouth (x,y) and tail-tip x -> old mouth (x,y) and tail x
# V17.99 (owner: "parts are cut off on the glass"): the male's bristles ended at 121.5 css px of a 120 px cell and the
# female's lower pectoral at 70.8 of 70 -> male moved 5 css px toward the tail, female 2 css px up (same scale; the mouth
# spot in the V17.97 ::after CSS moves with them: male 97.4,35.6 / female 104.9,35.1)
MDX, FDY = -5 * F, -2 * F
BELLY = {'M': ('fr_M/M_glass01.png', 241.0, 96.8, 45.0, 535 + MDX, 907, 22 + MDX, 0),
         'F': ('fr_F/F_glass01.png', 243.9, 96.8, 48.2, 1175, 915 + FDY, 650, 627)}
ops = []
for s, (img, S, tip, G, oS, oT, oG, cx) in SIDE.items():
    k = (oS - oT) / (S - tip); ops.append(dict(src=u(os.path.join(INC, img)), k=k, x=oT - tip * k, y=oG - G * k, clip=[cx, 38 * F, 627, 70 * F]))
RI = {}
for s, (img, mx, my, tx, oMx, oMy, oTx, cx) in BELLY.items():
    k = (oMx - oTx) / (mx - tx); RI[s] = len(ops); ops.append(dict(src=u(os.path.join(OUT, img)), k=k, x=oMx - mx * k, y=oMy - my * k, clip=[cx, 138 * F, 627, 70 * F]))
# belly PHOTO over the render, mouth -> vent (sharp mouth disc for the rasping); photo is head-up, turned to head-right
# V17.100 (owner: "the tail looks very shortened"): seen from below, vent to caudal tip is ~half the fish; at the mouth->vent
# scale the tail had only ~37 % of the cell. The male belly photo is drawn 14 % smaller around the mouth (same cell length),
# the freed room goes to the stalk and the edge-on caudal (recolor_sheet.py fills the rest of the cell).
MK100 = float(os.environ.get('MK100', '.86'))
PH = {'M': ('anc_mfull_belly_cut.png', 258, 135, 560, MK100 * 1.063 * 1.40 * (590 - 14) / (1225 - 5), 535 + MDX, 907, 0),
      'F': ('anc_ffull_belly_cut.png', 705, 80, 520, 1.07 * 1.38 * (1227 - 643) / (1270 - 5), 1175, 915 + FDY, 627)}
# V17.100 (owner: "2 sets of bottom fins"): the photo used to fade out AT the vent, cutting its pelvic fins (they reach
# ~45 photo px past it), and the 3D render's own pectorals/pelvics showed round them. Now the photo runs on to just past
# its pelvic tips (SEAM: photo y where it is gone, fade length), and the render only shows behind that seam (stalk + tail).
SEAM = {'M': (733, 12), 'F': (580, 35)}   # V17.100: male photo stalk to its end - the real stalk is long (owner: the fan sat right behind the pelvics, body looked short)   # V17.100 (owner: "the tail looks wrong" - a thin render neck before the fan): the male photo's broad stalk runs to its end; recolor_sheet.py hangs the fan on it
for s_, (img, mx, my, vy, k, oMx, oMy, cx) in PH.items():
    sv, L = SEAM[s_]; xv = oMx - (sv - my) * k
    ops.append(dict(src=u(os.path.join(INC, img)), photo=[mx, my, sv, k, oMx, oMy, L * k], clip=[cx, 138 * F, 627, 70 * F]))
    ops[RI[s_]]['mask'] = [xv + L * k - 2, xv + L * k + 6]   # render stays under the whole fade (no see-through dip)
    if s_ == 'M': ops[RI[s_]]['mask'] = [-20, -10]   # male: no render at all in the belly cell (photo stalk + fan only)
# V17.91 young rows (css y): fry side 238, fry belly 338 (juvenile side 438, belly 538 when its photos arrive); sheet 240x620 css
FRY = 200 * F                                      # the fry rows sit 200 css px below the adult rows
for cx, oT, oS, oG, oM, oTail, oMy in ((0, 14, 590, 400, 535, 22, 907), (627, 643, 1227, 432, 1175, 650, 915)):
    k = (oS - oT) / (754 - 6); ops.append(dict(src=u(os.path.join(INC, 'anc_fry_side_cut.png')), k=k, x=oT - 6 * k, y=oG + FRY - 198 * k, clip=[cx, 238 * F, 627, 70 * F]))
    kb = (oM - oTail) / (481 - 40); ops.append(dict(src=u(os.path.join(INC, 'anc_fry_belly_cut.png')), photo=[124, 40, 900, kb, oM, oMy + FRY], clip=[cx, 338 * F, 627, 70 * F]))
# juvenile rows (css y 438 side, 538 belly): column 0 = olive-brown, column 1 = black. A missing photo is filled with the
# adult cell of that column (copy ops run after everything else) until the owner's photo arrives.
JUV = 400 * F
JUVS = {0: ('anc_juv_olive_side_cut.png', 5, 895, 305, 14, 590, 400), 627: ('anc_juv_black_side_cut.png', 5, 895, 305, 643, 1227, 432)}
copies = []
for cx, (img, tip, sn, G, oT, oS, oG) in JUVS.items():
    if os.path.exists(os.path.join(INC, img)):
        k = (oS - oT) / (sn - tip); ops.append(dict(src=u(os.path.join(INC, img)), k=k, x=oT - tip * k, y=oG + JUV - G * k, clip=[cx, 438 * F, 627, 70 * F]))
    else: copies.append([cx, 38 * F, 627, 70 * F, cx, 438 * F])
for cx, img in ((0, 'anc_juv_olive_belly_cut.png'), (627, 'anc_juv_black_belly_cut.png')):
    if not os.path.exists(os.path.join(INC, img)): copies.append([cx, 138 * F, 627, 70 * F, cx, 538 * F])   # no photo yet: the adult belly
ops.append(dict(copies=copies))
# juvenile belly photos: the whole photo (head-up), the tail end faded softly where the photo frame cut it
JB = {0: ('anc_juv_olive_belly_cut.png', 198, 70, 488, .703 * 228 / 178, 535, 907), 627: ('anc_juv_black_belly_cut.png', 200, 73, 491, .703 * 228 / 178, 1175, 915)}
for cx, (img, mx, my, vy, k, oMx, oMy) in JB.items():
    if os.path.exists(os.path.join(INC, img)):
        ops.append(dict(src=u(os.path.join(INC, img)), photo=[mx, my, vy, k, oMx, oMy + JUV], clip=[cx, 538 * F, 627, 70 * F]))
SHEET_H = round(620 * F)
JS = r"""(async (ops,SH)=>{const c=document.createElement('canvas');c.width=1254;c.height=SH;const g=c.getContext('2d');g.imageSmoothingQuality='high';
for(const o of ops){if(o.copies){for(const [sx,sy,w,h,dx,dy] of o.copies)g.drawImage(c,sx,sy,w,h,dx,dy,w,h);continue;}const im=new Image();im.src=o.src;await im.decode();
 if(o.photo){const [mx,my,vy,k,X,Y,FL]=o.photo,T=document.createElement('canvas');T.width=1254;T.height=SH;const t=T.getContext('2d');t.imageSmoothingQuality='high';
  t.save();t.translate(X,Y);t.scale(k,k);t.rotate(Math.PI/2);t.translate(-mx,-my);t.drawImage(im,0,0);t.restore();
  const xv=X-(vy-my)*k,gr=t.createLinearGradient(xv,0,xv+(FL||28),0);gr.addColorStop(0,'rgba(0,0,0,0)');gr.addColorStop(1,'rgba(0,0,0,1)');   /* soft seam at the vent */
  t.globalCompositeOperation='destination-in';t.fillStyle=gr;t.fillRect(0,0,1254,SH);
  g.save();g.beginPath();g.rect(...o.clip);g.clip();g.drawImage(T,0,0);g.restore();continue;}
 if(o.mask){const T=document.createElement('canvas');T.width=1254;T.height=SH;const t=T.getContext('2d');t.imageSmoothingQuality='high';t.drawImage(im,o.x,o.y,im.naturalWidth*o.k,im.naturalHeight*o.k);
  const gr=t.createLinearGradient(o.mask[0],0,o.mask[1],0);gr.addColorStop(0,'rgba(0,0,0,1)');gr.addColorStop(1,'rgba(0,0,0,0)');   /* V17.100: render only behind the photo seam */
  t.globalCompositeOperation='destination-in';t.fillStyle=gr;t.fillRect(0,0,1254,SH);g.save();g.beginPath();g.rect(...o.clip);g.clip();g.drawImage(T,0,0);g.restore();continue;}
 g.save();g.beginPath();g.rect(...o.clip);g.clip();g.drawImage(im,o.x,o.y,im.naturalWidth*o.k,im.naturalHeight*o.k);g.restore();}
return c.toDataURL('image/webp',.93);})"""
c = Chrome(400, 300, 1, port=int(os.environ.get('AF_PORT', '9495')))
try:
    url = c.js(JS + '(%s,%d)' % (json.dumps(ops), SHEET_H))
    open(os.path.join(OUT, 'sheet90.webp'), 'wb').write(base64.b64decode(url.split(',', 1)[1]))
finally: c.close()
# female flat-fin polygons in record space: record = the 120x70 css cell at natural px, 260 px wide
import types
for m_ in ('bpy', 'bmesh', 'bpy_extras', 'bpy_extras.object_utils'): sys.modules.setdefault(m_, types.ModuleType(m_))   # tables only: no Blender here
mu = sys.modules.setdefault('mathutils', types.ModuleType('mathutils')); mu.Vector = mu.Matrix = object
sys.path.insert(0, HERE); import anc_build2 as B2
sp = B2.SPEC['F']; img, S, tip, G, oS, oT, oG, cx = SIDE['F']; k = (oS - oT) / (S - tip)
RK = 260 / (120 * F)
def rec(px, py): return [round(((oT - tip * k + px * k) - cx) * RK, 1), round(((oG - G * k + py * k) - 38 * F) * RK, 1)]
def bot(px): return float(np.interp(px, [r[0] for r in sp['body']], [r[2] for r in sp['body']]))
fins = []
for (x0, x1, y0, y1), rot, row, m in ((sp['sfins'][2], .2, .12, 3), (sp['sfins'][1], .17, .07, 1)):        # pectoral, pelvic (as the old order)
    b0, b1 = bot(x0) - 4, bot(x1) - 4
    poly = [rec(x0, b0), rec(x1, b1), rec(x1, y1 - 25), rec((x0 + x1) / 2, y1), rec(x0, y1 - 10)]
    fins.append(dict(poly=poly, belly=[rec(x0 - 4, b0), rec(x1 + 4, b1)], root=rec(x1 - 6, b1 + 4), rot=rot, sq=.62, m=m, mr=3, row=row))
json.dump({'anc|120|38': fins}, open(os.path.join(OUT, 'sheet90_pfin.json'), 'w'))
print('ok', os.path.getsize(os.path.join(OUT, 'sheet90.webp')), 'bytes', json.dumps(fins)[:300])
