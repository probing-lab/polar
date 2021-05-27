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
from recurrences import RecBuilder, RecurrenceSolver
from simulation import Simulator

arg_parser = ArgumentParser(description="Run MORA on probabilistic programs stored in files")

arg_parser.add_argument(
    "benchmarks",
    metavar="benchmarks",
    type=str,
    nargs="+",
    help="A list of benchmarks to run MORA on"
)

arg_parser.add_argument(
    "--simulate",
    action="store_true",
    default=False,
    help="If set MORA simulates the program"
)

arg_parser.add_argument(
    "--simulation_iter",
    dest="simulation_iter",
    default=100,
    type=int,
    help="Number of iterations after which the simulation stops."
)

arg_parser.add_argument(
    "--number_samples",
    dest="number_samples",
    default=100,
    type=int,
    help="The number of samples to simulate."
)

arg_parser.add_argument(
    "--goals",
    dest="goals",
    type=str,
    default=[],
    nargs="+",
    help="A list of moments MORA should compute or simulate"
)

arg_parser.add_argument(
    "--plot",
    dest="plot",
    type=str,
    default=[],
    nargs="+",
    help="A list of moments MORA should plot. Only available in simulation mode."
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

    if args.simulate:
        simulate(args)
    else:
        compute_moments(args)


def simulate(args):
    start = time.time()
    for benchmark in args.benchmarks:
        parser = Parser()
        try:
            program = parser.parse_file(benchmark, args.transform_categoricals)
            print(program)
            print()

            simulator = Simulator(args.simulation_iter)
            result = simulator.simulate(program, args.goals, args.number_samples)
            for goal, mean in result.get_average_goals().items():
                print(f"Mean {goal}: {mean}")

            for plot in args.plot:
                result.plot_animated(plot)

            print(f"Elapsed time: {time.time() - start} s")
        except Exception as e:
            print(e)
            exit()


def compute_moments(args):
    start = time.time()
    for benchmark in args.benchmarks:
        parser = Parser()
        try:
            program = parser.parse_file(benchmark, args.transform_categoricals)

            print(program)
            print()

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

            print(program)
            print()

            rec_builder = RecBuilder(program)
            for goal in args.goals:
                monom = sympify(goal)
                recurrences = rec_builder.get_recurrences(monom)
                solver = RecurrenceSolver()
                solver.set_recurrences(recurrences)
                solver.solve()

            print(f"Elapsed time: {time.time() - start} s")
        except Exception as e:
            print(e)
            raise e
            exit()


if __name__ == "__main__":
    main()
