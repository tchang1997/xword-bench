import argparse
import json

def extract_answer(puzzle, clue_num, direction):
    cells = get_cells_for_clue(puzzle, clue_num, direction)
    return "".join(puzzle["answers"][r][c] for r, c in cells)

def get_cells_for_clue(puzzle, clue_num, direction):
    gridnums = puzzle["gridnums"]
    rows, cols = len(gridnums), len(gridnums[0])
    cells = []
    for r in range(rows):
        for c in range(cols):
            if gridnums[r][c] == clue_num:
                dr, dc = (0, 1) if direction == "Across" else (1, 0)
                for i in range(puzzle["clues"][direction.lower()][str(clue_num)]["length"]):
                    rr, cc = r + i * dr, c + i * dc
                    if puzzle["answers"][rr][cc] == "":
                        break
                    cells.append((rr, cc))
                return cells
    raise ValueError(f"Clue number {clue_num} not found in grid")

def evaluate_correctness(puzzle, predictions):
    correct = {"Across": {}, "Down": {}}
    for direction in ["Across", "Down"]:
        for num, _ in puzzle["clues"][direction.lower()].items():
            pred = predictions.get(direction, {}).get(num)
            if pred is None:
                correct[direction][num] = False
                continue
            # Get actual answer from the solution grid
            true_answer = extract_answer(puzzle, int(num), direction)
            correct[direction][num] = (pred.upper() == true_answer)
    return correct


def check_length_violations(puzzle, predictions):
    violations = {"Across": {}, "Down": {}}
    for direction in ["Across", "Down"]:
        for num, clue in puzzle["clues"][direction.lower()].items():
            pred = predictions.get(direction, {}).get(num)
            if pred is None:
                continue
            expected = clue["length"]
            actual = len(pred)
            if actual != expected:
                violations[direction][num] = {"expected": expected, "actual": actual}
    return violations


def check_grid_constraints(puzzle, predictions):
    grid_size = puzzle["size"]
    grid_pred = [[None for _ in range(grid_size["cols"])] for _ in range(grid_size["rows"])]

    # Apply across and down predictions to grid
    for direction in ["Across", "Down"]:
        for num_str, guess in predictions.get(direction, {}).items():
            cells = get_cells_for_clue(puzzle, int(num_str), direction)
            for (r, c), char in zip(cells, guess.upper()):
                if grid_pred[r][c] is None:
                    grid_pred[r][c] = char
                elif grid_pred[r][c] != char:
                    grid_pred[r][c] = "*"  # Conflict

    # Compare to actual answer grid
    constraint_violations = []
    for r in range(grid_size["rows"]):
        for c in range(grid_size["cols"]):
            pred = grid_pred[r][c]
            true = puzzle["answers"][r][c]
            if pred is None or pred == "*":
                continue
            if true and pred != true:
                constraint_violations.append((r, c, pred, true))
    return constraint_violations

def main():
    parser = argparse.ArgumentParser(description="Evaluate crossword submissions.")
    parser.add_argument("--puzzle", required=True, help="Path to puzzle JSON")
    parser.add_argument("--solution", required=True, help="Path(s) to solution JSON(s)")
    parser.add_argument(
        "--eval-functions",
        nargs="+",
        choices=["correctness", "length", "grid"],
        default=["correctness", "length", "grid"],
        help="Evaluation checks to run",
    )

    args = parser.parse_args()

    with open(args.puzzle, "r") as f:
        puzzle = json.load(f)

    with open(args.solution, "r") as f:
        predictions = json.load(f)

    print(f"\n=== Evaluating: {args.solution} ===")

    if "correctness" in args.eval_functions:
        correctness = evaluate_correctness(puzzle, predictions)
        total = sum(len(puzzle["clues"][k.lower()]) for k in ["Across", "Down"])
        correct = sum(v for d in correctness.values() for v in d.values())
        print(f"Answer correctness: {correct}/{total} clues correct")
        for direction in ["Across", "Down"]:
            for num, is_correct in correctness[direction].items():
                if not is_correct:
                    pred = predictions.get(direction, {}).get(num)
                    try:
                        truth = extract_answer(puzzle, int(num), direction)
                    except Exception as e:
                        truth = f"<error: {e}>"
                    print(f" \t* {num}-{direction}: expected {truth}, got {pred}")

    if "length" in args.eval_functions:
        length_violations = check_length_violations(puzzle, predictions)
        count = sum(len(v) for v in length_violations.values())
        print(f"Length violations: {count}")
        for dir_, issues in length_violations.items():
            for num, vals in issues.items():
                print(f"\t* {num}-{dir_}: expected {vals['expected']}, got {vals['actual']}")

    if "grid" in args.eval_functions:
        constraint_violations = check_grid_constraints(puzzle, predictions)
        print(f"Grid consistency violations: {len(constraint_violations)}")
        for r, c, _, _ in constraint_violations:
            print(f" \t* Cell ({r}, {c})")

if __name__ == "__main__":
    main()