import subprocess,time,json,collections
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8766','--bind','127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
breaks_all=set()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://127.0.0.1:8766/index15.html'); pg.wait_for_timeout(1500)
    for preset in ('1','2'):
        pg.click("[data-preset='%s']"%preset)
        dups=0; n=700; worst=collections.Counter(); sizes=set(); breaks=set()
        for i in range(n):
            pg.click('#shuffleBtn')
            seq=pg.evaluate("window.__seq().map(function(s){return {t:s.type,n:s.name,d:s.circuitDone,T:s.circuitTotal,dur:s.dur}})")
            moves=[s['n'] for s in seq if s['t'] in('work','warmup')]
            c=collections.Counter(moves)
            d=[k for k,v in c.items() if v>1]
            if d: dups+=1; worst.update(d)
            sizes.add(len(moves))
            for s in seq:
                if s['t']=='roundrest': breaks.add((s['d'],s['T'],s['dur'])); breaks_all.add((s['d'],s['T']))
        print('preset',preset,'workouts with a repeated move:',dups,'/',n,'move counts',sizes,'breaks',sorted(breaks),dict(worst))
    VB=pg.evaluate('VBRK'); miss=[k for k in breaks_all if (str(k[0])+'of'+str(k[1])) not in VB]; print('break keys without custom clips:',miss); print(errs); b.close()
srv.terminate()
