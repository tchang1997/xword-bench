from argparse import ArgumentParser

from datasets import Dataset

def create_dataset(data_dir: str):
    pass
    

if __name__ == '__main__':
    psr = ArgumentParser()
    psr.add_argument("--data-dir", default="nyt_parsed", type=str)
    args = psr.parse_args()
