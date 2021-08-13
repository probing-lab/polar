"""This file is part of MORA

This runnable script allows the user to run MORA on probabilistic programs stored in files
For the command line arguments run the script with "--help".
"""
import glob
import time
from copy import deepcopy
from argparse import ArgumentParser
from inputparser import Parser, GoalParser, MOMENT, TAIL_BOUND_LOWER, TAIL_BOUND_UPPER
from program.transformer import *
from recurrences import RecBuilder
from recurrences.solver import RecurrenceSolver
from symengine.lib.symengine_wrapper import Piecewise, Symbol, sympify
from sympy import N
from simulation import Simulator
from plots import StatesPlot, RunsPlot
from utils import indent_string
from termcolor import colored

header = """
  __  __  ____  _____            
 |  \/  |/ __ \|  __ \     /\    
 | \  / | |  | | |__) |   /  \   
 | |\/| | |  | |  _  /   / /\ \  
 | |  | | |__| | | \ \  / ____ \ 
 |_|  |_|\____/|_|  \_\/_/    \_\  By the PROBING group
"""

arg_parser = ArgumentParser(description="Run MORA on probabilistic programs stored in files")

arg_parser.add_argument(
    "benchmarks",
    metavar="benchmarks",
    type=str,
    nargs="+",
    help="A list of benchmarks to run MORA on"
)

arg_parser.add_argument(
    "--at_n",
    dest="at_n",
    default=-1,
    type=int,
    help="Iteration number to evaluate the expressions at"
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
    default="",
    help="A monomial to plot"
)

arg_parser.add_argument(
    "--states_plot",
    action="store_true",
    default=False,
    help="If true the states distribution gets plotted in an animated way"
)

arg_parser.add_argument(
    "--plot_expectation",
    action="store_true",
    default=False,
    help="If true the exact expectation gets included in the plot"
)

arg_parser.add_argument(
    "--plot_std",
    action="store_true",
    default=False,
    help="If true the exact standard deviation gets included in the plot"
)

arg_parser.add_argument(
    "--max_y",
    dest="max_y",
    type=int,
    help="The maximum value on the y axis of the states plot."
)

arg_parser.add_argument(
    "--anim_iter",
    action="store_true",
    default=False,
    help="If true the iterations are animated in the runs plot."
)

arg_parser.add_argument(
    "--anim_runs",
    action="store_true",
    default=False,
    help="If true the runs are animated in the runs plot."
)

arg_parser.add_argument(
    "--anim_time",
    dest="anim_time",
    default=10.0,
    type=float,
    help="The duration of plot animations in seconds. It is not exact as the time needed to compute the frame is neglected"
)

arg_parser.add_argument(
    "--anim_iterations",
    action="store_true",
    default=False,
    help="If true the iterations are animated in the runs plot"
)

arg_parser.add_argument(
    "--yscale",
    dest="yscale",
    type=str,
    default="linear",
    help="The y-scale for the plot"
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

arg_parser.add_argument(
    "--numeric_roots",
    action="store_true",
    default=False,
    help="If set the roots in the recurrence computation will be computed numerically"
)

arg_parser.add_argument(
    "--numeric_croots",
    action="store_true",
    default=False,
    help="If set the complex roots in the recurrence computation will be computed numerically"
)

arg_parser.add_argument(
    "--numeric_eps",
    dest="numeric_eps",
    default=1e-10,
    type=float,
    help="Interval epsilon for the potential approximation of roots"
)

arg_parser.add_argument(
    "--tail_bound_moments",
    dest="tail_bound_moments",
    default=2,
    type=int,
    help="The number of moments to consider when computing Markov's inequality"
)


def simulate(args):
    for benchmark in args.benchmarks:
        parser = Parser()
        try:
            program = parser.parse_file(benchmark, args.transform_categoricals)
            print(colored("------------------", "magenta"))
            print(colored("- Parsed program -", "magenta"))
            print(colored("------------------", "magenta"))
            print(program)
            print()

            goals = []
            for goal in args.goals:
                goal_type, goal_data = GoalParser.parse(goal)
                if goal_type == MOMENT:
                    goals.append(goal_data[0])
                if goal_type == TAIL_BOUND_UPPER:
                    goals.append(Piecewise((1, goal_data[0] >= goal_data[1]), (0, True)))
                if goal_type == TAIL_BOUND_LOWER:
                    goals.append(Piecewise((1, goal_data[0] > goal_data[1]), (0, True)))

            simulator = Simulator(args.simulation_iter)
            result = simulator.simulate(program, goals, args.number_samples)

            print(colored("---------------------", "cyan"))
            print(colored("- Simulation Result -", "cyan"))
            print(colored("---------------------", "cyan"))
            print()

            for goal, mean in result.get_average_goals().items():
                if isinstance(goal, Piecewise):
                    print(f"P({goal.args[1]}) = {mean}")
                else:
                    print(f"E({goal}) = {mean}")
            print()

        except Exception as e:
            print(e)
            exit()


def plot(args):
    for benchmark in args.benchmarks:
        try:
            monom = sympify(args.plot)
            first_moment = second_moment = None
            if args.plot_expectation or args.plot_std:
                program = prepare_program(benchmark, args)
                rec_builder = RecBuilder(program)
                solvers = {}
                solver_args = deepcopy(args)
                solver_args.numeric_roots = True
                solver_args.numeric_croots = True
                solver_args.numeric_eps = 0.0000001
                if args.plot_std:
                    second_moment, _ = get_moment(monom ** 2, solvers, rec_builder, solver_args)
                first_moment, _ = get_moment(monom, solvers, rec_builder, solver_args)

            program = Parser().parse_file(benchmark, args.transform_categoricals)
            simulator = Simulator(args.simulation_iter)
            result = simulator.simulate(program, [monom], args.number_samples)
            if args.states_plot:
                states_plot = StatesPlot(result, monom, args.anim_time, args.max_y, first_moment, second_moment)
                states_plot.draw()
            else:
                runs_plot = RunsPlot(result, monom, args.yscale, args.anim_iter, args.anim_runs, args.anim_time, first_moment, second_moment)
                runs_plot.draw()

        except Exception as e:
            raise e
            print(e)
            exit()


def compute_symbolically(args):
    for benchmark in args.benchmarks:
        try:
            program = prepare_program(benchmark, args)
            rec_builder = RecBuilder(program)
            solvers = {}

            print(colored("-------------------", "cyan"))
            print(colored("- Analysis Result -", "cyan"))
            print(colored("-------------------", "cyan"))
            print()

            for goal in args.goals:
                goal_type, goal_data = GoalParser.parse(goal)
                if goal_type == MOMENT:
                    handle_moment_goal(goal_data, solvers, rec_builder, args)
                elif goal_type == TAIL_BOUND_UPPER:
                    handle_tail_bound_upper_goal(goal_data, solvers, rec_builder, args)
                elif goal_type == TAIL_BOUND_LOWER:
                    handle_tail_bound_lower_goal(goal_data, solvers, rec_builder, args)
                else:
                    raise RuntimeError(f"Goal type {goal_type} does not exist.")
        except Exception as e:
            print(e)
            exit()


def handle_moment_goal(goal_data, solvers, rec_builder, args):
    monom = goal_data[0]
    moment, is_exact = get_moment(monom, solvers, rec_builder, args)
    print(f"E({monom}) = {moment}")
    if is_exact:
        print(colored("Solution is exact", "green"))
    else:
        print(colored("Solution is rounded", "yellow"))
    if args.at_n >= 0:
        moment_at_n = moment.xreplace({Symbol("n", integer=True, positive=True): args.at_n}).expand()
        print(f"E({monom} | n={args.at_n}) = {moment_at_n} ≅ {N(moment_at_n)}")
    print()


def handle_tail_bound_upper_goal(goal_data, solvers, rec_builder, args):
    monom, a = goal_data[0], goal_data[1]
    moments = {}
    is_always_exact = True
    for k in reversed(range(1, args.tail_bound_moments + 1)):
        monom_power = monom ** k
        moment, is_exact = get_moment(monom_power, solvers, rec_builder, args)
        moments[k] = moment
        is_always_exact = is_always_exact and is_exact

    bounds = [m / (a ** k) for k, m in moments.items()]
    bounds.reverse()
    print(f"Assuming {monom} is non-negative.")
    print(f"P({monom} >= {a}) <= minimum of")
    count = 1
    for bound in bounds:
        print(indent_string(f"({count}) {bound}", 4))
        count += 1
    if is_always_exact:
        print(colored("Solution is exact", "green"))
    else:
        print(colored("Solution is rounded", "yellow"))

    if args.at_n >= 0:
        bounds_at_n = [b.xreplace({Symbol("n", integer=True, positive=True): args.at_n}).expand() for b in bounds]
        can_take_min = all([not b.free_symbols for b in bounds_at_n])
        if can_take_min:
            bound_at_n = min(bounds_at_n)
            print(f"P({monom} >= {a} | n={args.at_n}) <= {bound_at_n} ≅ {N(bound_at_n)}")
        else:
            print(f"P({monom} >= {a} | n={args.at_n}) <= minimum of")
            count = 1
            for bound_at_n in bounds_at_n:
                print(indent_string(f"({count}) {bound_at_n} ≅ {N(bound_at_n)}", 4))
                count += 1
    print()


def handle_tail_bound_lower_goal(goal_data, solvers, rec_builder, args):
    monom, a = goal_data[0], goal_data[1]
    second_moment, is_exact2 = get_moment(monom ** 2, solvers, rec_builder, args)
    first_moment, is_exact1 = get_moment(monom, solvers, rec_builder, args)
    bound = ((first_moment - a) ** 2) / (second_moment - 2*a*first_moment + a**2)
    bound = bound.simplify()
    print(f"Assuming {monom - a} is non-negative.")
    print(f"P({monom} > {a}) >= {bound}")
    if is_exact1 and is_exact2:
        print(colored("Solution is exact", "green"))
    else:
        print(colored("Solution is rounded", "yellow"))
    if args.at_n >= 0:
        bound_at_n = bound.xreplace({Symbol("n", integer=True, positive=True): args.at_n}).expand()
        print(f"P({monom} > {a} | n={args.at_n}) >= {bound_at_n} ≅ {N(bound_at_n)}")
    print()


def get_moment(monom, solvers, rec_builder, args):
    if monom not in solvers:
        recurrences = rec_builder.get_recurrences(monom)
        s = RecurrenceSolver(recurrences, args.numeric_roots, args.numeric_croots, args.numeric_eps)
        solvers.update({sympify(m): s for m in recurrences.monomials})

    solver = solvers[monom]
    return sympify(solver.get(monom)), solver.is_exact


def prepare_program(benchmark, args):
    parser = Parser()
    program = parser.parse_file(benchmark, args.transform_categoricals)

    print(colored("------------------", "magenta"))
    print(colored("- Parsed program -", "magenta"))
    print(colored("------------------", "magenta"))
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
    # Replace/Add constants in loop body
    program = ConstantsTransformer().execute(program)
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

    print(colored("-----------------------", "magenta"))
    print(colored("- Transformed program -", "magenta"))
    print(colored("-----------------------", "magenta"))
    print(program)
    print()
    return program


def main():
    print(colored(header, "green"))
    print()
    print()

    start = time.time()
    args = arg_parser.parse_args()
    args.benchmarks = [b for bs in map(glob.glob, args.benchmarks) for b in bs]

    if len(args.benchmarks) == 0:
        raise Exception("No benchmark given.")

    if args.simulate:
        simulate(args)
    if args.plot:
        plot(args)
    else:
        compute_symbolically(args)
    print(f"Elapsed time: {time.time() - start} s")


if __name__ == "__main__":
    main()
