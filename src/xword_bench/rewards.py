import argparse
import json

from xword_bench.evaluation import (
    evaluate_correctness,
    check_length_violations,
    check_grid_constraints,
)

def reward_correctness(puzzle, predictions, normalize=True):
    correctness = evaluate_correctness(puzzle, predictions)
    num_total = sum(len(puzzle["clues"][k.lower()]) for k in ["Across", "Down"])
    num_correct = sum(v for d in correctness.values() for v in d.values())
    return num_correct / num_total if normalize else num_correct

def reward_length(puzzle, predictions, normalize=True):
    violations = check_length_violations(puzzle, predictions)
    num_total = sum(len(puzzle["clues"][k.lower()]) for k in ["Across", "Down"])
    num_violations = sum(len(v) for v in violations.values())
    return 1.0 - (num_violations / num_total) if normalize else -num_violations

def reward_grid_consistency(puzzle, predictions, normalize=True):
    violations = check_grid_constraints(puzzle, predictions)
    num_total_cells = puzzle["size"]["rows"] * puzzle["size"]["cols"]
    num_violations = len(violations)
    return 1.0 - (num_violations / num_total_cells) if normalize else -num_violations

def reward_json_format_adherence(predictions):
    if not isinstance(predictions, dict):
        return 0.0
    if "Across" not in predictions or "Down" not in predictions:
        return 0.0
    if not isinstance(predictions["Across"], dict) or not isinstance(predictions["Down"], dict):
        return 0.0
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in predictions["Across"].items()):
        return 0.0
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in predictions["Down"].items()):
        return 0.0
    return 1.0


REWARD_FN_MAP = {
    "correctness": reward_correctness,
    "length": reward_length,
    "grid": reward_grid_consistency,
    "json_format": reward_json_format_adherence,
}

def main():
    # testing entry point 
    parser = argparse.ArgumentParser(description="Compute rewards for crossword submissions.")
    parser.add_argument("--puzzle", required=True, help="Path to puzzle JSON")
    parser.add_argument("--solution", required=True, help="Path(s) to submission JSON(s)")
    parser.add_argument(
        "--reward-functions",
        nargs="+",
        choices=list(REWARD_FN_MAP.keys()),
        default=list(REWARD_FN_MAP.keys()),
        help="Which reward functions to apply",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable normalization of correctness/length/grid rewards",
    )
    args = parser.parse_args()

    with open(args.puzzle, "r") as f:
        puzzle = json.load(f)
    with open(args.solution, "r") as f:
        predictions = json.load(f)

    print(f"\n=== Rewards for: {args.solution} ===")
    for name in args.reward_functions:
        fn = REWARD_FN_MAP[name]
        if name == "json_format":
            score = fn(predictions)
        else:
            score = fn(puzzle, predictions, normalize=not args.no_normalize)
        print(f"{name}: {score:.4f}")

if __name__ == "__main__":
    main()
