import json,subprocess,re,os,sys,tempfile
from concurrent.futures import ThreadPoolExecutor
TARGET=-18.0
TRIM="silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse"
os.makedirs('clips3',exist_ok=True); os.makedirs('/tmp/tmpw3',exist_ok=True)
def lufs(path):
    t=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',path,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    I=re.findall(r'I:\s+(-?[\d.]+) LUFS',t)
    v=float(I[-1]) if I else -70.0
    if v<=-69.9:  # too short to gate: fall back to mean volume (+ small offset)
        t2=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',path,'-af','volumedetect','-f','null','-'],capture_output=True,text=True).stderr
        v=float(re.findall(r'mean_volume: (-?[\d.]+) dB',t2)[0])-0.7
    return v
def run(c):
    if os.path.exists('clips3/'+c['id']+'.mp3') and os.path.getsize('clips3/'+c['id']+'.mp3')>1500: return c['id']
    i=c['id']; src=f'raw2/{i}.mp3'; w=f'/tmp/tmpw3/{i}.wav'; w2=f'/tmp/tmpw3/{i}.b.wav'; dst=f'clips3/{i}.mp3'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',src,'-af',TRIM,'-ar','24000','-ac','1','-c:a','pcm_s16le',w],check=True)
    for it in range(4):
        I=lufs(w)
        g=TARGET-I
        if abs(g)<0.25 and it>0: break
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',w,'-af',f'volume={g:.2f}dB,alimiter=limit=0.84:attack=3:release=40:level=disabled','-c:a','pcm_s16le',w2],check=True)
        os.replace(w2,w)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',w,'-ar','24000','-ac','1','-c:a','libmp3lame','-b:a','40k',dst],check=True)
    os.remove(w)
    return i
m=json.load(open('manifest2.json'))
with ThreadPoolExecutor(2) as ex: r=list(ex.map(run,m))
print('done',len(r))
