# AFNICA - corydoras mini-story "They EAT their own eggs" (new format: a 22 s story, loop-friendly, big first-person
# captions, then the usual app icon + splash end and a socials card). 120 BPM (bar = 2 s), music style B (upbeat
# marimba) with drums from the first beat, drop on bar 11 = 22.0 s. Takes: takes_cory.py.
import os, json
DURATION = 31.0
MUSIC = dict(bars=16, drop=11, end=31.0, style='B', intro=0)
OUTNAME = 'AFNICA_cory_story.mp4'
HERE = os.path.dirname(os.path.abspath(__file__))

def S(t0, t1, take, tin='cut', td=0.0, zoom=(1.0, 1.06), punch=0.08, **kw):
    d = dict(t0=t0, t1=t1, take=take, tin=tin, td=td, zoom=list(zoom), punch=punch); d.update(kw); return d

def surf_peak():
    """take time when the glass-surfing group is highest (the camera follows it up the glass)"""
    try:
        log = json.load(open(os.path.join(HERE, 'raw', 'c_surf', 'cam.json')))
        ys = [e['clip']['y'] + e['clip']['height'] / 2 for e in log]
        k = min(range(30, len(ys) - 30), key=lambda i: ys[i]); return max(0.0, k / 30 - .5)
    except Exception: return 3.0

SHOTS = [
    # 1 HOOK (0-2): she eats one of her own eggs, slow motion, the caption is on the very first frame (thumbnail)
    S(0.0, 2.0, 'c_eat', zoom=(1.14, 1.04), punch=0, anchor='eat', anchorAt=.8, ramp=[-.3, .9, .45], sfx=[('eat', 'gulp', .55)]),
    # 2 the spawning (2-6): glass surfing, the T, eggs on the glass, eggs on stone/wood
    S(2.0, 3.0, 'c_surf', tin='whip', td=.3, zoom=(1.0, 1.08), at=surf_peak()),
    S(3.0, 4.5, 'c_ritual', tin='cut', punch=.1, zoom=(1.04, 1.12), anchor='T', anchorAt=2.0),
    S(4.5, 5.5, 'c_ritual', tin='cut', punch=.1, zoom=(1.1, 1.18), anchor='lay', anchorAt=3.6),
    S(5.5, 6.0, 'c_hard', tin='cut', punch=.12, zoom=(1.08, 1.14), anchor='lay', anchorAt=5.4),
    # 3 tension (6-9): a hungry fish comes for the clutch
    S(6.0, 7.5, 'c_hungry', tin='whip', td=.3, dir=-1, zoom=(1.0, 1.06), at=3.0),
    S(7.5, 9.0, 'c_hungry', tin='cut', punch=.12, zoom=(1.18, 1.32), at=7.2),
    # 4 the solution (9-14): the breeding box on the tank rim, eggs and babies safe inside
    S(9.0, 11.0, 'c_box', tin='zoom', td=.4, zoom=(1.0, 1.04), at=.5, sfx=[]),
    S(11.0, 12.5, 'c_nursery', tin='cut', punch=.08, zoom=(1.0, 1.08), at=1.0),
    S(12.5, 14.0, 'c_larva', tin='cut', punch=.08, zoom=(1.0, 1.1), at=.4),
    # 5 payoff (14-20): growth montage, one stage per beat
    S(14.0, 15.5, 'c_fry', tin='whip', td=.3, zoom=(1.0, 1.08), at=.5),
    S(15.5, 17.0, 'c_juv', tin='cut', punch=.14, zoom=(1.0, 1.08), at=1.0),
    S(17.0, 18.5, 'c_adult', tin='cut', punch=.14, zoom=(1.0, 1.08), at=1.0),
    S(18.5, 20.0, 'c_full', tin='cut', punch=.14, zoom=(1.0, 1.08), at=1.0),
    # 6 lead-out (20-22): the full-grown group on the sand
    S(20.0, 22.0, 'c_group', tin='cross', td=.4, zoom=(1.0, 1.06), at=.5),
    # 7 end, as in the other clips: a cory behind the app icon, then the splash screen
    S(22.0, 28.0, 'c_group', punch=.18, zoom=(1.0, 1.12), at=2.5, blur=[22.9, 9]),
]

def cap(text, t0, t1, **kw): d = dict(kind='cap', text=text, t0=t0, t1=t1); d.update(kw); return d
TEXTS = [
    cap('They EAT their own eggs 😱', 0.0, 1.97, hi=['EAT'], instant=True, size=96),
    cap('My corys are ready to spawn', 2.05, 2.97),
    cap('The T-position…', 3.05, 4.47, size=104),
    cap('She just laid 30 eggs…', 4.55, 5.97, hi=['30']),
    cap('…and the others are hungry', 6.05, 8.97, hi=['hungry']),
    cap('So I built them a nursery', 9.1, 10.97, hi=['nursery']),
    cap('My babies are safe now 🥚', 11.05, 12.47, hi=['safe']),
    cap('Day 1', 12.55, 13.97, y=1250, size=130, hi=['1']),
    cap('Day 4', 14.05, 15.47, y=1250, size=130, hi=['4']),
    cap('Day 9', 15.55, 16.97, y=1250, size=130, hi=['9']),
    cap('Day 20', 17.05, 18.47, y=1250, size=130, hi=['20']),
    cap('Day 40', 18.55, 19.97, y=1250, size=130, hi=['40']),
    cap('Follow to see them grow up', 20.05, 21.97, hi=['Follow']),
    # end card (unchanged from the other clips, shifted to the drop at 22 s)
    dict(kind='word', text='AFNICA', t0=22.7, t1=26.1, y=1205, size=118, font='%spx Georgia', track=34, stagger=.05, glow='rgba(120,220,255,.25)'),
    dict(kind='sub', text='AQUARIUM SIMULATOR', t0=23.0, t1=26.1, y=1290, size=40, font='%spx Goth', color='#e8f8ff', track0=10, track1=19),
    dict(kind='word', text='MORE TO FOLLOW', t0=23.8, t1=26.1, y=1500, size=76, track=8, stagger=.03),
    dict(kind='line', t0=24.0, t1=26.1, y=1538, w=420),
    dict(kind='sub', text='FOLLOW THE JOURNEY', t0=24.6, t1=26.1, y=1610, size=34),
]

TL = dict(
    shots=SHOTS, texts=TEXTS,
    logos=[dict(src='../logo/app_icon_1024.png', t0=22.15, t1=26.1, y=760, w=430, round=.22),
           dict(src='../logo/logo_aquarium_simulator.png', t0=26.1, t1=28.0, y=900, w=1040, splash=True, bg='#fefefe')],
    socials=dict(t0=28.0, t1=31.0, icon='../logo/app_icon_1024.png', title='FOLLOW AFNICA', sub='Aquarium Simulator',
                 items=[dict(net='tiktok', label='TikTok', handle='@afnicaaquariumsim'),
                        dict(net='instagram', label='Instagram', handle='@afnica_aquarium_simulator'),
                        dict(net='facebook', label='Facebook', handle='AFNICA - Aquarium Simulator')]),
    dim=[(22.1, 28, .5)],
    flashes=[(22.0, 1.0, .55), (26.1, 1.0, .45), (28.0, .5, .3), (2.0, .16, .2), (6.0, .16, .2), (9.0, .2, .25), (14.0, .16, .2),
             (15.5, .2, .15), (17.0, .2, .15), (18.5, .2, .15)],
    shake=[(22.0, 18), (0.8, 7), (3.0, 4), (15.5, 4), (17.0, 4), (18.5, 4)],
    leak=.6, rays=.6, bokeh=.8, grade_k=.9,
)

SFX = [[t, 'whoosh', .28] for t in (2.0, 6.0, 9.0, 14.0)] + [[t, 'tick', .25] for t in (15.5, 17.0, 18.5)] + [[26.1, 'impact', .35]]
