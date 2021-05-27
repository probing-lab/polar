from typing import List

from symengine.lib.symengine_wrapper import Expr, Symbol, Zero

from utils import get_all_roots, characteristic_poly
from .recurrences import Recurrences


class RecurrenceSolver:

    n: Symbol
    recurrences: Recurrences
    characteristic_poly: Expr
    general_solution: Expr
    gen_sol_unknowns: List[Symbol]

    def __init__(self):
        self.n = Symbol("n", integer=True, positive=True)

    def set_recurrences(self, r: Recurrences):
        self.recurrences = r

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
        print(solution)

    def solve(self):
        self.__compute_charcteristic_poly__()
        self.__compute_general_solution__()
