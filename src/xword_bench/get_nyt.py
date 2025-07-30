from argparse import ArgumentParser

import requests
import json
import os
from pathlib import Path
import time

# === USER CONFIG ===
NYT_COOKIE = os.environ["NYT_COOKIE"]  # <- paste from browser

SAVE_DIR = Path("nyt_full")
# ====================

SAVE_DIR.mkdir(exist_ok=True)
HEADERS = {"Cookie": f"NYT-S={NYT_COOKIE}"}

# generated via GPT-4o
def get_full_puzzle_ids(start_date, end_date):
    url = f"https://www.nytimes.com/svc/crosswords/v3/36569100/puzzles.json?date_start={start_date}&date_end={end_date}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    data = r.json()["results"]
    return [p["puzzle_id"] for p in data if p.get("publish_type") == "Daily"]

def download_puzzle(puzzle_id):
    url = f"https://www.nytimes.com/svc/crosswords/v6/puzzle/{puzzle_id}.json"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def save_puzzle(puzzle_data):
    pid = puzzle_data["id"]
    date = puzzle_data["publicationDate"]
    with open(SAVE_DIR / f"{date}.json", "w") as f:
        json.dump(puzzle_data, f)

if __name__ == "__main__":
    psr = ArgumentParser()
    psr.add_argument("--start", default="2025-01-01", type=str)
    psr.add_argument("--end", default="2025-01-31", type=str)
    args = psr.parse_args()

    ids = get_full_puzzle_ids(args.start, args.end)
    print(f"Found {len(ids)} puzzles between {args.start} and {args.end}")
    for pid in ids:
        data = download_puzzle(pid)
        save_puzzle(data)
        print(f"✅ Saved puzzle {pid}")
        time.sleep(1)  

