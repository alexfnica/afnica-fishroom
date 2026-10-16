# Pack frame PNGs into one WebP sprite sheet (headless Chrome canvas) + a JSON index {name: [x, y]} (cells all the same size).
# Run: python pack_atlas.py <out_prefix> <cols> <quality 0..1> <png> <png> ...
import sys, os, json, base64, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
out, cols, q = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]); files = sys.argv[4:]
srcs = ['data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode() for f in files]
JS = r"""(async (srcs,cols,q)=>{const ims=[];for(const s of srcs){const i=new Image();i.src=s;await i.decode();ims.push(i);}
const w=ims[0].naturalWidth,h=ims[0].naturalHeight,rows=Math.ceil(ims.length/cols),c=document.createElement('canvas');c.width=w*cols;c.height=h*rows;
const g=c.getContext('2d');const pos=[];ims.forEach((im,k)=>{const x=(k%cols)*w,y=Math.floor(k/cols)*h;g.drawImage(im,x,y);pos.push([x,y]);});
return JSON.stringify({url:c.toDataURL('image/webp',q),w,h,W:c.width,H:c.height,pos});})"""
c = Chrome(400, 300, 1, port=int(os.environ.get('AF_PORT', '9481')))
try:
    r = json.loads(c.js(JS + "(%s,%d,%f)" % (json.dumps(srcs), cols, q)))
    url = r.pop('url'); open(out + '.webp', 'wb').write(base64.b64decode(url.split(',', 1)[1]))
    r['names'] = [os.path.splitext(os.path.basename(f))[0] for f in files]
    json.dump(r, open(out + '.json', 'w')); print('ok', out, r['W'], r['H'], os.path.getsize(out + '.webp'), 'bytes')
finally: c.close()
