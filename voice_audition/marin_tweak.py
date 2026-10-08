#!/usr/bin/env python3
"""
Marin intro re-test: slower pace, crisp enunciation, rising "up", smooth flow into the exercise name.
Renders 3 wordings x 2 takes (TTS varies run to run) into voice_audition\out_tweak\.
Run from the No Think HIIT folder, same PowerShell window that has OPENAI_API_KEY set:
  py voice_audition\marin_tweak.py
"""
import json, os, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_tweak"); os.makedirs(OUT, exist_ok=True)
key = os.environ.get("OPENAI_API_KEY")
if not key: raise SystemExit("OPENAI_API_KEY not set in this window.")

STYLE = (
 "You are a calm, warm, relaxed trail-running coach on an early-morning forest run. Speak like a real person "
 "talking to a friend, in natural phrases, with a hint of a smile; never robotic, never announcer-like, never shouty. "
 "PACE: unhurried and clear, noticeably slower than casual speech, with a small natural pause between phrases. "
 "ENUNCIATION: pronounce every word crisply, especially the first sound of each word, so that no word is swallowed "
 "or blended into the one before it. "
 "INTONATION when introducing the next exercise: keep the energy bright and lifted. Raise your pitch slightly on the "
 "word 'up' and never let it drop or go flat. Carry that lift straight into the exercise name with no dip or pause, as if "
 "you are happy to show them the next move. Then settle into a calm, steady, encouraging tone for the form cue."
)
VARIANTS = {
 "A": "Next up, goblet squats! Hold the weight at your chest, then sit back and down, and keep your chest proud. Let's go.",
 "B": "Up next: goblet squats! Weight at your chest, sit back and down, nice and tall. Here we go.",
 "C": "Alright, goblet squats! Hold the weight right at your chest, then sit back and down, nice and slow. Let's go.",
}
for name, text in VARIANTS.items():
    for take in (1, 2):
        path = os.path.join(OUT, f"marin_intro_{name}_take{take}.mp3")
        req = urllib.request.Request("https://api.openai.com/v1/audio/speech",
            data=json.dumps({"model": "gpt-4o-mini-tts", "voice": "marin", "input": text,
                             "instructions": STYLE, "response_format": "mp3"}).encode("utf-8"),
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, method="POST")
        try:
            open(path, "wb").write(urllib.request.urlopen(req, timeout=120).read()); print("wrote", os.path.basename(path))
        except urllib.error.HTTPError as e:
            print("!!", name, take, e.code, e.read()[:200].decode("utf-8", "replace"))
print("Done. Listen in", OUT)
