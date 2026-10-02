import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from takes import game
c = game("T.tank('main',[T.fish('guppy','M',30),T.fish('guppy','F',30),T.fish('cory','M',30)])", warm=2)
try:
    print(c.js("JSON.stringify([...document.querySelector('#tank-main').children].map(e=>e.tagName+'.'+String(e.className).slice(0,60)+' z='+getComputedStyle(e).zIndex))"))
    print(c.js("JSON.stringify([...document.querySelectorAll('#tank-main *')].filter(e=>getComputedStyle(e).backgroundImage!=='none').slice(0,30).map(e=>e.tagName+'.'+String(e.className).slice(0,50)))"))
    print(c.js("getComputedStyle(document.querySelector('#tank-main')).backgroundImage.slice(0,200)"))
finally: c.close()
