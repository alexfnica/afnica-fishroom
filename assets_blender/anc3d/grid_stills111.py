# V17.111: the 3 stage stills with a labelled 50 px grid (to read larva positions). Output D:/ClaudeWork/wriggler_clip/grid_<stage>.jpg
import sys, os, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
INC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'incoming')
JS = r"""(async (src)=>{const im=new Image();im.src=src;await im.decode();const c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;const g=c.getContext('2d');g.drawImage(im,0,0);
g.font='11px sans-serif';for(let x=0;x<c.width;x+=50){g.fillStyle=x%100?'rgba(0,255,255,.25)':'rgba(0,255,255,.5)';g.fillRect(x,0,1,c.height);if(x%100==0){g.fillStyle='#0ff';g.fillText(x,x+2,10)}}
for(let y=0;y<c.height;y+=50){g.fillStyle=y%100?'rgba(0,255,255,.25)':'rgba(0,255,255,.5)';g.fillRect(0,y,c.width,1);if(y%100==0){g.fillStyle='#0ff';g.fillText(y,2,y+11)}}
return c.toDataURL('image/jpeg',.9)})"""
c = Chrome(400, 300, 1, port=9473)
try:
    for k in ('full', 'half', 'low'):
        b = base64.b64encode(open(os.path.join(INC, 'anc_wriggler_scene_%s.webp' % k), 'rb').read()).decode()
        r = c.js(JS + "(%s)" % json.dumps('data:image/webp;base64,' + b))
        open('D:/ClaudeWork/wriggler_clip/grid_%s.jpg' % k, 'wb').write(base64.b64decode(r.split(',')[1]))
    print('ok')
finally: c.close()
