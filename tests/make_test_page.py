i=open('vtest/index13.html').read(); ai=open('app_build/app_v13_interim.html').read()
pre=i[:i.find(ai[:200])]
a=open('app_build/app_v14.html').read()
assert a.count('        BUFS[id] = buf;\n')==1; a=a.replace('        BUFS[id] = buf;\n','        BUFS[id] = buf; buf.__id = id;\n').replace('  function armClock() {','  window.__seq=function(){return sequence;}; function armClock() {')
open('vtest/index15.html','w').write(pre+a+'\n</body></html>')
