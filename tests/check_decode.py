import subprocess,time
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8767','--bind','127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('http://127.0.0.1:8767/index15.html'); pg.wait_for_timeout(1500)
    r=pg.evaluate("""async()=>{var c=new AudioContext({sampleRate:24000});var out=[];var t0=performance.now();
      for (var id of Object.keys(VG)){
        var s=atob(VG[id]),u=new Uint8Array(s.length);for(var i=0;i<s.length;i++)u[i]=s.charCodeAt(i);
        try{var buf=await c.decodeAudioData(u.buffer);out.push([id,buf.duration.toFixed(2),VDUR[id]]);}catch(e){out.push([id,'FAIL',String(e)]);}}
      return [(performance.now()-t0)/out.length, out.length];}""")
    print('avg decode ms per clip, n:',r); b.close(); srv.terminate(); raise SystemExit
    print(len(r),'checked; bad:',bad); b.close()
srv.terminate()
