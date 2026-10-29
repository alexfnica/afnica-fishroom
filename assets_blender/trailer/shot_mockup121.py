# Renders docs/mockup_ui121.html (4 phone frames, each a real game instance) to docs/ui_mockup_*.png in a throw-away headless Chrome.
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome
out = sys.argv[1] if len(sys.argv) > 1 else 'D:/Retirement/docs/ui_mockup_v1.png'
c = Chrome(1700, 860, 1, port=9344)
try:
    c.cmd('Emulation.setDeviceMetricsOverride', width=1700, height=860, deviceScaleFactor=1, mobile=False)
    c.cmd('Page.navigate', url='http://127.0.0.1:8791/docs/mockup_ui121.html')
    time.sleep(float(os.environ.get('WAIT', '60')))
    c.shot(out, fmt='png')
    print('saved', out)
finally:
    c.close()
