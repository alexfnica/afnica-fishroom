# Facebook cover banner 1640x624 for AFNICA - Aquarium Simulator, composed from the game's own fish sprites on a water background.
# Text stays in the centre 1100 px (mobile crops the sides); nothing important in the bottom-left corner (profile picture).
# Run: D:\Blender\blender.exe -b -P make_banner.py
import bpy, os, numpy as np
D = 'D:/Retirement/assets_blender/logo/'; SRCD = D + 'banner_src/'
GOTHIC, SERIF = 'C:/Windows/Fonts/GOTHIC.TTF', 'C:/Windows/Fonts/georgia.ttf'
for f in (GOTHIC, SERIF):
    if not os.path.exists(f): raise SystemExit('missing font ' + f)
W, H = 1640, 624
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def load(name):
    im = bpy.data.images.load(SRCD + name + '.png'); w, h = im.size
    p = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(p); return p.reshape(h, w, 4)[::-1].copy()

def over(base, alpha, rgb):
    a = np.clip(alpha, 0, 1)[..., None]; base[..., :3] = base[..., :3] * (1 - a) + np.asarray(rgb, np.float32) * a

def render_text(text, font, target_w, band_w, band_h, spacing, ss=3):
    sc = bpy.data.scenes.new('t'); bpy.context.window.scene = sc
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = text; cu.font = bpy.data.fonts.load(font)
    cu.space_character = spacing; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    ob = bpy.data.objects.new('t', cu); sc.collection.objects.link(ob)
    bpy.context.view_layer.update(); w0 = ob.dimensions.x; cu.size = target_w / 100.0 / w0; bpy.context.view_layer.update()
    cam = bpy.data.cameras.new('c'); cam.type = 'ORTHO'; cam.ortho_scale = band_w / 100.0
    co = bpy.data.objects.new('c', cam); co.location = (0, 0, 10); sc.collection.objects.link(co); sc.camera = co
    r = sc.render; r.engine = 'BLENDER_WORKBENCH'; r.film_transparent = True; r.resolution_x = band_w * ss; r.resolution_y = band_h * ss
    r.resolution_percentage = 100; r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'; r.filepath = D + '_t.png'
    sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'SINGLE'; sc.display.shading.single_color = (0, 0, 0)
    sc.display.render_aa = '8'; sc.view_settings.view_transform = 'Standard'
    bpy.ops.render.render(write_still=True)
    t = bpy.data.images.load(D + '_t.png'); tw, th = t.size
    p = np.empty(tw * th * 4, np.float32); t.pixels.foreach_get(p); A = p.reshape(th, tw, 4)[::-1, :, 3]
    A = A.reshape(band_h, ss, band_w, ss).mean((1, 3)); os.remove(D + '_t.png'); return A

# ---------- water ----------
t = yy / H
img = np.zeros((H, W, 4), np.float32); img[..., 3] = 1
img[..., 0] = .09 - .075 * t; img[..., 1] = .40 - .31 * t; img[..., 2] = .53 - .42 * t
WATER = np.array([.05, .22, .31], np.float32)
img[..., :3] += (.10 * np.exp(-((xx - 820) ** 2 + (yy - 40) ** 2) / (2 * 520.0 ** 2)))[..., None] * np.array([.5, 1, 1], np.float32)
rng = np.random.default_rng(11)
for _ in range(7):                                               # soft slanting light rays from the surface
    x0 = rng.uniform(-100, W); w = rng.uniform(50, 130); ang = np.deg2rad(rng.uniform(12, 22))
    d = (xx - x0) * np.cos(ang) - yy * np.sin(ang)
    over(img, np.exp(-(d / w) ** 2) * (1 - t) ** 1.4 * rng.uniform(.05, .10), (.85, 1, 1))
over(img, np.clip(1 - yy / 10, 0, 1) * .25, (.9, 1, 1))          # shimmering surface line
for _ in range(120):                                             # floating particles
    px, py, pr = rng.uniform(0, W), rng.uniform(10, H), rng.uniform(.8, 2.0)
    over(img, np.clip(1.2 - np.hypot(xx - px, yy - py) / pr, 0, 1) * rng.uniform(.12, .4), (.85, .97, 1))

# ---------- fish ----------
def place(spr, cx, cy, width, flip=False, rot=0.0, fog=0.0, alpha=1.0):
    h0, w0 = spr.shape[:2]; s = width / w0; c, sn = np.cos(np.deg2rad(rot)), np.sin(np.deg2rad(rot))
    half = int(width * .75) + 8; xs0, xs1 = max(0, int(cx - half)), min(W, int(cx + half)); ys0, ys1 = max(0, int(cy - half)), min(H, int(cy + half))
    gy, gx = np.mgrid[ys0:ys1, xs0:xs1].astype(np.float32); dx, dy = gx - cx, gy - cy
    u = (dx * c + dy * sn) / s; v = (-dx * sn + dy * c) / s
    if flip: u = -u
    X = u + w0 / 2 - .5; Y = v + h0 / 2 - .5
    P = spr.copy(); P[..., :3] *= P[..., 3:4]
    x0 = np.floor(X).astype(int); y0 = np.floor(Y).astype(int); fx = X - x0; fy = Y - y0; out = np.zeros(X.shape + (4,), np.float32)
    for ddy in (0, 1):
        for ddx in (0, 1):
            xi = x0 + ddx; yi = y0 + ddy; ok = (xi >= 0) & (xi < w0) & (yi >= 0) & (yi < h0)
            v4 = np.zeros(X.shape + (4,), np.float32); v4[ok] = P[yi[ok], xi[ok]]
            out += v4 * ((fx if ddx else 1 - fx) * (fy if ddy else 1 - fy))[..., None]
    a = out[..., 3] * alpha; rgb = out[..., :3] / np.maximum(out[..., 3:4], 1e-4)
    rgb = rgb * (1 - fog) + WATER * fog * 1.4                    # distant fish sink into the water
    sub = img[ys0:ys1, xs0:xs1]; over(sub, a, 0); sub[..., :3] = sub[..., :3] * (1 - a[..., None]) + rgb * a[..., None]; img[ys0:ys1, xs0:xs1] = sub

SPECIES = ('guppy_m', 'guppy_f', 'guppy_fry', 'guppy_nb', 'xipho_m', 'xipho_f', 'xipho_fry', 'molly_m', 'molly_f', 'platy_m', 'platy_f',
           'neon_m', 'neon_f', 'cory_m', 'cory_f', 'anc_m', 'anc_f')
S = {n: load(n) for n in SPECIES}

# sand along the bottom so the catfish have somewhere to sit
sand = np.clip((yy - (H - 58)) / 58, 0, 1)
grain = rng.normal(0, 1, (H, W)).astype(np.float32)
over(img, np.clip(sand ** .7, 0, 1) * .92, (.50 + .03 * grain, .41 + .03 * grain, .28 + .03 * grain) if False else (.46, .38, .27))
img[..., :3] += (sand[..., None] * grain[..., None] * .025)
over(img, np.clip(1.0 - np.abs(yy - (H - 58)) / 14, 0, 1) * .10, (.05, .12, .16))

# (sprite, x, y, width, flip, tilt, fog, alpha)  far fish first
FISH = [
 # far, small, hazy
 ('guppy_f', 110, 70, 140, False, -5, .45, .95), ('molly_f', 410, 80, 190, True, 3, .40, .95), ('guppy_m', 1250, 80, 160, False, 6, .50, .90),
 ('xipho_f', 1530, 112, 200, True, 4, .40, .95), ('guppy_fry', 60, 250, 62, False, -6, .30, .9), ('xipho_fry', 1440, 470, 80, True, 5, .30, .9),
 ('platy_f', 440, 385, 150, True, -3, .30, .95), ('platy_m', 1265, 250, 205, False, 4, .20, .95),
 # mid
 ('molly_m', 300, 235, 255, False, -3, .10, 1), ('guppy_m', 345, 515, 170, True, -4, .35, .95), ('xipho_m', 1300, 545, 250, False, -3, .30, 1),
 # bottom dwellers on the sand
 ('cory_m', 500, 592, 185, False, 0, .15, 1), ('cory_f', 1160, 594, 170, True, 0, .15, 1), ('anc_m', 1545, 588, 300, True, 0, .0, 1), ('anc_f', 215, 592, 250, False, 0, .0, 1),
 # near, big, sharp
 ('xipho_f', 150, 395, 260, False, 4, 0, 1), ('guppy_m', 1500, 335, 250, True, -5, 0, 1),
]
# two neon schools: tight groups moving the same way
for (sx, sy, fl, n) in ((760, 105, False, 8), (860, 535, True, 7)):
    for i in range(n):
        FISH.append(('neon_' + ('m' if i % 2 else 'f'), sx + rng.uniform(-120, 120), sy + rng.uniform(-38, 38), rng.uniform(70, 92), fl, rng.uniform(-6, 6), .38, .95))
for n, x, y, w, fl, rot, fog, al in FISH: place(S[n], x, y, w, fl, rot, fog, al)
for _ in range(14):                                              # bubbles
    bx, by, br = rng.uniform(30, W - 30), rng.uniform(30, H - 30), rng.uniform(4, 15)
    over(img, np.clip(1.3 - np.abs(np.hypot(xx - bx, yy - by) - br), 0, 1) * .3, (.85, .96, 1))
    over(img, np.clip(1.4 - np.hypot(xx - bx + br * .35, yy - by + br * .4), 0, 1) * .45, (1, 1, 1))

# ---------- text (centre block) ----------
CREAM = (.96, .98, 1.0)
def put(text, font, tw, cy, bh, spacing, rgb, op=1.0):
    A = render_text(text, font, tw, W, bh, spacing); y0 = int(cy - bh / 2)
    sub = img[y0:y0 + bh]; over(sub, A * op, rgb); img[y0:y0 + bh] = sub
over(img, np.exp(-(((xx - 820) / 430) ** 2 + ((yy - 312) / 150) ** 2)) * .40, (.01, .09, .13))   # soft dark pool behind the text for legibility
put('AFNICA', SERIF, 560, 270, 170, 1.9, CREAM)
put('AQUARIUM SIMULATOR', GOTHIC, 560, 365, 60, 1.55, CREAM, .95)
put('IN DEVELOPMENT', GOTHIC, 250, 425, 40, 1.7, (.62, .88, .96), .9)

# vignette
v = np.clip(((xx - 820) / 980) ** 2 + ((yy - 312) / 520) ** 2, 0, 1)
img[..., :3] *= (1 - .30 * v)[..., None]
out = bpy.data.images.new('b', W, H, alpha=True); out.pixels.foreach_set(np.ascontiguousarray(img[::-1], np.float32).reshape(-1))
out.filepath_raw = D + 'facebook_banner_1640x624.png'; out.file_format = 'PNG'; out.save(); print('SAVED banner', W, H)
