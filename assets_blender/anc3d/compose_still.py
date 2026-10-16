# Lay a transparent Blender render over a crop of the game background (both at 4x game px) -> one JPEG.
# Run: python compose_still.py <render.png> <bg.jpg> <crop_x> <crop_y> <out.jpg> [caption]
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
r, bg, cx, cy, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]; cap = sys.argv[6] if len(sys.argv) > 6 else ''
u = lambda p: 'file:///' + os.path.abspath(p).replace(os.sep, '/')
h = ('<body style="margin:0;width:1200px;height:680px;overflow:hidden;background:url(\'%s\') -%dpx -%dpx no-repeat">'
     '<img src="%s" style="position:absolute;left:0;top:0;width:1200px;height:680px">'
     '<div style="position:absolute;left:0;top:0;right:0;padding:10px 14px;font:600 19px system-ui;color:#fff;text-shadow:0 1px 3px #000">%s</div></body>') % (u(bg), cx, cy, u(r), cap)
p = os.path.join(os.path.dirname(os.path.abspath(out)), '_still.html'); open(p, 'w', encoding='utf-8').write(h)
c = Chrome(1200, 680, 1, port=int(os.environ.get('AF_PORT', '9463')))
try:
    c.cmd('Emulation.setDeviceMetricsOverride', width=1200, height=680, deviceScaleFactor=1, mobile=False)
    c.cmd('Page.navigate', url=u(p)); time.sleep(2); c.shot(out, q=92); print('ok', out)
finally: c.close()
