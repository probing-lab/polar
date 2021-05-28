from typing import List, Set

from symengine.lib.symengine_wrapper import Expr, Symbol, Zero

from utils import get_all_roots, characteristic_poly, solve_linear
from .exceptions import SolverException
from .recurrences import Recurrences


class RecurrencesSolutions:

    n: Symbol
    monomials: Set[Expr]
    recurrences: Recurrences
    characteristic_poly: Expr
    general_solution: Expr
    gen_sol_unknowns: List[Symbol]

    def __init__(self, recurrences: Recurrences):
        self.n = Symbol("n", integer=True, positive=True)
        self.recurrences = recurrences
        self.monomials = set(recurrences.variables)
        self.monom_to_index = {m: i for m, i in zip(recurrences.variables, range(len(recurrences.variables)))}
        self.__compute_charcteristic_poly__()
        self.__compute_general_solution__()

    def __compute_charcteristic_poly__(self):
        self.characteristic_poly = characteristic_poly(self.recurrences.recurrence_matrix)

    def __compute_general_solution__(self):
        unknowns = []
        roots = get_all_roots(self.characteristic_poly)
        solution = Zero()
        count = 0
        for root, multiplicity in roots:
            for i in range(multiplicity):
                if root != 0:
                    new_unknown = Symbol(f"C{count}")
                    unknowns.append(new_unknown)
                    solution += new_unknown * (self.n ** i) * (root ** self.n)
                    count += 1
        self.gen_sol_unknowns = unknowns
        self.general_solution = solution

    def get(self, monomial: Expr):
        if monomial not in self.monomials:
            raise SolverException(f"Monomial {monomial} not in current system of recurrences")

        number_equations = len(self.gen_sol_unknowns)
        monom_index = self.monom_to_index[monomial]
        concrete_values = self.recurrences.get_values_up_to_n(number_equations - 1)
        concrete_values = [cv[monom_index] for cv in concrete_values]
        equations = []
        for n in range(number_equations):
            eq = (self.general_solution.xreplace({self.n: n}) - concrete_values[n]).expand()
            equations.append(eq)
        concrete_unknowns = solve_linear(equations, self.gen_sol_unknowns)
        unknown_subs = {u: s for u, s in zip(self.gen_sol_unknowns, concrete_unknowns)}
        solution = self.general_solution.xreplace(unknown_subs).expand()
        return solution
