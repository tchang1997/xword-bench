# TODO: script for vLLM inference
from argparse import ArgumentParser

from xword_bench.dataset import create_dataset

if __name__ == '__main__':
    psr = ArgumentParser()
    psr.add_argument("--data-dir", type=str, required=True)
    psr.add_argument("--prompt-class", type=str, default="SimpleCrosswordPrompt")
    psr.add_argument("--endpoint", type=int, required=True)
    args = psr.parse_args()

    dataset = create_dataset(args.data_dir, args.prompt_class)