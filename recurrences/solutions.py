from functools import lru_cache
from typing import List, Set

from sympy import symbols, Symbol, Expr, Poly, sympify

from utils import get_all_roots, solve_linear
from .exceptions import SolverException
from .recurrences import Recurrences


class RecurrencesSolutions:

    n: Symbol
    t: Symbol
    monomials: Set[Expr]
    recurrences: Recurrences
    characteristic_poly: Poly
    general_solution: Expr
    gen_sol_unknowns: List[Symbol]
    numeric_roots: bool
    numeric_croots: bool

    def __init__(self, recurrences: Recurrences, numeric_roots: bool, numeric_croots: bool):
        self.n = symbols("n", integer=True, positive=True)
        self.recurrences = recurrences
        self.numeric_roots = numeric_roots
        self.numeric_croots = numeric_croots
        self.monomials = set(recurrences.variables)
        self.monom_to_index = {m: i for m, i in zip(recurrences.variables, range(len(recurrences.variables)))}
        self.characteristic_poly = self.recurrences.recurrence_matrix.charpoly()
        self.__compute_general_solution__()

    def __compute_general_solution__(self):
        unknowns = []
        roots = get_all_roots(self.characteristic_poly, self.numeric_roots, self.numeric_croots)
        solution = sympify(0)
        count = 0
        for root, multiplicity in roots:
            for i in range(multiplicity):
                if root != 0:
                    new_unknown = symbols(f"C{count}")
                    unknowns.append(new_unknown)
                    term = new_unknown * (self.n ** i)
                    if root != 1:
                        term = term * (root ** self.n)
                    solution += term
                    count += 1
        self.gen_sol_unknowns = unknowns
        self.general_solution = solution

    @lru_cache(maxsize=None)
    def get(self, monomial):
        monomial = sympify(monomial)
        if monomial not in self.monomials:
            raise SolverException(f"Monomial {monomial} not in current system of recurrences")

        concrete_unknowns = self.__solve_for_unknowns__(monomial)
        unknown_subs = {u: s for u, s in zip(self.gen_sol_unknowns, concrete_unknowns)}
        solution = self.general_solution.xreplace(unknown_subs).expand()
        return solution

    def __solve_for_unknowns__(self, monomial: Expr):
        number_equations = len(self.gen_sol_unknowns)
        monom_index = self.monom_to_index[monomial]
        concrete_values = [self.recurrences.init_values_vector]
        equations = []
        for n in range(1, number_equations+1):
            concrete_values.append(self.recurrences.recurrence_matrix * concrete_values[-1])
            eq = (self.general_solution.xreplace({self.n: n}) - concrete_values[n][monom_index]).expand()
            equations.append(eq)
        concrete_unknowns = solve_linear(equations, self.gen_sol_unknowns)

        not_solved = self.__any_is_still_unknown__(concrete_unknowns)
        next_n = number_equations+1
        while not_solved:
            concrete_values.append(self.recurrences.recurrence_matrix * concrete_values[-1])
            eq = (self.general_solution.xreplace({self.n: next_n}) - concrete_values[-1][monom_index]).expand()
            equations.append(eq)
            next_n += 1
            concrete_unknowns = solve_linear(equations, self.gen_sol_unknowns)
            not_solved = self.__any_is_still_unknown__(concrete_unknowns)

        return concrete_unknowns

    def __any_is_still_unknown__(self, solutions):
        for s in solutions:
            if s.is_Symbol and s in self.gen_sol_unknowns:
                return True
        return False
