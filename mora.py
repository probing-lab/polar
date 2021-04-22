"""This file is part of MORA

This runnable script allows the user to run MORA on probabilistic programs stored in files
For the command line arguments run the script with "--help".
"""
import glob
import time
from symengine.lib.symengine_wrapper import sympify
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

arg_parser.add_argument(
    "--transform_categoricals",
    action="store_true",
    default=False,
    help="If set transform categorical assignments into multiple individual assignments"
)

arg_parser.add_argument(
    "--cond2arithm",
    action="store_true",
    default=False,
    help="If set converts all conditions to arithmetic ahead of the main computation"
)


def main():
    args = arg_parser.parse_args()
    args.benchmarks = [b for bs in map(glob.glob, args.benchmarks) for b in bs]

    if len(args.benchmarks) == 0:
        raise Exception("No benchmark given.")

    start = time.time()
    for benchmark in args.benchmarks:
        parser = Parser()
        try:
            program = parser.parse_file(benchmark, args.transform_categoricals)
            program = DistTransformer().execute(program)
            program = IfTransformer().execute(program)
            program = MultiAssignTransformer().execute(program)
            program = TypeInferer().execute(program)
            if args.cond2arithm:
                program = ConditionsToArithm().execute(program)
            program = PrepareTransformer().execute(program)
            print(program)
            rec_builder = RecBuilder(program)
            recurrences = rec_builder.get_recurrences(sympify("x**2*y**2"))
            print(recurrences[0])
            print(f"Elapsed time: {time.time() - start} s")
        except Exception as e:
            print(e)
            raise e
            exit()


if __name__ == "__main__":
    main()
