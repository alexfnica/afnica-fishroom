# Render the trailer: timeline -> frames (compose.html in headless Chrome) -> music with synced SFX -> MP4.
# Shots are placed on EVENTS found in the takes' phase logs (the strike of a hunt, the thrust of a courtship, a nip in a
# fight...), so a re-recorded take still lines up. A shot can slow down around its event (speed ramp) when the take was
# filmed at 120 fps. The SFX list (whooshes, gulps, thuds, plops) is built from the same events.
# Run: python compose.py [first_frame last_frame]   (a range renders only those frames, for previews)
import os, sys, json, time, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
import timeline
from timeline import TL, SFX, DURATION, MUSIC
HERE = os.path.dirname(os.path.abspath(__file__)); OUTF = os.path.join(HERE, 'out', 'frames'); os.makedirs(OUTF, exist_ok=True)
BL = r'D:\Blender\blender.exe'; FPS = 30
N = int(round(DURATION * FPS))

def take_info(take):
    d = os.path.join(HERE, 'raw', take)
    n = len([f for f in os.listdir(d) if f.endswith('.jpg')])
    fps = json.load(open(os.path.join(d, 'meta.json')))['fps'] if os.path.exists(os.path.join(d, 'meta.json')) else 30
    log = json.load(open(os.path.join(d, 'cam.json'))) if os.path.exists(os.path.join(d, 'cam.json')) else []
    return n, fps, log

def events(take, log, fps):
    """take time (s) of named events, from the phase log"""
    ev = {}
    ph = [(e.get('ph') if isinstance(e, dict) else None) for e in log]
    def first(pred, name, extra=0.0):
        for i, p in enumerate(ph):
            try:
                if pred(p): ev[name] = i / fps + extra; return
            except Exception: pass
    if take.startswith('hunt'):
        first(lambda p: p and p.get('phase') == 'strike', 'strike')
        first(lambda p: p and p.get('phase') == 'chew', 'chew')
    if take in ('guppy_court', 'xipho_court'):
        first(lambda p: p and p.get('T', -9) >= 1.0, 'display')
        first(lambda p: p and p.get('res') is not None, 'thrust')
        hits = [i / fps for i, p in enumerate(ph) if p and p.get('hit') is not None and p['hit'] < .03]
        ev['hits'] = hits
    if take == 'fight':
        nips = []; prev = None
        for i, p in enumerate(ph):
            seg = p.get('seg') if p else None
            if seg == 'nip' and prev != 'nip': nips.append(i / fps)
            prev = seg
        ev['nips'] = nips
        if nips: ev['nip'] = nips[0]
        if len(nips) > 1: ev['nip2'] = nips[1]
        first(lambda p: p and p.get('seg') == 'chase', 'chase')
    if take == 'net': ev['dodge'] = 40 / 30 + .25; ev['catch'] = 110 / 30 + .33
    if take == 'feed': ev['feed'] = 15 / 30 + .4
    return ev

def speed_fn(ramp):
    """speed as a function of source time relative to the anchor: [a0, a1, k] = slow to k between a0 and a1 (s, source)"""
    if not ramp: return lambda u: 1.0
    a0, a1, k = ramp; e = .12
    def f(u):
        if u < a0 - e or u > a1 + e: return 1.0
        if u < a0: q = (a0 - u) / e
        elif u > a1: q = (u - a1) / e
        else: return k
        return k + (1 - k) * (q * q * (3 - 2 * q))
    return f

def source_times(shot, ev, fps, n):
    """source time for every output frame of the shot (plus transition margins)"""
    td = shot.get('td', 0) or 0
    f0 = int(math.floor((shot['t0'] - td) * FPS)); f1 = int(math.ceil((shot['t1'] + td) * FPS))
    if 'anchor' in shot:
        ta = ev.get(shot['anchor'])
        if ta is None: ta = shot.get('at', 0); print('  ! no event', shot['anchor'], 'in', shot['take'])
        out_a = shot['anchorAt']; spd = speed_fn(shot.get('ramp'))
        res = {}; dt = 1 / FPS
        # integrate forward and backward from the anchor
        fa = int(round(out_a * FPS)); u = 0.0; res[fa] = ta
        for fi in range(fa + 1, f1 + 1):
            sub = 8;
            for _ in range(sub): u += spd(u) * dt / sub
            res[fi] = ta + u
        u = 0.0
        for fi in range(fa - 1, f0 - 1, -1):
            sub = 8
            for _ in range(sub): u -= spd(u) * dt / sub
            res[fi] = ta + u
        times = [res[fi] for fi in range(f0, f1 + 1)]
    else:
        start = shot.get('at', shot.get('from', 0) / 30.0)
        times = [start + (fi / FPS - shot['t0']) * shot.get('speed', 1) for fi in range(f0, f1 + 1)]
    srcs = [max(0, min(n - 1, int(round(x * fps)))) for x in times]
    return f0, srcs, times

def build():
    sfx = list(SFX)
    for s in TL['shots']:
        n, fps, log = take_info(s['take']); ev = events(s['take'], log, fps)
        f0, srcs, times = source_times(s, ev, fps, n)
        s['f0'], s['srcs'], s['len'] = f0, srcs, n
        # map the take's events into the visible part of this shot -> sound effects
        def out_time(te):                                   # the output frame whose source time is closest to the event
            best, bd = None, 1e9
            for k, x in enumerate(times):
                t = (f0 + k) / FPS
                if s['t0'] <= t < s['t1'] and abs(x - te) < bd: best, bd = t, abs(x - te)
            return best if bd < .05 else None
        for name, kind, gain in s.get('sfx', []):
            vals = ev.get(name); vals = vals if isinstance(vals, list) else [vals] if vals is not None else []
            for te in vals:
                ot = out_time(te)
                if ot is not None: sfx.append([round(ot, 3), kind, gain])
        print('%-12s %5.2f-%5.2f fps=%3d src %d..%d %s' % (s['take'], s['t0'], s['t1'], fps, srcs[0], srcs[-1], {k: (round(v, 2) if isinstance(v, float) else len(v)) for k, v in ev.items()}))
    return sfx

if __name__ == '__main__':
    rng = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, N - 1)
    sfx = build()
    if len(sys.argv) > 1 and sys.argv[1] == 'audio': rng = None
    c = Chrome(1080, 1920, 1, port=9555) if rng else None
    try:
      if rng:
        c.cmd('Page.navigate', url='file:///' + os.path.join(HERE, 'compose.html').replace(os.sep, '/')); c.wait_event('Page.loadEventFired', 30)
        c.js('ready'); c.js('window.TL=' + json.dumps(TL) + ';1')
        t0 = time.time()
        for i in range(rng[0], rng[1] + 1):
            c.js('renderFrame(%d)' % i)
            c.shot(os.path.join(OUTF, '%05d.jpg' % i), clip=dict(x=0, y=0, width=1080, height=1920, scale=1), q=95)
            if i % 60 == 0: print('frame', i, '/', N, round(time.time() - t0), 's', flush=True)
    finally:
        if c: c.close()
    if rng is None or rng == (0, N - 1):
        json.dump(sfx, open(os.path.join(HERE, 'out', 'sfx.json'), 'w')); print('sfx', sorted(sfx))
        wav = os.path.join(HERE, 'out', 'music_trailer.wav')
        r = subprocess.run([BL, '-b', '-P', os.path.join(HERE, 'music.py'), '--', 'A', wav, str(MUSIC['bars']), os.path.join(HERE, 'out', 'sfx.json'), str(MUSIC['drop']), str(MUSIC['end'])], capture_output=True, text=True)
        print([l for l in r.stdout.splitlines() if 'SAVED' in l or 'rror' in l][-3:])
        mp4 = os.path.join(HERE, 'out', 'AFNICA_trailer.mp4')
        r = subprocess.run([BL, '-b', '-P', os.path.join(HERE, 'encode.py'), '--', OUTF, wav, mp4], capture_output=True, text=True)
        print([l for l in r.stdout.splitlines() if 'ENCODED' in l or 'rror' in l][-3:])
