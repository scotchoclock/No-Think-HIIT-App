import json,subprocess,re,sys,statistics as st,collections
from concurrent.futures import ThreadPoolExecutor
D=sys.argv[1]
m=json.load(open('manifest2.json'))
def meas(c):
    t=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',f'{D}/{c["id"]}.mp3','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    I=re.findall(r'I:\s+(-?[\d.]+) LUFS',t); P=re.findall(r'Peak:\s+(-?[\d.]+) dBFS',t)
    d=re.findall(r'Duration: (\d+):(\d+):([\d.]+)',t)
    dur=int(d[0][0])*3600+int(d[0][1])*60+float(d[0][2]) if d else 0
    return dict(id=c['id'],cat=c['cat'],I=float(I[-1]) if I else -70,P=float(P[-1]) if P else 0,dur=dur)
with ThreadPoolExecutor(2) as ex: r=list(ex.map(meas,m))
json.dump(r,open(f'loud_{D}.json','w'))
I=[x['I'] for x in r]; print('LUFS min %.1f max %.1f mean %.1f sd %.2f'%(min(I),max(I),st.mean(I),st.pstdev(I)))
print('peak max %.1f'%max(x['P'] for x in r))
by=collections.defaultdict(list)
for x in r: by[x['cat']].append(x)
for k,v in by.items(): ii=[x['I'] for x in v]; print('%-12s %.1f..%.1f'%(k,min(ii),max(ii)))
for x in sorted(r,key=lambda x:abs(x['I']+18),reverse=True)[:6]: print('outlier',x['id'],x['I'],x['P'],x['dur'])
