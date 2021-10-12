from argparse import Namespace
from .action import Action
from expansions import CornishFisherExpansion
from symengine.lib.symengine_wrapper import sympify
from sympy import Symbol
from sympy.plotting import plot as symplot
from cli.common import prepare_program, get_all_cumulants, transform_to_after_loop


class CornishFisherAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        monom = sympify(self.cli_args.cornish_fisher)
        program = prepare_program(benchmark, self.cli_args)
        cumulants = get_all_cumulants(program, monom, self.cli_args.cornish_fisher_order, self.cli_args)
        if self.cli_args.after_loop:
            cumulants = transform_to_after_loop(cumulants)
        expansion = CornishFisherExpansion(cumulants)
        quantile_function = expansion()
        print(quantile_function)
        if self.cli_args.at_n >= 0 or self.cli_args.after_loop:
            symplot(quantile_function, (Symbol("p"), 0.01, 0.99))
