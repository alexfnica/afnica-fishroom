# Lay transparent Blender frames (2x game px) over the game background (bg_main.jpg, 4x) -> JPEG frames for the encoder.
# Run: python compose_frames.py <frames_dir> <out_dir> <crop_x4> <crop_y4> [caption]
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trailer'))
from cdp import Chrome
src, out, cx, cy = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); cap = sys.argv[5] if len(sys.argv) > 5 else ''
os.makedirs(out, exist_ok=True)
u = lambda p: 'file:///' + os.path.abspath(p).replace(os.sep, '/')
bg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'bg_main.jpg')
fr = sorted(f for f in os.listdir(src) if f.endswith('.png'))
probe = open(os.path.join(src, fr[0]), 'rb').read(); import struct; W, H = struct.unpack('>II', probe[16:24])
h = ('<body style="margin:0;width:%dpx;height:%dpx;overflow:hidden;background:url(\'%s\') -%gpx -%gpx/1920px 1080px no-repeat">'
     '<img id="f" style="position:absolute;left:0;top:0;width:%dpx;height:%dpx">'
     '<div style="position:absolute;left:0;top:0;right:0;padding:7px 10px;font:600 14px/1.3 system-ui;color:#fff;text-shadow:0 1px 3px #000;background:linear-gradient(rgba(0,0,0,.55),transparent)">%s</div></body>') % (W, H, u(bg), cx / 2, cy / 2, W, H, cap)
p = os.path.join(out, '_page.html'); open(p, 'w', encoding='utf-8').write(h)
c = Chrome(W, H, 1, port=int(os.environ.get('AF_PORT', '9464')))
try:
    c.cmd('Emulation.setDeviceMetricsOverride', width=W, height=H, deviceScaleFactor=1, mobile=False)
    c.cmd('Page.navigate', url=u(p)); time.sleep(1.5)
    for i, f in enumerate(fr):
        c.js("new Promise(r=>{const i=document.getElementById('f');i.onload=()=>r(1);i.src=%s})" % json.dumps(u(os.path.join(src, f))))
        c.shot(os.path.join(out, '%05d.jpg' % i), q=93)
    print('composed', len(fr))
finally: c.close()
