import json, subprocess, time, sys
from playwright.sync_api import sync_playwright
D=json.load(open('durations.json'))
srv=subprocess.Popen(['python3','-m','http.server','8769','--bind','127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
INIT="""
window.__ses=[]; try{ localStorage.setItem('nth.duck','%s'); }catch(e){}
(function(){ var t='auto'; Object.defineProperty(navigator,'audioSession',{value:{get type(){return t;},set type(v){ t=v; window.__ses.push([Date.now(),v]); }},configurable:true}); })();
window.__log=[]; window.__D=%s;
(function(){
  Object.defineProperty(AudioContext.prototype,'currentTime',{get:function(){return Date.now()/1000;}});
  var P=AudioBufferSourceNode.prototype;
  P.start=function(){ var src=this,id=src.buffer&&src.buffer.__id; if(!id) return;
    window.__log.push([Date.now(),'play',id]); src.__t=setTimeout(function(){src.__t=null; if(src.onended) src.onended();}, (window.__D[id]||2)*1000+300); };
  P.stop=function(){ if(this.__t){clearTimeout(this.__t);this.__t=null;} };
})();
"""
def run(flag):
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':844}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.clock.install(); pg.add_init_script(INIT%(flag,json.dumps(D)))
        pg.goto('http://127.0.0.1:8769/index15.html'); pg.clock.run_for(1500)
        pg.click("[data-preset='1']"); pg.click("[data-ratio='standard']"); pg.clock.run_for(300)
        lbl0=pg.evaluate("[document.getElementById('boostBtn').textContent,document.getElementById('duckBtn').textContent,document.getElementById('duckNote').hidden,document.getElementById('duckNote').textContent]")
        pg.click('#primaryBtn')
        for i in range(1500): pg.clock.run_for(1000)
        ses=pg.evaluate('window.__ses'); log=pg.evaluate('window.__log')
        lbl=lbl0
        b.close(); return ses,log,lbl,errs
for flag in ('1','0'):
    ses,log,lbl,errs=run(flag)
    types=[s[1] for s in ses]
    dup=[i for i in range(len(types)-1) if types[i]==types[i+1]]; print('adjacent duplicate indices',dup[:6],types[:8])
    alt=all(types[i]!=types[i+1] for i in range(len(types)-1))
    print('duck pref',flag,'| clips played',len(log),'| session switches',len(ses),'| strictly alternating',alt,'| last type',types[-1] if types else None,'| ui',lbl,'| page errors',[e for e in errs])
    if flag=='1':
        # every clip start must be inside a transient window
        tr=[]; cur=None
        for t,v in ses: tr.append((t,v))
        def state_at(t):
            s='ambient'
            for tt,v in tr:
                if tt<=t: s=v
            return s
        notin=[l for l in log if state_at(l[0])!='transient']
        print('clips starting while NOT transient:',len(notin))
srv.terminate()
