from typing import Dict, List

from symengine.lib.symengine_wrapper import Matrix, Expr, Zero, One

from program import Program
from utils import get_monoms


class Recurrences:

    program: Program
    recurrence_dict: Dict[Expr, Expr]
    init_values_dict: Dict[Expr, Expr]
    recurrence_matrix: Matrix
    init_values_vector: Matrix
    variables: List[Expr]
    is_inhomogeneous = False

    def __init__(self, recurrence_dict: Dict[Expr, Expr], init_values_dict: Dict[Expr, Expr], program: Program):
        self.program = program
        self.recurrence_dict = recurrence_dict
        self.init_values_dict = init_values_dict
        self.variables = list(recurrence_dict.keys())
        self.__init_data__()

    def __init_data__(self):
        coefficients = []
        default = {w: Zero() for w in self.variables}
        for v in self.variables:
            current_coeffs = default.copy()
            monoms = get_monoms(self.recurrence_dict[v], constant_symbols=self.program.symbols, with_constant=True)
            for coeff, monom in monoms:
                if monom == 1:
                    current_coeffs[monom] = coeff
                    self.is_inhomogeneous = True
                else:
                    current_coeffs[monom] += coeff
            coefficients.append([c.expand() for c in current_coeffs.values()])

        initial_values = [self.init_values_dict[v] for v in self.variables]

        if self.is_inhomogeneous:
            initial_values.append(One())
            for cs in coefficients:
                if len(cs) == len(self.variables):
                    cs.append(Zero())
            coefficients.append([Zero() for _ in self.variables] + [One()])

        self.init_values_vector = Matrix(initial_values)
        self.recurrence_matrix = Matrix(coefficients)

    def get_values_up_to_n(self, n: int):
        results = [self.init_values_vector]
        last = self.init_values_vector
        for _ in range(n):
            last = self.recurrence_matrix * last
            results.append(last)
        return results
