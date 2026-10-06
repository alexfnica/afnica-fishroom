# AFNICA - "What's new: Black Molly" clip. Same music and structure as the trailer (music A, 120 BPM: bar = 2 s,
# 19 bars, drop on bar 16 = 32.0 s, splash at 36.1 s). Each new molly feature gets one 2 s bar; a four-cut build; then
# the app icon, MORE TO FOLLOW and the splash screen. Shots use the molly takes (takes_molly.py).
DURATION = 38.0
MUSIC = dict(bars=19, drop=16, end=38.0)
OUTNAME = 'AFNICA_whats_new_molly.mp4'

def S(t0, t1, take, tin='cut', td=0.0, zoom=(1.0, 1.06), punch=0.08, **kw):
    d = dict(t0=t0, t1=t1, take=take, tin=tin, td=td, zoom=list(zoom), punch=punch); d.update(kw); return d

SHOTS = [
    S(0.0, 4.0, 'm_hero', zoom=(1.12, 1.0), punch=0, at=1.0),
    S(4.0, 6.0, 'm_court', tin='zoom', td=.4, zoom=(1.0, 1.07), anchor='display', anchorAt=4.3),
    S(6.0, 8.0, 'm_court', tin='cut', punch=.1, zoom=(1.04, 1.12), anchor='thrust', anchorAt=7.0, ramp=[-.6, .35, .3], sfx=[('thrust', 'bubbles', .3)]),
    S(8.0, 10.0, 'm_tails', tin='whip', td=.36, zoom=(1.0, 1.06), at=1.5),
    S(10.0, 12.0, 'm_stages', tin='zoom', td=.4, zoom=(1.35, 1.45), at=2.0),
    S(12.0, 14.0, 'm_fight', tin='whip', td=.36, dir=-1, zoom=(1.0, 1.08), anchor='nip', anchorAt=13.0, ramp=[-.15, .45, .35], sfx=[('nips', 'thud', .55)]),
    S(14.0, 16.0, 'm_fight', tin='cut', punch=.12, zoom=(1.06, 1.12), at=7.2),
    S(16.0, 18.0, 'm_breath', tin='zoom', td=.4, zoom=(1.0, 1.08), at=1.5),
    S(18.0, 20.0, 'm_algae', tin='whip', td=.36, zoom=(1.0, 1.05), at=1.0),
    S(20.0, 22.0, 'm_oxygen', tin='cross', td=.5, zoom=(1.0, 1.05), at=.6),
    S(22.0, 24.0, 'm_oxygen', tin='cut', zoom=(1.06, 1.1), at=5.4),
    S(24.0, 26.0, 'm_shimmy', tin='zoom', td=.4, zoom=(1.0, 1.08), at=1.0),
    S(26.0, 28.0, 'm_hero', tin='whip', td=.36, dir=-1, zoom=(1.1, 1.2), at=4.5),
    S(28.0, 30.0, 'm_court', tin='zoom', td=.4, zoom=(1.0, 1.06), at=9.0),
    # build: four half-beat cuts
    S(30.0, 30.5, 'm_court', punch=.14, zoom=(1.1, 1.16), anchor='display', anchorAt=29.9),
    S(30.5, 31.0, 'm_fight', punch=.14, zoom=(1.1, 1.16), anchor='nip', anchorAt=30.65),
    S(31.0, 31.5, 'm_algae', punch=.14, zoom=(1.1, 1.16), at=6.0),
    S(31.5, 32.0, 'm_hero', punch=.14, zoom=(1.1, 1.22), at=5.0),
    # drop: the molly behind the app icon, then the splash screen
    S(32.0, 38.0, 'm_hero', punch=.18, zoom=(1.0, 1.12), at=2.0, blur=[32.9, 9]),
]

TEXTS = [
    dict(kind='sub', text='WHAT\'S NEW', t0=.5, t1=3.95, y=1122, size=46),
    dict(kind='word', text='BLACK MOLLY', t0=.7, t1=3.95, y=1290, size=140, stagger=.03, dur=.35),
    dict(kind='line', t0=1.0, t1=3.95, y=1330, w=420),
    dict(kind='tag', text='BLACK MOLLY', latin='Poecilia sphenops', t0=1.4, t1=3.9),
    # courtship
    dict(kind='sub', text='SAILFIN DISPLAY', t0=4.25, t1=7.95, y=1122),
    dict(kind='word', text='COURTSHIP', t0=4.4, t1=7.95, y=1300, size=160),
    dict(kind='line', t0=4.6, t1=7.95, y=1340, w=380),
    # tails
    dict(kind='sub', text='ONE PAIR  ·  BOTH TAILS', t0=8.25, t1=9.95, y=1122),
    dict(kind='word', text='ROUNDTAIL', t0=8.4, t1=9.95, y=1300, size=160),
    # life stages
    dict(kind='sub', text='NEW: FULL GROWN', t0=10.25, t1=11.95, y=1122),
    dict(kind='word', text='5 LIFE STAGES', t0=10.4, t1=11.95, y=1300, size=130),
    # rivalry
    dict(kind='sub', text='THE BIGGEST SAIL RULES', t0=12.25, t1=15.95, y=1122),
    dict(kind='word', text='RIVALRY', t0=12.4, t1=15.95, y=1300, size=180, glow='rgba(255,120,90,.35)'),
    dict(kind='line', t0=12.6, t1=15.95, y=1340, w=340, color='rgba(255,170,150,.9)'),
    dict(kind='sub', text='TORN FINS', t0=14.3, t1=15.95, y=1420, color='#ff9a8a', size=40),
    # breathing
    dict(kind='sub', text='MOUTH  ·  GILLS  ·  PECTORALS', t0=16.25, t1=17.95, y=1122),
    dict(kind='word', text='THEY BREATHE', t0=16.4, t1=17.95, y=1300, size=140),
    # algae
    dict(kind='sub', text='THEY CLEAN THE GLASS', t0=18.25, t1=19.95, y=1122),
    dict(kind='word', text='ALGAE EATERS', t0=18.4, t1=19.95, y=1300, size=140),
    # oxygen
    dict(kind='sub', text='OVERCROWDED?', t0=20.25, t1=23.95, y=1122, color='#ff9a8a'),
    dict(kind='word', text='LOW OXYGEN', t0=20.4, t1=23.95, y=1300, size=150),
    dict(kind='sub', text='GASPING AT THE SURFACE', t0=20.7, t1=21.95, y=1400, size=38),
    dict(kind='sub', text='CORYS DASH UP FOR AIR', t0=22.1, t1=23.95, y=1400, size=38),
    # shimmy
    dict(kind='sub', text='CLAMPED FINS  ·  A SICK FISH', t0=24.25, t1=25.95, y=1122),
    dict(kind='word', text='SHIMMYING', t0=24.4, t1=25.95, y=1300, size=160),
    # the sail keeps growing / female choice
    dict(kind='sub', text='THE SAIL KEEPS GROWING', t0=26.25, t1=27.95, y=1122),
    dict(kind='word', text='FULL GROWN', t0=26.4, t1=27.95, y=1300, size=160),
    dict(kind='sub', text='SHE CHOOSES THE BEST SAIL', t0=28.25, t1=29.95, y=1122),
    dict(kind='word', text='FEMALE CHOICE', t0=28.4, t1=29.95, y=1300, size=130),
    # build: one word per cut
    dict(kind='word', text='COURT', t0=30.0, t1=30.5, y=1000, size=230, stagger=.012, dur=.16, exit=.08),
    dict(kind='word', text='FIGHT', t0=30.5, t1=31.0, y=1000, size=230, stagger=.012, dur=.16, exit=.08, glow='rgba(255,120,90,.35)'),
    dict(kind='word', text='GRAZE', t0=31.0, t1=31.5, y=1000, size=230, stagger=.012, dur=.16, exit=.08),
    dict(kind='word', text='GROW', t0=31.5, t1=32.0, y=1000, size=230, stagger=.012, dur=.16, exit=.08),
    # end card
    dict(kind='word', text='AFNICA', t0=32.7, t1=36.1, y=1205, size=118, font='%spx Georgia', track=34, stagger=.05, glow='rgba(120,220,255,.25)'),
    dict(kind='sub', text='AQUARIUM SIMULATOR', t0=33.0, t1=36.1, y=1290, size=40, font='%spx Goth', color='#e8f8ff', track0=10, track1=19),
    dict(kind='word', text='MORE TO FOLLOW', t0=33.8, t1=36.1, y=1500, size=76, track=8, stagger=.03),
    dict(kind='line', t0=34.0, t1=36.1, y=1538, w=420),
    dict(kind='sub', text='FOLLOW THE JOURNEY', t0=34.6, t1=36.1, y=1610, size=34),
]

TL = dict(
    shots=SHOTS, texts=TEXTS,
    logos=[dict(src='../logo/app_icon_1024.png', t0=32.15, t1=36.1, y=760, w=430, round=.22),
           dict(src='../logo/logo_aquarium_simulator.png', t0=36.1, t1=38.0, y=900, w=1040, splash=True, bg='#fefefe')],
    dim=[(32.1, 38, .5)],
    flashes=[(32.0, 1.0, .55), (36.1, 1.0, .45), (4.0, .16, .2), (12.0, .16, .2), (20.0, .16, .2),
             (30.0, .25, .15), (30.5, .25, .15), (31.0, .25, .15), (31.5, .25, .15)],
    fades=[(0.0, .3, 'in')],
    shake=[(32.0, 18), (14.0, 6), (30.0, 5), (30.5, 5), (31.0, 5), (31.5, 5)],
    leak=.7, rays=.8, bokeh=1, grade_k=1,
)

SFX = [[t, 'whoosh', .28] for t in (4.0, 12.0, 20.0)] + [[t, 'tick', .25] for t in (30.0, 30.5, 31.0, 31.5)] + [[36.1, 'impact', .35]]
