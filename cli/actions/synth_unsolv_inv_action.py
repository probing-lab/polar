from argparse import Namespace
from .action import Action
from symengine.lib.symengine_wrapper import sympify
import sympy
from termcolor import colored
from unsolvable_analysis import UnsolvInvSynthesizer
from cli.common import prepare_program, parse_program


class SynthUnsolvInvAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        inv_deg = self.cli_args.inv_deg
        program = parse_program(benchmark, self.cli_args.transform_categoricals)
        program = prepare_program(program, self.cli_args)

        if len(program.non_mc_variables) == 0:
            print(
                f"--synth_unsolv_inv not applicable to {benchmark} since all variables are already effective."
            )
            return

        candidate_vars = []
        if len(self.cli_args.synth_unsolv_inv) == 0:
            for var in program.non_mc_variables:
                if var in program.original_variables:
                    candidate_vars.append(var)
        else:
            candidate_vars = [sympify(v) for v in self.cli_args.synth_unsolv_inv]

        print(colored("-------------------", "cyan"))
        print(colored("- Analysis Result -", "cyan"))
        print(colored("-------------------", "cyan"))
        print()

        # First look for combinations where k=1
        print("Searching for combinations for special case k = 1..")
        solutions = UnsolvInvSynthesizer.synth_inv_for_k(
            1,
            candidate_vars,
            inv_deg,
            program,
            self.cli_args.numeric_roots,
            self.cli_args.numeric_croots,
            self.cli_args.numeric_eps,
        )

        if solutions is None:
            print(f"No combination found with degree {inv_deg} and k=1")
        else:
            for sol in solutions:
                invariant, closed_form = sol[0], sol[1]
                invariant = sympy.sympify(invariant).factor()
                id = f"E({invariant})" if program.is_probabilistic else str(invariant)
                print(f"{id} = {closed_form}")
        print()

        # Then look for the general case
        print("Searching for combinations, general case..")
        solutions = UnsolvInvSynthesizer.synth_inv(
            candidate_vars,
            inv_deg,
            program,
            self.cli_args.numeric_roots,
            self.cli_args.numeric_croots,
            self.cli_args.numeric_eps,
        )
        if solutions is None:
            print(
                f"No combination found with degree {inv_deg}. Try using other degrees."
            )
        else:
            for sol in solutions:
                invariant, closed_form = sol[0], sol[1]
                invariant = sympy.sympify(invariant).factor()
                id = f"E({invariant})" if program.is_probabilistic else str(invariant)
                print(f"{id} = {closed_form}")
