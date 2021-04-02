"""This file is part of MORA

This runnable script allows the user to run MORA on probabilistic programs stored in files
For the command line arguments run the script with "--help".
"""
import glob
from argparse import ArgumentParser
from parser import Parser

arg_parser = ArgumentParser(description="Run MORA on probabilistic programs stored in files")

arg_parser.add_argument(
    "--benchmarks",
    dest="benchmarks",
    required=True,
    type=str,
    nargs="+",
    help="A list of benchmarks to run MORA on"
)

arg_parser.add_argument(
    "--goals",
    dest="goals",
    type=int,
    nargs="+",
    default=[1, 2, 3],
    help="A list of moments MORA should consider"
)


def main():
    args = arg_parser.parse_args()
    args.benchmarks = [b for bs in map(glob.glob, args.benchmarks) for b in bs]

    for benchmark in args.benchmarks:
        parser = Parser()
        parser.parse_file(benchmark)


if __name__ == "__main__":
    main()
