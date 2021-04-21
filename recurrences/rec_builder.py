from typing import Set
from symengine.lib.symengine_wrapper import Expr, Symbol
from program import Program
from program.assignment import DistAssignment
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
            if assignment.is_probabilistic():
                if assignment.variable in right_side.free_symbols:
                    right_side = self.__replace_dist_assign_moments__(right_side, assignment)
            else:
                if assignment.variable in right_side.free_symbols:
                    right_side = right_side.xreplace({assignment.variable: assignment.poly})
        return right_side

    def __get_last_assign_index__(self, variables: Set[Symbol]):
        m = -1
        for v in variables:
            if self.program.var_to_index[v] > m:
                m = self.program.var_to_index[v]
        return m

    def __replace_dist_assign_moments__(self, expr: Expr, dist_assign: DistAssignment):
        var = dist_assign.variable
        dist = dist_assign.distribution
        poly = expr.expand()
        terms_with_var, rest_without_var = get_terms_with_var(poly, var)

        result = rest_without_var
        for var_power, rest in terms_with_var:
            result += dist.get_moment(var_power) * rest
        return result
