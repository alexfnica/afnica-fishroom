# V17.90 bristlenose 3D, second generation: built from the owner's specimen photos (assets_blender/incoming, see
# memory "anc-specimen-photos"): full-grown male (olive-brown) and female (black), each from its OWN side + top + belly photo.
# side photo -> flanks, dorsal, adipose, caudal; top photo -> back + pectoral/pelvic fins (spread flat like wings);
# belly photo -> underside with the sucker mouth. Cave, scene and clearance helpers come from anc_build.py.
import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector
import anc_build as B

INC = os.path.join(B.HERE, '..', 'incoming')
LEN = {'M': 3.39, 'F': 3.30, 'JO': 3.39, 'JB': 3.30}   # juveniles sit in the male / female column of the sheet
EMIT = .22                                     # photo brightness added on top of the lighting
HANG = False                                   # V17.100 turn frames: paired fins + chin bristles hang below the belly like the photo (no ground clamp; the caller lifts the fish)
FIN_REACH = .5                                 # how far out the paired fins reach the sand (smaller = steeper, more visible from the side)                    # snout -> caudal tip in units (1 unit = 32.5 game px), like the old sprites

# Measured on the cut photos (px). Side: snout x S, ground (belly line) G, caudal tip x; body rows = (side x, back y, belly y,
# half width in TOP-photo px). Top: snout x, centre line y, side px per top px (kt). Belly (head up): centre x, snout y,
# top px per belly px (kb), last usable row (bmax: the photo is cut off / the tail curls below it).
SPEC = {
 'M': dict(side='anc_mfull_side_cut.png', top='anc_mfull_top_fix.png', belly='anc_mfull_belly_cut.png',
   S=1225, G=412, tip=5, kt=1.063, top_snout=1170, top_cy=315, kb=1.40, b_cx=258, b_snout=45, bmax=720,
   body=[(300, 265, 340, 18), (400, 255, 360, 38), (500, 245, 380, 60), (600, 232, 395, 81), (700, 215, 405, 105), (800, 202, 410, 133),
         (900, 205, 412, 148), (1000, 225, 411, 150), (1100, 255, 410, 140), (1150, 280, 411, 130), (1200, 318, 405, 100), (1225, 360, 392, 60)],
   caudal=(0, 312, 135, 440), dorsal=[(432, 245), (440, 190), (520, 90), (610, 12), (650, 8), (700, 60), (760, 150), (795, 200), (780, 212), (600, 236)],
   adipose=[(345, 272), (352, 242), (390, 250), (425, 262), (420, 278)],
   pect=(668, 912, 0), pect_base=880, pelv=(505, 708, 92), pelv_base=690, bristles=True,
   sfins=[(415, 532, 350, 425), (512, 728, 345, 460), (712, 948, 345, 480)], bris=(1040, 1285, 140, 479)),
 'F': dict(side='anc_ffull_side_cut.png', top='anc_ffull_top_cut.png', belly='anc_ffull_belly_cut.png',
   S=1270, G=425, tip=5, kt=1.07, top_snout=1178, top_cy=292, kb=1.38, b_cx=705, b_snout=5, bmax=520,
   body=[(345, 285, 360, 15), (400, 272, 375, 35), (500, 255, 395, 55), (600, 240, 410, 75), (700, 225, 420, 100), (800, 210, 425, 125),
         (900, 210, 425, 140), (1000, 225, 420, 145), (1100, 255, 415, 130), (1150, 270, 415, 115), (1200, 295, 415, 95), (1250, 330, 410, 70), (1270, 370, 395, 40)],
   caudal=(0, 348, 170, 505), dorsal=[(470, 255), (478, 200), (560, 110), (650, 30), (700, 8), (760, 60), (810, 140), (840, 200), (820, 215), (640, 240)],
   adipose=[(372, 300), (380, 268), (410, 272), (445, 285), (440, 300)],
   pect=(698, 935, 0), pect_base=900, pelv=(518, 722, 92), pelv_base=700, bristles=False,
   sfins=[(448, 578, 385, 485), (558, 782, 385, 528), (768, 1003, 375, 500)], bris=None),
}

# V17.91 juveniles (owner's photos, same pose for both colours; measured on the olive one, black offsets +-3 px)
_JBODY = [(215, 214, 300, 19), (316, 208, 300, 31), (422, 189, 307, 52), (528, 170, 318, 77), (634, 154, 323, 102),
          (741, 173, 325, 112), (826, 215, 329, 90), (879, 265, 328, 50), (895, 300, 322, 25)]
_JCOMMON = dict(G=330, tip=5, kt=1.063, top_cy=232, kb=1.0, b_cx=198, b_snout=5, bmax=480,
   caudal=(5, 215, 185, 335), dorsal=[(330, 165), (345, 120), (410, 50), (455, 8), (495, 25), (560, 100), (592, 150), (580, 160), (450, 185), (340, 195)],
   adipose=[(255, 225), (262, 205), (285, 200), (305, 210), (300, 225)],
   pect=(500, 665, 0), pect_base=630, pelv=(355, 505, 60), pelv_base=470, bristles=False,
   sfins=[(315, 385, 295, 335), (372, 540, 280, 358), (528, 722, 270, 368)], bris=None)
SPEC['JO'] = dict(_JCOMMON, side='anc_juv_olive_side_cut.png', top='anc_juv_olive_top_fix.png', belly='anc_juv_olive_belly_cut.png', S=895, top_snout=845, body=_JBODY)
SPEC['JB'] = dict(_JCOMMON, side='anc_juv_black_side_cut.png', top='anc_juv_black_top_fix.png', belly='anc_juv_black_belly_cut.png', S=902, top_snout=839, top_cy=231, b_cx=200,
                  body=[(x + 6, t, b, w) for x, t, b, w in _JBODY])

_img = {}
def img(name):
    if name not in _img:
        im = bpy.data.images.load(os.path.join(INC, name)); im.pack(); _img[name] = im
    return _img[name]

def pixels(im):
    W, H = im.size; px = np.empty(W * H * 4, np.float32); im.pixels.foreach_get(px); return px.reshape(H, W, 4)[::-1]   # [y down, x]

def masked(sp, which):
    """a copy of the side or top photo with only the fins kept (for the fin plates)"""
    key = (id(sp), which)
    if key in _img: return _img[key]
    src = img(sp[which]); W, H = src.size; px = pixels(src).copy()
    Y, X = np.mgrid[0:H, 0:W]; keep = np.zeros((H, W), bool)
    if which == 'side':
        x0, x1, y0, y1 = sp['caudal']; keep |= (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
        keep |= B.poly_mask(sp['dorsal'], X, Y) | B.poly_mask(sp['adipose'], X, Y)
        bx = [r[0] for r in sp['body']]; bot = np.interp(X, bx, [r[2] for r in sp['body']]); top = np.interp(X, bx, [r[1] for r in sp['body']])
        for (x0, x1, y0, y1) in sp.get('sfins', []): keep |= (X >= x0) & (X <= x1) & (Y >= np.maximum(y0, bot - 4)) & (Y <= y1)
        if sp.get('bris'):
            x0, x1, y0, y1 = sp['bris']; inside = (Y >= top - 2) & (Y <= bot + 2) & (X <= sp['S'])
            keep |= (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & ~inside
    else:
        txs = [sp['top_snout'] - (sp['S'] - r[0]) / sp['kt'] for r in sp['body']]; hws = [r[3] for r in sp['body']]
        edge = np.interp(X, txs, hws)
        for key2 in ('pect', 'pelv'):
            fx0, fx1, fy0 = sp[key2]
            up = (X >= fx0) & (X <= fx1) & (Y >= fy0) & (Y <= sp['top_cy'] - edge - 1)                       # the fin on the upper side of the photo
            keep |= up
    px[..., 3] *= keep
    im = bpy.data.images.new('fins_%s_%s' % (which, sp['side'][:8]), W, H, alpha=True); im.pixels.foreach_set(px[::-1].ravel()); im.pack()
    _img[key] = im; _img[key + ('alpha',)] = px[..., 3].copy()
    return im

def mat_body(name, sp):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial'); bs = N.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value = .55
    try: bs.inputs['Specular IOR Level'].default_value = .28
    except Exception: pass
    def tex(im, uv):
        t = N.new('ShaderNodeTexImage'); t.image = im; t.interpolation = 'Cubic'; t.extension = 'EXTEND'
        u = N.new('ShaderNodeUVMap'); u.uv_map = uv; L.new(u.outputs['UV'], t.inputs['Vector']); return t
    ts, tt, tb = tex(img(sp['side']), 'side'), tex(img(sp['top']), 'top'), tex(img(sp['belly']), 'belly')
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Normal'], sep.inputs[0])
    wb = N.new('ShaderNodeMapRange'); wb.inputs['From Min'].default_value = -.3; wb.inputs['From Max'].default_value = -.7; L.new(sep.outputs['Z'], wb.inputs['Value'])
    wt = N.new('ShaderNodeMapRange'); wt.inputs['From Min'].default_value = .45; wt.inputs['From Max'].default_value = .85; L.new(sep.outputs['Z'], wt.inputs['Value'])
    m1 = N.new('ShaderNodeMix'); m1.data_type = 'RGBA'; L.new(wt.outputs['Result'], m1.inputs['Factor']); L.new(ts.outputs['Color'], m1.inputs[6]); L.new(tt.outputs['Color'], m1.inputs[7])
    m2 = N.new('ShaderNodeMix'); m2.data_type = 'RGBA'; L.new(wb.outputs['Result'], m2.inputs['Factor']); L.new(m1.outputs[2], m2.inputs[6]); L.new(tb.outputs['Color'], m2.inputs[7])
    L.new(m2.outputs[2], bs.inputs['Base Color']); L.new(m2.outputs[2], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = EMIT
    L.new(bs.outputs['BSDF'], out.inputs['Surface']); return m

def mat_fin(name, im):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial'); bs = N.new('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value = .6
    t = N.new('ShaderNodeTexImage'); t.image = im; t.interpolation = 'Cubic'; t.extension = 'CLIP'
    u = N.new('ShaderNodeUVMap'); u.uv_map = 'uv'; L.new(u.outputs['UV'], t.inputs['Vector'])
    L.new(t.outputs['Color'], bs.inputs['Base Color']); L.new(t.outputs['Color'], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = EMIT
    L.new(t.outputs['Alpha'], bs.inputs['Alpha']); L.new(bs.outputs['BSDF'], out.inputs['Surface'])
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m

def table(sp, x):
    b = sp['body']; xs = [r[0] for r in b]; x = min(max(x, xs[0]), xs[-1])
    return [float(np.interp(x, xs, [r[i] for r in b])) for i in (1, 2, 3)]

def build_fish(sex='M', name='anc', fold=0.0, spread=1.0, sweep=0.0, bend=0.0, bend_from=1.4, wave=0.0, wave_ph=0.0, coll=None, paired='side'):
    """same parameters and conventions as anc_build.build_fish: faces +X, snout at x=0, belly on z=0"""
    sp = SPEC[sex]; S, G = sp['S'], sp['G']; K = LEN[sex] / (S - sp['tip']); kt, kb = sp['kt'], sp['kb']
    coll = coll or bpy.context.scene.collection
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    Ws, Hs = img(sp['side']).size; Wt, Ht = img(sp['top']).size; Wb, Hb = img(sp['belly']).size
    def to3(sx, sy): return ((sx - S) * K, (G - sy) * K)
    LB = (S - sp['body'][0][0]) * K
    def bendp(x, y, z):
        if wave: y += wave * max(0., -x / LB) ** 1.5 * math.sin(wave_ph + 2.4 * x)   # nothing ahead of the snout
        if not bend: return Vector((x, y, z))
        Lr = max(.3, LB - bend_from); s_ = max(0., -x - bend_from)
        if s_ <= 0: return Vector((x, y, z))
        kap = bend / Lr; sl = min(s_, Lr); th = kap * sl
        cx_ = -bend_from - math.sin(th) / kap; cy_ = (1 - math.cos(th)) / kap
        if s_ > Lr: cx_ -= (s_ - Lr) * math.cos(th); cy_ += (s_ - Lr) * math.sin(th)
        return Vector((cx_ + y * math.sin(th), cy_ + y * math.cos(th), z))
    def uv_side(sx, sy): return (sx / Ws, 1 - sy / Hs)
    def uv_top(sx, Y): tx = sp['top_snout'] - (S - sx) / kt; ty = sp['top_cy'] - Y / K / kt; return (tx / Wt, 1 - ty / Ht)
    def uv_belly(sx, Y):
        by = min(sp['b_snout'] + (S - sx) / kt / kb, sp['bmax']); bx = sp['b_cx'] + Y / K / kt / kb; return (bx / Wb, 1 - by / Hb)
    # ---- body
    me = bpy.data.meshes.new(name + '_body'); bm = bmesh.new()
    x0, x1 = sp['body'][0][0], sp['body'][-1][0]; NR = 72; N = 44; rings = []
    for i in range(NR):
        sx = x0 + (x1 - x0) * i / (NR - 1); top, bot, hwt = table(sp, sx)
        X, zt = to3(sx, top); _, zb = to3(sx, bot); hw3 = hwt * kt * K
        if i == NR - 1: hw3 *= .55; zt = zb + (zt - zb) * .7
        pts, zm = B.ring_shape(hw3, max(zb, .004), zt, N)
        rings.append([bm.verts.new((X, y, z)) for y, z in pts])
    for i in range(NR - 1):
        for j in range(N): bm.faces.new((rings[i][j], rings[i][(j + 1) % N], rings[i + 1][(j + 1) % N], rings[i + 1][j]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1]); bm.normal_update()
    us, ut, ub = bm.loops.layers.uv.new('side'), bm.loops.layers.uv.new('top'), bm.loops.layers.uv.new('belly')
    for f in bm.faces:
        for lp in f.loops:
            v = lp.vert.co; sx = S + v.x / K; sy = G - v.z / K
            lp[us].uv = uv_side(sx, sy); lp[ut].uv = uv_top(sx, v.y); lp[ub].uv = uv_belly(sx, v.y)
    for v in bm.verts: v.co = bendp(*v.co)
    bm.normal_update(); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    body = bpy.data.objects.new(name + '_body', me); coll.objects.link(body); body.parent = root
    me.materials.append(mat_body(name + '_skin', sp))
    fs, ft = masked(sp, 'side'), masked(sp, 'top'); As, At = _img[(id(sp), 'side', 'alpha')], _img[(id(sp), 'top', 'alpha')]
    ms, mt = mat_fin(name + '_finS', fs), mat_fin(name + '_finT', ft)
    def plane(nm, box, f3, uvf, A, mat, nx=24, ny=20):
        ux0, ux1, uy0, uy1 = box; me = bpy.data.meshes.new(nm); bm = bmesh.new(); grid = []
        for j in range(ny + 1):
            grid.append([(bm.verts.new(f3(ux0 + (ux1 - ux0) * i / nx, uy0 + (uy1 - uy0) * j / ny)), ux0 + (ux1 - ux0) * i / nx, uy0 + (uy1 - uy0) * j / ny) for i in range(nx + 1)])
        uv = bm.loops.layers.uv.new('uv'); Hh, Ww = A.shape
        def al(px, py): return A[min(max(int(round(py)), 0), Hh - 1), min(max(int(round(px)), 0), Ww - 1)]
        for j in range(ny):
            for i in range(nx):
                q = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
                cx_, cy_ = sum(a[1] for a in q) / 4, sum(a[2] for a in q) / 4
                if max([al(a[1], a[2]) for a in q] + [al(cx_, cy_)]) < .03: continue
                f = bm.faces.new([a[0] for a in q])
                for lp, a in zip(f.loops, q): lp[uv].uv = uvf(a[1], a[2])
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(nm, me); coll.objects.link(o); o.parent = root; me.materials.append(mat); return o
    sideuv = lambda px, py: (px / Ws, 1 - py / Hs); topuv = lambda px, py: (px / Wt, 1 - py / Ht)
    cx0, cx1, cy0, cy1 = sp['caudal']
    def f_caud(sx, sy):
        X, Z = to3(sx, sy); d = (cx1 - sx) * K; return bendp(X, 0, max(Z + .06 * d, .025 + .02 * d))
    plane(name + '_caudal', sp['caudal'], f_caud, sideuv, As, ms, 28, 24)
    xs = [p[0] for p in sp['dorsal']]; ys = [p[1] for p in sp['dorsal']]
    hx, hy = max(sp['dorsal']); HX, HZ = to3(hx, hy); ang = fold * math.radians(68); sq = 1 - .45 * fold
    def f_dors(sx, sy):
        X, Z = to3(sx, sy); dx, dz = X - HX, (Z - HZ) * sq
        x2 = HX + dx * math.cos(ang) - dz * math.sin(ang); z2 = HZ + dx * math.sin(ang) + dz * math.cos(ang)
        sx2 = min(max(x2 / K + S, x0), S); return bendp(x2, 0, max(z2, to3(sx2, table(sp, sx2)[0])[1] - .01))
    plane(name + '_dorsal', (min(xs), max(xs), min(ys), max(ys)), f_dors, sideuv, As, ms, 26, 24)
    xa = [p[0] for p in sp['adipose']]; ya = [p[1] for p in sp['adipose']]
    plane(name + '_adipose', (min(xa), max(xa), min(ya), max(ya)), lambda sx, sy: bendp(*(lambda X, Z: (X, 0, Z))(*to3(sx, sy))), sideuv, As, ms, 8, 8)
    Kt = K * kt; cyT = sp['top_cy']; tS = sp['top_snout']
    # paired fins from the SIDE photo (owner: must look like the photos): the fin as photographed, hinged on the belly edge
    # and tilted outward (spread 1 = ~29 deg from vertical, small spread = folded against the body, e.g. in the cave)
    if paired == 'side':
        tilt = .5 * spread + 1.15 * (1 - spread)               # folding = laid flat against the belly, not hanging down
        if HANG and spread > 1: tilt = .5 * spread            # V17.100: spread > 1 = props wider out, never steeper
        for k_, (x0, x1, y0, y1) in enumerate(sp['sfins']):
            for side in (1, -1):
                def f_sf(sx, sy, side=side):
                    top, bot, hwt = table(sp, sx); syb = bot - 4; d = max(0., sy - syb) * K
                    zb_ = (G - syb) * K; hw3 = hwt * Kt * .88
                    rr = .2 + .8 * spread                                    # folded: most of the fin's length lies back along the body
                    if HANG: rr = min(1., rr)                                # V17.100: never longer than in the photo
                    sw = sweep * d + (1 - spread) * .85 * d
                    return bendp((sx - S) * K - sw, side * (hw3 + d * math.sin(tilt) * rr), (zb_ - d * math.cos(tilt) * rr) if HANG else max(.012, zb_ - d * math.cos(tilt) * rr))
                plane('%s_sfin%d%d' % (name, k_, side), (x0, x1, y0, y1), f_sf, sideuv, As, ms, 22, 16)
    for key, btx in ((('pect', sp['pect_base']), ('pelv', sp['pelv_base'])) if paired == 'top' else ()):
        fx0, fx1, fy0 = sp[key]; bsx = S - (tS - btx) * kt; top, bot, hwt = table(sp, bsx)
        zb_ = to3(bsx, bot)[1]; zbase = zb_ + .36 * (to3(bsx, top)[1] - zb_); byY = hwt * Kt
        for side in (1, -1):
            def f_fin(tx, ty, side=side, btx=btx, zbase=zbase, byY=byY):
                X = -(tS - tx) * Kt; Y = (cyT - ty) * Kt; bX = -(tS - btx) * Kt
                dx, dy = X - bX, (Y - byY) * spread; ca, sa = math.cos(sweep), math.sin(sweep)
                dx2 = dx * ca - dy * sa; dy2 = dx * sa + dy * ca                  # +y fin: turning back = clockwise seen from above
                if dy2 * dy <= 0 or abs(dy2) < .02: dy2 = math.copysign(.02, dy if dy else 1)
                X2, Y2 = bX + dx2, byY + dy2; reach = abs(Y2 - byY) + abs(dx2) * .3
                z = zbase - min(1, reach / FIN_REACH) * (zbase - .012)
                return bendp(X2, Y2 * side, z)
            tyEdge = cyT - hwt - 1
            plane('%s_%s%d' % (name, key, side), (fx0, fx1, fy0, cyT - 2), f_fin, topuv, At, mt, 22, 18)
    if sp.get('bris') and paired == 'side':
        # the photo's own bristles: three upright plates fanned round the head (0, +-35 deg) - exact at the side view,
        # still bushy when the fish turns
        x0, x1, y0, y1 = sp['bris']; hx_ = -.12
        for k_, ang_ in enumerate((0, .6, -.6)):
            def f_br(sx, sy, ang_=ang_):
                X, Z = to3(sx, sy); dx_ = X - hx_
                return bendp(hx_ + dx_ * math.cos(ang_), dx_ * math.sin(ang_), Z if HANG else max(Z, .012))   # chin bristles rest on the ground, never sink into it
            plane('%s_bris%d' % (name, k_), (x0, x1, y0, y1), f_br, sideuv, As, ms, 24, 22)
    elif sp['bristles']:
        bmat = B.mat_plain(name + '_bristle', (.42, .36, .16), .55, .3)
        cu = bpy.data.curves.new(name + '_bristles', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .016; cu.bevel_resolution = 2
        rng = np.random.default_rng(11)
        for i in range(34):
            front = i < 22
            sx = S - (rng.uniform(0, 45) if front else rng.uniform(25, 120))
            top, bot, hwt = table(sp, sx); X, zt = to3(sx, top); _, zb = to3(sx, bot)
            a = rng.uniform(-.25, 1.0) * math.pi / 2 if front else rng.uniform(.5, 1.0) * math.pi / 2
            side = 1 if i % 2 else -1; hw3 = hwt * Kt
            y = math.cos(a) * hw3 * side; z = zb + .36 * (zt - zb) + math.sin(a) * (zt - zb) * .62
            base = Vector((X, y, z)); nrm = Vector((0, math.cos(a) * side, math.sin(a) * .8)).normalized()
            d = (nrm * .6 + Vector((1, 0, 0)) * (.7 if front else .35)).normalized(); ln = rng.uniform(.14, .3) * (1 if front else .7)
            for br in range(2 if (front and i % 3 == 0) else 1):          # some tentacles fork near the tip
                spl = cu.splines.new('POLY'); spl.points.add(4)
                dd = d if br == 0 else (d + Vector((0, 0, .5))).normalized()
                for k in range(5):
                    t = k / 4; p = base + (d * ln * min(t, .55) + dd * ln * max(0, t - .55)) + Vector((0, 0, -.025 * t * t))
                    spl.points[k].co = (*p, 1); spl.points[k].radius = 1.15 - .85 * t
        o = bpy.data.objects.new(name + '_bristles', cu); coll.objects.link(o); o.parent = root; cu.materials.append(bmat)
    return root
