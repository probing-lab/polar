from functools import lru_cache
from math import prod
from typing import Set, List
from symengine.lib.symengine_wrapper import Expr, Symbol, sympify, One, Zero
from program import Program
from program.assignment import Assignment
from program.type import Finite
from .recurrences import Recurrences
from .rec_builder_context import RecBuilderContext
from utils import get_terms_with_var, get_terms_with_vars, get_monoms


class RecBuilder:
    """
    This class provides the functionality to construct the recurrences (of expected values) of monomials and
    polynomials of program variables.
    """

    program: Program
    context: RecBuilderContext

    def __init__(self, program: Program):
        self.program = program

    @lru_cache(maxsize=None)
    def get_recurrences(self, monomial: Expr) -> Recurrences:
        """
        Constructs a complete system of linear recurrences (over expected values) completely describing
        the expected value of "monomial".
        """
        monomial = sympify(monomial)
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

    def get_recurrence_poly(self, poly: Expr, variables: List[Symbol]):
        """
        Constructs a single recurrence (the moment recurrence) for a given polynomial. Essentially, the
        moment recurrence for the polynomial is the sum of the moment recurrences of the individual moment
        recurrences of the monomials (by linearity of expectation).
        """
        monoms = get_terms_with_vars(poly, variables)
        monoms = monoms[0]
        index_to_vars = {i: var for i, var in enumerate(variables)}
        poly, poly_rec = Zero(), Zero()
        for monom, coeff in monoms:
            term = One()
            for i in range(len(monom)):
                term *= index_to_vars[i] ** monom[i]
            poly_rec += coeff * self.get_recurrence(term)
            poly += term
        return poly_rec.expand()

    @lru_cache(maxsize=None)
    def get_recurrence(self, monomial: Expr):
        """
        Constructs a single recurrence (the moment recurrence) for a given monomial, by bottom up substitution,
        and reducing the powers of finite-valued variables.
        """
        self.context = RecBuilderContext()
        right_side = monomial
        last_assign_index = self.__get_last_assign_index__(monomial.free_symbols)
        for i in reversed(range(last_assign_index+1)):
            assignment = self.program.loop_body[i]
            if self.__assign_replace_is_necessary__(assignment, right_side):
                right_side = right_side.expand()
                right_side = self.__replace_assign__(right_side, assignment).expand()
                right_side = self.__reduce_powers__(right_side)

        right_side = self.__reduce_powers__(right_side)
        return right_side.simplify().expand()

    def __assign_replace_is_necessary__(self, assign: Assignment, poly: Expr):
        """
        Returns true iff assign needs to be considered when constructing a moment recurrence.
        The argument "poly" is the intermediate result of constructing a moment recurrence.
        """
        if assign.variable in poly.free_symbols:
            return True
        if assign.variable not in self.context.triggers:
            return False
        return bool(self.context.triggers[assign.variable] & poly.free_symbols)

    def __get_last_assign_index__(self, variables: Set[Symbol]):
        """
        Returns the maximum index of the assignments of all given variables.
        """
        max_index = -1
        for v in variables:
            if self.program.var_to_index[v] > max_index:
                max_index = self.program.var_to_index[v]
        return max_index

    def __replace_assign__(self, poly: Expr, assign: Assignment):
        """
        Intuitively, the method returns the expected value of "poly" after executing assign.
        You can also think of the result as wp(assign, poly) (where wp is the weakest pre-expectation).
        The concrete operation very much depends on the type of the assignment.
        Hence, the method goes through all relevant monomials of poly and hands them to the assignment object.
        """
        cond = assign.condition.to_arithm(self.program)
        # if poly doesn't contain triggers of assign.variables, we only need to worry about assign.variable itself
        if not self.context.var_has_triggers_in_expr(assign.variable, poly):
            terms_with_var, rest_without_var = get_terms_with_var(poly, assign.variable)
            result = rest_without_var
            for var_power, rest in terms_with_var:
                result += assign.get_moment(var_power, self.context, cond, rest)
            return result
        # if poly contains triggers of assign.variable, we need to consider all monomials contain assign.variable
        # or any trigger variables.
        else:
            triggers = list(self.context.triggers[assign.variable])
            variables = [assign.variable] + triggers
            terms_with_vars, rest_without_vars = get_terms_with_vars(poly, variables)
            result = rest_without_vars
            for var_powers, rest in terms_with_vars:
                var_power = var_powers[0]
                trigger_monom = prod([v ** p for v, p in zip(triggers, var_powers[1:])])
                result += assign.get_moment(var_power, self.context, cond, trigger_monom*rest)
            return result

    def __reduce_powers__(self, poly: Expr):
        """
        Reduces the power of finite-valued variables in a given expression.
        """
        terms_with_vars, rest_without_vars = get_terms_with_vars(poly, self.program.finite_variables)
        finite_types: List[Finite] = [self.program.get_type(v) for v in self.program.finite_variables]
        result = rest_without_vars
        for var_powers, rest in terms_with_vars:
            term = rest
            for i in range(len(var_powers)):
                term *= finite_types[i].reduce_power(var_powers[i])
            result += term.expand()
        return result

    def get_initial_value(self, monom: Expr):
        """
        Computes the initial expected value of a given monomial, by bottom up substitution of the initial
        assignments block.
        """
        self.context = RecBuilderContext()
        result = monom
        for assign in reversed(self.program.initial):
            if self.__assign_replace_is_necessary__(assign, result):
                result = self.__replace_assign__(result, assign)
                result = result.expand()

        for sym in monom.free_symbols.difference(self.program.symbols):
            result = result.xreplace({sym: Symbol(f"{sym}0")})

        return result.expand()

    def get_initial_values(self, monomials: Set[Expr]):
        """
        Computes the initial expected values of a given set of monomials.
        """
        result = {}
        for monom in monomials:
            result[monom] = self.get_initial_value(monom)
        return result

    def get_solution(self, monom: Expr, solvers):
        # just lookup the solution
        solver = solvers[monom]
        return solver.get(monom), solver.is_exact
