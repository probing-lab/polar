from functools import lru_cache

from sympy import sympify, symbols, summation

from .solver import Solver
from recurrences import Recurrences
from utils import without_piecewise


class AcyclicSolver(Solver):

    recurrences: Recurrences

    def __init__(self, recurrences: Recurrences):
        self.recurrences = recurrences
        self.monom_to_index = {m: i for m, i in zip(recurrences.monomials, range(len(recurrences.monomials)))}
        self.n = symbols("n", integer=True, positive=True)

    @property
    def is_exact(self) -> bool:
        return True

    @lru_cache(maxsize=None)
    def get(self, monomial):
        monomial = sympify(monomial)
        monom_index = self.monom_to_index[monomial]
        rec_coeff = sympify(0)
        inhom_part = sympify(0)
        for i in range(len(self.recurrences.monomials)):
            coeff = self.recurrences.recurrence_matrix[monom_index, i]
            if coeff == 0:
                continue
            if i == monom_index:
                rec_coeff = coeff
                continue
            sol = self.get(self.recurrences.monomials[i]).xreplace({self.n: self.n-1}).expand()
            inhom_part += coeff * sol
        if self.recurrences.is_inhomogeneous:
            inhom_part += self.recurrences.recurrence_matrix[monom_index, -1]

        inhom_part = inhom_part.expand()
        if rec_coeff == 0:
            return inhom_part

        hom_solution = (rec_coeff ** self.n) * self.recurrences.init_values_vector[monom_index]
        k = symbols('_k', integer=True, positive=True)
        summand = ((rec_coeff ** k) * inhom_part.xreplace({self.n: self.n - k})).simplify()
        particular_solution = summation(summand, (k, 0, (self.n - 1)))
        particular_solution = without_piecewise(particular_solution)
        solution = (hom_solution + particular_solution).simplify()
        return solution
