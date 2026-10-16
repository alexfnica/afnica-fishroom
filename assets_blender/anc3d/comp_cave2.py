# Composite check for the V17.92 cave layers, exactly as the game will draw them: tube -> _in clipped to the mouth
# ellipse -> _out. Run: python comp_cave2.py <out.jpg> <name> [<name> ...]   (names like C2_i+040)
import sys, os, json, base64, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'out', 'cave92'); T = os.path.join(HERE, 'out', 'cave90', 'C_tube00.png')
u = lambda p: 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
out, names = sys.argv[1], sys.argv[2:]
MX, MY, RX, RY = 173.8 * 2, 72 * 2, 7.0 * 2, 22.6 * 2      # mouth opening (frame px at 2x)
items = [[n, u(os.path.join(D, n + '_in.png')), u(os.path.join(D, n + '_out.png'))] for n in names]
JS = r"""(async (tube,items,MX,MY,RX,RY)=>{const L=s=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src=s;});const T=await L(tube);
const cols=3,W=680,H=220,c=document.createElement('canvas');c.width=W*cols;c.height=H*Math.ceil(items.length/cols);const g=c.getContext('2d');
g.fillStyle='#c8b591';g.fillRect(0,0,c.width,c.height);
for(let k=0;k<items.length;k++){const [n,a,b]=items[k],x=(k%cols)*W,y=Math.floor(k/cols)*H;g.save();g.translate(x,y);
 g.fillStyle='#0d4a5a';g.fillRect(0,0,W,120);g.drawImage(T,0,0);
 const I=await L(a),O=await L(b);g.save();g.beginPath();g.ellipse(MX,MY,RX,RY,0,0,7);g.clip();g.drawImage(I,0,0);g.restore();g.drawImage(O,0,0);
 g.fillStyle='#ff0';g.font='bold 16px sans-serif';g.fillText(n,6,18);g.restore();}
return c.toDataURL('image/jpeg',.9);})"""
c = Chrome(400, 300, 1, port=int(os.environ.get('AF_PORT', '9498')))
try:
    url = c.js(JS + '(%s,%s,%f,%f,%f,%f)' % (json.dumps(u(T)), json.dumps(items), MX, MY, RX, RY))
    open(out, 'wb').write(base64.b64decode(url.split(',', 1)[1])); print('ok', out)
finally: c.close()
