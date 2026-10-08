import subprocess,time,json,sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8768','--bind','127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
G=float(sys.argv[1]) if len(sys.argv)>1 else 1.5
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('http://127.0.0.1:8768/index15.html'); pg.wait_for_timeout(1500)
    r=pg.evaluate("""async(G)=>{
      var ids=Object.keys(VG).filter(i=>/^g\\.(cnt2|fin2|go2|half2|rest|breakstart|complete|cooldown)\\./.test(i)||/^b\\./.test(i));
      var c=new AudioContext({sampleRate:24000}); var res=[];
      function stats(d){var pk=0,s=0;for(var i=0;i<d.length;i++){var a=Math.abs(d[i]);if(a>pk)pk=a;s+=d[i]*d[i];}return [pk,Math.sqrt(s/d.length)];}
      for (var id of ids){
        var s=atob(VG[id]),u=new Uint8Array(s.length);for(var i=0;i<s.length;i++)u[i]=s.charCodeAt(i);
        var buf=await c.decodeAudioData(u.buffer);
        var o=new OfflineAudioContext(1,buf.length+2400,24000);
        var src=o.createBufferSource();src.buffer=buf;
        var g=o.createGain();g.gain.value=G;var comp=o.createDynamicsCompressor();
        comp.threshold.value=-3;comp.knee.value=0;comp.attack.value=0.002;comp.release.value=0.12;comp.ratio.value=20;
        src.connect(g);g.connect(comp);comp.connect(o.destination);src.start();
        var out=await o.startRendering();
        var a=stats(buf.getChannelData(0)),z=stats(out.getChannelData(0));
        res.push([id,a[0],z[0],20*Math.log10(z[1]/a[1])]);
      }
      return res;}""",G)
    import statistics as st
    gains=[x[3] for x in r]; peaks=[x[2] for x in r]
    print('gain',G,'clips',len(r),'RMS change dB: mean %.2f min %.2f max %.2f'%(st.mean(gains),min(gains),max(gains)),'| max output peak %.3f (1.0 = full scale)'%max(peaks),'| clips peaking >1.0:',sum(1 for x in peaks if x>1.0))
    b.close()
srv.terminate()
