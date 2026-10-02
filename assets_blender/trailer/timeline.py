# AFNICA - Aquarium Simulator: 38 s vertical trailer, cut on the beat of music A (120 BPM: beat 0.5 s, bar 2 s).
# Music: 19 bars. Bars 0-1 intro, 2-14 groove, 15 build (riser + four quick cuts), drop on bar 16 (32.0 s), splash at 36 s.
# Every shot is real game footage from raw/<take>/ (recorded by takes.py); 'from' = first take frame used.
DURATION = 38.0
MUSIC = dict(bars=19, drop=16, end=38.0)

def S(t0, t1, take, frm, tin='cut', td=0.0, zoom=(1.0, 1.06), punch=0.08, **kw):
    d = dict(t0=t0, t1=t1, take=take, **{'from': frm}, tin=tin, td=td, zoom=list(zoom), punch=punch); d.update(kw); return d

SHOTS = [
    S(0.0, 2.0, 'xipho_court', 230, tin='cut', zoom=(1.12, 1.0), punch=0),            # hook: swordtail courtship, close
    S(2.0, 4.0, 'neon', 60, tin='whip', td=.36, zoom=(1.0, 1.08)),                    # the neon school
    S(4.0, 6.0, 'guppy_court', 150, tin='zoom', td=.4, zoom=(1.0, 1.07)),              # guppy display
    S(6.0, 8.0, 'guppy_court', 330, tin='cut', punch=.1, zoom=(1.04, 1.12)),           # the thrust
    S(8.0, 10.0, 'fry', 60, tin='zoom', td=.4, zoom=(1.0, 1.1)),                      # newborn fry
    S(10.0, 12.0, 'net', 85, tin='whip', td=.36, dir=-1, zoom=(1.0, 1.05)),            # catching fry with the net
    S(12.0, 14.0, 'hunt', 20, tin='cut', punch=.12, zoom=(1.05, 1.12)),                # ... or they get eaten
    S(14.0, 16.0, 'fight', 110, tin='zoom', td=.4, zoom=(1.0, 1.08)),                  # swordtail males squaring up
    S(16.0, 18.0, 'fight', 280, tin='cut', punch=.12, zoom=(1.06, 1.12)),              # the clash and the chase
    S(18.0, 20.0, 'feed', 20, tin='whip', td=.36, zoom=(1.0, 1.06)),                   # feeding burst
    S(20.0, 22.0, 'anc_fan', 0, tin='whip', td=.36, dir=-1, zoom=(1.0, 1.06)),         # bristlenose male fanning the eggs
    S(22.0, 24.0, 'anc_glass', 0, tin='cross', td=.5, zoom=(1.0, 1.05)),               # female grazing on the glass
    S(24.0, 26.0, 'beauty', 30, tin='zoom', td=.4, zoom=(1.0, 1.06)),                  # SELL: a show-quality male
    S(26.0, 28.0, 'hero', 60, tin='whip', td=.36, zoom=(1.3, 1.0)),                    # UPGRADE: pull back over the tank
    S(28.0, 30.0, 'ui', 30, tin='zoom', td=.4, zoom=(1.0, 1.04)),                      # inspect a fish in the app
    # build: four half-beat cuts
    S(30.0, 30.5, 'xipho_court', 300, tin='cut', punch=.14, zoom=(1.1, 1.16)),
    S(30.5, 31.0, 'neon', 160, tin='cut', punch=.14, zoom=(1.1, 1.16)),
    S(31.0, 31.5, 'fight', 330, tin='cut', punch=.14, zoom=(1.1, 1.16)),
    S(31.5, 32.0, 'beauty', 150, tin='cut', punch=.14, zoom=(1.1, 1.22)),
    # drop: the hero tank behind the app icon, then the splash screen
    S(32.0, 38.0, 'hero', 30, tin='cut', punch=.18, zoom=(1.0, 1.12), blur=[32.9, 9]),
]

TEXTS = [
    # documentary species labels (names as in the game's species table)
    dict(kind='tag', text='SWORDTAIL', latin='Xiphophorus hellerii', t0=.5, t1=1.95),
    dict(kind='tag', text='NEON TETRA', latin='Paracheirodon innesi', t0=2.35, t1=3.95),
    dict(kind='tag', text='RED TUXEDO GUPPY', latin='Poecilia reticulata', t0=4.35, t1=7.9),
    dict(kind='tag', text='BRISTLENOSE PLECO', latin='Ancistrus sp.', t0=20.3, t1=23.9),
    # hook
    dict(kind='sub', text='EVERY FISH', t0=.35, t1=1.95, y=1122, size=40),
    dict(kind='word', text='IS ALIVE', t0=.55, t1=1.95, y=1290, size=150),
    # sections
    dict(kind='sub', text='REAL COURTSHIP', t0=4.25, t1=7.95, y=1122),
    dict(kind='word', text='BREED', t0=4.4, t1=7.95, y=1300, size=190),
    dict(kind='line', t0=4.6, t1=7.95, y=1340, w=330),
    dict(kind='sub', text='LIVE BIRTH  ·  4 LIFE STAGES', t0=8.25, t1=9.95, y=1122),
    dict(kind='word', text='NEW LIFE', t0=8.4, t1=9.95, y=1300, size=170),
    dict(kind='sub', text='CATCH THE FRY', t0=10.25, t1=11.95, y=1122),
    dict(kind='word', text='RAISE', t0=10.4, t1=11.95, y=1300, size=190),
    dict(kind='sub', text='OR THEY GET EATEN', t0=12.2, t1=13.95, y=1240, color='#ff9a8a', size=46),
    dict(kind='sub', text='FOR THE ALPHA', t0=14.25, t1=17.95, y=1122),
    dict(kind='word', text='FIGHT', t0=14.4, t1=17.95, y=1300, size=200, glow='rgba(255,120,90,.35)'),
    dict(kind='line', t0=14.6, t1=17.95, y=1340, w=330, color='rgba(255,170,150,.9)'),
    dict(kind='sub', text='FEED  ·  CLEAN  ·  TREAT', t0=18.25, t1=19.95, y=1122),
    dict(kind='word', text='CARE', t0=18.4, t1=19.95, y=1300, size=190),
    dict(kind='sub', text='GUARDING THE EGGS', t0=20.3, t1=21.95, y=1240, size=42),
    dict(kind='sub', text='EACH WITH ITS OWN BEHAVIOUR', t0=22.25, t1=23.95, y=1122),
    dict(kind='word', text='7 SPECIES', t0=22.4, t1=23.95, y=1300, size=160),
    dict(kind='sub', text='BREED THE BEST BLOODLINES', t0=24.25, t1=25.95, y=1122),
    dict(kind='word', text='SELL', t0=24.4, t1=25.95, y=1300, size=200, glow='rgba(255,210,110,.35)'),
    dict(kind='line', t0=24.6, t1=25.95, y=1340, w=300, color='rgba(255,215,130,.9)'),
    dict(kind='word', text='UPGRADE', t0=26.25, t1=27.95, y=1300, size=180),
    dict(kind='sub', text='YOUR SYSTEM', t0=26.4, t1=27.95, y=1395),
    dict(kind='sub', text='GENES  ·  HEALTH  ·  VALUE', t0=28.25, t1=29.95, y=1560),
    dict(kind='word', text='INSPECT', t0=28.4, t1=29.95, y=1700, size=170),
    # build: one word per cut
    dict(kind='word', text='BREED', t0=30.0, t1=30.5, y=1000, size=230, stagger=.012, dur=.16, exit=.08),
    dict(kind='word', text='RAISE', t0=30.5, t1=31.0, y=1000, size=230, stagger=.012, dur=.16, exit=.08),
    dict(kind='word', text='FIGHT', t0=31.0, t1=31.5, y=1000, size=230, stagger=.012, dur=.16, exit=.08, glow='rgba(255,120,90,.35)'),
    dict(kind='word', text='SELL', t0=31.5, t1=32.0, y=1000, size=230, stagger=.012, dur=.16, exit=.08, glow='rgba(255,210,110,.35)'),
    # end card: the app icon over the blurred tank, the name, COMING SOON; then the splash screen
    dict(kind='word', text='AFNICA', t0=32.7, t1=36.1, y=1205, size=118, font='%spx Georgia', track=34, stagger=.05, glow='rgba(120,220,255,.25)'),
    dict(kind='sub', text='AQUARIUM SIMULATOR', t0=33.0, t1=36.1, y=1290, size=40, font='%spx Goth', color='#e8f8ff', track0=10, track1=19),
    dict(kind='word', text='COMING SOON', t0=33.8, t1=36.1, y=1500, size=84, track=10, stagger=.03),
    dict(kind='line', t0=34.0, t1=36.1, y=1538, w=380),
    dict(kind='sub', text='FOLLOW THE JOURNEY', t0=34.6, t1=36.1, y=1610, size=34),
]

TL = dict(
    shots=SHOTS, texts=TEXTS,
    logos=[dict(src='../logo/app_icon_1024.png', t0=32.15, t1=36.1, y=760, w=430, round=.22),
           dict(src='../logo/logo_aquarium_simulator.png', t0=36.1, t1=38.0, y=900, w=1040, splash=True, bg='#fefefe')],
    dim=[(32.1, 38, .5)],
    flashes=[(0.0, .9, .5), (32.0, 1.0, .55), (36.1, 1.0, .45), (8.0, .16, .2), (14.0, .16, .2), (24.0, .16, .2),
             (30.0, .25, .15), (30.5, .25, .15), (31.0, .25, .15), (31.5, .25, .15)],
    fades=[(0.0, .45, 'in')],
    shake=[(32.0, 18), (6.0, 6), (16.0, 8), (12.0, 5), (30.0, 5), (30.5, 5), (31.0, 5), (31.5, 5)],
    leak=.8, rays=.9,
)

# sound design synced to the cuts (added to music A): whooshes on whip/zoom transitions, ticks on the build cuts, a hit on the splash
SFX = [[s['t0'], 'whoosh', .55] for s in SHOTS if s['tin'] in ('whip', 'zoom')] + [[t, 'tick', .25] for t in (30.0, 30.5, 31.0, 31.5)] + [[36.1, 'impact', .35]]
