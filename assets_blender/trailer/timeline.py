# AFNICA - Aquarium Simulator: 38 s vertical trailer v2, cut on the beat of music A (120 BPM: beat 0.5 s, bar 2 s).
# Music: 19 bars. Bars 0-1 intro, 2-14 groove, 15 build (riser + four quick cuts), drop on bar 16 (32.0 s), splash at 36 s.
# Shots are placed on EVENTS of the takes (compose.py reads them from the phase logs): anchor=<event>, anchorAt=<output s>.
# ramp=[a0, a1, k]: slow motion to speed k from a0 to a1 seconds (source time) around the anchor (120 fps takes).
# at=<s>: plain start time in the take. sfx=[(event, kind, gain)]: sound effects placed where that event shows up.
DURATION = 38.0
MUSIC = dict(bars=19, drop=16, end=38.0)

def S(t0, t1, take, tin='cut', td=0.0, zoom=(1.0, 1.06), punch=0.08, **kw):
    d = dict(t0=t0, t1=t1, take=take, tin=tin, td=td, zoom=list(zoom), punch=punch); d.update(kw); return d

SHOTS = [
    # HOOK: a swordtail female snaps up a newborn fry, in slow motion
    S(0.0, 2.0, 'hunt', zoom=(1.18, 1.04), punch=0, anchor='strike', anchorAt=.95, ramp=[-.4, .7, .25], sfx=[('strike', 'gulp', .55)]),
    S(2.0, 4.0, 'neon', tin='whip', td=.36, zoom=(1.0, 1.08), at=2.0, focus=[10, .6]),
    # BREED: the swordtail dance, then the guppy's lightning thrust in slow motion
    S(4.0, 6.0, 'xipho_court', tin='zoom', td=.4, zoom=(1.0, 1.07), anchor='display', anchorAt=4.2),
    S(6.0, 8.0, 'guppy_court', tin='cut', punch=.1, zoom=(1.04, 1.12), anchor='thrust', anchorAt=7.0, ramp=[-.6, .35, .3], sfx=[('thrust', 'bubbles', .3)]),
    S(8.0, 10.0, 'fry', tin='zoom', td=.4, zoom=(1.0, 1.1), at=2.0, focus=[16, .9]),
    S(10.0, 12.0, 'net', tin='whip', td=.36, dir=-1, zoom=(1.0, 1.05), anchor='catch', anchorAt=11.25, sfx=[('catch', 'plop', .5), ('dodge', 'plop', .25)]),
    S(12.0, 14.0, 'hunt2', tin='cut', punch=.12, zoom=(1.05, 1.12), anchor='strike', anchorAt=13.0, ramp=[-.3, .5, .3], sfx=[('strike', 'gulp', .5)]),
    S(14.0, 16.0, 'fight', tin='zoom', td=.4, zoom=(1.0, 1.08), anchor='nip', anchorAt=15.0, ramp=[-.15, .45, .35], sfx=[('nips', 'thud', .55)]),
    S(16.0, 18.0, 'fight', tin='cut', punch=.12, zoom=(1.06, 1.12), anchor='nip2', anchorAt=16.6, ramp=[-.15, .4, .4], sfx=[('nips', 'thud', .55)]),
    S(18.0, 20.0, 'feed', tin='whip', td=.36, zoom=(1.0, 1.06), anchor='feed', anchorAt=18.35, sfx=[('feed', 'plop', .35)]),
    S(20.0, 22.0, 'anc_fan', tin='whip', td=.36, dir=-1, zoom=(1.0, 1.06), at=1.0, focus=[12, .8]),
    S(22.0, 24.0, 'anc_glass', tin='cross', td=.5, zoom=(1.0, 1.05), at=1.0),
    S(24.0, 26.0, 'beauty', tin='zoom', td=.4, zoom=(1.0, 1.06), at=1.0, focus=[10, .6]),
    S(26.0, 28.0, 'hero', tin='whip', td=.36, zoom=(1.3, 1.0), at=2.0),
    S(28.0, 30.0, 'ui', tin='zoom', td=.4, zoom=(1.0, 1.04), at=1.0, ui=True),
    # build: four half-beat cuts
    S(30.0, 30.5, 'xipho_court', punch=.14, zoom=(1.1, 1.16), anchor='display', anchorAt=30.0),
    S(30.5, 31.0, 'neon', punch=.14, zoom=(1.1, 1.16), at=5.0),
    S(31.0, 31.5, 'fight', punch=.14, zoom=(1.1, 1.16), anchor='nip2', anchorAt=31.15),
    S(31.5, 32.0, 'beauty', punch=.14, zoom=(1.1, 1.22), at=4.5),
    # drop: the hero tank behind the app icon, then the splash screen
    S(32.0, 38.0, 'hero', punch=.18, zoom=(1.0, 1.12), at=1.0, blur=[32.9, 9]),
]

TEXTS = [
    # documentary species labels (names as in the game's species table)
    dict(kind='tag', text='NEON TETRA', latin='Paracheirodon innesi', t0=2.35, t1=3.95),
    dict(kind='tag', text='SWORDTAIL', latin='Xiphophorus hellerii', t0=4.3, t1=5.95),
    dict(kind='tag', text='RED TUXEDO GUPPY', latin='Poecilia reticulata', t0=6.1, t1=7.9),
    dict(kind='tag', text='BRISTLENOSE PLECO', latin='Ancistrus sp.', t0=20.3, t1=23.9),
    # hook
    dict(kind='sub', text='EVERY FISH', t0=1.05, t1=1.97, y=1122, size=40),
    dict(kind='word', text='IS ALIVE', t0=1.15, t1=1.97, y=1290, size=150, stagger=.025, dur=.3),
    # sections: one big word each, a line under the few that need context
    dict(kind='word', text='BREED', t0=4.4, t1=7.95, y=1300, size=190),
    dict(kind='line', t0=4.6, t1=7.95, y=1340, w=330),
    dict(kind='sub', text='LIVE BIRTH  ·  4 LIFE STAGES', t0=8.25, t1=9.95, y=1122),
    dict(kind='word', text='NEW LIFE', t0=8.4, t1=9.95, y=1300, size=170),
    dict(kind='word', text='RAISE', t0=10.4, t1=11.95, y=1300, size=190),
    dict(kind='sub', text='OR THEY GET EATEN', t0=12.3, t1=13.95, y=1240, color='#ff9a8a', size=46),
    dict(kind='sub', text='FOR THE ALPHA', t0=14.25, t1=17.95, y=1122),
    dict(kind='word', text='FIGHT', t0=14.4, t1=17.95, y=1300, size=200, glow='rgba(255,120,90,.35)'),
    dict(kind='line', t0=14.6, t1=17.95, y=1340, w=330, color='rgba(255,170,150,.9)'),
    dict(kind='word', text='CARE', t0=18.4, t1=19.95, y=1300, size=190),
    dict(kind='sub', text='GUARDING THE EGGS', t0=20.4, t1=21.95, y=1240, size=42),
    dict(kind='word', text='7 SPECIES', t0=22.4, t1=23.95, y=1300, size=160),
    dict(kind='sub', text='BREED THE BEST BLOODLINES', t0=24.25, t1=25.95, y=1122),
    dict(kind='word', text='SELL', t0=24.4, t1=25.95, y=1300, size=200, glow='rgba(255,210,110,.35)'),
    dict(kind='line', t0=24.6, t1=25.95, y=1340, w=300, color='rgba(255,215,130,.9)'),
    dict(kind='word', text='UPGRADE', t0=26.25, t1=27.95, y=1300, size=180),
    dict(kind='sub', text='YOUR SYSTEM', t0=26.4, t1=27.95, y=1395),
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
    flashes=[(32.0, 1.0, .55), (36.1, 1.0, .45), (8.0, .16, .2), (14.0, .16, .2), (24.0, .16, .2),
             (30.0, .25, .15), (30.5, .25, .15), (31.0, .25, .15), (31.5, .25, .15)],
    fades=[(0.0, .3, 'in')],
    shake=[(32.0, 18), (16.0, 6), (30.0, 5), (30.5, 5), (31.0, 5), (31.5, 5)],
    leak=.7, rays=.8, bokeh=1, grade_k=1,
)

# base sound design (the event sounds - gulps, thuds, plops - are added by compose.py from the takes)
# only the three big section changes get a (soft) whoosh
SFX = [[t, 'whoosh', .28] for t in (4.0, 14.0, 24.0)] + [[t, 'tick', .25] for t in (30.0, 30.5, 31.0, 31.5)] + [[36.1, 'impact', .35]]
