# AFNICA - "What's new: Platy" species clip. Same music and structure as the trailer and the molly clip (music A,
# 120 BPM: bar = 2 s, 19 bars, drop on bar 16 = 32.0 s, splash at 36.1 s). Shots use the platy takes (takes_platy.py).
DURATION = 38.0
MUSIC = dict(bars=19, drop=16, end=38.0)
OUTNAME = 'AFNICA_whats_new_platy.mp4'

def S(t0, t1, take, tin='cut', td=0.0, zoom=(1.0, 1.06), punch=0.08, **kw):
    d = dict(t0=t0, t1=t1, take=take, tin=tin, td=td, zoom=list(zoom), punch=punch); d.update(kw); return d

SHOTS = [
    # HOOK: an adult snaps up a newborn fry, in slow motion
    S(0.0, 2.0, 'p_hunt', zoom=(1.18, 1.04), punch=0, anchor='strike', anchorAt=.95, ramp=[-.4, .7, .25], sfx=[('strike', 'gulp', .55)]),
    S(2.0, 4.0, 'p_hero', tin='whip', td=.36, zoom=(1.0, 1.08), at=1.0),
    S(4.0, 6.0, 'p_net', tin='zoom', td=.4, zoom=(1.0, 1.05), anchor='catch', anchorAt=5.25, sfx=[('catch', 'plop', .5), ('dodge', 'plop', .25)]),
    S(6.0, 8.0, 'p_brood', tin='cross', td=.5, zoom=(1.0, 1.05), at=1.0),
    S(8.0, 10.0, 'p_court', tin='zoom', td=.4, zoom=(1.0, 1.07), anchor='display', anchorAt=8.3),
    S(10.0, 12.0, 'p_court', tin='cut', punch=.1, zoom=(1.04, 1.12), anchor='thrust', anchorAt=11.0, ramp=[-.6, .35, .3], sfx=[('thrust', 'bubbles', .3)]),
    S(12.0, 14.0, 'p_stages', tin='whip', td=.36, zoom=(1.35, 1.45), at=2.0),
    S(14.0, 16.0, 'p_fight', tin='zoom', td=.4, zoom=(1.0, 1.08), anchor='nip', anchorAt=15.0, ramp=[-.15, .45, .4], sfx=[('nips', 'thud', .55)]),
    S(16.0, 18.0, 'p_fight', tin='cut', punch=.12, zoom=(1.06, 1.12), at=7.2),
    S(18.0, 20.0, 'p_breath', tin='zoom', td=.4, zoom=(1.0, 1.08), at=1.5),
    S(20.0, 22.0, 'p_oxygen', tin='cross', td=.5, zoom=(1.0, 1.05), at=1.5),
    S(22.0, 24.0, 'p_hunt', tin='whip', td=.36, zoom=(1.05, 1.12), anchor='strike', anchorAt=22.6, ramp=[-.3, .5, .35], sfx=[('strike', 'gulp', .45)]),
    S(24.0, 26.0, 'p_court', tin='zoom', td=.4, zoom=(1.05, 1.12), anchor='display', anchorAt=22.4),
    S(26.0, 28.0, 'p_hero', tin='whip', td=.36, dir=-1, zoom=(1.1, 1.2), at=4.5),
    S(28.0, 30.0, 'p_brood', tin='cross', td=.5, zoom=(1.1, 1.18), at=4.5),
    # build: four half-beat cuts
    S(30.0, 30.5, 'p_hunt', punch=.14, zoom=(1.1, 1.16), anchor='strike', anchorAt=30.15),
    S(30.5, 31.0, 'p_court', punch=.14, zoom=(1.1, 1.16), anchor='display', anchorAt=30.4),
    S(31.0, 31.5, 'p_fight', punch=.14, zoom=(1.1, 1.16), anchor='nip', anchorAt=31.15),
    S(31.5, 32.0, 'p_hero', punch=.14, zoom=(1.1, 1.22), at=5.0),
    # drop: the platy behind the app icon, then the splash screen
    S(32.0, 38.0, 'p_hero', punch=.18, zoom=(1.0, 1.12), at=2.0, blur=[32.9, 9]),
]

TEXTS = [
    # hook
    dict(kind='sub', text='THEY EAT', t0=1.0, t1=1.97, y=1122, size=44, color='#ff9a8a'),
    dict(kind='word', text='THEIR OWN BABIES', t0=1.1, t1=1.97, y=1290, size=120, stagger=.025, dur=.3, glow='rgba(255,120,90,.35)'),
    # title
    dict(kind='sub', text="WHAT'S NEW", t0=2.25, t1=3.95, y=1122, size=46),
    dict(kind='word', text='PLATY', t0=2.4, t1=3.95, y=1290, size=190, stagger=.03, dur=.3),
    dict(kind='tag', text='PLATY', latin='Xiphophorus maculatus', t0=2.4, t1=3.9),
    dict(kind='sub', text='CATCH THEM FIRST', t0=4.25, t1=5.95, y=1122),
    dict(kind='word', text='SAVE THE FRY', t0=4.4, t1=5.95, y=1300, size=140),
    dict(kind='sub', text='UP TO 35 FRY', t0=6.25, t1=7.95, y=1122),
    dict(kind='word', text='LIVE BIRTH', t0=6.4, t1=7.95, y=1300, size=160),
    dict(kind='sub', text='A QUIVER BESIDE HER', t0=8.25, t1=11.95, y=1122),
    dict(kind='word', text='COURTSHIP', t0=8.4, t1=11.95, y=1300, size=160),
    dict(kind='line', t0=8.6, t1=11.95, y=1340, w=380),
    dict(kind='sub', text='NEW: FULL GROWN', t0=12.25, t1=13.95, y=1122),
    dict(kind='word', text='5 LIFE STAGES', t0=12.4, t1=13.95, y=1300, size=130),
    dict(kind='sub', text='THE BIGGEST FIN RULES', t0=14.25, t1=17.95, y=1122),
    dict(kind='word', text='RIVALRY', t0=14.4, t1=17.95, y=1300, size=180, glow='rgba(255,120,90,.35)'),
    dict(kind='line', t0=14.6, t1=17.95, y=1340, w=340, color='rgba(255,170,150,.9)'),
    dict(kind='sub', text='MOUTH  ·  GILLS  ·  PECTORALS', t0=18.25, t1=19.95, y=1122),
    dict(kind='word', text='THEY BREATHE', t0=18.4, t1=19.95, y=1300, size=140),
    dict(kind='sub', text='OVERCROWDED?', t0=20.25, t1=21.95, y=1122, color='#ff9a8a'),
    dict(kind='word', text='LOW OXYGEN', t0=20.4, t1=21.95, y=1300, size=150),
    dict(kind='sub', text='A HUNGRY TANK', t0=22.25, t1=23.95, y=1122, color='#ff9a8a'),
    dict(kind='word', text='HUNTS MORE', t0=22.4, t1=23.95, y=1300, size=160, glow='rgba(255,120,90,.35)'),
    dict(kind='sub', text='NIBBLES UNDER HER BELLY', t0=24.25, t1=25.95, y=1122),
    dict(kind='word', text='PERSUASION', t0=24.4, t1=25.95, y=1300, size=140),
    dict(kind='sub', text='THE FIN KEEPS GROWING', t0=26.25, t1=27.95, y=1122),
    dict(kind='word', text='FULL GROWN', t0=26.4, t1=27.95, y=1300, size=160),
    dict(kind='sub', text='TIP', t0=28.25, t1=29.95, y=1122),
    dict(kind='word', text='PLANTS SAVE FRY', t0=28.4, t1=29.95, y=1300, size=120),
    # build: one word per cut
    dict(kind='word', text='HUNT', t0=30.0, t1=30.5, y=1000, size=230, stagger=.012, dur=.16, exit=.08, glow='rgba(255,120,90,.35)'),
    dict(kind='word', text='COURT', t0=30.5, t1=31.0, y=1000, size=230, stagger=.012, dur=.16, exit=.08),
    dict(kind='word', text='FIGHT', t0=31.0, t1=31.5, y=1000, size=230, stagger=.012, dur=.16, exit=.08, glow='rgba(255,120,90,.35)'),
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
    flashes=[(32.0, 1.0, .55), (36.1, 1.0, .45), (2.0, .16, .25), (8.0, .16, .2), (14.0, .16, .2), (20.0, .16, .2),
             (30.0, .25, .15), (30.5, .25, .15), (31.0, .25, .15), (31.5, .25, .15)],
    fades=[(0.0, .3, 'in')],
    shake=[(32.0, 18), (.95, 8), (15.0, 6), (30.0, 5), (30.5, 5), (31.0, 5), (31.5, 5)],
    leak=.7, rays=.8, bokeh=1, grade_k=1,
)

SFX = [[t, 'whoosh', .28] for t in (2.0, 8.0, 14.0, 20.0)] + [[t, 'tick', .25] for t in (30.0, 30.5, 31.0, 31.5)] + [[36.1, 'impact', .35]]
