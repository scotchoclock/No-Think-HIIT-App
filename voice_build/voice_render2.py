#!/usr/bin/env python3
"""
Render the REVISED clips (calmer countdown / ten-second / go / halfway lines, and circuit-aware break lines) with OpenAI gpt-4o-mini-tts (voice: marin).
Run from the No Think HIIT folder, in the PowerShell window that has OPENAI_API_KEY set:
    py voice_build\voice_render2.py
Safe to re-run: clips that already exist are skipped. ~476 clips, roughly $0.60.
Output: voice_build\raw2\<clip-id>.mp3
"""
import json, os, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw2"); os.makedirs(RAW, exist_ok=True)
key = os.environ.get("OPENAI_API_KEY")
if not key: raise SystemExit("OPENAI_API_KEY not set in this window.")
manifest = json.load(open(os.path.join(HERE, "manifest2.json"), encoding="utf-8"))

BASE = (
 "You are a calm, warm, relaxed trail-running coach on an early-morning forest run. Speak like a real person "
 "talking to a friend, in natural phrases, with a hint of a smile; never robotic, never announcer-like, never shouty. "
 "PACE: unhurried and clear, noticeably slower than casual speech, with a small natural pause between phrases. "
 "ENUNCIATION: pronounce every word crisply, especially the first sound of each word, so that no word is swallowed "
 "or blended into the one before it. "
)
INTRO = (
 "INTONATION when introducing the next exercise: keep the energy bright and lifted. Raise your pitch slightly on the "
 "word 'up' (or on the opening word) and never let it drop or go flat. Carry that lift straight into the exercise name "
 "with no dip or pause, as if you are happy to show them the next move. Then settle into a calm, steady, encouraging tone for the form cue."
)
TONE = {
 "fin2": "Tone: warm, natural and encouraging, like a friend quietly cheering you through the last stretch. A touch more energy than usual, but the same relaxed pace as the rest. Do not speed up, do not shout, no staccato, no announcer voice.",
 "cnt2": "Tone: calm, natural and steady, like a friend counting you in. Unhurried, even pace with a short natural pause between numbers. Not mechanical, not a robotic countdown.",
 "go2": "Tone: short, upbeat and warm, a quick go-signal with a smile. Natural and lifted, not loud, not shouty.",
 "half2": "Tone: warm and encouraging, a friendly checkpoint. Steady, natural energy.",
 "brk": "Tone: relaxed, proud and soothing, like a friend celebrating a finished round. Slow and warm. Say the numbers clearly and naturally.",
}
def style(cat): return BASE + TONE[cat]

lock = threading.Lock(); done = [0]; fails = []
def render(c):
    path = os.path.join(RAW, c["id"] + ".mp3")
    if os.path.exists(path) and os.path.getsize(path) > 1000: return
    body = json.dumps({"model": "gpt-4o-mini-tts", "voice": "marin", "input": c["text"],
                       "instructions": style(c["cat"]), "response_format": "mp3"}).encode("utf-8")
    for attempt in range(6):
        req = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=body, method="POST",
              headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        try:
            data = urllib.request.urlopen(req, timeout=120).read()
            with open(path + ".tmp", "wb") as f: f.write(data)
            os.replace(path + ".tmp", path)
            with lock:
                done[0] += 1
                if done[0] % 20 == 0: print(f"  {done[0]} rendered...", flush=True)
            return
        except urllib.error.HTTPError as e:
            msg = e.read()[:200].decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt + 1); continue
            with lock: fails.append((c["id"], e.code, msg)); print("!!", c["id"], e.code, msg)
            return
        except Exception as e:
            time.sleep(2 ** attempt + 1)
    with lock: fails.append((c["id"], "retries", "")); print("!! gave up on", c["id"])

todo = [c for c in manifest if not (os.path.exists(os.path.join(RAW, c["id"] + ".mp3")))]
print(f"{len(manifest)} clips in manifest, {len(todo)} to render.")
if "--test" in sys.argv: todo = todo[:3]
with ThreadPoolExecutor(max_workers=4) as ex: list(ex.map(render, todo))
print(f"Done. {done[0]} rendered, {len(fails)} failed. Output: {RAW}")
if fails: print("Re-run the script to retry failures.")
