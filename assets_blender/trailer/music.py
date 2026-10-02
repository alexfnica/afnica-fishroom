# Original trailer music for AFNICA - Aquarium Simulator, synthesised from scratch with numpy (no samples, no copyright).
# 120 BPM (one beat = 0.5 s) so the trailer cuts land on the beat. Key: A minor, progression Am - F - C - G.
# Run: D:\Blender\blender.exe -b -P music.py -- <style A|B|C> <out.wav> [bars]
import sys, wave, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
STYLE, OUT = a[0].upper(), a[1]; BARS = int(a[2]) if len(a) > 2 else 10
SR = 44100; BPM = 120; BEAT = 60 / BPM; BAR = 4 * BEAT
N = int(SR * (BARS * BAR + 3.0)); T = N / SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(5)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    s = sig[:N - i] * gain
    L[i:i + len(s)] += s * np.sqrt(.5 * (1 - pan)) * 1.414
    R[i:i + len(s)] += s * np.sqrt(.5 * (1 + pan)) * 1.414

def env(n, att, rel, dur=None):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(att, 1e-4))
    if dur is not None: e *= np.clip(1 - (t - dur) / max(rel, 1e-4), 0, 1)
    return e

def fft_filter(x, lo=0, hi=SR / 2, slope=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi < SR / 2: g *= 1 / (1 + (f / hi) ** (2 * slope))
    if lo > 0: g *= 1 / (1 + (lo / np.maximum(f, 1)) ** (2 * slope))
    return np.fft.irfft(X * g, len(x))

# ---------------- instruments ----------------
def pad(notes, dur, bright=10):
    n = int((dur + 1.5) * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for det in (-.11, 0, .09):
            f = mtof(m + det)
            for k in range(1, bright + 1):
                if f * k > 9000: break
                s += np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6.28)) / k ** 1.25
    return s * env(n, .45, 1.2, dur) / (len(notes) * 3)

def pluck(m, dur=.6, bright=1.0):
    n = int((dur + .3) * SR); t = np.arange(n) / SR; f = mtof(m); s = np.zeros(n)
    for k in range(1, 14):
        if f * k > 12000: break
        s += np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (3 + 2.2 * k / bright))
    return s * np.minimum(1, t / .002)

def marimba(m, dur=.5):
    n = int((dur + .4) * SR); t = np.arange(n) / SR; f = mtof(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) + .45 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 18) + .15 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 40)
    return s * np.minimum(1, t / .001)

def epiano(m, dur=1.0):
    n = int((dur + .8) * SR); t = np.arange(n) / SR; f = mtof(m)
    mod = 1.6 * np.exp(-t * 2.5) * np.sin(2 * np.pi * f * t)
    s = np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 1.4) + .25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
    return s * env(n, .003, .3, dur) * (1 + .15 * np.sin(2 * np.pi * 4.5 * t))     # gentle tremolo

def sub(m, dur):
    n = int((dur + .05) * SR); t = np.arange(n) / SR; f = mtof(m)
    s = np.tanh(1.6 * np.sin(2 * np.pi * f * t)) * .8 + .2 * np.sin(2 * np.pi * 2 * f * t)
    return s * env(n, .01, .06, dur)

def kick(power=1.0):
    n = int(.5 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5 * (1.3 - .3 * power)) + .3 * np.exp(-t * 300) * rng.uniform(-1, 1, n)
    return np.tanh(1.5 * s) * power

def snare():
    n = int(.35 * SR); t = np.arange(n) / SR
    nz = fft_filter(rng.uniform(-1, 1, n), 900, 9000) * np.exp(-t * 16)
    return nz * 1.4 + .5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)

def clap():
    n = int(.3 * SR); t = np.arange(n) / SR; nz = fft_filter(rng.uniform(-1, 1, n), 1000, 6000); e = np.zeros(n)
    for d in (0, .011, .022): e += np.exp(-np.maximum(0, t - d) * 60) * (t >= d)
    return nz * (e * .5 + np.exp(-t * 12) * .5) * 1.6

def hat(open_=False):
    n = int((.25 if open_ else .06) * SR); t = np.arange(n) / SR
    return fft_filter(rng.uniform(-1, 1, n), 7000) * np.exp(-t * (10 if open_ else 60)) * .9

def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = t / dur
    nz = rng.uniform(-1, 1, n); out = np.zeros(n); seg = n // 16
    for i in range(16):                                         # noise that opens up
        a0, a1 = i * seg, (i + 1) * seg if i < 15 else n
        out[a0:a1] = fft_filter(nz[a0:a1], 300 + 9000 * (i / 15) ** 2, 1200 + 14000 * (i / 15))
    f = 200 * 2 ** (x * 3); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * .25
    return (out * .8 + tone) * x ** 2

def impact():
    n = int(3.0 * SR); t = np.arange(n) / SR
    f = 30 + 90 * np.exp(-t * 6); boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    nz = fft_filter(rng.uniform(-1, 1, n), 60, 3000) * np.exp(-t * 4)
    return np.tanh(2 * boom) * 1.1 + nz * .6

def whoosh(dur=.8):
    n = int(dur * SR); t = np.arange(n) / SR; x = t / dur
    nz = fft_filter(rng.uniform(-1, 1, n), 400, 5000)
    return nz * np.sin(np.pi * x) ** 2 * .7

def reverb(x, secs=2.2, seed=1, damp=4000):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = np.random.default_rng(seed).uniform(-1, 1, n) * np.exp(-t * 6.9 / secs)
    ir = fft_filter(ir, 150, damp); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n - 1; k = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, k) * np.fft.rfft(ir, k), k)[:len(x)]

# ---------------- arrangement ----------------
CH = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]   # Am F C G (voiced close)
ROOT = [33, 29, 36, 31]
ARP = [0, 1, 2, 1, 2, 3, 2, 1]                                   # 8th-note pattern over the chord (+octave)

def chord_at(bar): return bar % 4

pads = np.zeros(N); padsR = np.zeros(N)
DROP = int(a[4]) if len(a) > 4 else BARS - 2                     # the drop bar (default: the last two bars)
INTRO, BUILD = 2, DROP - 1                                       # bars 0-1 intro, build in the bar before the drop
END = float(a[5]) if len(a) > 5 else None                        # optional hard end: fade out just before it
pump = np.ones(N)                                                # sidechain: pads duck under each kick

def kick_at(t0, power=1.0):
    add(kick(power), t0, .95)
    i = int(t0 * SR); n = int(.32 * SR); d = 1 - .55 * np.exp(-np.arange(n) / SR * 10)
    if i < N: pump[i:i + n] = np.minimum(pump[i:i + n], d[:N - i])

for b in range(BARS):
    t0 = b * BAR; c = chord_at(b); notes = CH[c]
    intro = b < INTRO; build = b == BUILD; drop = b >= DROP
    # ---- harmony ----
    if STYLE == 'A':                                             # cinematic: wide pad + low strings-like pad, piano motif
        p = pad([n - 12 for n in notes] + [notes[0]], BAR, 9); add(p, t0, .55 if not drop else .75, -.25); add(p, t0 + .013, .5 if not drop else .7, .25)
        if not intro:
            for s in range(8): add(pluck(notes[ARP[s] % 3] + 12 * (1 + ARP[s] // 3), .5, .8), t0 + s * BEAT / 2, .22, (-.4, .4)[s % 2])
    elif STYLE == 'B':                                           # upbeat: marimba chords on the off-beats, pluck lead
        add(pad(notes, BAR, 6), t0, .25)
        for s in range(8):
            if s % 2 == 1 or drop:
                for m in notes: add(marimba(m + 12, .3), t0 + s * BEAT / 2, .2, -.3)
        if not intro:
            mel = [76, 74, 72, 74, 76, 79, 76, 72] if c in (0, 2) else [77, 76, 74, 72, 74, 76, 74, 71]
            for s, m in enumerate(mel):
                if s in (1, 5) and not drop: continue
                add(pluck(m, .35, 1.4), t0 + s * BEAT / 2, .2, .3)
    else:                                                        # chill: electric piano chords + soft high plucks like drops of water
        for m in notes + [notes[0] + 12]: add(epiano(m, BAR * .9), t0, .22, rng.uniform(-.3, .3))
        add(pad(notes, BAR, 5), t0, .18)
        for s in (3, 6, 7) if not intro else (6,):
            add(pluck(notes[s % 3] + 24, .5, .6), t0 + s * BEAT / 2 + .03, .11, rng.uniform(-.6, .6))
    # ---- bass ----
    if not intro or STYLE == 'A':
        r = ROOT[c] + 12 if STYLE != 'A' else ROOT[c]
        if STYLE == 'A':
            for s in range(8): add(sub(r + 12, BEAT / 2 * .8), t0 + s * BEAT / 2, .30 if not intro else .16)     # pulsing 8ths
        elif STYLE == 'B':
            for s in (0, 3, 4, 7): add(sub(r, BEAT / 2 * .9), t0 + s * BEAT / 2, .38)
        else:
            add(sub(r, BEAT * 1.8), t0, .34); add(sub(r + 7, BEAT * .9), t0 + BEAT * 2.5, .3)
    # ---- drums ----
    if intro and STYLE != 'C': continue
    if build:                                                    # snare roll + riser into the drop
        add(riser(BAR), t0, .55)
        for s in range(16):
            if STYLE == 'C' and s % 2: continue
            add(snare(), t0 + s * BEAT / 4, .12 + .3 * s / 16)
        kick_at(t0, .8); kick_at(t0 + BEAT * 2, .8)
        continue
    if STYLE == 'A':
        if drop:
            for k in range(4): kick_at(t0 + k * BEAT)
            add(snare(), t0 + BEAT, .45); add(snare(), t0 + 3 * BEAT, .45)
            for s in range(8): add(hat(), t0 + s * BEAT / 2, .2)
        else:
            kick_at(t0, .8); kick_at(t0 + 2.5 * BEAT, .6)
            for s in (2, 6): add(hat(True), t0 + s * BEAT / 2, .12)
    elif STYLE == 'B':
        for k in range(4): kick_at(t0 + k * BEAT, .9)
        add(clap(), t0 + BEAT, .4); add(clap(), t0 + 3 * BEAT, .4)
        for s in range(8): add(hat(s % 2 == 1), t0 + s * BEAT / 2, .14 if s % 2 else .08)
    else:
        if intro: continue
        swing = .045
        kick_at(t0, .75); kick_at(t0 + 2.5 * BEAT, .6)
        add(snare(), t0 + BEAT, .22); add(snare(), t0 + 3 * BEAT, .22)
        for s in range(8): add(hat(), t0 + s * BEAT / 2 + (swing if s % 2 else 0), .07)

# drop: big impact on its first beat and a whoosh going into it
add(impact(), DROP * BAR, .75)
add(whoosh(1.0), DROP * BAR - .9, .4)
add(impact(), 0, .45)                                            # opening hit for the title card
# extra sound design synced to the picture: [[time, kind, gain], ...] from a json file (4th argument)
if len(a) > 3:
    import json
    for t_, kind, gn in json.load(open(a[3])):
        if kind == 'whoosh': add(fft_filter(whoosh(.7), 300, 2600), t_ - .4, gn, rng.uniform(-.3, .3))   # darker, longer, quieter
        elif kind == 'impact': add(impact(), t_, gn)
        elif kind == 'riser': add(riser(BAR), t_, gn)
        elif kind == 'tick':
            n = int(.08 * SR); tt = np.arange(n) / SR; add(np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 60), t_, gn)

# sidechain + reverb + master
L *= pump; R *= pump
L += reverb(L, 2.4, 1) * .28; R += reverb(R, 2.4, 2) * .28
fade = np.ones(N); tail = int(2.5 * SR); fade[-tail:] = np.linspace(1, 0, tail) ** 2
if END:                                                          # ring out over the last 1.6 s before the picture ends
    e1 = int(END * SR); e0 = int((END - 1.6) * SR); fade[e0:e1] = np.minimum(fade[e0:e1], np.linspace(1, 0, e1 - e0) ** 1.5); fade[e1:] = 0
L *= fade; R *= fade
mx = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L / mx * 1.25) / np.tanh(1.25) * .95; R = np.tanh(R / mx * 1.25) / np.tanh(1.25) * .95
pcm = (np.stack([L, R], -1) * 32767).astype('<i2')
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('SAVED', OUT, round(T, 2), 's')
