# AFNICA - corydoras mini-story "They EAT their own eggs", v2 (owner feedback on v1: transitions too fast; open on the
# splash screen, then "What we've been working on"; the nursery shows only eggs and day-1 larvae).
# 0-1.5 s splash (black logo on white, on from the first frame), 1.5-3.5 title, 3.5-34 the story in 2-3 s shots with
# soft cross-dissolves, then the usual app icon + splash end and a 3 s socials card. 120 BPM (bar = 2 s), music style B
# (upbeat marimba), one quiet bar, drop on bar 17 = 34.0 s. Takes: takes_cory.py.
import os, json
DURATION = 43.0
MUSIC = dict(bars=22, drop=17, end=43.0, style='B', intro=1)
OUTNAME = 'AFNICA_cory_story.mp4'
HERE = os.path.dirname(os.path.abspath(__file__))

def S(t0, t1, take, tin='cross', td=0.5, zoom=(1.0, 1.06), punch=0.0, **kw):
    d = dict(t0=t0, t1=t1, take=take, tin=tin, td=td, zoom=list(zoom), punch=punch); d.update(kw); return d

def surf_peak():
    """take time when the glass-surfing group is highest (the camera follows it up the glass)"""
    try:
        log = json.load(open(os.path.join(HERE, 'raw', 'c_surf', 'cam.json')))
        ys = [e['clip']['y'] + e['clip']['height'] / 2 for e in log]
        k = min(range(45, len(ys) - 45), key=lambda i: ys[i]); return k / 30
    except Exception: return 4.0

SHOTS = [
    # opening: under the splash and the title, a female carrying her eggs
    S(1.0, 3.5, 'c_hard', tin='cut', td=0, zoom=(1.0, 1.08), at=1.0),
    # the hook: she eats one of her own eggs (slow motion)
    S(3.5, 6.0, 'c_eat', zoom=(1.12, 1.02), anchor='eat', anchorAt=4.6, ramp=[-.4, 1.1, .5], sfx=[('eat', 'gulp', .55)]),
    # the spawning: glass surfing, the T, eggs on the glass, eggs on stone or wood
    S(6.0, 8.5, 'c_surf', at=max(0.0, surf_peak() - 1.2)),
    S(8.5, 11.0, 'c_ritual', zoom=(1.0, 1.08), anchor='T', anchorAt=8.0),
    S(11.0, 12.5, 'c_ritual', td=.4, zoom=(1.06, 1.12), anchor='lay', anchorAt=12.2),
    S(12.5, 13.5, 'c_hard', td=.4, zoom=(1.04, 1.1), anchor='lay', anchorAt=12.5),
    # the tension: a hungry fish comes for the clutch
    S(13.5, 16.5, 'c_hungry', zoom=(1.0, 1.14), at=4.5),
    # the solution: the breeding box on the tank rim, eggs and day-1 larvae on its grate
    S(16.5, 19.0, 'c_box', at=.3),
    S(19.0, 21.5, 'c_nursery', at=1.0),
    # the payoff: growth montage, one stage per bar
    S(21.5, 23.5, 'c_larva', td=.4, at=.8),
    S(23.5, 25.5, 'c_fry', td=.4, at=.8),
    S(25.5, 27.5, 'c_juv', td=.4, at=1.0),
    S(27.5, 29.5, 'c_adult', td=.4, at=1.0),
    S(29.5, 31.5, 'c_full', td=.4, at=1.0),
    S(31.5, 34.0, 'c_group', at=.3),
    # end, as in the other clips: a cory behind the app icon, then the splash screen
    S(34.0, 40.0, 'c_group', tin='cut', td=0, punch=.18, zoom=(1.0, 1.12), at=1.0, blur=[34.9, 9]),
]

def cap(text, t0, t1, **kw): d = dict(kind='cap', text=text, t0=t0, t1=t1); d.update(kw); return d
TEXTS = [
    dict(kind='sub', text='AFNICA  ·  CORYDORAS', t0=1.65, t1=3.45, y=1290, size=38),
    cap("What we've been working on", 1.6, 3.45, y=1400, size=96, hi=['working']),
    cap('They EAT their own eggs 😱', 3.6, 5.95, hi=['EAT']),
    cap('My corys are ready to spawn', 6.1, 8.45),
    cap('The T-position…', 8.6, 10.95, size=104),
    cap('She just laid 30 eggs…', 11.1, 13.45, hi=['30']),
    cap('…and the others are hungry', 13.6, 16.45, hi=['hungry']),
    cap('So I built them a nursery', 16.6, 18.95, hi=['nursery']),
    cap('My babies are safe now 🥚', 19.1, 21.45, hi=['safe']),
    cap('Day 1', 21.6, 23.45, y=1250, size=130, hi=['1']),
    cap('Day 4', 23.6, 25.45, y=1250, size=130, hi=['4']),
    cap('Day 9', 25.6, 27.45, y=1250, size=130, hi=['9']),
    cap('Day 20', 27.6, 29.45, y=1250, size=130, hi=['20']),
    cap('Day 40', 29.6, 31.45, y=1250, size=130, hi=['40']),
    cap('Follow to see them grow up', 31.6, 33.95, hi=['Follow']),
    # end card (unchanged from the other clips, at the drop)
    dict(kind='word', text='AFNICA', t0=34.7, t1=38.1, y=1205, size=118, font='%spx Georgia', track=34, stagger=.05, glow='rgba(120,220,255,.25)'),
    dict(kind='sub', text='AQUARIUM SIMULATOR', t0=35.0, t1=38.1, y=1290, size=40, font='%spx Goth', color='#e8f8ff', track0=10, track1=19),
    dict(kind='word', text='MORE TO FOLLOW', t0=35.8, t1=38.1, y=1500, size=76, track=8, stagger=.03),
    dict(kind='line', t0=36.0, t1=38.1, y=1538, w=420),
    dict(kind='sub', text='FOLLOW THE JOURNEY', t0=36.6, t1=38.1, y=1610, size=34),
]

SPLASH = dict(src='../logo/logo_aquarium_simulator.png', y=900, w=1040, splash=True, bg='#fefefe')
TL = dict(
    shots=SHOTS, texts=TEXTS,
    logos=[dict(SPLASH, t0=0.0, t1=1.5, fin=0, fout=.5),                       # opening: on from the very first frame
           dict(src='../logo/app_icon_1024.png', t0=34.15, t1=38.1, y=760, w=430, round=.22),
           dict(SPLASH, t0=38.1, t1=40.0)],
    socials=dict(t0=40.0, t1=43.0, icon='../logo/app_icon_1024.png', title='FOLLOW AFNICA', sub='Aquarium Simulator',
                 items=[dict(net='tiktok', label='TikTok', handle='@afnicaaquariumsim'),
                        dict(net='instagram', label='Instagram', handle='@afnica_aquarium_simulator'),
                        dict(net='facebook', label='Facebook', handle='AFNICA - Aquarium Simulator')]),
    dim=[(34.1, 40, .5)],
    flashes=[(34.0, 1.0, .55), (38.1, 1.0, .45), (40.0, .5, .3)],
    shake=[(34.0, 18)],
    leak=.6, rays=.6, bokeh=.8, grade_k=.9,
)

SFX = [[3.5, 'whoosh', .22]] + [[t, 'tick', .2] for t in (23.5, 25.5, 27.5, 29.5)] + [[38.1, 'impact', .35]]
