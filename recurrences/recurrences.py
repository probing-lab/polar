from typing import Dict, List

from symengine.lib.symengine_wrapper import Matrix, Symbol, Expr, Zero, One

from program import Program
from utils import get_monoms


class Recurrences:

    program: Program
    recurrence_dict: Dict[Symbol, Expr]
    recurrence_matrix: Matrix
    variables: List[Symbol]
    is_inhomogeneous = False

    def __init__(self, recurrence_dict: Dict[Symbol, Expr], program: Program):
        self.program = program
        self.recurrence_dict = recurrence_dict
        self.variables = list(recurrence_dict.keys())
        self.__init_data__()

    def __init_data__(self):
        coefficients = []
        default = {w: Zero() for w in self.variables}
        for v in self.variables:
            current_coeffs = default.copy()
            monoms = get_monoms(self.recurrence_dict[v], constant_symbols=self.program.symbols, with_constant=True)
            for coeff, monom in monoms:
                current_coeffs[monom] = coeff
                if monom == 1:
                    self.is_inhomogeneous = True
            coefficients.append(list(current_coeffs.values()))

        if self.is_inhomogeneous:
            for cs in coefficients:
                if len(cs) == len(self.variables):
                    cs.append(Zero())
            coefficients.append([Zero() for _ in self.variables] + [One()])

        self.recurrence_matrix = Matrix(coefficients)
