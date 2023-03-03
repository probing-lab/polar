from functools import lru_cache
from math import prod
from typing import Set, List, Dict, TYPE_CHECKING
from symengine.lib.symengine_wrapper import Expr, Symbol, sympify, One, Zero
from program import Program
if TYPE_CHECKING:
    from program.assignment import Assignment, FunctionalAssignment
from program.type import Finite
from .recurrences import Recurrences
from utils import get_terms_with_var, get_terms_with_vars, get_monoms


class Context:
    # maps a variable v to their triggers, if a trigger occurs in a monomial, then get_moment of the assignment
    # of v will be called on this monomial, even if v doesn't occur in the monomial.
    triggers: Dict[Symbol, Set[Symbol]]
    # maps variables to their functional assignments
    func_assignments: Dict[Symbol, "FunctionalAssignment"]
    # Maps distribution variables v to functional variables that use v as a parameter
    dist_var_dependent_func_vars: Dict[Symbol, Set[Symbol]]

    def __init__(self):
        self.triggers = {}
        self.func_assignments = {}
        self.dist_var_dependent_func_vars = {}

    def add_trigger(self, var: Symbol, trigger: Symbol):
        if var in self.triggers:
            self.triggers[var].add(trigger)
        else:
            self.triggers[var] = {trigger}

    def add_func_assignments(self, fassign: "FunctionalAssignment"):
        self.func_assignments[fassign.variable] = fassign
        if fassign.argument in self.dist_var_dependent_func_vars:
            self.dist_var_dependent_func_vars[fassign.argument].add(fassign.variable)
        else:
            self.dist_var_dependent_func_vars[fassign.argument] = {fassign.variable}


class RecBuilder:
    """
    Class providing the construction of recurrences of monomials for a given program.
    """

    program: Program
    context: Context

    def __init__(self, program: Program):
        self.program = program

    @lru_cache(maxsize=None)
    def get_recurrences(self, monomial: Expr) -> Recurrences:
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
        self.context = Context()
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

    def __assign_replace_is_necessary__(self, assign: "Assignment", poly: Expr):
        if assign.variable in poly.free_symbols:
            return True
        if assign.variable not in self.context.triggers:
            return False
        return bool(self.context.triggers[assign.variable] & poly.free_symbols)

    def __assign_replace_is_trigger_free__(self, assign: "Assignment", poly: Expr):
        if assign.variable not in self.context.triggers:
            return True
        return not bool(self.context.triggers[assign.variable] & poly.free_symbols)

    def __get_last_assign_index__(self, variables: Set[Symbol]):
        max_index = -1
        for v in variables:
            if self.program.var_to_index[v] > max_index:
                max_index = self.program.var_to_index[v]
        return max_index

    def __replace_assign__(self, poly: Expr, assign: "Assignment"):
        cond = assign.condition.to_arithm(self.program)
        if self.__assign_replace_is_trigger_free__(assign, poly):
            terms_with_var, rest_without_var = get_terms_with_var(poly, assign.variable)
            result = rest_without_var
            for var_power, rest in terms_with_var:
                result += assign.get_moment(var_power, self.context, cond, rest)
            return result
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
        terms_with_vars, rest_without_vars = get_terms_with_vars(poly, self.program.finite_variables)
        finite_types: List[Finite] = [self.program.get_type(v) for v in self.program.finite_variables]
        result = rest_without_vars
        for var_powers, rest in terms_with_vars:
            term = rest
            for i in range(len(var_powers)):
                term *= finite_types[i].reduce_power(var_powers[i])
            result += term.expand()
        return result

    def get_initial_values(self, monomials: Set[Expr]):
        result = {}
        for monom in monomials:
            result[monom] = self.get_initial_value(monom)
        return result

    def get_initial_value(self, monom: Expr):
        self.context = Context()
        result = monom
        for assign in reversed(self.program.initial):
            if self.__assign_replace_is_necessary__(assign, result):
                result = self.__replace_assign__(result, assign)
                result = result.expand()

        for sym in monom.free_symbols.difference(self.program.symbols):
            result = result.xreplace({sym: Symbol(f"{sym}0")})

        return result.expand()

    def get_solution(self, monom: Expr, solvers):
        # just lookup the solution
        solver = solvers[monom]
        return solver.get(monom), solver.is_exact
