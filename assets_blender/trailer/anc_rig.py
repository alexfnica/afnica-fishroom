# Bristlenose (V17.89) test rig: a throw-away headless game (never the owner's save), a landscape tank built in memory,
# forced breeding states, per-frame measurements and short review clips with a caption.
# Run: D:/Blender/5.2/python/bin/python.exe anc_rig.py <cmd> [...]
import os, sys, json, time, math
sys.path.insert(0, os.path.dirname(__file__))
from scene import open_game, advance, HERE

VW, VH = 960, 540
BLEED = r'''(k=>{let s=document.getElementById('ancBleed');if(!s){s=document.createElement('style');s.id='ancBleed';document.head.appendChild(s);}
 s.textContent='#tank-'+k+'{position:fixed!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;z-index:9000!important;border-radius:0!important;margin:0!important;aspect-ratio:auto!important;max-width:none!important;max-height:none!important;box-shadow:none!important}body{overflow:hidden!important}.toast,.toastV9,#toast{display:none!important}#tank-'+k+' .waterTimer,#tank-'+k+' .waterMeter{display:none!important}';
 window.dispatchEvent(new Event('resize'));return 1;})'''
CAP = r'''((txt,x,y,w,fs)=>{let d=document.getElementById('ancCap');if(!d){d=document.createElement('div');d.id='ancCap';document.body.appendChild(d);}
 d.style.cssText='position:fixed;z-index:99999;pointer-events:none;box-sizing:border-box;color:#fff;text-shadow:0 1px 2px #000;background:linear-gradient(rgba(0,0,0,.72) 55%,transparent);font:600 '+fs+'px/1.3 system-ui,sans-serif;padding:'+(fs*.45)+'px '+(fs*.8)+'px '+(fs*.9)+'px;left:'+x+'px;top:'+y+'px;width:'+w+'px';
 d.textContent=txt;d.style.display=txt?'block':'none';return 1;})'''

def anc_game(tank='breeder', fish="[T.fish('anc','M',40),T.fish('anc','F',36)]", pre='', warm=3, dsf=1):
    c = open_game(VW, VH, dsf, port=int(os.environ.get('AF_PORT', '9333')))
    c.js("window.__afHourOverride=12;" + pre + "(()=>{T.tank('%s',%s);if(k0==='breeder'){v8Tank='breeder';renderV103Breeder();}else T.show(k0);return 1})()".replace('k0',json.dumps(tank)) % (tank, fish))
    c.js(BLEED + "('%s')" % tank)
    advance(c, warm)
    return c

def ids(c, tank='breeder'):
    return json.loads(c.js("JSON.stringify(tankArrayV14('%s').map(f=>String(f.id)))" % tank))

def shot(c, path, clip=None):
    c.shot(path, clip=clip, q=90)

def film(c, name, seconds, fps=30, caption=None, every=None, clip=None, log=None):
    """frames to raw/<name>/ ; log(i) returns a dict per frame, saved to raw/<name>/log.json"""
    out = os.path.join(HERE, 'raw', name); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    n = int(seconds * fps); L = []; t0 = time.time()
    for i in range(n):
        if every: every(i)
        cl = clip(i) if callable(clip) else clip
        if caption:
            z = cl['scale'] if cl else 1; cx, cy, cw = (cl['x'], cl['y'], cl['width']) if cl else (0, 0, VW)
            c.js(CAP + "(%s,%f,%f,%f,%f)" % (json.dumps(caption(i) if callable(caption) else caption), cx, cy, cw, 15 / z))
        c.js('__afStep(%f, 2)' % (1000 / fps))
        c.shot(os.path.join(out, '%05d.jpg' % i), clip=cl, q=90)
        if log: L.append(log(i))
    json.dump(L, open(os.path.join(out, 'log.json'), 'w'))
    print('DONE', name, n, 'frames', round(time.time() - t0), 's', flush=True)
    return out

def state_js(fid, tank='breeder'):
    return ("(()=>{const e=document.querySelector('#tank-%s [data-fish-id=\"%s\"]');if(!e)return null;const d=e.dataset;"
            "return {x:+d.ancX,y:+d.ancY,m:d.ancMode,s:d.ancSurface,g:+(e.style.getPropertyValue('--anc-glass')||0),tr:e.style.transform,op:e.style.opacity}})()") % (tank, fid)

if __name__ == '__main__':
    import importlib
    mod = importlib.import_module(sys.argv[1]); getattr(mod, sys.argv[2])(*sys.argv[3:])
