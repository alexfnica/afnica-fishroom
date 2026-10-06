# Compile every <script> block of the game in headless Chrome and report syntax errors with the file line.
# Run after every edit to the game HTML: D:/Blender/5.2/python/bin/python.exe assets_blender/syntax_check.py
import sys, json, re
sys.path.insert(0, r'D:\Retirement\assets_blender\trailer')
from cdp import Chrome
s=open(r'D:\Retirement\AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html',encoding='utf-8').read()
blocks=[m for m in re.finditer(r'<script>(.*?)</script>',s,re.S)]
c=Chrome(400,300,1,port=9778)
bad=0
try:
    c.cmd('Page.navigate',url='about:blank'); c.wait_event('Page.loadEventFired',20)
    for i,m in enumerate(blocks):
        r=c.cmd('Runtime.compileScript',expression=m.group(1),sourceURL='b%d.js'%i,persistScript=False)
        if 'exceptionDetails' in r:
            bad+=1;e=r['exceptionDetails'];line=s[:m.start(1)].count('\n')+e['lineNumber']+1
            print('block',i,'file line',line,e['exception']['description'][:120])
    print('blocks',len(blocks),'with syntax errors',bad)
finally: c.close()
