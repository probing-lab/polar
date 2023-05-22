from argparse import Namespace
from symengine.lib.symengine_wrapper import sympify
from .action import Action
from cli.common import prepare_program, parse_program
from termcolor import colored
from program.solvable_synthesizer import SolvableSynthesizer


class SynthSolvAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        combination_deg = self.cli_args.mc_comb_deg
        program = parse_program(benchmark, self.cli_args.transform_categoricals)
        program = prepare_program(program, self.cli_args)

        combination_vars = []
        if len(self.cli_args.synth_solv) == 0:
            for var in program.non_mc_variables:
                if var in program.original_variables:
                    combination_vars.append(var)
        else:
            combination_vars = [sympify(v) for v in self.cli_args.synth_solv]

        print(colored("-------------------", "cyan"))
        print(colored("- Analysis Result -", "cyan"))
        print(colored("-------------------", "cyan"))
        print()
        invariants, solvable_programs = SolvableSynthesizer.synthesize(
            combination_vars,
            combination_deg,
            program,
            self.cli_args.numeric_roots,
            self.cli_args.numeric_croots,
            self.cli_args.numeric_eps,
        )

        if len(invariants) == 0:
            print(solvable_programs[0])
            return [], solvable_programs

        for invariant, solvable_program in zip(invariants, solvable_programs):
            print("Synthesized solvable loop: ")
            print(solvable_program)
            print()
            print("Invariant used: ")
            print(invariant)
            print()
            print()
        return invariants, solvable_programs
