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
    type=str,
    default=[],
    nargs="+",
    help="A list of moments MORA should compute"
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

arg_parser.add_argument(
    "--disable_type_inference",
    action="store_true",
    default=False,
    help="If set there won't be automatic type inference"
)

arg_parser.add_argument(
    "--type_fp_iterations",
    dest="type_fp_iterations",
    default=100,
    type=int,
    help="Number of iterations in the fixedpoint computation of the type inference"
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

            # Transform non-constant distributions parameters
            program = DistTransformer().execute(program)

            # Flatten if-statements
            program = IfTransformer().execute(program)

            # Make sure every variable has only 1 assignment
            program = MultiAssignTransformer().execute(program)

            # Create aliases for expressions in conditions.
            program = ConditionsReducer().execute(program)

            # Update program info like variables and symbols
            program = UpdateInfoTransformer().execute(program)

            # Infer types for variables
            if not args.disable_type_inference:
                program = TypeInferer(args.type_fp_iterations).execute(program)

            # Turn all conditions into normalized form
            program = ConditionsNormalizer().execute(program)

            # Convert all conditions to arithmetic
            if args.cond2arithm:
                program = ConditionsToArithm().execute(program)
                program = UpdateInfoTransformer().execute(program)

            print(program)

            rec_builder = RecBuilder(program)
            for goal in args.goals:
                monom = sympify(goal)
                recurrences = rec_builder.get_recurrences(monom)
                print(recurrences)

            print(f"Elapsed time: {time.time() - start} s")
        except Exception as e:
            print(e)
            raise e
            exit()


if __name__ == "__main__":
    main()
