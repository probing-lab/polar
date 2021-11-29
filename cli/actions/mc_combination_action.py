from argparse import Namespace
from .action import Action
from symengine.lib.symengine_wrapper import sympify
import sympy
from termcolor import colored
from program.mc_comb_finder import MCCombFinder
from cli.common import prepare_program, parse_program


class MCCombinationAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        combination_deg = self.cli_args.mc_comb_deg
        program = parse_program(benchmark, self.cli_args.transform_categoricals)
        program = prepare_program(program, self.cli_args)

        if len(program.non_mc_variables) == 0:
            print(f"--mc_comb not applicable to {benchmark} since all variables are already moment computable.")
            return

        combination_vars = []
        if len(self.cli_args.mc_comb) == 0:
            for var in program.non_mc_variables:
                if var in program.original_variables:
                    combination_vars.append(var)
        else:
            combination_vars = [sympify(v) for v in self.cli_args.mc_comb]

        print(colored("-------------------", "cyan"))
        print(colored("- Analysis Result -", "cyan"))
        print(colored("-------------------", "cyan"))
        print()

        combinations = MCCombFinder.find_good_combination(
            combination_vars, combination_deg, program, self.cli_args.numeric_roots, self.cli_args.numeric_croots,
            self.cli_args.numeric_eps
        )
        if combinations is None:
            print(f"No combination found with degree {combination_deg}. Try using other degrees.")
        else:
            for combination in combinations:
                candidate, solution = combination[0], combination[1]
                candidate = sympy.sympify(candidate).factor()
                print(f"E({candidate})[n] = {solution}")
