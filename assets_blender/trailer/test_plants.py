import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from takes import game, advance, HERE
c = game("st.scapes=st.scapes||{};st.scapes.main=Object.assign(st.scapes.main||{},{ground:'amazonia',surface:'redroot',substrate:'vallisneria',epiphyte:'javafern',wood:'branch',rock:'dragon'});T.tank('main',[T.fish('xipho','M',40)])", warm=2, dof=0)
try:
    print(c.js(r"""JSON.stringify([...document.querySelectorAll('#tank-main .v175SubstrateAssetLayer *, #tank-main .v176EpiphyteAssetLayer *, #tank-main .v174SurfaceAssetLayer *, #tank-main .v171BackPlantGroup *')].map(e=>{const cs=getComputedStyle(e),r=e.getBoundingClientRect();
      const bg=cs.backgroundImage;return {tag:e.tagName,cls:String(e.className).slice(0,40),w:Math.round(r.width),h:Math.round(r.height),bg:bg==='none'?null:bg.slice(0,40)+'...'+bg.length,src:e.src?e.src.slice(0,40)+'...'+e.src.length:null}}).filter(o=>o.bg||o.src).slice(0,30))"""))
finally: c.close()
