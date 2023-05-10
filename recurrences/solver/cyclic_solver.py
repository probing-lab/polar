from functools import lru_cache
from typing import List, Set

from sympy import symbols, Symbol, Expr, Poly, sympify, Piecewise

from .solver import Solver
from utils import get_all_roots, solve_linear
from recurrences.exceptions import SolverException
from recurrences import Recurrences


class CyclicSolver(Solver):
    n: Symbol
    t: Symbol
    monomials: Set[Expr]
    recurrences: Recurrences
    characteristic_poly: Poly
    general_solution: Expr
    gen_sol_unknowns: List[Symbol]
    gen_sol_unknowns_set: Set[Symbol]
    numeric_roots: bool
    numeric_croots: bool
    numeric_eps: float
    _is_exact: bool

    def __init__(
        self,
        recurrences: Recurrences,
        numeric_roots: bool,
        numeric_croots: bool,
        numeric_eps: float,
    ):
        self.n = symbols("n", integer=True)
        self.recurrences = recurrences
        self.numeric_roots = numeric_roots
        self.numeric_croots = numeric_croots
        self.numeric_eps = numeric_eps
        self.monomials = set(recurrences.monomials)
        self.monom_to_index = {
            m: i
            for m, i in zip(recurrences.monomials, range(len(recurrences.monomials)))
        }
        self.characteristic_poly = self.recurrences.recurrence_matrix.charpoly()
        self._compute_general_solution()

    def _compute_general_solution(self):
        unknowns = []
        roots, self._is_exact = get_all_roots(
            self.characteristic_poly,
            self.numeric_roots,
            self.numeric_croots,
            self.numeric_eps,
        )
        solution = sympify(0)
        count = 0
        for root, multiplicity in roots:
            for i in range(multiplicity):
                if root != 0:
                    new_unknown = symbols(f"C{count}")
                    unknowns.append(new_unknown)
                    term = new_unknown * (self.n**i)
                    if root != 1:
                        term = term * (root**self.n)
                    solution += term
                    count += 1
        self.gen_sol_unknowns = unknowns
        self.gen_sol_unknowns_set = set(unknowns)
        self.general_solution = solution

    @property
    def is_exact(self) -> bool:
        return self._is_exact

    @lru_cache(maxsize=None)
    def get(self, monomial):
        monomial = sympify(monomial)
        if monomial not in self.monomials:
            raise SolverException(
                f"Monomial {monomial} not in current system of recurrences"
            )

        solution = self.general_solution
        if self.gen_sol_unknowns:
            concrete_unknowns = self._solve_for_unknowns(monomial)
            unknown_subs = {
                u: s for u, s in zip(self.gen_sol_unknowns, concrete_unknowns)
            }
            solution = self.general_solution.xreplace(unknown_subs)

        solution = self._add_beginning_values(solution, self.monom_to_index[monomial])

        return solution.expand()

    def _solve_for_unknowns(self, monomial: Expr):
        number_equations = len(self.gen_sol_unknowns)
        monom_index = self.monom_to_index[monomial]
        concrete_values = [self.recurrences.init_values_vector]
        equations = []
        for n in range(1, number_equations + 1):
            concrete_values.append(
                self.recurrences.recurrence_matrix * concrete_values[-1]
            )
            eq = (
                self.general_solution.xreplace({self.n: n})
                - concrete_values[n][monom_index]
            ).expand()
            equations.append(eq)
        concrete_unknowns = solve_linear(equations, self.gen_sol_unknowns)

        not_solved = self._any_is_still_unknown(concrete_unknowns)
        next_n = number_equations + 1
        while not_solved:
            concrete_values.append(
                self.recurrences.recurrence_matrix * concrete_values[-1]
            )
            eq = (
                self.general_solution.xreplace({self.n: next_n})
                - concrete_values[-1][monom_index]
            ).expand()
            equations.append(eq)
            next_n += 1
            concrete_unknowns = solve_linear(equations, self.gen_sol_unknowns)
            not_solved = self._any_is_still_unknown(concrete_unknowns)

        return concrete_unknowns

    def _add_beginning_values(self, solution, monom_index):
        beginning_values = [self.recurrences.init_values_vector]
        for _ in range(self.characteristic_poly.degree() - 1):
            beginning_values.append(
                self.recurrences.recurrence_matrix * beginning_values[-1]
            )

        pieces = []
        for i, v in enumerate(beginning_values):
            pieces.append((v[monom_index], self.n <= i))
        pieces.append((solution, True))
        return Piecewise(*pieces)

    def _any_is_still_unknown(self, solutions):
        for s in solutions:
            if s.free_symbols & set(self.gen_sol_unknowns_set):
                return True
        return False
