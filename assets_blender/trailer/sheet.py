# Contact sheet of a take: every Nth frame, small, in a grid, with the frame number. Uses headless Chrome to draw it.
# Run: python sheet.py <take> [step=15] [cols=6]
import os, sys, base64
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome
HERE = os.path.dirname(os.path.abspath(__file__))
take = sys.argv[1]; step = int(sys.argv[2]) if len(sys.argv) > 2 else 15; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
d = os.path.join(HERE, 'raw', take); files = sorted(f for f in os.listdir(d) if f.endswith('.jpg'))[::step]
cw, ch = 180, 320; rows = (len(files) + cols - 1) // cols
html = '<body style="margin:0;background:#111;display:grid;grid-template-columns:repeat(%d,%dpx);gap:2px;font:12px sans-serif">' % (cols, cw)
for f in files:
    html += '<div style="position:relative;width:%dpx;height:%dpx"><img src="file:///%s" style="width:100%%;height:100%%"><b style="position:absolute;left:3px;top:2px;color:#ff0;text-shadow:0 0 3px #000">%s</b></div>' % (cw, ch, os.path.join(d, f).replace('\\', '/'), f[:-4])
p = os.path.join(HERE, 'test', '_sheet.html'); open(p, 'w').write(html + '</body>')
W = cols * (cw + 2); H = rows * (ch + 2)
c = Chrome(W, H, 1, port=9444)
try:
    c.cmd('Page.navigate', url='file:///' + p.replace('\\', '/')); c.wait_event('Page.loadEventFired', 30)
    import time; time.sleep(.5)
    out = os.path.join(HERE, 'test', 'sheet_%s.jpg' % take.replace('/', '_').replace('.', '')); c.shot(out, clip=dict(x=0, y=0, width=W, height=H, scale=1), q=85); print(out)
finally: c.close()
