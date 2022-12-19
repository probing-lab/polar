from argparse import Namespace
import itertools
from typing import Dict
from symengine.lib.symengine_wrapper import sympify, Expr, One
from sympy import zeros
from sympy.physics.quantum import TensorProduct
from program import Program
from .action import Action
from recurrences import RecBuilder
from recurrences.solver import RecurrenceSolver
from sympy import N
from utils import eval_re
from termcolor import colored
from cli.common import get_moment_given_termination, parse_program, prepare_program,\
    get_moment, print_is_exact, prettify_piecewise, transform_to_after_loop


class DistributionAction(Action):
    cli_args: Namespace
    solvers: Dict[Expr, RecurrenceSolver]
    rec_builder: RecBuilder
    program: Program

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        program = parse_program(benchmark, self.cli_args.transform_categoricals)
        program = prepare_program(program, self.cli_args)
        rec_builder = RecBuilder(program)
        self.program = program
        self.rec_builder = rec_builder
        self.solvers = {}
        self.extract_distribution()

    def extract_distribution(self):
        print(colored("-------------------", "cyan"))
        print(colored("- Analysis Result -", "cyan"))
        print(colored("-------------------", "cyan"))
        print()

        # sanity checks
        target_variables = [sympify(v) for v in self.cli_args.distribution]
        target_variables_ranges = []

        if len(target_variables) == 0:
            raise Exception("No variables for argument distribution specified.")
        if not self.program.variables.issuperset(target_variables):
            raise Exception("Distribution variables are not proper program variables.")
        for v in target_variables:
            t = self.program.get_type(v)
            if t is None or not t.is_finite():
                raise Exception(f"Variable {v} does not seem to have finite support.")
            target_variables_ranges.append(t.enumerate_values())

        valuations, moments, is_exact = self.get_moment_vector(target_variables, target_variables_ranges)
        p = moments * self.combine_and_invert_moment_matrices(target_variables)

        self.print_distribution(target_variables, valuations, p, is_exact)

    def get_vandermonde_matrix(self, values):
        """Create a Vandermonde matrix containing the values as entries."""
        V = zeros(len(values))
        for i, v in enumerate(values):
            for j in range(len(values)):
                V[i, j] = v**j
        return V

    def combine_and_invert_moment_matrices(self, variables):
        result = 1
        for i, v in enumerate(variables):
            m = self.get_vandermonde_matrix(self.program.get_type(v).enumerate_values())
            if i == 0:
                result = m.inv()
            else:
                result = TensorProduct(result, m.inv())
        return result

    def get_moment_vector(self, target_variables, target_variables_ranges):
        monomials = []
        valuations = list(itertools.product(*target_variables_ranges))
        for powers in valuations:
            moment = One()
            for var, power in zip(target_variables, powers):
                moment *= (var**power)
            monomials.append(moment)

        n = len(monomials)
        moments = zeros(1, n)
        all_exact = True
        for i, monomial in enumerate(reversed(monomials)):
            moment, is_exact = self.get_single_moment(monomial)
            all_exact = all_exact and is_exact
            moments[0, n-1-i] = moment
        return valuations, moments, all_exact

    def get_single_moment(self, monom):
        if self.cli_args.after_loop:
            moment_given_termination, is_exact = get_moment_given_termination(
                monom, self.solvers, self.rec_builder, self.cli_args, self.program)
            moment = transform_to_after_loop(moment_given_termination)
            if moment is None:
                raise Exception("Could not compute after_loop since limit of expression could not be computed")
        else:
            moment, is_exact = get_moment(monom, self.solvers, self.rec_builder, self.cli_args, self.program)
        return moment, is_exact

    def print_distribution(self, ordering, valuations, probs, is_exact):
        str = ""
        for valuation, prob in zip(valuations, probs):
            str += "("
            for i, (var, val) in enumerate(zip(ordering, valuation)):
                if i == 0:
                    str += f"{var} = {val}"
                else:
                    str += f", {var} = {val}"
            str += f"): {prettify_piecewise(prob)}\n"
        print(str)
        print_is_exact(is_exact)
        if self.cli_args.at_n >= 0:
            str = ""
            for valuation, prob in zip(valuations, probs):
                str += "("
                for i, (var, val) in enumerate(zip(ordering, valuation)):
                    if i == 0:
                        str += f"{var} = {val}"
                    else:
                        str += f", {var} = {val}"
                prob_at_n = eval_re(self.cli_args.at_n, prob).expand()
                str += f" | n={self.cli_args.at_n}): {prob_at_n} ≅ {N(prob_at_n)}\n"
            print(str)
        print()
