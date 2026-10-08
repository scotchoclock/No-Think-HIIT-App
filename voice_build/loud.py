import json,subprocess,re,sys
from concurrent.futures import ThreadPoolExecutor
m=json.load(open('manifest.json'))
def meas(c):
    r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',f'clips/{c["id"]}.mp3','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True)
    t=r.stderr
    I=re.findall(r'I:\s+(-?[\d.]+) LUFS',t); P=re.findall(r'Peak:\s+(-?[\d.]+) dBFS',t); S=re.findall(r'LRA:\s+([\d.]+) LU',t)
    # short-term max & momentary max via second run? use volumedetect for rms
    r2=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',f'clips/{c["id"]}.mp3','-af','volumedetect','-f','null','-'],capture_output=True,text=True).stderr
    mean=re.findall(r'mean_volume: (-?[\d.]+) dB',r2); mx=re.findall(r'max_volume: (-?[\d.]+) dB',r2)
    return dict(id=c['id'],cat=c['cat'],I=float(I[-1]) if I else None,P=float(P[-1]) if P else None,mean=float(mean[0]),mx=float(mx[0]))
with ThreadPoolExecutor(2) as ex: res=list(ex.map(meas,m))
json.dump(res,open('loudness.json','w'))
print(len(res))
