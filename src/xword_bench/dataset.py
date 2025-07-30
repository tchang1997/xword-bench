from pathlib import Path

from datasets import Dataset

from xword_bench.xword_prompter import get_prompt_class

def create_dataset(data_dir: str, prompt_class: str):
    prompts = []
    for file in Path(data_dir).iterdir():
        prompt_class = get_prompt_class(prompt_class)
        prompt = prompt_class.to_prompt(file)
        prompts.append(prompt)
    return Dataset.from_list({"prompt": [prompts]})
