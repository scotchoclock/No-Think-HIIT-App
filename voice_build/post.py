import json, os, subprocess, re, sys
from concurrent.futures import ThreadPoolExecutor
os.makedirs('clips', exist_ok=True)
TRIM = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse"
def run(c):
    i=c['id']; src=f'raw/{i}.mp3'; dst=f'clips/{i}.mp3'
    if os.path.exists(dst): return (i,'skip')
    f1=TRIM+",loudnorm=I=-18:TP=-2:LRA=11:print_format=json"
    r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',src,'-af',f1,'-f','null','-'],capture_output=True,text=True)
    m=re.search(r'\{[^{}]*"input_i"[^{}]*\}',r.stderr,re.S)
    if not m: return (i,'measure-fail')
    j=json.loads(m.group(0))
    f2=TRIM+f",loudnorm=I=-18:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    r=subprocess.run(['ffmpeg','-hide_banner','-y','-i',src,'-af',f2,'-ar','24000','-ac','1','-c:a','libmp3lame','-b:a','40k',dst+'.tmp.mp3'],capture_output=True,text=True)
    if r.returncode: return (i,'enc-fail '+r.stderr[-200:])
    os.replace(dst+'.tmp.mp3',dst); return (i,'ok')
m=json.load(open('manifest.json'))
with ThreadPoolExecutor(4) as ex: res=list(ex.map(run,m))
bad=[r for r in res if r[1] not in('ok','skip')]
print('done',len(res),'bad',bad[:5])
