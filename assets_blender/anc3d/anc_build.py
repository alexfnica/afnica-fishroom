# V17.90 bristlenose 3D (Blender): a real 3D Ancistrus built from the game's own wild-type photo sprites.
# Body = lofted rings (flat belly, broad head) with the side photo projected on the flanks, the belly photo on the underside
# and the flank continued over the back; fins = 3D plates cut from the same photos (dorsal folds, pectorals/pelvics lie
# flat and can sweep back); male bristles = soft 3D tentacles. Cave = the owner's terracotta photo projected on a 3D tube.
# Library module: imported by the render scripts (still_target.py, ...). Units: 1 = 32.5 game px.
import bpy, bmesh, math, os, json
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS = os.path.join(HERE, 'atlas.png'); AW = 1254
K = 0.191 / 32.5                      # atlas px -> units (the game shows the atlas at 240/1254 = 0.191)

# per sex, in atlas px: snout x, ground y (belly line), belly-view centre line y, and the body table
#   rows: x, back y (side view), belly y (side view), half width (belly view)
SPEC = {
 'M': dict(snout=590, ground=400, bc=907, body=[
    (145, 330, 370, 22), (175, 323, 373, 25), (210, 318, 377, 31), (260, 312, 382, 41), (310, 306, 387, 50), (360, 303, 391, 58),
    (400, 304, 395, 62), (450, 310, 398, 64), (500, 322, 400, 63), (540, 340, 402, 60), (570, 360, 400, 50), (590, 385, 396, 25)],
    caudal=(14, 148, 255, 420), dorsal=[(226, 313), (240, 245), (300, 214), (345, 238), (398, 298), (402, 313)],
    adipose=[(172, 327), (178, 313), (200, 314), (214, 322), (210, 329)],
    pect=(355, 500, 745), pelv=(232, 356, 800), pect_base=486, pelv_base=345, bristles=True),
 'F': dict(snout=1227, ground=432, bc=917, body=[
    (780, 330, 368, 27), (830, 322, 375, 32), (880, 312, 390, 45), (930, 305, 405, 57), (980, 300, 415, 65), (1030, 297, 422, 72),
    (1080, 303, 420, 75), (1130, 315, 410, 75), (1170, 335, 405, 68), (1200, 355, 403, 55), (1227, 385, 400, 25)],
    caudal=(643, 783, 255, 450), dorsal=[(853, 312), (868, 248), (925, 214), (970, 240), (1027, 295), (1030, 307)],
    adipose=[(797, 324), (803, 312), (826, 313), (840, 320), (836, 327)],
    pect=(985, 1125, 748), pelv=(858, 990, 798), pect_base=1112, pelv_base=985, bristles=False),
}

def table(sp, x):
    b = sp['body']; xs = [r[0] for r in b]
    x = min(max(x, xs[0]), xs[-1])
    return [float(np.interp(x, xs, [r[i] for r in b])) for i in (1, 2, 3)]

# ----------------------------------------------------------------------------------------------- images
_img = {}
def atlas():
    if 'atlas' not in _img:
        im = bpy.data.images.load(ATLAS); im.pack(); _img['atlas'] = im
    return _img['atlas']

def poly_mask(pts, X, Y):
    m = np.zeros(X.shape, bool); n = len(pts); j = n - 1
    for i in range(n):
        xi, yi = pts[i]; xj, yj = pts[j]
        c = ((yi > Y) != (yj > Y)) & (X < (xj - xi) * (Y - yi) / (yj - yi + 1e-9) + xi)
        m ^= c; j = i
    return m

def fin_atlas():
    """the atlas with everything except the fins made transparent (both sexes)"""
    if 'fins' in _img: return _img['fins']
    a = atlas(); W, H = a.size
    px = np.empty(W * H * 4, np.float32); a.pixels.foreach_get(px); px = px.reshape(H, W, 4)
    Y, X = np.mgrid[0:H, 0:W]; Y = (H - 1) - Y                      # atlas px coords (y down)
    keep = np.zeros((H, W), bool)
    for s, sp in SPEC.items():
        x0, x1, y0, y1 = sp['caudal']; keep |= (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
        keep |= poly_mask(sp['dorsal'], X, Y) | poly_mask(sp['adipose'], X, Y)
        for key in ('pect', 'pelv'):
            fx0, fx1, fy0 = sp[key]
            hw = np.interp(X, [r[0] for r in sp['body']], [r[3] for r in sp['body']])
            keep |= (X >= fx0) & (X <= fx1) & (Y >= fy0) & (Y <= sp['bc'] - hw - 1)
    px[..., 3] *= keep
    _img['fin_alpha'] = px[::-1, :, 3].copy()                       # [atlas y, atlas x]
    im = bpy.data.images.new('anc_fins', W, H, alpha=True); im.pixels.foreach_set(px.ravel()); im.pack(); _img['fins'] = im
    return im

# ----------------------------------------------------------------------------------------------- materials
def mat_fish(name, img, body=True):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N, L = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial'); bs = N.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Roughness'].default_value = .58
    try: bs.inputs['Specular IOR Level'].default_value = .25
    except Exception: pass
    def tex(uv):
        t = N.new('ShaderNodeTexImage'); t.image = img; t.interpolation = 'Cubic'; t.extension = 'CLIP'
        u = N.new('ShaderNodeUVMap'); u.uv_map = uv; L.new(u.outputs['UV'], t.inputs['Vector']); return t
    if body:
        ts, tt, tb = tex('side'), tex('top'), tex('belly')
        tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Normal'], sep.inputs[0])
        wb = N.new('ShaderNodeMapRange'); wb.inputs['From Min'].default_value = -.25; wb.inputs['From Max'].default_value = -.65; L.new(sep.outputs['Z'], wb.inputs['Value'])
        wt = N.new('ShaderNodeMapRange'); wt.inputs['From Min'].default_value = .55; wt.inputs['From Max'].default_value = .92; L.new(sep.outputs['Z'], wt.inputs['Value'])
        m1 = N.new('ShaderNodeMix'); m1.data_type = 'RGBA'; L.new(wt.outputs['Result'], m1.inputs['Factor']); L.new(ts.outputs['Color'], m1.inputs[6]); L.new(tt.outputs['Color'], m1.inputs[7])
        m2 = N.new('ShaderNodeMix'); m2.data_type = 'RGBA'; L.new(wb.outputs['Result'], m2.inputs['Factor']); L.new(m1.outputs[2], m2.inputs[6]); L.new(tb.outputs['Color'], m2.inputs[7])
        col = m2.outputs[2]; alpha = None
    else:
        t = tex('side'); col = t.outputs['Color']; alpha = t.outputs['Alpha']
    L.new(col, bs.inputs['Base Color']); L.new(col, bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = .22
    if alpha is not None:
        L.new(alpha, bs.inputs['Alpha'])
    L.new(bs.outputs['BSDF'], out.inputs['Surface'])
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m

def mat_plain(name, rgb, rough=.7, emit=0.):
    m = bpy.data.materials.new(name); m.use_nodes = True; bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1); bs.inputs['Roughness'].default_value = rough
    if emit: bs.inputs['Emission Color'].default_value = (*rgb, 1); bs.inputs['Emission Strength'].default_value = emit
    return m

# ----------------------------------------------------------------------------------------------- the fish
def ring_shape(hw, zb, zt, n=40):
    """cross-section: flat belly (superellipse 4), rounded back (2.3); widest point low (35 % of the height)"""
    zm = zb + .36 * (zt - zb); pts = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2                       # -pi/2 = bottom, going round the +y side first
        c, s = math.cos(a), math.sin(a)
        if s < 0: e = 2 / 4.5; y = math.copysign(abs(c) ** e, c) * hw; z = zm - (zm - zb) * abs(s) ** e
        else: e = 2 / 2.3; y = math.copysign(abs(c) ** e, c) * hw; z = zm + (zt - zm) * abs(s) ** e
        pts.append((y, z))
    return pts, zm

def build_fish(sex='M', name='anc', fold=0.0, spread=1.0, sweep=0.0, bend=0.0, bend_from=1.4, wave=0.0, wave_ph=0.0, coll=None):
    """fold: dorsal 0 raised .. 1 flat; spread: pectoral/pelvic span factor; sweep: rad, fins swept back;
    bend: tail angle (rad, + = tail to +y) reached at the caudal base, the body curving from bend_from units behind the snout;
    wave: small travelling lateral wave (units) for crawling. Returns the root empty; fish faces +X, snout at x=0."""
    sp = SPEC[sex]; S, G, BC = sp['snout'], sp['ground'], sp['bc']
    coll = coll or bpy.context.scene.collection
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    def to3(sx, sy): return ((sx - S) * K, (G - sy) * K)
    LB = (S - sp['body'][0][0]) * K                                  # snout -> caudal base
    def bendp(x, y, z):                                           # constant-curvature arc behind bend_from (no stretching)
        if wave: y += wave * (-x / LB) ** 1.5 * math.sin(wave_ph + 2.4 * x)
        if not bend: return Vector((x, y, z))
        Lr = max(.3, LB - bend_from); s_ = max(0., -x - bend_from)
        if s_ <= 0: return Vector((x, y, z))
        kap = bend / Lr; sl = min(s_, Lr); th = kap * sl
        cx_ = -bend_from - math.sin(th) / kap; cy_ = (1 - math.cos(th)) / kap      # centre line at arc length sl
        if s_ > Lr: cx_ -= (s_ - Lr) * math.cos(th); cy_ += (s_ - Lr) * math.sin(th)   # straight beyond (the caudal)
        return Vector((cx_ + y * math.sin(th), cy_ + y * math.cos(th), z))     # + the offset along the arc's normal
    # ---- body
    me = bpy.data.meshes.new(name + '_body'); bm = bmesh.new()
    x0, x1 = sp['body'][0][0], sp['body'][-1][0]; NR = 70; N = 40; rings = []
    for i in range(NR):
        t = i / (NR - 1); sx = x0 + (x1 - x0) * (1 - (1 - t) ** 1.0)
        top, bot, hw = table(sp, sx)
        X, zt = to3(sx, top); _, zb = to3(sx, bot); hw3 = hw * K
        if i == NR - 1: hw3 *= .5; zt = zb + (zt - zb) * .7
        pts, zm = ring_shape(hw3, max(zb, 0.004), zt, N)
        rings.append([bm.verts.new((X, y, z)) for y, z in pts])
    for i in range(NR - 1):
        for j in range(N): bm.faces.new((rings[i][j], rings[i][(j + 1) % N], rings[i + 1][(j + 1) % N], rings[i + 1][j]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bm.normal_update()
    uvs, uvt, uvb = bm.loops.layers.uv.new('side'), bm.loops.layers.uv.new('top'), bm.loops.layers.uv.new('belly')
    for f in bm.faces:
        for lp in f.loops:
            v = lp.vert.co; sx = S + v.x / K; sy = G - v.z / K; by = BC + v.y / K
            lp[uvs].uv = (sx / AW, 1 - sy / AW)
            top = table(sp, sx)[0]; lp[uvt].uv = (sx / AW, 1 - (top + 4 + abs(v.y) / K * .85) / AW)
            lp[uvb].uv = (sx / AW, 1 - by / AW)
    for v in bm.verts: v.co = bendp(*v.co)                         # bend after the photo UVs are set
    bm.normal_update(); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    body = bpy.data.objects.new(name + '_body', me); coll.objects.link(body); body.parent = root
    me.materials.append(mat_fish(name + '_skin', atlas(), True))
    fm = mat_fish(name + '_fin', fin_atlas(), False)
    # ---- fins (planes with UVs into the fin atlas)
    def plane(nm, pts_uv, f3, nx=24, ny=24):
        (ux0, ux1, uy0, uy1) = pts_uv
        me = bpy.data.meshes.new(nm); bm = bmesh.new(); grid = []
        for j in range(ny + 1):
            row = []
            for i in range(nx + 1):
                sx = ux0 + (ux1 - ux0) * i / nx; sy = uy0 + (uy1 - uy0) * j / ny
                row.append((bm.verts.new(f3(sx, sy)), sx, sy))
            grid.append(row)
        uv = bm.loops.layers.uv.new('side'); A = _img['fin_alpha']
        def al(sx, sy): return A[min(max(int(round(sy)), 0), AW - 1), min(max(int(round(sx)), 0), AW - 1)]
        for j in range(ny):
            for i in range(nx):
                q = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
                cx_, cy_ = sum(a[1] for a in q) / 4, sum(a[2] for a in q) / 4
                if max([al(a[1], a[2]) for a in q] + [al(cx_, cy_)]) < .03: continue      # only where the fin really is
                f = bm.faces.new([a[0] for a in q])
                for lp, a in zip(f.loops, q): lp[uv].uv = (a[1] / AW, 1 - a[2] / AW)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(nm, me); coll.objects.link(o); o.parent = root; me.materials.append(fm); return o
    # caudal: vertical plane, drooping a little
    cx0, cx1, cy0, cy1 = sp['caudal']
    def f_caud(sx, sy):
        X, Z = to3(sx, sy); d = (cx1 - sx) * K; return bendp(X, 0, max(Z + .06 * d, .025 + .02 * d))   # held a little up, never under the belly line
    plane(name + '_caudal', sp['caudal'], f_caud)
    # dorsal (+ adipose): vertical plane hinged at its front base, folds back flat onto the back
    xs = [p[0] for p in sp['dorsal']]; ys = [p[1] for p in sp['dorsal']]
    hx, hy = max(sp['dorsal']); HX, HZ = to3(hx, hy)                 # pivot = the FRONT base of the dorsal
    ang = fold * math.radians(68); sq = 1 - .45 * fold
    def f_dors(sx, sy):
        X, Z = to3(sx, sy); dx, dz = X - HX, (Z - HZ) * sq
        x2 = HX + dx * math.cos(ang) - dz * math.sin(ang); z2 = HZ + dx * math.sin(ang) + dz * math.cos(ang)
        sx2 = min(max(x2 / K + S, sp['body'][0][0]), S)
        return bendp(x2, 0, max(z2, to3(sx2, table(sp, sx2)[0])[1] - .01))   # never sinks below the back line
    plane(name + '_dorsal', (min(xs), max(xs), min(ys), max(ys)), f_dors)
    xa = [p[0] for p in sp['adipose']]; ya = [p[1] for p in sp['adipose']]
    plane(name + '_adipose', (min(xa), max(xa), min(ya), max(ya)), lambda sx, sy: bendp(*(lambda X, Z: (X, 0, Z))(*to3(sx, sy))), 8, 8)
    # pectorals + pelvics: horizontal plates from the belly view, both sides, drooping to the sand at the tips
    for key, bx in (('pect', sp['pect_base']), ('pelv', sp['pelv_base'])):
        fx0, fx1, fy0 = sp[key]; hwb = table(sp, bx)[2]; yb = BC - hwb
        _, zbase = to3(bx, table(sp, bx)[1]); zbase += .36 * (to3(bx, table(sp, bx)[0])[1] - zbase)
        for side in (1, -1):
            def f_fin(sx, sy, side=side, bx=bx, yb=yb, zbase=zbase, key=key):
                X = (sx - S) * K; Y = (sy - BC) * K                  # belly view: y<BC = the +side fin
                bxX = (bx - S) * K; byY = (yb - BC) * K
                dx, dy = X - bxX, (Y - byY) * spread
                ca, sa = math.cos(sweep), math.sin(sweep)
                dx2 = dx * ca + dy * sa; dy2 = -dx * sa + dy * ca            # turns the fin back along the body
                if dy2 * dy <= 0 or abs(dy2) < .02: dy2 = math.copysign(.02, dy if dy else -1)
                X2, Y2 = bxX + dx2, byY + dy2
                reach = abs(Y2 - byY) + abs(dx2) * .3; z = zbase - min(1, reach / .5) * (zbase - .012)
                return bendp(X2, -Y2 * side, z)
            plane('%s_%s%d' % (name, key, side), (fx0, fx1, fy0, BC - hwb - 1), f_fin, 20, 16)
    # bristles (male): soft tentacles round the snout and on the head
    if sp['bristles']:
        bmat = mat_plain(name + '_bristle', (.30, .22, .10), .6, .25)
        cu = bpy.data.curves.new(name + '_bristles', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .02; cu.bevel_resolution = 2
        rng = np.random.default_rng(7 if sex == 'M' else 3)
        for i in range(30):
            sx = S - rng.uniform(0, 70) ** 1.0 * (.35 if i < 18 else 1.0)
            top, bot, hw = table(sp, sx); X, zt = to3(sx, top); _, zb = to3(sx, bot)
            a = rng.uniform(-.35, 1.0) * math.pi / 2 if i < 18 else rng.uniform(.55, 1.0) * math.pi / 2
            side = 1 if i % 2 else -1; hw3 = hw * K
            y = math.cos(a) * hw3 * side; z = zb + .36 * (zt - zb) + math.sin(a) * (zt - zb) * .62
            base = Vector((X, y, z)); nrm = Vector((0, math.cos(a) * side, math.sin(a) * .8)).normalized()
            d = (nrm * .55 + Vector((1, 0, 0)) * (.75 if i < 18 else .3)).normalized(); ln = rng.uniform(.14, .26) * (1 if i < 18 else .7)
            spl = cu.splines.new('POLY'); spl.points.add(3)
            for k in range(4):
                t = k / 3; p = base + d * ln * t + Vector((0, 0, -.03 * t * t))
                spl.points[k].co = (*p, 1); spl.points[k].radius = 1 - .8 * t
        o = bpy.data.objects.new(name + '_bristles', cu); coll.objects.link(o); o.parent = root; cu.materials.append(bmat)
    return root

def fish_points(root):
    """world-space vertices of every mesh under root (for clearance checks)"""
    dg = bpy.context.evaluated_depsgraph_get(); out = []
    for o in root.children_recursive:
        if o.type != 'MESH': continue
        mw = o.matrix_world; out += [mw @ v.co for v in o.data.vertices]
    return out

# ----------------------------------------------------------------------------------------------- the cave
CAVE_PHOTO = os.path.join(HERE, '..', 'incoming', 'anc_cave_photo.jpg')
CAVE = dict(R=.96, lip=1.0, r=.78, L=4.65, lipL=.28, yaw=math.radians(22.2), mouth_px=(225, 395), px_per_unit=219.)

def build_cave(cam, scene, coll=None, loc=(0, 0, 0)):
    """terracotta tube lying on the sand, mouth at local -x, turned 22 deg toward the camera (as in the photo);
    the photo is projected from the camera so the visible clay looks exactly like it."""
    coll = coll or scene.collection; c = CAVE
    me = bpy.data.meshes.new('cave'); bm = bmesh.new(); N = 72
    prof = [(-c['L'] / 2, c['r']), (-c['L'] / 2, c['lip']), (-c['L'] / 2 + c['lipL'], c['lip']), (-c['L'] / 2 + c['lipL'] + .08, c['R']),
            (c['L'] / 2 - .1, c['R']), (c['L'] / 2, c['R'] - .06), (c['L'] / 2, c['r']), (-c['L'] / 2, c['r'])]   # outer then back along the inside
    # densify the profile
    P = []
    for (a, b) in zip(prof, prof[1:]):
        n = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / .08))
        for i in range(n): t = i / n; P.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    rows = [[bm.verts.new((x, rr * math.cos(2 * math.pi * j / N), rr * math.sin(2 * math.pi * j / N))) for j in range(N)] for x, rr in P]
    for i in range(len(rows)):
        A, B = rows[i], rows[(i + 1) % len(rows)]
        for j in range(N): bm.faces.new((A[j], A[(j + 1) % N], B[(j + 1) % N], B[j]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('cave', me); coll.objects.link(o)
    o.rotation_euler = (0, 0, c['yaw']); o.location = (loc[0], loc[1], loc[2] + c['R'])
    bpy.context.view_layer.update()
    # photo UVs: the tube as the photo saw it (level, turned by yaw), anchored at the mouth centre, 225 photo px per unit;
    # fixed to the tube, so it stays right from the slightly higher game camera
    img = bpy.data.images.load(CAVE_PHOTO); img.pack(); PW, PH = img.size
    mx, my = c['mouth_px']; k = c['px_per_unit']; cy_, sy_ = math.cos(c['yaw']), math.sin(c['yaw'])
    Xm = -c['L'] / 2 * cy_
    uv = me.uv_layers.new(name='photo')
    for lp in me.loops:
        q = me.vertices[lp.vertex_index].co; X = q.x * cy_ - q.y * sy_
        uv.data[lp.index].uv = ((mx + (X - Xm) * k) / PW, 1 - (my - q.z * k) / PH)
    m = bpy.data.materials.new('clay'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N_, L_ = nt.nodes, nt.links
    out = N_.new('ShaderNodeOutputMaterial'); t = N_.new('ShaderNodeTexImage'); t.image = img; t.extension = 'EXTEND'
    u = N_.new('ShaderNodeUVMap'); u.uv_map = 'photo'; L_.new(u.outputs['UV'], t.inputs['Vector'])
    em = N_.new('ShaderNodeEmission'); L_.new(t.outputs['Color'], em.inputs['Color'])
    L_.new(em.outputs['Emission'], out.inputs['Surface']); me.materials.append(m)
    return o

def cave_axis(cave):
    """world mouth centre, unit axis pointing INTO the tube, inner floor height at the axis"""
    c = CAVE; mw = cave.matrix_world
    mouth = mw @ Vector((-c['L'] / 2, 0, 0)); back = mw @ Vector((c['L'] / 2, 0, 0))
    ax = (back - mouth).normalized(); return mouth, ax, mouth.z - c['r']

def clearance(points, cave):
    """worst intrusion (units) of fish points into the clay: >0 means a point is inside the wall"""
    c = CAVE; inv = cave.matrix_world.inverted(); worst = -9
    for p in points:
        q = inv @ p; rr = math.hypot(q.y, q.z)
        if -c['L'] / 2 - .02 <= q.x <= c['L'] / 2:
            outer = c['lip'] if q.x < -c['L'] / 2 + c['lipL'] + .04 else c['R']
            if c['r'] - .005 < rr < outer + .005: worst = max(worst, min(rr - c['r'], outer - rr))
    return worst

# ----------------------------------------------------------------------------------------------- scene
def scene_setup(res=(1200, 680), ortho=9.23, pitch=8, target=(0, 0, .6), samples=64):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    try: sc.cycles.device = 'CPU'
    except Exception: pass
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    p = math.radians(pitch); d = 20
    cam.location = (target[0], target[1] - d * math.cos(p), target[2] + d * math.sin(p))
    cam.rotation_euler = (math.pi / 2 - p, 0, 0)
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (.32, .42, .46, 1); bg.inputs['Strength'].default_value = .75
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun)
    sun.data.energy = 2.6; sun.data.angle = math.radians(28); sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(10))
    gp = bpy.data.objects.new('ground', bpy.data.meshes.new('ground')); sc.collection.objects.link(gp)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40); bm.to_mesh(gp.data); bm.free()
    gp.is_shadow_catcher = True
    return sc, cam
