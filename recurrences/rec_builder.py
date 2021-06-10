from functools import lru_cache
from typing import Set, List
from symengine.lib.symengine_wrapper import Expr, Symbol
from program import Program
from program.assignment import Assignment
from program.type import Finite
from .recurrences import Recurrences
from utils import get_terms_with_var, get_terms_with_vars, get_monoms


class RecBuilder:
    """
    Class providing the construction of recurrences of monomials for a given program.
    """

    program: Program

    def __init__(self, program: Program):
        self.program = program

    @lru_cache(maxsize=None)
    def get_recurrences(self, monomial: Expr) -> Recurrences:
        to_process = {monomial}
        processed = set()
        recurrence_dict = {}
        while to_process:
            next_monom = to_process.pop()
            recurrence_dict[next_monom] = self.get_recurrence(next_monom)
            processed.add(next_monom)
            monoms = get_monoms(recurrence_dict[next_monom], constant_symbols=self.program.symbols)
            for _, monom in monoms:
                if monom not in processed:
                    to_process.add(monom)

        init_values_dict = self.get_initial_values(processed)
        return Recurrences(recurrence_dict, init_values_dict, self.program)

    @lru_cache(maxsize=None)
    def get_recurrence(self, monomial: Expr):
        right_side = monomial
        last_assign_index = self.__get_last_assign_index__(monomial.free_symbols)
        for i in reversed(range(last_assign_index+1)):
            assignment = self.program.loop_body[i]
            if assignment.variable in right_side.free_symbols:
                right_side = right_side.expand()
                right_side = self.__replace_assign__(right_side, assignment).expand()
                right_side = self.__reduce_powers__(right_side)

        right_side = self.__reduce_powers__(right_side)
        return right_side.simplify().expand()

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

    def __reduce_powers__(self, poly: Expr):
        terms_with_vars, rest_without_vars = get_terms_with_vars(poly, self.program.finite_variables)
        finite_types: List[Finite] = [self.program.get_type(v) for v in self.program.finite_variables]

        result = rest_without_vars
        for var_powers, rest in terms_with_vars:
            term = rest
            for i in range(len(var_powers)):
                term *= finite_types[i].reduce_power(var_powers[i])
            result += term

        return result

    def get_initial_values(self, monomials: Set[Expr]):
        result = {}
        for monom in monomials:
            result[monom] = self.get_initial_value(monom)
        return result

    def get_initial_value(self, monom: Expr):
        result = monom
        for assign in reversed(self.program.initial):
            if assign.variable in result.free_symbols:
                result = self.__replace_assign__(result, assign)
                result = result.expand()

        for sym in monom.free_symbols.difference(self.program.symbols):
            result = result.xreplace({sym: Symbol(f"{sym}0")})

        return result.expand()
