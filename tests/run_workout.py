import json, subprocess, time, sys
from playwright.sync_api import sync_playwright
D=json.load(open('durations.json')); T={c['id']:c['text'] for c in json.load(open('manifest.json'))}
srv=subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
INIT="""
(function(){ if(window.speechSynthesis){ var o=speechSynthesis.speak.bind(speechSynthesis); speechSynthesis.speak=function(u){ window.__log.push({t:Date.now(),ev:'play',id:'TTS-FALLBACK:'+(u&&u.text||'').slice(0,50)}); }; } })();

window.__log=[]; window.__t0=null;
window.__D=%s;
(function(){
  var P=HTMLMediaElement.prototype, origPlay=P.play, origPause=P.pause;
  P.play=function(){
    var el=this, id=(window.__ids||{})[el.src];
    if(!id){ return Promise.resolve(); }
    el.__id=id; el.__start=Date.now(); el.__playing=true;
    window.__log.push({t:Date.now(),ev:'play',id:id});
    var d=(window.__D[id]||2)*1000+300;
    el.__timer=setTimeout(function(){ el.__playing=false; if(el.onended) el.onended(); }, d);
    return Promise.resolve();
  };
  P.pause=function(){
    var el=this;
    if(el.__playing){ clearTimeout(el.__timer); el.__playing=false;
      var left=(window.__D[el.__id]*1000+300)-(Date.now()-el.__start);
      window.__log.push({t:Date.now(),ev:'cut',id:el.__id,left:Math.round(left)}); }
  };
})();

(function(){
  Object.defineProperty(AudioContext.prototype,'currentTime',{get:function(){return Date.now()/1000;}});
  var P=AudioBufferSourceNode.prototype;
  P.start=function(){
    var src=this, id=src.buffer&&src.buffer.__id;
    if(!id) return;
    window.__log.push({t:Date.now(),ev:'play',id:id});
    src.__id=id; src.__s=Date.now(); src.__d=(window.__D[id]||2)*1000+300;
    src.__t=setTimeout(function(){ src.__t=null; if(src.onended) src.onended(); }, src.__d);
  };
  P.stop=function(){
    if(this.__t){ clearTimeout(this.__t); this.__t=null;
      window.__log.push({t:Date.now(),ev:'cut',id:this.__id,left:Math.round(this.__d-(Date.now()-this.__s))}); }
  };
})();
"""%json.dumps(D)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':844})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
    pg.clock.install(); pg.add_init_script(INIT)
    pg.goto('http://127.0.0.1:8765/index14.html'); pg.clock.run_for(1500)
    for sel in sys.argv[2:]: pg.click(sel)
    pg.clock.run_for(300)
    pg.click('#primaryBtn')
    t0=pg.evaluate('Date.now()')
    steps=int(sys.argv[1]) if len(sys.argv)>1 else 600
    dom=[]; last=None
    for i in range(steps):
        pg.clock.run_for(1000)
        try: st=pg.evaluate("[document.getElementById('phaseLabel').textContent,document.getElementById('exerciseName').textContent,document.getElementById('timeDisplay').textContent,document.getElementById('statusPill').textContent]")
        except Exception: continue
        key=(st[0],st[1])
        if key!=last: dom.append((i+1,st)); last=key
    log=pg.evaluate('window.__log')
    for e in log:
        t=(e['t']-t0)/1000
        print('%7.1f %-4s %-34s %s'%(t,e['ev'],e['id'], (T.get(e['id'],'')[:70] if e['ev']=='play' else 'left=%dms'%e['left'])))
    for t,st in dom[:int(__import__('os').environ.get('DOMN','0'))]: print('DOM %5d %s'%(t,st))
    print('errors',errs)
    b.close()
srv.terminate()
