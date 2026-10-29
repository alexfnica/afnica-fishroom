# V17.111 living still: in the yolk-stage popup the canvas twitches larva tails. Measures changed pixels per frame vs the first frame
# (static parts must not change except dust / beam), counts bursts, saves the frame with the most change + the first frame (docs/living111_*.jpg).
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
PRE = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};"
c = anc_game(tank='breeder', fish="[T.fish('anc','M',40),T.fish('anc','F',40)]", warm=2, pre=PRE)
KEY = os.environ.get('KEY', 'full'); HD = {'full': -1, 'half': -3, 'low': -5}[KEY]; RD = {'full': 4, 'half': 2, 'low': 1}[KEY]
try:
    c.js("""(()=>{const m=st.breederTank[0],f=st.breederTank[1];st.ancClutch={id:'cl1',stage:'yolk',count:26,laidDay:st.day-6,hatchDay:st.day+(%d),releaseDay:st.day+(%d),lastDay:st.day,parents:{mom:f,dad:m}};inspectAncCave40();window.__cv=document.querySelector('.anc111box canvas');window.__d=[];window.__best=null;window.__bd=-1;window.__f0=null;return 1})()""" % (HD, RD))
    for i in range(30 * 14):
        c.js('__afStep(%f, 2)' % (1000 / 30))
        if i % 3 == 0:
            c.js("""(()=>{const g=__cv.getContext('2d'),D=g.getImageData(0,0,__cv.width,__cv.height).data;if(!__f0){__f0=D.slice();__first=__cv.toDataURL('image/jpeg',.9)}let n=0;for(let p=0;p<D.length;p+=16){if(Math.abs(D[p]-__f0[p])+Math.abs(D[p+1]-__f0[p+1])>40)n++}__d.push(n);if(n>__bd){__bd=n;__best=__cv.toDataURL('image/jpeg',.92)}return 1})()""")
    d = json.loads(c.js("JSON.stringify(__d)"))
    print(KEY, 'canvas', c.js("JSON.stringify([__cv.width,__cv.height,__cv.isConnected])"), 'changed samples per frame: min %d max %d mean %.0f, frames with >0 extra: %d/%d' % (min(d), max(d), sum(d) / len(d), sum(1 for v in d if v > min(d) + 60), len(d)), 'errors', c.js('JSON.stringify(window.__err)'))
    for nm, js in (('first', '__first'), ('burst', '__best')):
        u = c.js(js); open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'living111_%s_%s.jpg' % (KEY, nm)), 'wb').write(base64.b64decode(u.split(',')[1]))
finally:
    c.close()
