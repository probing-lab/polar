from argparse import Namespace
from .action import Action
from expansions import GramCharlierExpansion
from symengine.lib.symengine_wrapper import sympify
from sympy import Symbol
from sympy.plotting import plot as symplot
from cli.common import (
    get_all_cumulants,
    get_all_cumulants_after_loop,
)
from program import normalize_program
from inputparser import parse_program


class GramCharlierAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        monom = sympify(self.cli_args.gram_charlier)
        program = parse_program(benchmark)
        program = normalize_program(program)
        if self.cli_args.after_loop:
            cumulants = get_all_cumulants_after_loop(
                program, monom, self.cli_args.gram_charlier_order, self.cli_args
            )
        else:
            cumulants = get_all_cumulants(
                program, monom, self.cli_args.gram_charlier_order, self.cli_args
            )
        expansion = GramCharlierExpansion(cumulants)
        density = expansion()
        print(density)
        if self.cli_args.at_n >= 0 or self.cli_args.after_loop:
            mu = float(cumulants[1])
            sigma = float(cumulants[2]) ** (1 / 2)
            symplot(density, (Symbol("x"), mu - 5 * sigma, mu + 5 * sigma))
