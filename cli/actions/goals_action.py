from argparse import Namespace
from typing import Dict
from symengine.lib.symengine_wrapper import Expr
from program import Program
from .action import Action
from inputparser import GoalParser, MOMENT, CUMULANT, CENTRAL, TAIL_BOUND_LOWER, TAIL_BOUND_UPPER
from recurrences import RecBuilder
from recurrences.solver import RecurrenceSolver
from sympy import N
from utils import indent_string, raw_moments_to_cumulants, raw_moments_to_centrals, eval_re
from termcolor import colored
from cli.common import prepare_program, get_moment, get_all_moments, transform_to_after_loop, print_is_exact, \
    prettify_piecewise


class GoalsAction(Action):
    cli_args: Namespace
    solvers: Dict[Expr, RecurrenceSolver]
    rec_builder: RecBuilder
    program: Program

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        self.program = prepare_program(benchmark, self.cli_args)
        self.rec_builder = RecBuilder(self.program)
        self.solvers = {}

        print(colored("-------------------", "cyan"))
        print(colored("- Analysis Result -", "cyan"))
        print(colored("-------------------", "cyan"))
        print()

        for goal in self.cli_args.goals:
            goal_type, goal_data = GoalParser.parse(goal)
            if goal_type == MOMENT:
                self.handle_moment_goal(goal_data)
            elif goal_type == CUMULANT:
                self.handle_cumulant_goal(goal_data)
            elif goal_type == CENTRAL:
                self.handle_central_moment_goal(goal_data)
            elif goal_type == TAIL_BOUND_UPPER:
                self.handle_tail_bound_upper_goal(goal_data)
            elif goal_type == TAIL_BOUND_LOWER:
                self.handle_tail_bound_lower_goal(goal_data)
            else:
                raise RuntimeError(f"Goal type {goal_type} does not exist.")

    def handle_moment_goal(self, goal_data):
        monom = goal_data[0]
        moment, is_exact = get_moment(monom, self.solvers, self.rec_builder, self.cli_args, self.program)
        if self.cli_args.after_loop:
            moment = transform_to_after_loop(moment)
        print(f"E({monom}) = {prettify_piecewise(moment)}")
        print_is_exact(is_exact)
        if self.cli_args.at_n >= 0:
            moment_at_n = eval_re(self.cli_args.at_n, moment).expand()
            print(f"E({monom} | n={self.cli_args.at_n}) = {moment_at_n} ≅ {N(moment_at_n)}")
        print()

    def handle_cumulant_goal(self, goal_data):
        number = goal_data[0]
        monom = goal_data[1]
        moments, is_exact = get_all_moments(monom, number, self.solvers, self.rec_builder, self.cli_args, self.program)
        cumulants = raw_moments_to_cumulants(moments)
        cumulant = cumulants[number]
        if self.cli_args.after_loop:
            cumulant = transform_to_after_loop(cumulant)
        print(f"k{number}({monom}) = {prettify_piecewise(cumulant)}")
        print_is_exact(is_exact)
        if self.cli_args.at_n >= 0:
            cumulant_at_n = eval_re(self.cli_args.at_n, cumulant).expand()
            print(f"k{number}({monom} | n={self.cli_args.at_n}) = {cumulant_at_n} ≅ {N(cumulant_at_n)}")
        print()

    def handle_central_moment_goal(self, goal_data):
        number = goal_data[0]
        monom = goal_data[1]
        moments, is_exact = get_all_moments(monom, number, self.solvers, self.rec_builder, self.cli_args, self.program)
        central_moments = raw_moments_to_centrals(moments)
        central_moment = central_moments[number]
        if self.cli_args.after_loop:
            central_moment = transform_to_after_loop(central_moment)
        print(f"c{number}({monom}) = {prettify_piecewise(central_moment)}")
        print_is_exact(is_exact)
        if self.cli_args.at_n >= 0:
            central_at_n = eval_re(self.cli_args.at_n, central_moments).expand()
            print(f"c{number}({monom} | n={self.cli_args.at_n}) = {central_at_n} ≅ {N(central_at_n)}")
        print()

    def handle_tail_bound_upper_goal(self, goal_data):
        monom, a = goal_data[0], goal_data[1]
        moments, is_exact = get_all_moments(
            monom, self.cli_args.tail_bound_moments, self.solvers, self.rec_builder, self.cli_args, self.program)
        if self.cli_args.after_loop:
            moments = transform_to_after_loop(moments)
        bounds = [m / (a ** k) for k, m in moments.items()]
        bounds.reverse()
        print(f"Assuming {monom} is non-negative.")
        print(f"P({monom} >= {a}) <= minimum of")
        count = 1
        for bound in bounds:
            print(indent_string(f"({count}) {prettify_piecewise(bound)}", 4))
            count += 1
        print_is_exact(is_exact)

        if self.cli_args.at_n >= 0:
            bounds_at_n = [eval_re(self.cli_args.at_n, b).expand() for b in bounds]
            can_take_min = all([not b.free_symbols for b in bounds_at_n])
            if can_take_min:
                bound_at_n = min(bounds_at_n)
                print(f"P({monom} >= {a} | n={self.cli_args.at_n}) <= {bound_at_n} ≅ {N(bound_at_n)}")
            else:
                print(f"P({monom} >= {a} | n={self.cli_args.at_n}) <= minimum of")
                count = 1
                for bound_at_n in bounds_at_n:
                    print(indent_string(f"({count}) {bound_at_n} ≅ {N(bound_at_n)}", 4))
                    count += 1
        print()

    def handle_tail_bound_lower_goal(self, goal_data):
        monom, a = goal_data[0], goal_data[1]
        moments, is_exact = get_all_moments(monom, 2, self.solvers, self.rec_builder, self.cli_args, self.program)
        if self.cli_args.after_loop:
            moments = transform_to_after_loop(moments)
        bound = ((moments[1] - a) ** 2) / (moments[2] - 2 * a * moments[1] + a ** 2)
        bound = bound.simplify()
        print(f"Assuming {monom - a} is non-negative.")
        print(f"P({monom} > {a}) >= {prettify_piecewise(bound)}")
        print_is_exact(is_exact)
        if self.cli_args.at_n >= 0:
            bound_at_n = eval_re(self.cli_args.at_n, bound)
            print(f"P({monom} > {a} | n={self.cli_args.at_n}) >= {bound_at_n} ≅ {N(bound_at_n)}")
        print()
