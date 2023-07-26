from argparse import Namespace
from symengine.lib.symengine_wrapper import sympify
from .action import Action
from cli.common import prepare_program
from inputparser import parse_program
from termcolor import colored
from unsolvable_analysis import SolvLoopSynthesizer


class SynthSolvLoopAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        inv_deg = self.cli_args.inv_deg
        program = parse_program(benchmark, self.cli_args.transform_categoricals)
        program = prepare_program(program, self.cli_args)

        candidate_vars = []
        if len(self.cli_args.synth_solv_loop) == 0:
            for var in program.defective_variables:
                if var in program.original_variables:
                    candidate_vars.append(var)
        else:
            candidate_vars = [sympify(v) for v in self.cli_args.synth_solv_loop]

        print(colored("-------------------", "cyan"))
        print(colored("- Analysis Result -", "cyan"))
        print(colored("-------------------", "cyan"))
        print()
        invariants, solvable_programs = SolvLoopSynthesizer.synth_loop(
            candidate_vars,
            inv_deg,
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
