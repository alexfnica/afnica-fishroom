# AFNICA - "What's new: Guppy" species clip. Same structure as the other clips (120 BPM: bar = 2 s, 19 bars, drop on
# bar 16 = 32.0 s, splash at 36.1 s) but its own music: style B (upbeat marimba + pluck lead). Takes: takes_guppy.py.
# The S-display is shown once (4-6 s) plus one half-beat cut in the build.
DURATION = 38.0
MUSIC = dict(bars=19, drop=16, end=38.0, style='B')
OUTNAME = 'AFNICA_whats_new_guppy.mp4'

def S(t0, t1, take, tin='cut', td=0.0, zoom=(1.0, 1.06), punch=0.08, **kw):
    d = dict(t0=t0, t1=t1, take=take, tin=tin, td=td, zoom=list(zoom), punch=punch); d.update(kw); return d

SHOTS = [
    # HOOK: the lightning thrust, in slow motion
    S(0.0, 2.0, 'g_court', zoom=(1.18, 1.04), punch=0, anchor='thrust', anchorAt=1.0, ramp=[-.5, .5, .2], sfx=[('thrust', 'bubbles', .35)]),
    S(2.0, 4.0, 'g_hero', tin='whip', td=.36, zoom=(1.0, 1.08), at=1.0),
    S(4.0, 6.0, 'g_court', tin='zoom', td=.4, zoom=(1.0, 1.07), anchor='display', anchorAt=4.0),
    S(6.0, 8.0, 'g_court', tin='cut', punch=.1, zoom=(1.05, 1.12), anchor='thrust', anchorAt=7.5, sfx=[('thrust', 'bubbles', .3)]),
    S(8.0, 10.0, 'g_stages', tin='whip', td=.36, zoom=(1.35, 1.45), at=2.0),
    S(10.0, 12.0, 'g_breath', tin='zoom', td=.4, zoom=(1.0, 1.08), at=1.5),
    S(12.0, 14.0, 'g_fight', tin='whip', td=.36, dir=-1, zoom=(1.0, 1.08), at=1.0),
    S(14.0, 16.0, 'g_fight', tin='cut', punch=.12, zoom=(1.06, 1.12), at=5.0),
    S(16.0, 18.0, 'g_brood', tin='cross', td=.5, zoom=(1.0, 1.05), at=1.0),
    S(18.0, 20.0, 'g_hunt', tin='whip', td=.36, zoom=(1.12, 1.04), punch=0, anchor='strike', anchorAt=18.95, ramp=[-.4, .7, .25], sfx=[('strike', 'gulp', .55)]),
    S(20.0, 22.0, 'g_net', tin='zoom', td=.4, zoom=(1.0, 1.05), anchor='catch', anchorAt=21.25, sfx=[('catch', 'plop', .5), ('dodge', 'plop', .25)]),
    S(22.0, 24.0, 'g_oxygen', tin='cross', td=.5, zoom=(1.0, 1.05), at=1.5),
    S(24.0, 26.0, 'g_hero', tin='whip', td=.36, dir=-1, zoom=(1.1, 1.2), at=4.5),
    S(26.0, 28.0, 'g_hero', tin='zoom', td=.4, zoom=(1.0, 1.05), at=6.0),
    S(28.0, 30.0, 'g_fight', tin='whip', td=.36, zoom=(1.0, 1.06), at=7.4),
    # build: four half-beat cuts
    S(30.0, 30.5, 'g_court', punch=.14, zoom=(1.1, 1.16), anchor='display', anchorAt=29.6),
    S(30.5, 31.0, 'g_court', punch=.14, zoom=(1.1, 1.16), anchor='thrust', anchorAt=30.7),
    S(31.0, 31.5, 'g_hunt', punch=.14, zoom=(1.1, 1.16), anchor='strike', anchorAt=31.15),
    S(31.5, 32.0, 'g_hero', punch=.14, zoom=(1.1, 1.22), at=5.0),
    # drop: the guppy behind the app icon, then the splash screen
    S(32.0, 38.0, 'g_hero', punch=.18, zoom=(1.0, 1.12), at=2.0, blur=[32.9, 9]),
]

TEXTS = [
    # hook
    dict(kind='sub', text='FASTER THAN', t0=1.0, t1=1.97, y=1122, size=44, color='#ffd27a'),
    dict(kind='word', text='A BLINK', t0=1.1, t1=1.97, y=1290, size=170, stagger=.025, dur=.3, glow='rgba(255,210,110,.35)'),
    # title
    dict(kind='sub', text="WHAT'S NEW", t0=2.25, t1=3.95, y=1122, size=46),
    dict(kind='word', text='GUPPY', t0=2.4, t1=3.95, y=1290, size=190, stagger=.03, dur=.3),
    dict(kind='tag', text='GUPPY', latin='Poecilia reticulata', t0=2.4, t1=3.9),
    dict(kind='sub', text='BENDS  ·  SPREADS  ·  QUIVERS', t0=4.25, t1=5.95, y=1122, size=40),
    dict(kind='word', text='THE S-DANCE', t0=4.4, t1=5.95, y=1300, size=150),
    dict(kind='line', t0=4.6, t1=5.95, y=1340, w=380),
    dict(kind='sub', text='IN FROM BELOW', t0=6.25, t1=7.95, y=1122),
    dict(kind='word', text='THEN HE STRIKES', t0=6.4, t1=7.95, y=1300, size=96),
    dict(kind='sub', text='NEW: FULL GROWN', t0=8.25, t1=9.95, y=1122),
    dict(kind='word', text='5 LIFE STAGES', t0=8.4, t1=9.95, y=1300, size=130),
    dict(kind='sub', text='MOUTH  ·  GILLS  ·  PECTORALS', t0=10.25, t1=11.95, y=1122),
    dict(kind='word', text='THEY BREATHE', t0=10.4, t1=11.95, y=1300, size=140),
    dict(kind='sub', text='NO BITES, JUST FINS', t0=12.25, t1=15.95, y=1122),
    dict(kind='word', text='SHOW-OFF', t0=12.4, t1=15.95, y=1300, size=170, glow='rgba(255,210,110,.35)'),
    dict(kind='line', t0=12.6, t1=15.95, y=1340, w=340, color='rgba(255,215,130,.9)'),
    dict(kind='sub', text='UP TO 25 FRY', t0=16.25, t1=17.95, y=1122),
    dict(kind='word', text='LIVE BIRTH', t0=16.4, t1=17.95, y=1300, size=160),
    dict(kind='sub', text='THE ADULTS ARE HUNGRY', t0=18.25, t1=19.95, y=1122, color='#ff9a8a'),
    dict(kind='word', text='FRY HUNTERS', t0=18.4, t1=19.95, y=1300, size=140, glow='rgba(255,120,90,.35)'),
    dict(kind='sub', text='CATCH THEM FIRST', t0=20.25, t1=21.95, y=1122),
    dict(kind='word', text='SAVE THE FRY', t0=20.4, t1=21.95, y=1300, size=140),
    dict(kind='sub', text='OVERCROWDED?', t0=22.25, t1=23.95, y=1122, color='#ff9a8a'),
    dict(kind='word', text='LOW OXYGEN', t0=22.4, t1=23.95, y=1300, size=150),
    dict(kind='sub', text='THE TAIL KEEPS GROWING', t0=24.25, t1=25.95, y=1122),
    dict(kind='word', text='FULL GROWN', t0=24.4, t1=25.95, y=1300, size=160),
    dict(kind='sub', text='TIP', t0=26.25, t1=27.95, y=1122),
    dict(kind='word', text='MORE FEMALES', t0=26.4, t1=27.95, y=1250, size=120),
    dict(kind='sub', text='LESS STRESS', t0=26.6, t1=27.95, y=1380, size=56),
    dict(kind='sub', text='THE ALPHA CHASES', t0=28.25, t1=29.95, y=1122),
    dict(kind='word', text='ONE MALE RULES', t0=28.4, t1=29.95, y=1300, size=100, glow='rgba(255,210,110,.35)'),
    # build: one word per cut
    dict(kind='word', text='DANCE', t0=30.0, t1=30.5, y=1000, size=230, stagger=.012, dur=.16, exit=.08, glow='rgba(255,210,110,.35)'),
    dict(kind='word', text='STRIKE', t0=30.5, t1=31.0, y=1000, size=210, stagger=.012, dur=.16, exit=.08),
    dict(kind='word', text='HUNT', t0=31.0, t1=31.5, y=1000, size=230, stagger=.012, dur=.16, exit=.08, glow='rgba(255,120,90,.35)'),
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
    flashes=[(32.0, 1.0, .55), (36.1, 1.0, .45), (2.0, .16, .25), (4.0, .16, .2), (12.0, .16, .2), (18.0, .16, .2),
             (30.0, .25, .15), (30.5, .25, .15), (31.0, .25, .15), (31.5, .25, .15)],
    fades=[(0.0, .3, 'in')],
    shake=[(32.0, 18), (1.0, 8), (18.95, 6), (30.0, 5), (30.5, 5), (31.0, 5), (31.5, 5)],
    leak=.7, rays=.8, bokeh=1, grade_k=1,
)

SFX = [[t, 'whoosh', .28] for t in (2.0, 4.0, 12.0, 18.0)] + [[t, 'tick', .25] for t in (30.0, 30.5, 31.0, 31.5)] + [[36.1, 'impact', .35]]
