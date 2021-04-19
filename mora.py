"""This file is part of MORA

This runnable script allows the user to run MORA on probabilistic programs stored in files
For the command line arguments run the script with "--help".
"""
import glob
import time
from diofant import sympify
from argparse import ArgumentParser
from inputparser import Parser
from program.transformer import *
from recurrences import *

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

    start = time.time()
    for benchmark in args.benchmarks:
        parser = Parser()
        try:
            program = parser.parse_file(benchmark)
            program = DistTransformer().execute(program)
            program = IfTransformer().execute(program)
            program = MultiAssignTransformer().execute(program)
            program = TypeInferer().execute(program)
            program = ConditionsToArithm().execute(program)
            program = PrepareTransformer().execute(program)
            print(program)
            rec_builder = RecBuilder(program)
            recurrences = rec_builder.get_recurrences(sympify("x"))
            print(recurrences)
            print(f"Elapsed time: {time.time() - start} s")
        except Exception as e:
            print(e)
            raise e
            exit()


if __name__ == "__main__":
    main()
