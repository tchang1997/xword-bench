import argparse
import json
from pathlib import Path

from typing import Dict, List

def parse_cells(cells: List[Dict], width: int, height: int):
    grid = [["" for _ in range(width)] for _ in range(height)]
    gridnums = [[0 for _ in range(width)] for _ in range(height)]

    for idx, cell in enumerate(cells):
        row, col = divmod(idx, width)
        if "answer" in cell:
            grid[row][col] = cell["answer"]
        if "label" in cell and cell["label"].isdigit():
            gridnums[row][col] = int(cell["label"])

    return grid, gridnums


def extract_clues(clues_list: List[Dict]):
    clues = {"across": {}, "down": {}}
    for clue in clues_list:
        dir_key = clue["direction"].lower()
        label = clue["label"]
        clue_text = " ".join(t["plain"] for t in clue["text"])
        length = len(clue["cells"])
        clues[dir_key][label] = {
            "text": clue_text,
            "length": length,
        }
    return clues


def parse_puzzle(puzzle_json):
    body = puzzle_json["body"][0]
    cells = body["cells"]
    width = body["dimensions"]["width"]
    height = body["dimensions"]["height"]
    raw_clues = body["clues"]

    grid, gridnums = parse_cells(cells, width, height)
    clues = extract_clues(raw_clues)
    size = {"rows": height, "cols": width}
    results = {
        "puzzle_id": puzzle_json["id"],
        "date": puzzle_json["publicationDate"],
        "title": puzzle_json.get("title", ""),
        "author": ", ".join(puzzle_json.get("constructors", [])),
        "size": size,
        "gridnums": gridnums,
        "answers": grid,
        "clues": clues,
    }

    return results

def batch_parse(input_dir: Path, output_dir: Path):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in input_dir.glob("*.json"):
        try:
            with open(file) as f:
                raw = json.load(f)
            structured = parse_puzzle(raw)
            output_path = output_dir / (file.stem + ".parsed.json")
            with open(output_path, "w") as f:
                json.dump(structured, f, indent=2)
            print(f"✅ Parsed {file.name}")
        except Exception as e:
            print(f"❌ Failed {file.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse raw NYT puzzle JSONs into structured format.")
    parser.add_argument("--input_dir", type=Path, help="Directory with raw NYT puzzle JSONs", default="nyt_full")
    parser.add_argument("--output_dir", type=Path, help="Directory to write parsed JSONs", default="nyt_parsed")
    args = parser.parse_args()

    batch_parse(args.input_dir, args.output_dir)

