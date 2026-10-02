# AFNICA - Aquarium Simulator logos, built from the owner's AFNICA Fishroom logo (afnica_fishroom_src.webp, 1254x1254).
#  1) logo_aquarium_simulator.png : the original logo with "FISHROOM" replaced by "AQUARIUM SIMULATOR" (same width as AFNICA)
#  2) app_icon_1024.png / app_icon_512.png : the circle + guppy as a badge on a deep-water background (profile picture / app icon)
# Run: D:\Blender\blender.exe -b -P make_app_logo.py
import bpy, os, numpy as np
D = 'D:/Retirement/assets_blender/logo/'
FONTS = ['C:/Windows/Fonts/GOTHIC.TTF', 'C:/Windows/Fonts/arial.ttf']
FONT = next(f for f in FONTS if os.path.exists(f)); print('FONT', FONT)

img = bpy.data.images.load(D + 'afnica_fishroom_src.webp'); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); SRC = px.reshape(H, W, 4)[::-1].copy()   # top-down
SRC[..., 3] = 1
lum = SRC[..., :3].mean(-1)
INK = np.clip(SRC[lum < .35][:, :3].mean(0), 0, 1) if (lum < .35).any() else np.zeros(3)
BG = np.median(SRC[:10, :, :3].reshape(-1, 3), 0)
CX, CY = 623.5, 502.0                                           # centre of the ring (measured)
print('INK', INK, 'BG', BG)

def save(a, path):
    h, w = a.shape[:2]; r = bpy.data.images.new('o', w, h, alpha=True)
    r.pixels.foreach_set(np.ascontiguousarray(a[::-1], np.float32).reshape(-1)); r.filepath_raw = path; r.file_format = 'PNG'; r.save()
    print('SAVED', path, w, h)

def sample(src, X, Y):                                          # bilinear
    h, w = src.shape[:2]; x0 = np.floor(X).astype(int); y0 = np.floor(Y).astype(int); fx = X - x0; fy = Y - y0
    out = np.zeros(X.shape + (src.shape[2],), np.float32)
    for dy in (0, 1):
        for dx in (0, 1):
            xi = np.clip(x0 + dx, 0, w - 1); yi = np.clip(y0 + dy, 0, h - 1)
            out += src[yi, xi] * ((fx if dx else 1 - fx) * (fy if dy else 1 - fy))[..., None]
    return out

def render_text(text, font, target_w, band_w, band_h, spacing, ss=3):
    """black text with a transparent background, centred in a band_w x band_h image, scaled to target_w wide"""
    sc = bpy.data.scenes.new('t'); bpy.context.window.scene = sc
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = text; cu.font = bpy.data.fonts.load(font)
    cu.space_character = spacing; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    ob = bpy.data.objects.new('t', cu); sc.collection.objects.link(ob)
    bpy.context.view_layer.update(); w0 = ob.dimensions.x; cu.size = target_w / 100.0 / w0
    bpy.context.view_layer.update()
    cam = bpy.data.cameras.new('c'); cam.type = 'ORTHO'; cam.ortho_scale = band_w / 100.0
    co = bpy.data.objects.new('c', bpy.data.cameras['c']); co.location = (0, 0, 10); sc.collection.objects.link(co); sc.camera = co
    r = sc.render; r.engine = 'BLENDER_WORKBENCH'; r.film_transparent = True; r.resolution_x = band_w * ss; r.resolution_y = band_h * ss
    r.resolution_percentage = 100; r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'; r.filepath = D + '_t.png'
    sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'SINGLE'; sc.display.shading.single_color = (0, 0, 0)
    sc.display.render_aa = '8'; sc.view_settings.view_transform = 'Standard'
    bpy.ops.render.render(write_still=True)
    t = bpy.data.images.load(D + '_t.png'); tw, th = t.size
    p = np.empty(tw * th * 4, np.float32); t.pixels.foreach_get(p); A = p.reshape(th, tw, 4)[::-1, :, 3]
    A = A.reshape(band_h, ss, band_w, ss).mean((1, 3)); os.remove(D + '_t.png')
    return A

def over_mask(base, alpha, rgb):
    a = np.clip(alpha, 0, 1)[..., None]; base[..., :3] = base[..., :3] * (1 - a) + np.array(rgb, np.float32) * a

# ---------- 1) the logo with the new wordmark ----------
L = SRC.copy()
L[972:1040, :, :3] = BG                                         # remove FISHROOM and its two side lines
TXT = 'AQUARIUM SIMULATOR'; BAND_H = 90
A = render_text(TXT, FONT, 832, W, BAND_H, 1.55)
A = np.roll(A, int(round((218 + 1050) / 2 - W / 2)), 1)        # AFNICA is centred at x=634, the image at 627
ys, xs = np.nonzero(A > .3); print('TEXT bbox', xs.min(), xs.max(), 'height', ys.max() - ys.min() + 1)
y0 = 1005 - BAND_H // 2; sub = L[y0:y0 + BAND_H, :, :]
over_mask(sub, A, INK); L[y0:y0 + BAND_H] = sub
save(L, D + 'logo_aquarium_simulator.png')

# ---------- 2) app icon: the badge on deep water ----------
N = 1024; yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
t = yy / N
bg = np.stack([.10 - .08 * t, .43 - .32 * t, .56 - .40 * t], -1)
glow = (.10 * np.exp(-((xx - 512) ** 2 + (yy - 260) ** 2) / (2 * 380.0 ** 2)))[..., None] * np.array([.5, 1, 1], np.float32)
icon = np.concatenate([np.clip(bg + glow, 0, 1), np.ones((N, N, 1), np.float32)], -1)
rng = np.random.default_rng(7); d = np.hypot(xx - 512, yy - 512)
for _ in range(16):                                              # a few bubbles around the badge
    bx, by, br = rng.uniform(40, N - 40), rng.uniform(40, N - 40), rng.uniform(5, 20)
    if np.hypot(bx - 512, by - 512) < 420: continue
    dd = np.hypot(xx - bx, yy - by)
    over_mask(icon, np.clip(1.3 - np.abs(dd - br), 0, 1) * .28, (.85, .96, 1))
    over_mask(icon, np.clip(1.5 - np.hypot(xx - bx + br * .35, yy - by + br * .4), 0, 1) * .4, (1, 1, 1))
R = 360.0; S = 1.22                                              # disc radius on the icon, source scale
disc = np.clip(R - d + .5, 0, 1)
# soft shadow under the disc
sh = bpy.data.images.new('sh', N, N, alpha=True); sh.pixels.foreach_set(np.ascontiguousarray(np.roll(disc, 18, 0)[::-1, :, None].repeat(4, -1), np.float32).reshape(-1))
sh.scale(64, 64); sh.scale(N, N); sp = np.empty(N * N * 4, np.float32); sh.pixels.foreach_get(sp); shadow = sp.reshape(N, N, 4)[::-1, :, 0]
over_mask(icon, shadow * .45, (0, .03, .05))
over_mask(icon, np.clip(4.5 - np.abs(d - (R + 34)), 0, 1) * .8, (.80, .93, .97))   # thin outer ring
body = sample(SRC, CX + (xx - 512) / S, CY + (yy - 512) / S)[..., :3] * np.array([1, .99, .96], np.float32)
over_mask(icon, disc, 0)
icon[..., :3] = icon[..., :3] * (1 - disc[..., None]) + body * disc[..., None]
save(icon, D + 'app_icon_1024.png')
sm = bpy.data.images.new('s5', N, N, alpha=True); sm.pixels.foreach_set(np.ascontiguousarray(icon[::-1], np.float32).reshape(-1))
sm.scale(512, 512); sm.filepath_raw = D + 'app_icon_512.png'; sm.file_format = 'PNG'; sm.save(); print('SAVED 512')
