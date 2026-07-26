#!/usr/bin/env python3
"""Barra Math daily auto-poster. Posts ONE content item per run to Instagram + Pinterest via Zernio.
Reads ZERNIO_API_KEY from the environment (never hardcode it here — this repo is public).
State (rotation index) is stored in scripts/post_state.json in this repo so it survives across runs.
"""
import json, os, subprocess, sys, time
from pathlib import Path

STATE_FILE = Path(__file__).parent / "post_state.json"
# NOTE: barramath.com custom domain HTTPS cert is still provisioning on GitHub Pages
# (https_enforced=false as of 2026-07-26). Using the github.io URL for images/link
# until the cert is live, so posts don't fail cert validation. Switch back once ready.
BASE = "https://ellyim.github.io/barra-math-site/assets"
SITE = "https://ellyim.github.io/barra-math-site/"

IG_ACCOUNT_ID = "6a66530b542d8bc5a60d8493"
PIN_ACCOUNT_ID = "6a665234542d8bc5a60d7b5f"

LEVEL_RANGES = {2:10,3:12,4:13,5:15,6:16,7:18,8:20,9:21,10:23,11:24,12:26,
                13:28,14:29,15:31,16:32,17:34,18:36,19:37,20:39,21:40}

def level_caption(n, rng):
    return (f"Level {n} of Barra's Number Sense journey — numbers within {rng}! "
            f"All 21 levels are free right now, link in bio. \U0001F9EE\n"
            f"#preschoolmath #numbersense #kindergartenmath #barmodel #homeschoolmath")

QUEUE = [{
    "image": f"{BASE}/promo/level-01_promo.png",
    "caption": level_caption(1, 10),
}]
for lv, rng in LEVEL_RANGES.items():
    QUEUE.append({
        "image": f"{BASE}/promo/level-{lv:02d}_promo.png",
        "caption": level_caption(lv, rng),
    })

QUEUE += [
    {"image": f"{BASE}/promo/shapes_promo.png",
     "caption": "New free pack: Shapes with Barra! Recognize, count & sort shapes — ages 5-6. Link in bio. \U0001F53A⚪️\U0001F7E9\n#preschoolmath #shapes #kindergarten #homeschool"},
    {"image": f"{BASE}/promo/time_promo.png",
     "caption": "New free pack: Time & Days with Barra! Telling time, days of the week, and fun time word problems. Link in bio. \U0001F550\n#preschoolmath #tellingtime #kindergarten #homeschool"},
    {"image": f"{BASE}/promo/patterns_promo.png",
     "caption": "New free pack: Patterns with Barra! AB & ABC repeating patterns — ages 5-6. Link in bio. \U0001F534\U0001F7E1\U0001F534\U0001F7E1\n#preschoolmath #patterns #kindergarten #homeschool"},
]

QUEUE += [
    {"image": f"{BASE}/carousel-01/carousel-01-singapore-math-secret-01.png",
     "caption": "Singapore has topped world math rankings 4 times since 1995 (TIMSS 2023, #1 of 64 countries). Here's the teaching method behind it \U0001F447\n#preschoolmath #singaporemath #barmodel #numbersense"},
    {"image": f"{BASE}/carousel-01/carousel-01-singapore-math-secret-03.png",
     "caption": "The numbers don't lie — TIMSS 2023 Grade 4 math scores. Singapore's method is behind this result.\n#preschoolmath #mathfacts #singaporemath #barmodel"},
    {"image": f"{BASE}/carousel-01/carousel-01-singapore-math-secret-04.png",
     "caption": "Meet the bar model: numbers become pictures kids can actually see. This is the core idea behind Barra Math.\n#preschoolmath #barmodel #numbersense #kindergartenmath"},
    {"image": f"{BASE}/carousel-01/carousel-01-singapore-math-secret-05.png",
     "caption": "Word problems, solved visually. This is how Barra teaches subtraction — no memorized steps required.\n#preschoolmath #barmodel #wordproblems #homeschoolmath"},
    {"image": f"{BASE}/carousel-01/carousel-01-singapore-math-secret-06.png",
     "caption": "Singapore Math textbooks are now used in 600+ U.S. schools. Here's why researchers went looking for what Singapore was doing differently.\n#preschoolmath #singaporemath #education"},
    {"image": f"{BASE}/carousel-01/carousel-01-singapore-math-secret-07.png",
     "caption": "Most worksheets skip straight from counting to equations. The bar model is the missing bridge — and it's free with Barra Math.\n#preschoolmath #barmodel #numbersense"},
    {"image": f"{BASE}/carousel-01/carousel-01-singapore-math-secret-08.png",
     "caption": "We built the Singapore Math approach into a free, story-driven worksheet series for ages 5-6. Link in bio.\n#preschoolmath #barmodel #kindergartenmath #homeschool"},
]

QUEUE += [
    {"image": f"{BASE}/barra_portrait.png",
     "caption": "Meet Barra! \U0001F44B Our bar-model mascot is here to make math feel like a story, not a worksheet. Free packs, link in bio.\n#preschoolmath #kindergarten #mathmascot"},
    {"image": f"{BASE}/scene_market.png",
     "caption": "Barra counts fruit at the market to practice number sense! Try it yourself — free worksheets in bio.\n#preschoolmath #countingpractice #homeschoolmath"},
    {"image": f"{BASE}/scene_sharing.png",
     "caption": "Sharing cookies = learning part-part-whole! That's the idea behind every Barra Math worksheet. Free download in bio.\n#preschoolmath #barmodel #numbersense"},
    {"image": f"{BASE}/scene_blocks.png",
     "caption": "Building blocks, building number sense. Meet the bar model with Barra! Free worksheets in bio.\n#preschoolmath #barmodel #kindergartenmath"},
]

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"index": 0, "history": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def curl_json(args):
    result = subprocess.run(["curl", "-s"] + args, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Non-JSON response:", result.stdout[:500], file=sys.stderr)
        raise

def main():
    key = os.environ.get("ZERNIO_API_KEY")
    if not key:
        print("ERROR: ZERNIO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    item = QUEUE[state["index"] % len(QUEUE)]

    payload = {
        "content": item["caption"],
        "mediaItems": [{"url": item["image"]}],
        "platforms": [
            {"platform": "instagram", "accountId": IG_ACCOUNT_ID},
            {"platform": "pinterest", "accountId": PIN_ACCOUNT_ID},
        ],
        "link": SITE,
        "publishNow": True,
    }
    resp = curl_json([
        "-X", "POST", "https://zernio.com/api/v1/posts",
        "-H", f"Authorization: Bearer {key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
    ])

    post_id = resp.get("post", {}).get("_id")
    print(f"Posted queue item {state['index']} -> post_id={post_id}, image={item['image']}")
    if "error" in resp:
        print("ERROR:", resp, file=sys.stderr)
        sys.exit(1)

    if post_id:
        time.sleep(20)
        status_resp = curl_json([
            "-H", f"Authorization: Bearer {key}",
            f"https://zernio.com/api/v1/posts/{post_id}",
        ])
        for p in status_resp.get("post", {}).get("platforms", []):
            print(f"  {p.get('platform')}: {p.get('status')} {p.get('platformPostUrl', '')}")

    state["index"] = (state["index"] + 1) % len(QUEUE)
    state["history"].append({"image": item["image"], "post_id": post_id})
    state["history"] = state["history"][-100:]
    save_state(state)

if __name__ == "__main__":
    main()
