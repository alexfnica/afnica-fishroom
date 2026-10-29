# V17.120: splits the owner's cut-out into body + his right arm (screen left) so he can hand the bag over.
# Frame = D:\ClaudeWork\outro\f2.png (1280x720). Outputs (240 px wide, same x scale as owner_cut.png):
#   owner_body.png  = owner_cut without the arm (crop y 15..640)
#   owner_arm.png   = the arm (sleeve + forearm, y 15..775) with a painted hand where the frame ends; shoulder pivot (330,420) frame px
# Needs the little http server: cd D:\ClaudeWork\outro && python -m http.server 8792
import sys, os, json, time, base64
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'trailer'))
from cdp import Chrome
src = open(os.path.join(HERE, 'cut_owner.py'), encoding='utf-8').read()
POLY = eval(src.split('POLY = ')[1].split('\nX0')[0])
ARM = [(320,383),(322,405),(330,450),(340,500),(348,545),(350,600),(346,650),(340,720),(250,720),(248,680),(252,620),(256,560),(262,520),(275,470),(290,430),(305,400)]
JS = """(async()=>{const im=new Image();im.src='f2.png';await im.decode();const P=%s,A=%s,x0=245,y0=15,w=477,hb=625,ha=760;
const poly=(g,pts)=>{g.beginPath();pts.forEach((p,i)=>i?g.lineTo(p[0]-x0,p[1]-y0):g.moveTo(p[0]-x0,p[1]-y0));g.closePath();};
const cv=(h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return [c,c.getContext('2d')];};
const erode=(g,pts,lw)=>{g.globalCompositeOperation='destination-out';poly(g,pts);g.lineWidth=lw;g.lineJoin='round';g.strokeStyle='#000';g.stroke();g.globalCompositeOperation='source-over';};
/* body outline mask (eroded like owner_cut) */
const [M,mg]=cv(ha);mg.fillStyle='#000';poly(mg,P);mg.fill();erode(mg,P,9);
/* arm mask: inside the body outline above y 638, the eroded arm polygon below */
const [A1,a1]=cv(ha);a1.fillStyle='#000';poly(a1,A);a1.fill();erode(a1,A,9);
const [AM,am]=cv(ha);am.fillStyle='#000';poly(am,A);am.fill();am.globalCompositeOperation='destination-in';am.drawImage(M,0,0);am.globalCompositeOperation='source-over';
am.drawImage(A1,0,638-y0,w,ha,0,638-y0,w,ha);
/* body mask = outline minus the arm */
const [BM,bm]=cv(hb);bm.drawImage(M,0,0);bm.globalCompositeOperation='destination-out';bm.fillStyle='#000';poly(bm,A);bm.fill();
const soft=(c,h)=>{const [o,og]=cv(h);og.filter='blur(.9px)';og.drawImage(c,0,0);return o;};
const layer=(mask,h,hand)=>{const [o,og]=cv(h);og.drawImage(im,x0,y0,w,Math.min(h,720-y0),0,0,w,Math.min(h,720-y0));
 if(hand){/* the frame stops mid-forearm: paint a relaxed hand in the forearm's skin tone */
  const d=og.getImageData(292-x0,700-y0,1,1).data,sk='rgb('+d[0]+','+d[1]+','+d[2]+')';
  og.save();og.translate(293-x0,712-y0);const gr=og.createLinearGradient(-26,0,26,0);gr.addColorStop(0,'rgba(0,0,0,.18)');gr.addColorStop(.45,'rgba(255,255,255,.08)');gr.addColorStop(1,'rgba(0,0,0,.22)');
  og.fillStyle=sk;og.beginPath();og.moveTo(-24,0);og.quadraticCurveTo(-28,40,-14,62);og.quadraticCurveTo(0,72,14,62);og.quadraticCurveTo(28,40,24,0);og.closePath();og.fill();og.fillStyle=gr;og.fill();og.restore();
  mask.getContext('2d').fillStyle='#000';const mk=mask.getContext('2d');mk.save();mk.translate(293-x0,712-y0);mk.beginPath();mk.moveTo(-24,0);mk.quadraticCurveTo(-28,40,-14,62);mk.quadraticCurveTo(0,72,14,62);mk.quadraticCurveTo(28,40,24,0);mk.closePath();mk.fill();mk.restore();}
 og.globalCompositeOperation='destination-in';og.drawImage(soft(mask,h),0,0);
 const [q,qg]=[document.createElement('canvas'),null];q.width=240;q.height=Math.round(h*240/w);const qq=q.getContext('2d');qq.imageSmoothingQuality='high';qq.drawImage(o,0,0,q.width,q.height);return q.toDataURL('image/png');};
const hem=(g,below)=>{g.globalCompositeOperation='destination-in';g.fillStyle='#000';g.beginPath();
  if(below){g.moveTo(0,553-y0);g.lineTo(350-x0,595-y0);g.lineTo(w,600-y0);g.lineTo(w,ha);g.lineTo(0,ha);}else{g.moveTo(0,0);g.lineTo(w,0);g.lineTo(w,604-y0);g.lineTo(350-x0,599-y0);g.lineTo(0,557-y0);}
  g.closePath();g.fill();g.globalCompositeOperation='source-over';};
const [UM,um]=cv(ha);um.drawImage(AM,0,0);hem(um,false);
const [FM,fm]=cv(ha);fm.drawImage(AM,0,0);hem(fm,true);
const upper=layer(UM,ha,false),fore=layer(FM,ha,true),arm=layer(AM,ha,true),body=layer(BM,hb,false);
/* preview: body + arm on magenta */
const [pv,pg]=cv(ha);pg.fillStyle='#ff00ff';pg.fillRect(0,0,w,ha);const ia=new Image();ia.src=arm;await ia.decode();const ib=new Image();ib.src=body;await ib.decode();pg.drawImage(ib,0,0,w,hb);pg.save();pg.translate(330-x0,420-y0);pg.rotate(1.05);pg.translate(-(330-x0),-(420-y0));pg.drawImage(ia,0,0,w,ha);pg.restore();
return [body,arm,pv.toDataURL('image/png'),upper,fore]})()"""
c = Chrome(800, 800, 1, port=9555)
try:
    c.cmd('Page.navigate', url='http://127.0.0.1:8792/l.html'); c.wait_event('Page.loadEventFired', 20); time.sleep(.5)
    r = c.js(JS % (json.dumps(POLY), json.dumps(ARM)))
    for n, u in (('owner_body.png', r[0]), ('owner_arm.png', r[1]), ('owner_arm_upper.png', r[3]), ('owner_arm_fore.png', r[4])): open(os.path.join(HERE, n), 'wb').write(base64.b64decode(u.split(',')[1]))
    open(r'D:\ClaudeWork\outro\arm_preview.png', 'wb').write(base64.b64decode(r[2].split(',')[1]))
    print('ok')
finally: c.close()
