from argparse import Namespace
from typing import Tuple

import sympy
from cli.actions.goals_action import GoalsAction
from cli.common import parse_program, prepare_program
from inputparser.exceptions import ParseException
from inputparser.goal_parser import CENTRAL, CUMULANT, MOMENT
from program.sensitivity.sensitivity_analyzer import SymbolSet
from recurrences.diff_rec_builder import DiffRecBuilder
from recurrences.rec_builder import RecBuilder
from .action import Action
from termcolor import colored
from program.sensitivity import SensivitiyAnalyzer
from symengine.lib.symengine_wrapper import sympify
from symengine.lib.symengine_wrapper import Symbol as SymengineSymbol
from symengine.lib.symengine_wrapper import Expr as SymengineExpr


class SensitivityAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        program = parse_program(benchmark, self.cli_args.transform_categoricals)
        self.program = prepare_program(program, self.cli_args)

        if self.cli_args.sensitivity_analysis:
            self.__analyze_sensitivity___()
        elif self.cli_args.sensitivity_analysis_diff:
            self.__diff_closed_form___()
        return

    def __is_str_symbolic_param(self, paramstr: str) -> Tuple[bool, SymengineSymbol]:
        """
        Check if the given string is actually a symbolic parameter of the program.
        """
        expr = sympify(paramstr)
        if expr in self.program.symbols:
            return True, expr
        else:
            return False, expr

    def __diff_closed_form___(self):
        """
        Compute the sensitivity of the goals by solving the recurrences
        and then differentiating, only works if all variables are effective.
        """

        valid, param = self.__is_str_symbolic_param(self.cli_args.sensitivity_analysis_diff)
        if valid is False:
            raise ParseException(f"Unknown symbolic constant {self.cli_args.sensitivity_analysis_diff}")

        print(colored("----------------------", "cyan"))
        print(colored("- Sensitivity Result -", "cyan"))
        print(colored("----------------------", "cyan"))

        goals_action = GoalsAction(self.cli_args)
        goals_action.initialize_program(self.program, RecBuilder(self.program))
        for goal_type, goal_data in goals_action.parse_goals():
            if goal_type == MOMENT:
                result, is_exact = goals_action.handle_moment_goal(goal_data)
                goals_action.print_moment_goal(goal_data[0], result, is_exact)
                result_diff = result.diff(param).simplify()
                goals_action.print_moment_goal(goal_data[0], result_diff, is_exact, prefix="∂")
            elif goal_type == CUMULANT:
                result, is_exact = goals_action.handle_cumulant_goal(goal_data)
                goals_action.print_cumulant_goal(goal_data[0], goal_data[1], result, is_exact)
                result_diff = result.diff(param).simplify()
                goals_action.print_cumulant_goal(goal_data[0], goal_data[1], result_diff, is_exact, prefix="∂")
            elif goal_type == CENTRAL:
                result, is_exact = goals_action.handle_central_moment_goal(goal_data)
                goals_action.print_central_moment_goal(goal_data[0], goal_data[1], result, is_exact)
                result_diff = result.diff(param).simplify()
                goals_action.print_central_moment_goal(goal_data[0], goal_data[1], result_diff, is_exact, prefix="∂")
            else:
                raise RuntimeError(f"Goal type {goal_type} does not exist or cannot be used for sensitivity analysis.")

    def __analyze_sensitivity___(self):
        """
        Compute the sensitivity of the goals by removing diff-defective and param-independent variables.
        """

        print(colored("----------------------", "cyan"))
        print(colored("- Sensitivity Result -", "cyan"))
        print(colored("----------------------", "cyan"))

        # try parse parameter and make sure this is a symbolic param
        valid, param = self.__is_str_symbolic_param(self.cli_args.sensitivity_analysis)
        if valid is False:
            raise ParseException(f"Unknown symbolic constant {self.cli_args.sensitivity_analysis}")

        goals_action = GoalsAction(self.cli_args)
        diff_rec_builder = DiffRecBuilder(self.program, param)
        goals_action.initialize_program(self.program, diff_rec_builder)

        # using DiffRecBuilder will return the differentiated solutions directly
        for goal_type, goal_data in goals_action.parse_goals():
            if goal_type == MOMENT:
                result, is_exact = goals_action.handle_moment_goal(goal_data)
                goals_action.print_moment_goal(goal_data[0], result, is_exact, prefix="∂")
            # elif goal_type == CUMULANT:
            #     result, is_exact = goals_action.handle_cumulant_goal(goal_data)
            #     goals_action.print_cumulant_goal(goal_data[0], goal_data[1], result, is_exact, prefix="∂")
            # elif goal_type == CENTRAL:
            #     result, is_exact = goals_action.handle_central_moment_goal(goal_data)
            #     goals_action.print_central_moment_goal(goal_data[0], goal_data[1], result, is_exact, prefix="∂")
            else:
                raise RuntimeError(f"Goal type {goal_type} does not exist or cannot be used for sensitivity analysis.")