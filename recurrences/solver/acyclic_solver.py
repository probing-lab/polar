from functools import lru_cache

from sympy import sympify, symbols, summation, Piecewise

from .solver import Solver
from recurrences import Recurrences
from utils import without_piecewise


class AcyclicSolver(Solver):
    recurrences: Recurrences

    def __init__(self, recurrences: Recurrences):
        self.recurrences = recurrences
        self.monom_to_index = {
            m: i
            for m, i in zip(recurrences.monomials, range(len(recurrences.monomials)))
        }
        self.n = symbols("n", integer=True)

    @property
    def is_exact(self) -> bool:
        return True

    @lru_cache(maxsize=None)
    def get(self, monomial):
        monomial = sympify(monomial)
        monom_index = self.monom_to_index[monomial]
        solution = self.__get_without_zero__(monomial)
        solution = Piecewise(
            (self.recurrences.init_values_vector[monom_index], self.n <= 0),
            (solution, True),
        )
        return solution

    @lru_cache(maxsize=None)
    def __get_without_zero__(self, monomial):
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
            sol = self.__get_without_zero__(self.recurrences.monomials[i])
            inhom_part += coeff * sol
        if self.recurrences.is_inhomogeneous:
            inhom_part += self.recurrences.recurrence_matrix[monom_index, -1]

        inhom_part = inhom_part.expand()
        if rec_coeff == 0:
            return inhom_part.xreplace({self.n: self.n - 1}).simplify()

        first_value = (
            self.recurrences.recurrence_matrix * self.recurrences.init_values_vector
        )[monom_index]
        return self.__solve_rec_by_summing__(rec_coeff, first_value, inhom_part)

    @lru_cache(maxsize=None)
    def __solve_rec_by_summing__(self, rec_coeff, first_value, inhom_part):
        hom_solution = (rec_coeff ** (self.n - 1)) * first_value
        k = symbols("_k", integer=True)
        summand = (
            (rec_coeff ** (self.n - k - 1)) * inhom_part.xreplace({self.n: k})
        ).simplify()
        particular_solution = summation(summand, (k, 1, self.n - 1))
        particular_solution = without_piecewise(particular_solution)
        return (hom_solution + particular_solution).simplify()
