from argparse import ArgumentParser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import requests
import json
import os
from pathlib import Path
import time

# === USER CONFIG ===
NYT_COOKIE = os.environ["NYT_COOKIE"]  # <- paste from browser

SAVE_DIR = Path("data/nyt_full")
# ====================

SAVE_DIR.mkdir(exist_ok=True)
HEADERS = {"Cookie": f"NYT-S={NYT_COOKIE}"}


def chunk_date_range(start_date_str, end_date_str):
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")

    chunks = []
    current_start = start

    while current_start < end:
        current_end = min(current_start + relativedelta(months=3) - timedelta(days=1), end)
        chunks.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
        current_start = current_end + timedelta(days=1)

    return chunks

def get_full_puzzle_ids(start_date, end_date):
    # the API only returns ~3 months of puzzles, so we need to chunk if we are requesting a window longer than that.
    puzzles = []
    for chunk_start, chunk_end in chunk_date_range(start_date, end_date):
        url = f"https://www.nytimes.com/svc/crosswords/v3/36569100/puzzles.json?date_start={chunk_start}&date_end={chunk_end}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        data = r.json()["results"]
        for p in data:
            if p.get("publish_type") == "Daily":
                curr_date = p.get("print_date")
                if (SAVE_DIR / f'{curr_date}.json').exists():
                    print(f"Found puzzle for {curr_date} - skipping")
                else:
                    puzzles.append(p["puzzle_id"])
    return puzzles

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

