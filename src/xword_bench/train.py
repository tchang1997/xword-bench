from argparse import ArgumentParser
from pathlib import Path

from datasets import Dataset
from trl import GRPOTrainer

from xword_bench.rewards import REWARD_FN_MAP


if __name__ == '__main__':
    psr = ArgumentParser()
    psr.add_argument("--data-dir", default="data/nyt_parsed", type=str)
    args = psr.parse_args()

    dataset = create_dataset(args.data_dir, cfg["prompt_class"])
    trainer = GRPOTrainer(
        model=cfg["model"], # Qwen/Qwen3-4B
        reward_funcs=[REWARD_FN_MAP[name] for name in cfg["rewards"]],
        args=training_args,
        train_dataset=dataset,
    )
    trainer.train()