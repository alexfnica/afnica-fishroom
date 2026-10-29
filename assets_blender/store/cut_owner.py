# V17.120: cuts the owner's character out of a frame of the YouTube outro (D:\ClaudeWork\outro\f2.png, 1280x720) with a hand-traced polygon
# -> assets_blender/store/owner_cut.png (transparent, chest-up + arms down to y=640). Preview on magenta: D:\ClaudeWork\outro\cut_preview.png
# Needs the little http server: cd D:\ClaudeWork\outro && python -m http.server 8792
import sys, os, json, time, base64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
POLY = [(372,170),(372,125),(376,95),(390,65),(415,40),(445,26),(480,22),(520,30),(548,48),(572,75),(584,105),(585,140),(583,170),(587,185),(586,215),(580,235),(568,252),(556,285),(536,302),(530,320),(540,336),
        (578,356),(620,378),(655,408),(678,460),(692,520),(698,555),(706,580),(712,640),(716,640),(262,640),(262,600),(264,552),(266,540),(280,470),(305,420),(340,385),(380,358),(412,345),(430,338),
        (430,318),(421,296),(413,270),(402,248),(392,238),(378,232),(370,212),(367,185)]
X0, Y0, X1, Y1 = 245, 15, 722, 640
JS = """(async()=>{const im=new Image();im.src='f2.png';await im.decode();const P=%s,x0=%d,y0=%d,w=%d,h=%d;
const m=document.createElement('canvas');m.width=w;m.height=h;const g=m.getContext('2d');g.fillStyle='#000';g.beginPath();P.forEach((p,i)=>i?g.lineTo(p[0]-x0,p[1]-y0):g.moveTo(p[0]-x0,p[1]-y0));g.closePath();g.fill();g.globalCompositeOperation='destination-out';g.lineWidth=9;g.lineJoin='round';g.strokeStyle='#000';g.stroke();g.globalCompositeOperation='source-over';
const f=document.createElement('canvas');f.width=w;f.height=h;const fg=f.getContext('2d');fg.filter='blur(.9px)';fg.drawImage(m,0,0);fg.filter='none';
const o=document.createElement('canvas');o.width=w;o.height=h;const og=o.getContext('2d');og.drawImage(im,x0,y0,w,h,0,0,w,h);og.globalCompositeOperation='destination-in';og.drawImage(f,0,0);const q=document.createElement('canvas');q.width=240;q.height=Math.round(h*240/w);const qg=q.getContext('2d');qg.imageSmoothingQuality='high';qg.drawImage(o,0,0,q.width,q.height);
const pv=document.createElement('canvas');pv.width=w;pv.height=h;const pg=pv.getContext('2d');pg.fillStyle='#ff00ff';pg.fillRect(0,0,w,h);pg.drawImage(o,0,0);
return [q.toDataURL('image/png'),pv.toDataURL('image/png')]})()"""
c = Chrome(800, 800, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    r = c.js(JS % (json.dumps(POLY), X0, Y0, X1 - X0, Y1 - Y0))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'owner_cut.png'), 'wb').write(base64.b64decode(r[0].split(',')[1]))
    open(r'D:\ClaudeWork\outro\cut_preview.png', 'wb').write(base64.b64decode(r[1].split(',')[1]))
finally: c.close()
