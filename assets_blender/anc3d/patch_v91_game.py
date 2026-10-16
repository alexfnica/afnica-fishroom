# V17.91 hooks in the old drawing code (V17.42 fin canvas + anc main loop). One-off, exact snippets, each must match once.
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:90]; s = s.replace(a, b)
# 1 dorsal fold: a global like BEND, read in draw()'s dorsal loop (0 = raised as in the photo, 1 = folded back flat)
rep("let BEND=0,SIG=0,SFL=0,SWRG=null;", "let BEND=0,SIG=0,SFL=0,SWRG=null,DFOLD=0;   /* DFOLD (V17.91): bristlenose dorsal folded back 0..1 */")
rep("""    const hh=Math.min(2,B-y),dx=sh*Math.pow(Math.min(1,(B-y)/tipH),1.6)*Math.sin(wp(uM)-.9);
    g.drawImage(base,ax,y,aw,hh,ax+dx,pad+dyb+y,aw,hh);""",
    """    const hh=Math.min(2,B-y),dx=sh*Math.pow(Math.min(1,(B-y)/tipH),1.6)*Math.sin(wp(uM)-.9);
    if(DFOLD>.001){const q=1-.74*DFOLD,yy=B-(B-y)*q;g.drawImage(base,ax,y,aw,hh,ax+dx-DFOLD*(B-y)*.85,pad+dyb+yy,aw,hh*q+.7);continue;}   /* V17.91: folded back along the body */
    g.drawImage(base,ax,y,aw,hh,ax+dx,pad+dyb+y,aw,hh);""")
# 2 the anc call: per-fish inputs from V17.91 (nose down, tail sway, dorsal, bristles, extra beat)
rep("""     const tent=c.dataset.wk==='anc|0|38'?r.W/170*s.tm:0;                             // males only; up to ~0.7 screen px""",
    """     const X91=window.ancCanvasV1791?ancCanvasV1791(s,dt,sp,move,fan):null;if(X91&&X91.ph)s.ph+=X91.ph*dt;   /* V17.91 */
     const tent=c.dataset.wk==='anc|0|38'?r.W/170*Math.max(s.tm,X91?X91.tentMin:0):0;                             // males only; up to ~0.7 screen px""")
rep("""      else{c.dataset.gl89='0';draw(c,r,s.ph,amp,1-sp,fan?.8:move,0,tent,s.tt,fan?0:Math.min(1,s.rs),+s.fe.dataset.belly||0);""",
    """      else{c.dataset.gl89='0';DFOLD=X91?X91.fold:0;draw(c,r,s.ph,amp*(X91?X91.amp:1),1-sp,X91?X91.dors:(fan?.8:move),X91?X91.nose:0,tent,s.tt,X91?X91.sway:(fan?0:Math.min(1,s.rs)),+s.fe.dataset.belly||0);DFOLD=0;""")
# 3 breathing: slower at rest (a pleco ~50/min), the low gill slit clearly visible (vis)
rep("anc:{k:.24,r:60,m:0,low:1}};", "anc:{k:.24,r:50,m:0,low:1,vis:2.2}};")
rep("""rx=BL*.01+BL*.004*gi,ry=Math.max(1.2,h*.08);""", """rx=(BL*.01+BL*.004*gi)*(P.vis||1),ry=Math.max(1.2,h*.08)*(P.vis?1.3:1);""")
rep("""g.strokeStyle='rgba(4,6,8,'+(.28*gi).toFixed(3)+')';""", """g.strokeStyle='rgba(4,6,8,'+Math.min(.75,.28*gi*(P.vis||1)).toFixed(3)+')';""")
# 4 glass rasping: a clear grip-and-release of the oral disc instead of a faint flutter
rep("el.style.setProperty('--anc-mouth',s.surface==='glass'&&s.mode==='graze'?(.85+.15*Math.sin(s.time*7+i)):1);",
    "el.style.setProperty('--anc-mouth',s.surface==='glass'&&s.mode==='graze'?(.7+.3*Math.pow(Math.max(0,Math.sin(s.time*4.2+i)),.6)):1);   /* V17.91: grip and release */")
open(p, 'w', encoding='utf-8', newline='').write(s); print('game patched')
