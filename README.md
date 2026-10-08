# No Think HIIT

A voice-guided HIIT workout app: shuffled circuits, AI-generated exercise videos, and a spoken coach so you never look at the screen. Built and published as a Claude Artifact and shared with friends and family.

## How it fits together

| Piece | What it is | Where |
|---|---|---|
| App | One HTML file: UI, workout builder, timer, voice engine | `app/index.html` |
| Exercise videos | AI-generated clips, one per exercise plus rest scenes | `generate_videos.py` + `*_prompts.json` |
| Coach voice | OpenAI `gpt-4o-mini-tts`, voice "Marin", ~520 clips | `voice_build/` |
| Voice auditions | Scripts used to pick the voice | `voice_audition/` |
| Tests | Playwright checks for voice transitions and move uniqueness | `tests/` |

## Important limits of this repo

- `app/index.html` is the **source of truth for app logic**, but it does not run standalone. Videos and per-exercise voice bundles load from `/_blob/<id>` URLs that exist only inside the published artifact.
- Generated media (`output/`, `loops/`, `voice_build/clips*/`, ...) is **not committed**. It is ~700 MB and regenerable from the scripts and prompts. GitHub rejects files over 100 MB.
- API keys are never stored in files. Scripts read `OPENAI_API_KEY` from the environment.

## Rebuilding the voice library

```powershell
$env:OPENAI_API_KEY = "<your key>"
py voice_build\voice_render2.py      # renders the clips listed in manifest2.json
```

`voice_build/norm.py` then trims silence and levels every clip to -18 LUFS.

## Versions

Published artifact versions map to commits. Commit messages start with the artifact version, for example `v42:`.

| Artifact | Change |
|---|---|
| v39 | Voice overhaul: Marin clip library, lazy per-exercise bundles |
| v40 | Fix: "one" of the 3-2-1 count cut off at transitions |
| v41 | 3 s "Get ready" lead-in, 18 s prep, clip loudness leveling |
| v42 | Music keeps playing under voice (Web Audio), no repeated moves in a workout |
| v43 | Re-recorded countdown, final-ten, "go" and halfway clips; a different break line per circuit ("circuit 2 of 3 done, one to go"); timing clips stay decoded all workout; move picker can no longer repeat a move when a muscle group runs dry |
| v44 | Voice boost (+3.6 dB through a limiter, on by default) and an experimental "Duck music (beta)" toggle that asks the phone to lower music while the coach talks |

## Known open items

- Music mixing is untested on real phones. iPhone silent switch will mute the voice.
- The re-recorded clips are leveled and tested for timing, but nobody has listened to them on a phone yet.
- Music ducking is a browser hint (`audioSession.type = "transient"`), not a guarantee. Being tested on a Pixel; iPhone WebKit may ignore it.
