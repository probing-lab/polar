from argparse import Namespace
from .action import Action
from inputparser import Parser, GoalParser, MOMENT, TAIL_BOUND_LOWER, TAIL_BOUND_UPPER
from symengine.lib.symengine_wrapper import Piecewise
from simulation import Simulator
from termcolor import colored


class SimulationAction(Action):

    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        parser = Parser()
        program = parser.parse_file(benchmark, self.cli_args.transform_categoricals)
        print(colored("------------------", "magenta"))
        print(colored("- Parsed program -", "magenta"))
        print(colored("------------------", "magenta"))
        print(program)
        print()

        goals = []
        for goal in self.cli_args.goals:
            goal_type, goal_data = GoalParser.parse(goal)
            if goal_type == MOMENT:
                goals.append(goal_data[0])
            if goal_type == TAIL_BOUND_UPPER:
                goals.append(Piecewise((1, goal_data[0] >= goal_data[1]), (0, True)))
            if goal_type == TAIL_BOUND_LOWER:
                goals.append(Piecewise((1, goal_data[0] > goal_data[1]), (0, True)))

        simulator = Simulator(self.cli_args.simulation_iter)
        result = simulator.simulate(program, goals, self.cli_args.number_samples)

        print(colored("---------------------", "cyan"))
        print(colored("- Simulation Result -", "cyan"))
        print(colored("---------------------", "cyan"))
        print()

        for goal, mean in result.get_average_goals().items():
            if isinstance(goal, Piecewise):
                print(f"P({goal.args[1]}) = {mean}")
            else:
                print(f"E({goal}) = {mean}")

        for goal, interval in result.get_95_CI_interval().items():
            print(f"95-CI for E({goal}) is {interval}.")
        print()
