from argparse import Namespace
from .action import Action
from cli.common import prepare_program, parse_program


class SynthSolvAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        combination_deg = self.cli_args.synth_solv

        program = parse_program(benchmark, self.cli_args.transform_categoricals)
        program = prepare_program(program, self.cli_args)

        if len(program.non_mc_variables) == 0:
            print(f"Loop in {benchmark} is already solvable.")
            return
