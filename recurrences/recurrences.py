from typing import Dict, List

from sympy import sympify, Expr, Matrix

from program import Program
from utils import get_monoms


class Recurrences:
    """
    Class for storing a system of recurrences. The class uses (and converts everything to) sympy
    """
    program: Program
    recurrence_dict: Dict[Expr, Expr]
    init_values_dict: Dict[Expr, Expr]
    recurrence_matrix: Matrix
    init_values_vector: Matrix
    variables: List[Expr]
    is_inhomogeneous = False

    def __init__(self, recurrence_dict, init_values_dict, program: Program):
        self.program = program
        self.recurrence_dict = {sympify(k): sympify(v) for k, v in recurrence_dict.items()}
        self.init_values_dict = {sympify(k): sympify(v) for k, v in init_values_dict.items()}
        self.variables = list(self.recurrence_dict.keys())
        self.__init_data__()

    def __init_data__(self):
        """
        Initializes the recurrence matrix as well as the initial value vector
        """
        coefficients = []
        default = {w: sympify(0) for w in self.variables}
        for v in self.variables:
            # Every variable is described by one recurrence relation depending on other variables
            # So in every row we collect the dependency coefficients
            current_coeffs = default.copy()
            monoms = get_monoms(
                self.recurrence_dict[v],
                constant_symbols={sympify(s) for s in self.program.symbols},
                with_constant=True,
                zero=sympify(0), one=sympify(1)
            )
            for coeff, monom in monoms:
                # one monom might appear multiple times in monoms
                if monom == 1:
                    current_coeffs[monom] = coeff
                    self.is_inhomogeneous = True
                else:
                    current_coeffs[monom] += coeff
            coefficients.append([c.expand() for c in current_coeffs.values()])

        initial_values = [self.init_values_dict[v] for v in self.variables]

        # If the system is inhomogeneous (constant inhomogeneous part). Then we need to fill
        # up those recurrence coefficients which are homogeneous with "0".
        if self.is_inhomogeneous:
            initial_values.append(sympify(1))
            for cs in coefficients:
                if len(cs) == len(self.variables):
                    cs.append(sympify(0))
            coefficients.append([sympify(0) for _ in self.variables] + [sympify(1)])

        self.init_values_vector = Matrix(initial_values)
        self.recurrence_matrix = Matrix(coefficients)
