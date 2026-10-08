#!/usr/bin/env python3
"""
Generate the remaining No Think HIIT exercise-demo videos via the xAI
("Grok Imagine") API at 720p and download them locally.

SETUP (one time):
  1. Create an account + billing at https://console.x.ai and generate an
     API key (video generation is a paid, metered endpoint -- there is no
     free tier for the API, unlike the consumer Grok Imagine product).
  2. export XAI_API_KEY="your-key-here"
  3. pip install requests --break-system-packages   (if not already installed)

USAGE:
  python3 generate_videos.py
  python3 generate_videos.py --limit 5        # do just the first 5, to sanity-check cost/quality
  python3 generate_videos.py --resolution 1080p

This script is RESUMABLE: it writes progress to progress.json next to it and
skips any exercise whose video already exists in ./output/, so re-running
after an interruption (or after bumping --limit) only does the remaining work.

Cost: 46 clips x 6s each = 276 seconds of output. At the time this was
written, xAI's own pricing page was not fully consistent across reads, but
converged in the range of $0.07-0.14/sec for 720p on grok-imagine-video-1.5
-- so expect roughly $19-39 total for the full batch. VERIFY the live rate
at https://docs.x.ai/developers/pricing before running the full batch; the
--limit flag exists specifically so you can generate 1-2 clips first and
check what you were actually billed before committing to all 46.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

API_BASE = "https://api.x.ai/v1"
MODEL = "grok-imagine-video-1.5"
DURATION_SECONDS = 6
POLL_INTERVAL_S = 5
POLL_TIMEOUT_S = 300
REQUEST_SPACING_S = 2  # stay well under xAI's rate limits

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
PROGRESS_FILE = os.path.join(SCRIPT_DIR, "progress.json")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def api_request(method, path, api_key, body=None):
    url = API_BASE + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + api_key)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} from {path}: {err_body}") from None


def start_generation(api_key, prompt, resolution):
    body = {
        "model": MODEL,
        "prompt": prompt,
        "duration": DURATION_SECONDS,
        "resolution": resolution,
    }
    result = api_request("POST", "/videos/generations", api_key, body)
    request_id = result.get("request_id") or result.get("id")
    if not request_id:
        raise RuntimeError(f"No request_id in response: {result}")
    return request_id


def poll_until_done(api_key, request_id):
    waited = 0
    while waited < POLL_TIMEOUT_S:
        result = api_request("GET", f"/videos/{request_id}", api_key)
        status = result.get("status")
        if status == "done":
            video_url = (result.get("video") or {}).get("url") or result.get("url")
            if not video_url:
                raise RuntimeError(f"Status done but no video url: {result}")
            return video_url
        if status in ("failed", "expired"):
            raise RuntimeError(f"Generation {status}: {result}")
        time.sleep(POLL_INTERVAL_S)
        waited += POLL_INTERVAL_S
    raise RuntimeError(f"Timed out after {POLL_TIMEOUT_S}s waiting on {request_id}")


def download(url, dest_path):
    urllib.request.urlretrieve(url, dest_path)


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="only generate the first N exercises")
    parser.add_argument("--resolution", default="720p", choices=["480p", "720p", "1080p"])
    parser.add_argument("--prompts-file", default="remaining_prompts.json",
                         help="JSON file of exercises to generate, relative to this script's folder "
                              "(default: remaining_prompts.json; use test_prompts.json for a quick diagnostic run)")
    args = parser.parse_args()

    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        sys.exit("Set XAI_API_KEY first (open a NEW terminal window after running setx): $env:XAI_API_KEY")

    prompts_path = os.path.join(SCRIPT_DIR, args.prompts_file)
    with open(prompts_path, encoding="utf-8") as f:
        exercises = json.load(f)
    if args.limit:
        exercises = exercises[: args.limit]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    progress = load_progress()

    print(f"Generating {len(exercises)} clips at {args.resolution}, {DURATION_SECONDS}s each "
          f"(~${len(exercises) * DURATION_SECONDS * 0.07:.2f}-${len(exercises) * DURATION_SECONDS * 0.14:.2f} estimated)\n")

    for i, ex in enumerate(exercises, 1):
        ex_id = ex["id"]
        out_path = os.path.join(OUTPUT_DIR, f"{ex_id}-{slug(ex['name'])}.mp4")

        if os.path.exists(out_path):
            print(f"[{i}/{len(exercises)}] {ex['name']}: already downloaded, skipping")
            continue

        print(f"[{i}/{len(exercises)}] {ex['name']} ({ex['category']})... ", end="", flush=True)
        try:
            request_id = start_generation(api_key, ex["prompt"], args.resolution)
            progress[ex_id] = {"request_id": request_id, "status": "submitted"}
            save_progress(progress)

            video_url = poll_until_done(api_key, request_id)
            download(video_url, out_path)

            progress[ex_id] = {"request_id": request_id, "status": "done", "file": out_path}
            save_progress(progress)
            print("done ->", out_path)
        except Exception as e:
            progress[ex_id] = {"status": "error", "error": str(e)}
            save_progress(progress)
            print(f"FAILED: {e}")
            print("  (continuing with the next exercise -- re-run this script later to retry failures)")

        time.sleep(REQUEST_SPACING_S)

    done_count = sum(1 for v in progress.values() if v.get("status") == "done")
    print(f"\n{done_count}/{len(exercises)} clips generated. Files are in {OUTPUT_DIR}/")
    print("Send the finished .mp4 files back in chat (or point Claude at this machine) to get them wired into the app.")


if __name__ == "__main__":
    main()
