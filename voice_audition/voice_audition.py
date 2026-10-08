#!/usr/bin/env python3
"""
Render the same 6 coaching lines with OpenAI and/or ElevenLabs so you can listen and pick a voice.
Nothing is uploaded anywhere except the text of these 6 lines to the provider you choose.

SETUP (PowerShell), set whichever keys you have:
  $env:OPENAI_API_KEY="sk-..."
  $env:ELEVENLABS_API_KEY="..."
RUN (from the No Think HIIT folder):
  py voice_audition\voice_audition.py            # both providers if keys are set
  py voice_audition\voice_audition.py openai     # just OpenAI
  py voice_audition\voice_audition.py elevenlabs # just ElevenLabs
Output: .mp3 files in voice_audition\out\  (a few cents in total)
"""
import json, os, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
LINES = json.load(open(os.path.join(HERE, "audition_lines.json"), encoding="utf-8"))

BASE_STYLE = ("You are a calm, warm, relaxed trail-running coach on an early-morning forest run. "
              "Speak like a real person talking to a friend, in short natural phrases with small natural pauses, "
              "a hint of a smile, steady and unhurried. Never robotic, never announcer-like, never shouty.")
ENERGY = {
    "low":  " Tone: soft, easy and soothing, a touch slower, like a deep exhale.",
    "mid":  " Tone: relaxed but active, quietly motivating.",
    "high": " Tone: brisk and bright with controlled intensity, encouraging, still not shouting.",
}

def post(url, headers, body, label):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        print(f"  !! {label}: HTTP {e.code} {e.read()[:300].decode('utf-8','replace')}")
    except Exception as e:
        print(f"  !! {label}: {e}")
    return None

def openai():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("OPENAI_API_KEY not set, skipping OpenAI."); return
    for voice in ["coral", "sage", "ballad", "marin"]:
        print("OpenAI voice:", voice)
        for ln in LINES:
            path = os.path.join(OUT, f"openai_{voice}_{ln['id']}.mp3")
            if os.path.exists(path): continue
            audio = post("https://api.openai.com/v1/audio/speech",
                         {"Authorization": "Bearer " + key, "Content-Type": "application/json"},
                         {"model": "gpt-4o-mini-tts", "voice": voice, "input": ln["text"],
                          "instructions": BASE_STYLE + ENERGY[ln["energy"]], "response_format": "mp3"},
                         f"{voice} {ln['id']}")
            if audio is None: break
            open(path, "wb").write(audio); print("  wrote", os.path.basename(path))

def eleven():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print("ELEVENLABS_API_KEY not set, skipping ElevenLabs."); return
    model = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2")
    req = urllib.request.Request("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": key})
    try:
        voices = json.load(urllib.request.urlopen(req, timeout=60)).get("voices", [])
    except Exception as e:
        print("  !! could not list ElevenLabs voices:", e); return
    pick = [v for v in voices if v.get("category") == "premade"][:5] or voices[:5]
    for v in pick:
        name = "".join(c for c in v["name"] if c.isalnum()) or v["voice_id"][:6]
        print("ElevenLabs voice:", v["name"])
        for ln in LINES:
            path = os.path.join(OUT, f"eleven_{name}_{ln['id']}.mp3")
            if os.path.exists(path): continue
            audio = post(f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}?output_format=mp3_44100_64",
                         {"xi-api-key": key, "Content-Type": "application/json"},
                         {"text": ln["text"], "model_id": model,
                          "voice_settings": {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True}},
                         f"{name} {ln['id']}")
            if audio is None: break
            open(path, "wb").write(audio); print("  wrote", os.path.basename(path))

if __name__ == "__main__":
    which = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    if which in ("all", "openai"): openai()
    if which in ("all", "elevenlabs", "eleven"): eleven()
    print("Done. Listen to the files in", OUT)
