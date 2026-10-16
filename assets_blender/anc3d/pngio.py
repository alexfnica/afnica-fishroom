# Minimal PNG read/write with numpy only (8-bit RGB/RGBA, non-interlaced) - Blender's Python has no PIL.
import zlib, struct, numpy as np

def read(path):
    d = open(path, 'rb').read(); assert d[:8] == b'\x89PNG\r\n\x1a\n'
    i = 8; idat = b''; w = h = ct = None
    while i < len(d):
        n = struct.unpack('>I', d[i:i + 4])[0]; t = d[i + 4:i + 8]; c = d[i + 8:i + 8 + n]; i += 12 + n
        if t == b'IHDR': w, h, bd, ct, _, _, il = struct.unpack('>IIBBBBB', c); assert bd == 8 and il == 0
        elif t == b'IDAT': idat += c
    ch = {2: 3, 6: 4, 0: 1, 4: 2}[ct]; raw = zlib.decompress(idat); st = w * ch
    out = np.zeros((h, st), np.uint8); prev = np.zeros(st, np.int32); p = 0
    for y in range(h):
        f = raw[p]; line = np.frombuffer(raw, np.uint8, st, p + 1).astype(np.int32); p += st + 1
        if f == 0: cur = line
        elif f == 2: cur = (line + prev) & 255
        else:
            cur = np.zeros(st, np.int32)
            for x in range(st):
                a = cur[x - ch] if x >= ch else 0; b = prev[x]; cc = prev[x - ch] if x >= ch else 0
                if f == 1: v = a
                elif f == 3: v = (a + b) >> 1
                else:
                    pa, pb, pc = abs(b - cc), abs(a - cc), abs(a + b - 2 * cc)
                    v = a if pa <= pb and pa <= pc else (b if pb <= pc else cc)
                cur[x] = (line[x] + v) & 255
        out[y] = cur; prev = cur
    a = out.reshape(h, w, ch)
    if ch == 3: a = np.dstack([a, np.full((h, w), 255, np.uint8)])
    if ch == 1: a = np.dstack([a, a, a, np.full((h, w), 255, np.uint8)])
    if ch == 2: a = np.dstack([a[..., 0], a[..., 0], a[..., 0], a[..., 1]])
    return a

def write(path, a):
    a = np.ascontiguousarray(a.astype(np.uint8)); h, w = a.shape[:2]; ch = a.shape[2] if a.ndim == 3 else 1
    ct = {1: 0, 3: 2, 4: 6}[ch]
    raw = b''.join(b'\x00' + a[y].tobytes() for y in range(h))
    def chunk(t, c): return struct.pack('>I', len(c)) + t + c + struct.pack('>I', zlib.crc32(t + c) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, ct, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))
