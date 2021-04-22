from functools import lru_cache
from typing import Set
from symengine.lib.symengine_wrapper import Expr, Symbol
from program import Program
from program.assignment import Assignment
from utils import get_terms_with_var, get_monoms


class RecBuilder:
    """
    Class providing the construction of recurrences of monomials for a given program.
    """

    program: Program

    def __init__(self, program: Program):
        self.program = program

    @lru_cache(maxsize=None)
    def get_recurrences(self, monomial: Expr):
        to_process = {monomial}
        processed = set()
        recurrences = {}
        while to_process:
            next_monom = to_process.pop()
            recurrences[next_monom] = self.get_recurrence(next_monom)
            processed.add(next_monom)
            monoms = get_monoms(recurrences[next_monom], constant_symbols=self.program.symbols)
            for _, monom in monoms:
                if monom not in processed:
                    to_process.add(monom)
        return recurrences

    @lru_cache(maxsize=None)
    def get_recurrence(self, monomial: Expr):
        right_side = monomial
        last_assign_index = self.__get_last_assign_index__(monomial.free_symbols)
        for i in reversed(range(last_assign_index+1)):
            assignment = self.program.loop_body[i]
            if assignment.variable in right_side.free_symbols:
                right_side = right_side.expand()
                right_side = self.__replace_assign__(right_side, assignment)
        return right_side.simplify()

    def __get_last_assign_index__(self, variables: Set[Symbol]):
        max_index = -1
        for v in variables:
            if self.program.var_to_index[v] > max_index:
                max_index = self.program.var_to_index[v]
        return max_index

    def __replace_assign__(self, poly: Expr, assign: Assignment):
        cond = assign.condition.to_arithm(self.program)
        terms_with_var, rest_without_var = get_terms_with_var(poly, assign.variable)

        result = rest_without_var
        for var_power, rest in terms_with_var:
            result += assign.get_moment(var_power, cond, rest)
        return result
