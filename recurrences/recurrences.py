from typing import Dict, List, Set

from sympy import sympify, Expr, Matrix

from program import Program
from utils import get_monoms
import copy


class Recurrences:
    """
    Class for storing a system of recurrences. The class uses (and converts everything to) sympy
    """
    program: Program
    recurrence_dict: Dict[Expr, Expr]
    init_values_dict: Dict[Expr, Expr]
    recurrence_matrix: Matrix
    init_values_vector: Matrix
    monomials: List[Expr]
    dependencies: Dict[Expr, Set[Expr]]
    is_acyclic: bool
    is_inhomogeneous = False

    def __init__(self, recurrence_dict, init_values_dict, program: Program):
        self.program = program
        self.recurrence_dict = {sympify(k): sympify(v) for k, v in recurrence_dict.items()}
        self.init_values_dict = {sympify(k): sympify(v) for k, v in init_values_dict.items()}
        self.monomials = list(self.recurrence_dict.keys())
        self.dependencies = {}
        self.__init_data__()
        self.__init_is_acyclic__()
        pass

    def __init_data__(self):
        """
        Initializes the recurrence matrix as well as the initial value vector
        """
        coefficients = []
        default = {w: sympify(0) for w in self.monomials}
        for v in self.monomials:
            # Every monomial is described by one recurrence relation depending on other monomial
            # So in every row we collect the dependency coefficients
            current_coeffs = default.copy()
            monoms = get_monoms(
                self.recurrence_dict[v],
                constant_symbols={sympify(s) for s in self.program.symbols},
                with_constant=True,
                zero=sympify(0), one=sympify(1)
            )
            self.dependencies[v] = set()
            for coeff, monom in monoms:
                # one monom might appear multiple times in monoms
                if monom == 1:
                    current_coeffs[monom] = coeff
                    self.is_inhomogeneous = True
                else:
                    if monom != v:
                        self.dependencies[v].add(monom)
                    current_coeffs[monom] += coeff
            coefficients.append([c.expand() for c in current_coeffs.values()])

        initial_values = [self.init_values_dict[v] for v in self.monomials]

        # If the system is inhomogeneous (constant inhomogeneous part). Then we need to fill
        # up those recurrence coefficients which are homogeneous with "0".
        if self.is_inhomogeneous:
            initial_values.append(sympify(1))
            for cs in coefficients:
                if len(cs) == len(self.monomials):
                    cs.append(sympify(0))
            coefficients.append([sympify(0) for _ in self.monomials] + [sympify(1)])

        self.init_values_vector = Matrix(initial_values)
        self.recurrence_matrix = Matrix(coefficients)

    def __init_is_acyclic__(self):
        self.is_acyclic = True
        dependencies = copy.deepcopy(self.dependencies)
        while dependencies.keys():
            for v, ds in dependencies.items():
                if not ds:
                    next_var = v
                    break
            else:
                self.is_acyclic = False
                break
            dependencies.pop(next_var)
            for _, ds in dependencies.items():
                ds.discard(next_var)
