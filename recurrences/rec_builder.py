from typing import Set
from symengine.lib.symengine_wrapper import Expr, Symbol
from program import Program
from program.assignment import Assignment
from utils import get_terms_with_var


class RecBuilder:

    program: Program

    def __init__(self, program: Program):
        self.program = program

    def get_recurrences(self, monomial: Expr):
        recurrence = self.get_recurrence(monomial)
        return [recurrence]

    def get_recurrence(self, monomial: Expr):
        right_side = monomial
        last_assign_index = self.__get_last_assign_index__(monomial.free_symbols)
        for i in reversed(range(last_assign_index+1)):
            assignment = self.program.loop_body[i]
            right_side = right_side.expand()
            right_side = self.__replace_assign__(right_side, assignment)
        return right_side.simplify()

    def __get_last_assign_index__(self, variables: Set[Symbol]):
        m = -1
        for v in variables:
            if self.program.var_to_index[v] > m:
                m = self.program.var_to_index[v]
        return m

    def __replace_assign__(self, poly: Expr, assign: Assignment):
        cond = assign.condition.to_arithm(self.program)
        not_cond = 1 - cond
        terms_with_var, rest_without_var = get_terms_with_var(poly, assign.variable)

        result = rest_without_var
        for var_power, rest in terms_with_var:
            replacement = cond * assign.get_moment_of_content(var_power) + not_cond * (assign.default ** var_power)
            result += replacement * rest
        return result
