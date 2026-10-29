# V17.111: cave inspect popup shows the footage (interim poster) in the yolk stage; eggs keep the V17.43 canvas. Writes docs/inspect111.jpg
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from anc_rig import *
PRE = "window.__err=[];const _ce=console.error;console.error=function(){window.__err.push([...arguments].map(String).join(' ').slice(0,200));_ce.apply(console,arguments)};"
c = anc_game(tank='breeder', fish="[T.fish('anc','M',40),T.fish('anc','F',40)]", warm=2, pre=PRE)
try:
    for stage, hd, rd in (('yolk', -1, 4), ('yolk', -3, 2), ('yolk', -5, 1)):
        c.js("""(()=>{const m=st.breederTank[0],f=st.breederTank[1];st.ancClutch={id:'cl1',stage:'%s',count:26,laidDay:st.day-6,hatchDay:st.day+(%d),releaseDay:st.day+(%d),lastDay:st.day,parents:{mom:f,dad:m}};inspectAncCave40();return 1})()""" % (stage, hd, rd))
        for i in range(30): c.js('__afStep(%f, 2)' % (1000 / 30))
        print(stage, hd, rd, c.js("JSON.stringify({box:!!document.querySelector('.anc111box'),img:!!document.querySelector('.anc111box img'),canvas:!!document.getElementById('ancInspect43'),w:(document.querySelector('.anc111box')||{}).offsetWidth})"))
    c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'inspect111.jpg'), q=88)
    print('errors', c.js('JSON.stringify(window.__err)'))
finally:
    c.close()
