import sys, time, os
sys.path.insert(0, os.path.dirname(__file__))
from cdp import Chrome, CLOCK_JS
OUT = os.path.join(os.path.dirname(__file__), 'test'); os.makedirs(OUT, exist_ok=True)
c = Chrome()
try:
    c.cmd('Page.addScriptToEvaluateOnNewDocument', source=CLOCK_JS)
    t = time.time()
    c.cmd('Page.navigate', url='file:///D:/Retirement/AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html')
    c.wait_event('Page.loadEventFired', 90); print('loaded', round(time.time() - t, 1), 's')
    c.js('__afStep(1000, 30)')
    print(c.js('JSON.stringify({fish: document.querySelectorAll(".tank .modelFish").length, tank: (()=>{const r=document.querySelector(".tank").getBoundingClientRect();return [r.x,r.y,r.width,r.height]})(), title: document.title, scrollH: document.documentElement.scrollHeight})'))
    t = time.time(); c.shot(OUT + '/full.jpg'); print('shot', round(time.time() - t, 2), 's')
    for i in range(3):
        c.js('__afStep(33.333, 2)'); c.shot(OUT + '/f%d.jpg' % i)
    t = time.time()
    for i in range(10): c.js('__afStep(33.333, 2)'); c.shot(OUT + '/g%d.jpg' % i)
    print('10 frames', round(time.time() - t, 2), 's')
finally:
    c.close()
