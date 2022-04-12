from argparse import Namespace

import sympy
from cli.actions.goals_action import GoalsAction
from cli.common import parse_program, prepare_program
from inputparser.exceptions import ParseException
from .action import Action
from program.sensitivity import SensivitiyAnalyzer
from symengine.lib.symengine_wrapper import sympify
from symengine.lib.symengine_wrapper import Symbol as SymengineSymbol


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

    def __is_str_symbolic_param(self, paramstr: str) -> (bool, SymengineSymbol):
        expr = sympify(paramstr)
        if expr in self.program.symbols:
            return True, expr
        else:
            return False, expr

    def __diff_closed_form___(self):
        valid, param = self.__is_str_symbolic_param(self.cli_args.sensitivity_analysis_diff)
        if valid is False:
            raise ParseException(f"Unknown symbolic constant {self.cli_args.sensitivity_analysis_diff}")

        # TODO: refactor GoalsAction
        goals_action = GoalsAction(self.cli_args)
        goal = goals_action()
        sensitivity_function = goal.diff(param).simplify()

        # TODO: print sensitivity function
        return

    def __analyze_sensitivity___(self):
        # try parse parameter and make sure this is a symbolic param
        valid, param = self.__is_str_symbolic_param(self.cli_args.sensitivity_analysis)
        if valid is False:
            raise ParseException(f"Unknown symbolic constant {self.cli_args.sensitivity_analysis}")

        dep, indep = SensivitiyAnalyzer.get_dependent_variables(self.program, param)
        diffdef, diffeff = SensivitiyAnalyzer.get_diff_defective_variables(self.program, dep, param)

        # TODO: pass goals to core and handle result

        print("Depedent Vars:" + str(dep))
        print("Diff-Eff Vars:" + str(diffeff))
        print("Diff-Def Vars:" + str(diffdef))
        return
