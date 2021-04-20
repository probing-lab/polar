from typing import Set

from diofant import Expr, Symbol

from program import Program
from program.assignment import DistAssignment


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
        poly = expr.as_poly(dist_assign.variable)
        result = poly.coeff_monomial(1)
        for monom in poly.monoms():
            power = monom[0]
            if power > 0:
                moment = dist_assign.distribution.get_moment(power)
                coeff = poly.coeff_monomial(monom)
                assert dist_assign.variable not in (moment.free_symbols | coeff.free_symbols)
                result += moment * coeff
        return result.expand()
