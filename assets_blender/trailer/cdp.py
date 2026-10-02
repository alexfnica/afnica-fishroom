# Minimal Chrome DevTools Protocol client (stdlib only) + a deterministic frame recorder for the AFNICA trailer.
# Chrome runs headless with its OWN throw-away profile, so the player's real save is never touched.
# The page clock is replaced (Date, performance.now, rAF, timers, CSS animations) so every frame is exactly 1/FPS s apart,
# however long a screenshot takes.
import base64, hashlib, json, os, socket, struct, subprocess, time, urllib.request, random

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

class WS:
    def __init__(self, url):
        assert url.startswith('ws://'); hostport, path = url[5:].split('/', 1); host, port = hostport.split(':')
        self.s = socket.create_connection((host, int(port))); self.s.settimeout(90); key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(('GET /%s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\n'
                        'Sec-WebSocket-Version: 13\r\n\r\n' % (path, hostport, key)).encode())
        buf = b''
        while b'\r\n\r\n' not in buf: buf += self.s.recv(4096)
        assert b' 101 ' in buf.split(b'\r\n')[0], buf[:200]
        self.rest = buf.split(b'\r\n\r\n', 1)[1]
    def _read(self, n):
        while len(self.rest) < n:
            d = self.s.recv(1 << 20)
            if not d: raise EOFError
            self.rest += d
        out, self.rest = self.rest[:n], self.rest[n:]; return out
    def send(self, text):
        data = text.encode(); hdr = bytearray([0x81]); n = len(data)
        if n < 126: hdr.append(0x80 | n)
        elif n < 65536: hdr.append(0x80 | 126); hdr += struct.pack('>H', n)
        else: hdr.append(0x80 | 127); hdr += struct.pack('>Q', n)
        mask = os.urandom(4); hdr += mask
        self.s.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(data)) if n < 4096 else bytes(hdr) + _mask(data, mask))
    def recv(self):
        msg = b''
        while True:
            b0, b1 = self._read(2); n = b1 & 0x7f
            if n == 126: n = struct.unpack('>H', self._read(2))[0]
            elif n == 127: n = struct.unpack('>Q', self._read(8))[0]
            payload = self._read(n); op = b0 & 0x0f
            if op == 9: continue
            msg += payload
            if b0 & 0x80: return msg.decode('utf-8', 'replace')

def _mask(data, mask):
    import numpy as np
    a = np.frombuffer(data, np.uint8); m = np.frombuffer(mask * (len(data) // 4 + 1), np.uint8)[:len(data)]
    return (a ^ m).tobytes()

class Chrome:
    def __init__(self, w=540, h=960, scale=2, port=9333, profile=None):
        self.profile = profile or os.path.join(os.path.dirname(os.path.abspath(__file__)), '_profiles', 'p%d' % random.randint(0, 1 << 30))
        self.proc = subprocess.Popen([CHROME, '--headless=new', '--remote-debugging-port=%d' % port, '--user-data-dir=' + self.profile,
                                      '--no-first-run', '--no-default-browser-check', '--mute-audio', '--hide-scrollbars',
                                      '--allow-file-access-from-files', '--window-size=%d,%d' % (w, h), 'about:blank'],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                tabs = json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % port)); break
            except Exception: time.sleep(.1)
        page = next(t for t in tabs if t['type'] == 'page')
        self.ws = WS(page['webSocketDebuggerUrl']); self.id = 0; self.events = []
        self.cmd('Page.enable'); self.cmd('Runtime.enable')
        self.cmd('Emulation.setDeviceMetricsOverride', width=w, height=h, deviceScaleFactor=scale, mobile=True)
        self.cmd('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=5)
        self.w, self.h, self.scale = w, h, scale
    def cmd(self, method, **params):
        self.id += 1; my = self.id; self.ws.send(json.dumps({'id': my, 'method': method, 'params': params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == my:
                if 'error' in m: raise RuntimeError('%s: %s' % (method, m['error']))
                return m.get('result', {})
            self.events.append(m)
            if len(self.events) > 500: self.events = self.events[-200:]
    def js(self, expr, await_=True):
        r = self.cmd('Runtime.evaluate', expression=expr, awaitPromise=await_, returnByValue=True)
        if 'exceptionDetails' in r: raise RuntimeError('JS: ' + json.dumps(r['exceptionDetails'])[:800])
        return r.get('result', {}).get('value')
    def wait_event(self, name, timeout=30):
        t0 = time.time()
        while time.time() - t0 < timeout:
            for i, e in enumerate(self.events):
                if e.get('method') == name: del self.events[i]; return e
            m = json.loads(self.ws.recv()); self.events.append(m)
        raise TimeoutError(name)
    def shot(self, path, clip=None, fmt='jpeg', q=92):
        p = dict(format=fmt, captureBeyondViewport=False, optimizeForSpeed=True)
        if fmt == 'jpeg': p['quality'] = q
        if clip: p['clip'] = dict(clip, scale=clip.get('scale', 1))
        data = self.cmd('Page.captureScreenshot', **p)['data']
        with open(path, 'wb') as f: f.write(base64.b64decode(data))
    def close(self):
        try: self.proc.kill(); self.proc.wait(10)
        except Exception: pass
        import shutil
        for _ in range(20):                                   # the throw-away profile goes too
            try: shutil.rmtree(self.profile); break
            except FileNotFoundError: break
            except Exception: time.sleep(.3)

# Fake clock injected before any page script: time only moves when __afStep(ms) is called.
CLOCK_JS = r'''
(() => {
 let now = 0; const t0 = 1790000000000; let seq = 0;
 const timers = new Map(); let rafs = [];
 const realSetTimeout = window.setTimeout;
 window.__afReal = {setTimeout: realSetTimeout};
 performance.now = () => now;
 const RD = Date; class FD extends RD { constructor(...a){ if(a.length) super(...a); else super(t0 + now); } static now(){ return t0 + now; } }
 window.Date = FD;
 window.setTimeout = (fn, ms, ...a) => { const id = ++seq; timers.set(id, {fn, at: now + Math.max(0, +ms || 0), a, rep: 0}); return id; };
 window.setInterval = (fn, ms, ...a) => { const id = ++seq; const p = Math.max(1, +ms || 0); timers.set(id, {fn, at: now + p, a, rep: p}); return id; };
 window.clearTimeout = window.clearInterval = id => timers.delete(id);
 window.requestAnimationFrame = fn => { const id = ++seq; rafs.push({id, fn}); return id; };
 window.cancelAnimationFrame = id => { rafs = rafs.filter(r => r.id !== id); };
 Object.defineProperty(document, 'hidden', {get: () => false}); Object.defineProperty(document, 'visibilityState', {get: () => 'visible'});
 window.__afNow = () => now;
 window.__afStep = (ms, sub) => {
  sub = sub || 1; const dt = ms / sub;
  for (let k = 0; k < sub; k++) {
   const target = now + dt;
   for (let guard = 0; guard < 5000; guard++) {
    let best = null, bid = 0;
    for (const [id, t] of timers) if (t.at <= target && (!best || t.at < best.at)) { best = t; bid = id; }
    if (!best) break;
    now = Math.max(now, best.at);
    if (best.rep) best.at += best.rep; else timers.delete(bid);
    try { best.fn(...best.a); } catch (e) { console.error('timer', e); }
   }
   now = target;
   const list = rafs; rafs = [];
   for (const r of list) { try { r.fn(now); } catch (e) { console.error('raf', e); } }
  }
  try { for (const a of document.getAnimations()) { if (a.playState !== 'paused') a.pause(); a.currentTime = (a.__afT = (a.__afT == null ? (+a.currentTime || 0) : a.__afT) + ms); } } catch (e) {}
  return now;
 };
})();
'''
