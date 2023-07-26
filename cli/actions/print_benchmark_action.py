from argparse import Namespace
from termcolor import colored

from bayesnet.parser import BifParser
from bayesnet.code_generator import CodeGenerator

from inputparser import Parser
from .action import Action
from cli.common import prepare_program
from inputparser import parse_program


class PrintBenchmarkAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark: str = args[0]

        if benchmark.endswith(".bif"):
            network = BifParser().parse_file(benchmark)
            codegen = CodeGenerator(network)
            code = codegen.generate_code()
            program = Parser().parse_string(code, self.cli_args.transform_categoricals)
        else:
            program = parse_program(benchmark, self.cli_args.transform_categoricals)

        print(colored("------------------", "magenta"))
        print(colored("- Parsed program -", "magenta"))
        print(colored("------------------", "magenta"))
        print(program)
        print()

        program = prepare_program(program, self.cli_args)
        print(colored("-----------------------", "magenta"))
        print(colored("- Transformed program -", "magenta"))
        print(colored("-----------------------", "magenta"))
        print(program)
        print()
