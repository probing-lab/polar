from argparse import Namespace
from termcolor import colored

from inputparser import Parser
from .action import Action
from cli.common import prepare_program


class PrintBenchmarkAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        program = Parser().parse_file(benchmark, self.cli_args.transform_categoricals)
        print(colored("------------------", "magenta"))
        print(colored("- Parsed program -", "magenta"))
        print(colored("------------------", "magenta"))
        print(program)
        print()

        program = prepare_program(benchmark, self.cli_args)
        print(colored("-----------------------", "magenta"))
        print(colored("- Transformed program -", "magenta"))
        print(colored("-----------------------", "magenta"))
        print(program)
        print()
