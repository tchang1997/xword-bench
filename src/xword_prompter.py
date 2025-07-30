import argparse
import json
from abc import ABC, abstractmethod

class CrosswordPrompt(ABC):
    @staticmethod
    @abstractmethod
    def to_prompt(file_path: str) -> str:
        pass

class SimpleCrosswordPrompt(CrosswordPrompt):
    @staticmethod
    def instruction_block() -> str:
        return (
            "You are solving a crossword puzzle. You will be provided the layout of the grid, as well "
            "as all of the clues you will need. Each clue will be in the format `#. [CLUE] (length)`."
        )

    @staticmethod
    def grid_block(gridnums: list[list[int]]) -> str:
        lines = []
        for row in gridnums:
            cells = []
            for n in row:
                cells.append(" . " if n == 0 else f"{n:2d}")
            lines.append(" ".join(cells))
        return "The grid is:\n" + "\n".join(lines)

    @staticmethod
    def clues_block(clues: dict[str, dict]) -> str:
        def fmt(clue_dict: dict) -> str:
            return "\n".join(
                f"{num}. {clue['text']} ({clue['length']})"
                for num, clue in sorted(clue_dict.items(), key=lambda x: int(x[0]))
            )

        across = fmt(clues.get("across", {}))
        down   = fmt(clues.get("down",   {}))
        return "Clues (Across):\n" + across + "\n\nClues (Down):\n" + down

    @staticmethod
    def answer_format_block() -> str:
        return (
            "Return your answers in the following JSON format:\n\n"
            "{\n"
            '  "Across": {\n'
            '    "#": "ANSWER",\n'
            '    "#": "ANSWER",\n'
            "    ...\n"
            "  },\n"
            '  "Down": {\n'
            '    "#": "ANSWER",\n'
            '    "#": "ANSWER",\n'
            "    ...\n"
            "  }\n"
            "}\n"
        )

    @staticmethod
    def to_prompt(file_path: str) -> str:
        with open(file_path, "r") as f:
            puzzle = json.load(f)

        blocks = [
            SimpleCrosswordPrompt.instruction_block(),
            SimpleCrosswordPrompt.grid_block(puzzle["gridnums"]),
            SimpleCrosswordPrompt.clues_block(puzzle["clues"]),
            SimpleCrosswordPrompt.answer_format_block(),
        ]
        return "\n\n".join(blocks)


def get_prompt_class(name: str):
    if name == "SimpleCrosswordPrompt":
        return SimpleCrosswordPrompt
    else:
        raise ValueError(f"Unknown prompt class: {name}")

def main():
    parser = argparse.ArgumentParser(description="Generate crossword prompt from JSON.")
    parser.add_argument("json_file", help="Path to the crossword JSON file")
    parser.add_argument(
        "--prompt-class",
        default="SimpleCrosswordPrompt",
        help="Name of the prompt class to use",
    )
    args = parser.parse_args()

    prompt_class = get_prompt_class(args.prompt_class)
    prompt = prompt_class.to_prompt(args.json_file)
    print(prompt)


if __name__ == "__main__":
    main()
