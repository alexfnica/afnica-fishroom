# V17.97 colour for life (owner: "each fish keeps its brown or black colour for life, including as an adult"): the photo
# sheet gets two more columns - a BLACK adult male (column 240: the olive male photo recoloured to the black female's
# colours) and a BROWN adult female (column 360: the black female photo recoloured to the olive male's colours).
# Per-channel histogram matching inside the fish, per cell (adult side row 38, belly row 138); spots keep their rank, so the
# light spots stay light. The other rows of the new columns are copies (never shown). Uses headless Chrome to decode and
# encode WebP. Also usable on any RGBA frames: recolor(a, src_ref, dst_ref).
# Run: python recolor_sheet.py   -> out/sheet97.webp
import sys, os, json, base64, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')

def lum(px): return px[..., 0] * .299 + px[..., 1] * .587 + px[..., 2] * .114

def hist_map(src_px, dst_px):
    """brightness: the src brightness distribution matched onto the dst one (spots keep their rank); colour: the dst
    fish's average tint at that brightness (24 bins). Returns (brightness LUT 0..255, tint table 24x3)"""
    ys, yd = np.sort(lum(src_px.astype(float))), lum(dst_px.astype(float))
    q = np.searchsorted(ys, np.arange(256), side='right') / max(1, len(ys))
    lut = np.interp(q, np.linspace(0, 1, len(yd)), np.sort(yd))
    tint = np.ones((24, 3)); bi = np.minimum(23, (yd / 256 * 24).astype(int))
    for b in range(24):
        m = bi == b
        if m.sum() > 30: tint[b] = (dst_px[m].astype(float) / np.maximum(1, yd[m])[:, None]).mean(0)
    for b in range(24):                                          # empty bins: nearest filled one
        if not (bi == b).sum() > 30:
            filled = [k for k in range(24) if (bi == k).sum() > 30]
            tint[b] = tint[min(filled, key=lambda k: abs(k - b))]
    return lut, tint

def recolor(a, m):
    lut, tint = m; o = a.copy(); y = lum(a[..., :3].astype(float)).clip(0, 255).astype(np.uint8)
    yt = lut[y]; t = tint[np.minimum(23, (yt / 256 * 24).astype(int))]
    rgb = (yt[..., None] * t).clip(0, 255).astype(np.uint8)
    keep = a[..., 3] < 10; o[..., :3] = np.where(keep[..., None], a[..., :3], rgb)
    return o

def fishpx(a): return a[..., :3][a[..., 3] > 200].reshape(-1, 3)

if __name__ == '__main__':
    from cdp import Chrome
    c = Chrome(400, 300, 1, port=int(os.environ.get('AF_PORT', '9471')))
    try:
        src = 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(OUT, 'sheet90.webp'), 'rb').read()).decode()
        r = json.loads(c.js("(async s=>{const i=new Image();i.src=s;await i.decode();const c=document.createElement('canvas');c.width=i.naturalWidth;c.height=i.naturalHeight;"
                            "const g=c.getContext('2d');g.drawImage(i,0,0);const d=g.getImageData(0,0,c.width,c.height).data;let b='';for(let k=0;k<d.length;k+=32768)b+=String.fromCharCode.apply(null,d.subarray(k,k+32768));"
                            "return JSON.stringify({w:c.width,h:c.height,b:btoa(b)})})(%s)" % json.dumps(src)))
        W, H = r['w'], r['h']; A = np.frombuffer(base64.b64decode(r['b']), np.uint8).reshape(H, W, 4)
        CW = W // 2; F = W / 240.
        # V17.97 glass view tail (owner: "the tail is missing"): from below the caudal fin is edge-on, a thin line. Lay a
        # narrow fan of the real caudal (from the side photo, squashed to 30 % height = seen at a slight angle) under the line.
        A = A.copy()
        for col in (0, 1):
            x0 = col * CW; sr0, sr1, br0, br1 = int(38 * F), int(138 * F), int(138 * F), int(238 * F)
            side, bel = A[sr0:sr1, x0:x0 + CW].astype(float), A[br0:br1, x0:x0 + CW].astype(float)
            ha = (bel[..., 3] > 60).sum(0); xs = np.nonzero(ha)[0]; xl = xs[0]
            xb = xl + int(np.argmax(ha[xl:] > 22))                  # where the thin line meets the body
            if col == 0:
                # V17.100 male glass tail (owner's reference photos + feedback rounds): the belly photo's own long stalk runs to
                # its end (make_sheet SEAM M 733, photo 14 % smaller - MK100, no render); after it the caudal, seen edge-on
                # (upright against the glass = a thin line, FAN_H .22 of the side photo's fin height), straight along the axis,
                # filling the cell to the tail edge. Built as a smooth shape (owner: "visual corruption" at the join with the
                # first per-column version): the outline = the stalk's taper (from its end height, over 45 % of the caudal)
                # merged with the fin's own smoothed profile; the fin texture is mapped across that outline (anti-aliased
                # edges); the root cross-fades over the stalk's fully opaque part (no see-through, no seam).
                xe = xl; Lf = int(os.environ.get('FAN_L', '0')) or max(60, xe - 4); ov = int(Lf * .15)   # tip 4 px inside the cell (owner: the tail end looked cut flat)
                # the photo's last ~25 px of stalk are its feathered cut edge (a flat light band): the caudal is anchored at the
                # first clean stalk column xg and covers the ragged end; it fades out over 15 px of clean stalk
                fx0 = xe - Lf; xg = xe + 25; Lg = xg - fx0; ov = 15
                sx = np.nonzero((side[..., 3] > 60).sum(0))[0][0]
                src = side[:, sx:sx + Lg + ov]; W_ = src.shape[1]
                c_ = np.full(W_, np.nan); h_ = np.full(W_, np.nan)
                for j in range(W_):
                    rr = np.nonzero(src[:, j, 3] > 60)[0]
                    if len(rr) > 1: c_[j] = (rr[0] + rr[-1] + 1) / 2; h_[j] = rr[-1] + 1 - rr[0]
                ok_ = ~np.isnan(c_); c_ = np.interp(np.arange(W_), np.nonzero(ok_)[0], c_[ok_]); h_ = np.interp(np.arange(W_), np.nonzero(ok_)[0], h_[ok_])
                sm = lambda v, n: np.convolve(np.pad(v, n // 2, mode='edge'), np.ones(n) / n, mode='valid')
                c_ = sm(c_, 9); h_ = sm(h_, 9)
                hs = float((bel[:, xg:xg + 4, 3] > 60).sum(0).mean())
                # one taper from the stalk's end height (+8 %: covers the photo's ragged cut edge) to ~10 px at the tip, like the
                # owner's resting reference (no waist, no spearhead); the fin texture is still mapped along it
                Hc = sm(3 + (hs - 3) * np.clip(np.arange(W_) / Lg, 0, 1) ** 1.15, 5)   # down to a soft ~3 px point at the tip
                nh = int(np.ceil(Hc.max())) + 4; mid = nh / 2; yy = np.arange(nh) + .5 - mid
                fan = np.zeros((nh, W_, 4))
                # the stalk's own texture (a fully opaque column 12 px inside it) carries on into the root and gives way to the
                # fin texture toward the tip (owner: the fin texture's own root lines made a "V" at the join)
                cyb = np.average(np.nonzero(bel[:, xg:xg + 8, 3] > 60)[0])
                for j in range(W_):
                    sr = np.clip(c_[j] + (yy / max(Hc[j], 1)) * h_[j], 0, src.shape[0] - 1.001); r0 = sr.astype(int); f = (sr - r0)[:, None]
                    px = src[r0, j] * (1 - f) + src[np.minimum(r0 + 1, src.shape[0] - 1), j] * f
                    dd = int(max(0, xg - (fx0 + j))) % 60; scx = xg + (dd if dd < 30 else 60 - dd)   # the stalk's last 30 px mirrored back and forth
                    sc2 = bel[:, scx]; o2 = np.nonzero(sc2[:, 3] > 60)[0]; c2 = (o2[0] + o2[-1] + 1) / 2 if len(o2) > 1 else cyb; h2 = max(2., len(o2))
                    qr = np.clip(c2 + (yy / max(Hc[j], 1)) * h2, 0, bel.shape[0] - 1.001); q0 = qr.astype(int); g_ = (qr - q0)[:, None]
                    pq = sc2[q0] * (1 - g_) + sc2[np.minimum(q0 + 1, bel.shape[0] - 1)] * g_
                    ws = float(np.clip((j - .5 * Lg) / (.4 * Lg), 0, 1))
                    fan[:, j, :3] = px[:, :3] * (1 - ws) + pq[:, :3] * ws; fan[:, j, 3] = 255 * np.clip(Hc[j] / 2 - np.abs(yy) + .5, 0, 1)
                xs_ = fx0 + np.arange(W_)
                fan[..., 3] *= np.clip((xg + ov - xs_) / ov, 0, 1)[None, :]   # root fades out over clean, opaque stalk
                cy = int(round(cyb)); y0 = cy - nh // 2
                # trim the photo's ragged cut edge (the stalk's last columns) to the taper's outline
                hr = hs / 2 + 1; rows_ = np.arange(bel.shape[0])[:, None]; band = np.abs(rows_ + .5 - cy) <= hr
                bel[:, xe - 2:xg, 3] *= band
                fx0c = max(0, fx0); fan = fan[:, fx0c - fx0:]
                reg = bel[y0:y0 + nh, fx0c:fx0c + fan.shape[1]]
                fa = fan[..., 3:] / 255.; ra = reg[..., 3:] / 255.
                out_a = fa + ra * (1 - fa); rgb = (fan[..., :3] * fa + reg[..., :3] * ra * (1 - fa)) / np.maximum(out_a, 1e-6)
                bel[y0:y0 + nh, fx0c:fx0c + fan.shape[1], :3] = rgb; bel[y0:y0 + nh, fx0c:fx0c + fan.shape[1], 3] = out_a[..., 0] * 255
                A[br0:br1, x0:x0 + CW] = bel.clip(0, 255).astype(np.uint8)
                print('tail fan male: stalk end', xe, 'caudal', fx0c, '..', fx0c + fan.shape[1], 'h', nh); continue
            sx = np.nonzero((side[..., 3] > 60).sum(0))[0][0]; L = xb - xl
            fan = side[:, sx:sx + L]; ys = np.nonzero((fan[..., 3] > 60).sum(1))[0]; fan = fan[ys[0]:ys[-1] + 1]
            nh = max(6, int(fan.shape[0] * .7)); yi = (np.arange(nh) * fan.shape[0] / nh).astype(int); fan = fan[yi]   # V17.99 (owner: the tail looked corrupted, a stick with a blob): pressed flat on the glass, ~70 % of the side fan
            cy = int(np.average(np.nonzero(bel[:, xl:xb, 3] > 60)[0]))
            # V17.100 (owner: "the caudal looks like a double tail"): the render's edge-on stick lay OVER the fan (a line through
            # it) and poked out past the fan's notch (a spike). Now the stick is erased up to its last 20 % (the join to the
            # stalk, fading in), and the fan lies on top.
            keep = np.clip((np.arange(L) - L * .8) / (L * .15), 0, 1); bel[:, xl:xb, 3] *= keep[None, :]; bel[:, :xl, 3] = 0   # faint stick tip left of the fan too
            y0 = cy - nh // 2; reg = bel[y0:y0 + nh, xl:xb]
            fa = fan[..., 3:] / 255.; ra = reg[..., 3:] / 255.
            out_a = fa + ra * (1 - fa); rgb = (fan[..., :3] * fa + reg[..., :3] * ra * (1 - fa)) / np.maximum(out_a, 1e-6)
            bel[y0:y0 + nh, xl:xb, :3] = rgb; bel[y0:y0 + nh, xl:xb, 3] = out_a[..., 0] * 255
            A[br0:br1, x0:x0 + CW] = bel.clip(0, 255).astype(np.uint8)
            print('tail fan', col, 'stick', xl, xb, 'fan h', nh)
        S = np.zeros((H, CW * 4, 4), np.uint8); S[:, :W] = A
        S[:, 2 * CW:3 * CW] = A[:, :CW]; S[:, 3 * CW:] = A[:, CW:]
        for y0 in (38, 138):                                     # adult side, adult belly
            r0, r1 = int(y0 * F), int((y0 + 100) * F)
            m, f = A[r0:r1, :CW], A[r0:r1, CW:]
            S[r0:r1, 2 * CW:3 * CW] = recolor(m, hist_map(fishpx(m), fishpx(f)))   # black male
            S[r0:r1, 3 * CW:] = recolor(f, hist_map(fishpx(f), fishpx(m)))         # brown female
        # V17.99: the male belly moved 5 css px (make_sheet.py MDX), so the disc centre too
        # the oral disc stays pale on a black male (as on real black bristlenose): put the photo's disc back (soft circle)
        cy, cx, R = 907, round(535 - 5 * F), 58; yy, xx = np.mgrid[0:H, 0:CW]; w = np.clip((R + 8 - np.hypot(xx - cx, yy - cy)) / 16, 0, 1)[..., None]
        S[:, 2 * CW:3 * CW, :3] = (A[:, :CW, :3] * w + S[:, 2 * CW:3 * CW, :3] * (1 - w)).astype(np.uint8)
        b = base64.b64encode(S.tobytes()).decode()
        url = c.js("(async(b,w,h)=>{const s=atob(b),u=new Uint8ClampedArray(s.length);for(let i=0;i<s.length;i++)u[i]=s.charCodeAt(i);const c=document.createElement('canvas');c.width=w;c.height=h;"
                   "c.getContext('2d').putImageData(new ImageData(u,w,h),0,0);return c.toDataURL('image/webp',.9)})(%s,%d,%d)" % (json.dumps(b), S.shape[1], H))
        open(os.path.join(OUT, 'sheet97.webp'), 'wb').write(base64.b64decode(url.split(',', 1)[1]))
        import pngio; pngio.write(os.path.join(OUT, 'sheet97_adults.png'), S[int(30 * F):int(240 * F)])
        print('ok', S.shape, os.path.getsize(os.path.join(OUT, 'sheet97.webp')))
    finally: c.close()
