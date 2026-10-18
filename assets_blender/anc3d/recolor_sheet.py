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
            sx = np.nonzero((side[..., 3] > 60).sum(0))[0][0]; L = xb - xl
            fan = side[:, sx:sx + L]; ys = np.nonzero((fan[..., 3] > 60).sum(1))[0]; fan = fan[ys[0]:ys[-1] + 1]
            nh = max(6, int(fan.shape[0] * .7)); yi = (np.arange(nh) * fan.shape[0] / nh).astype(int); fan = fan[yi]   # V17.99 (owner: the tail looked corrupted, a stick with a blob): pressed flat on the glass, ~70 % of the side fan
            fan[..., 3] *= np.clip((np.arange(L) - L * .0) / (L * .15), 0, 1)[None, :] * .95   # soft where it meets the stick root
            cy = int(np.average(np.nonzero(bel[:, xl:xb, 3] > 60)[0]))
            y0 = cy - nh // 2; reg = bel[y0:y0 + nh, xl:xb]
            fa = fan[..., 3:] / 255.; ra = reg[..., 3:] / 255.
            out_a = ra + fa * (1 - ra); rgb = (reg[..., :3] * ra + fan[..., :3] * fa * (1 - ra)) / np.maximum(out_a, 1e-6)
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
