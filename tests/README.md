# Tests

Headless Chromium (Playwright) checks for the workout engine. They are not self-contained: they were run from a scratch directory that served a test page plus the voice bundles under `/_blob/`.

| Script | Checks |
|---|---|
| `make_test_page.py` | Builds `index14.html` from `app/index.html` with three test hooks: tags decoded buffers with their clip id, exposes the step list as `window.__seq`, and wraps the page in the preview header. |
| `run_workout.py` | Plays a whole workout on a fake clock and logs every clip start and every clip that gets cut off. Pass `<steps> <css selectors to click first>`. |
| `uniq.py` | Builds 700 workouts per preset and checks no move repeats and every circuit break has a matching voice line. |
| `duck.py` | With ducking on, checks every voice line starts while the audio session is `transient` and the session returns to `ambient` afterwards. |
| `boost.py <gain>` | Runs every voice clip through the boost + limiter offline and reports loudness gain and peak level (must stay under 1.0). |
| `check_decode.py` | Decodes every inline clip and compares its length with `VDUR`. |

Known test artifact: the fake clock fires the app's 2.5 s decode timeout before real decoding finishes, so on-demand clips sometimes log `TTS-FALLBACK`. Real decoding measures about 3 ms per clip.
