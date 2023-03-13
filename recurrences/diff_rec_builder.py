from functools import lru_cache
from typing import Set
from symengine.lib.symengine_wrapper import Expr, Zero, sympify, One, Symbol
from program import Program
from program.sensitivity.sensitivity_analyzer import SensivitiyAnalyzer
from .rec_builder import RecBuilder
from .recurrences import Recurrences
from utils import get_monoms, get_unique_var


class DiffRecBuilder:
    """
    Class providing the construction of recurrences of differentiated monomials for a given program.
    """

    program: Program

    def __init__(self, program: Program, param: Symbol):
        self.program = program
        #TODO: use Dummy here when updating symengine, current version is buggy
        self.delta = Symbol(get_unique_var("diff_symbol"))
        self.param = param
        self.rec_builder = RecBuilder(program)
        self.dep_vars, _ = SensivitiyAnalyzer.get_dependent_variables(program, param)

    def __is_monomial_p_dependent__(self, monomial: Expr):
        """Check if a given sympy monomial is parameter-depedent"""
        if self.param in monomial.free_symbols:
            return True
        if self.dep_vars.intersection(monomial.free_symbols):
            return True
        return False

    @lru_cache(maxsize=None)
    def get_recurrences(self, monomial: Expr) -> Recurrences:
        goal = sympify(monomial)
        to_process = {goal*self.delta}

        # iteratively get recurrences for monoms and then check if more monomials are needed
        # to solve the recurrence
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
        """
        Get recurrence for monomials that might be derivatives
        """
        
        # in case of non-diff monomial -> simply return
        if self.delta not in monomial.free_symbols:
            return self.rec_builder.get_recurrence(monomial)
            
        # replace delta for now and get recurrence
        monomial = monomial.subs(self.delta, 1)
        original_rec = self.rec_builder.get_recurrence(monomial)
        rec = Zero()

        # now go through each summand and differentiate it
        sum = original_rec.args if original_rec.is_Add else [original_rec]
        for summand in sum:

            # skip p-independent summands
            if self.__is_monomial_p_dependent__(summand) is False:
                continue

            # separate constant part and monomial part
            constant_part = One()
            monomial_part = One()

            factors = summand.args if summand.is_Mul else [summand]
            for factor in factors:
                if factor.free_symbols.difference(self.program.symbols):
                    monomial_part *= factor
                else:
                    constant_part *= factor

            # emulate diff
            if self.param in constant_part.free_symbols:
                if self.__is_monomial_p_dependent__(monomial_part):
                    # if both parts depend on param -> product rule
                    rec += constant_part.diff(self.param) * monomial_part
                    rec += constant_part * monomial_part * self.delta
                else:
                    # if only the constant part depends on param -> treat monomial as constant
                    rec += constant_part.diff(self.param) * monomial_part
            else:
                # if only monomial depends on param -> diff whole summand
                rec += summand * self.delta

        return rec

    def get_initial_values(self, monomials: Set[Expr]):
        result = {}
        for monom in monomials:
            result[monom] = self.get_initial_value(monom)
        return result

    def get_initial_value(self, monomial: Expr):
        """
        Get initial values for monomial, variable initial values are delegated to the standard rec_builder,
        differential initial values are obtained by differentiating the initial value of the variables.
        """
         # in case of non-diff monomial -> simply return
        if self.delta not in monomial.free_symbols:
            return self.rec_builder.get_initial_value(monomial)
            
        # replace delta for now and get recurrence
        monomial = monomial.subs(self.delta, 1)
        original_init_val = self.rec_builder.get_initial_value(monomial)
        return original_init_val.diff(self.param)

    def get_solution(self, monom: Expr, solvers):
        # just lookup the solution
        solver = solvers[monom*self.delta]
        return solver.get(monom*self.delta), solver.is_exact
