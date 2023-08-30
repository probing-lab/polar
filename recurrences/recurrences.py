from typing import Dict, List, Set

from sympy import sympify, Expr, Matrix, Symbol

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
    monomials: List[Expr]
    dependencies: Dict[Expr, Set[Expr]]
    is_acyclic: bool
    is_inhomogeneous = False
    constant_symbols: List[Symbol]
    # Stores the recurrence in homogenous form
    # i.e: Recurrence is recurrence_matrix^n * init_values_vector
    recurrence_matrix: Matrix
    init_values_vector: Matrix
    # Stores the recurrence in inhomogeneous form
    # i.e: Recurrence equation is f(n+1) = A*f(n) + b with initial values x (b might be 0)
    A: Matrix
    b: Matrix
    x: Matrix

    def __init__(
        self,
        recurrence_dict,
        init_values_dict,
        program: Program,
        const_symbols: List[Symbol] = None,
    ):
        self.program = program
        self.recurrence_dict = {
            sympify(k): sympify(v) for k, v in recurrence_dict.items()
        }
        self.init_values_dict = {
            sympify(k): sympify(v) for k, v in init_values_dict.items()
        }
        self.monomials = list(self.recurrence_dict.keys())
        self.dependencies = {}
        if const_symbols is None:
            self.constant_symbols = program.symbols
        else:
            self.constant_symbols = const_symbols
        self._init_data()
        self._init_is_acyclic()

    def _init_data(self):
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
                constant_symbols={sympify(s) for s in self.constant_symbols},
                with_constant=True,
                zero=sympify(0),
                one=sympify(1),
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

        if self.is_inhomogeneous:
            self.A = Matrix(coefficients)[:, :-1]
            self.b = Matrix(coefficients)[:, -1]
            self.x = Matrix(initial_values)

            # If the system is inhomogeneous (constant inhomogeneous part). Then we need to fill
            # up those recurrence coefficients which are homogeneous with "0".
            initial_values.append(sympify(1))
            for cs in coefficients:
                if len(cs) == len(self.monomials):
                    cs.append(sympify(0))
            coefficients.append([sympify(0) for _ in self.monomials] + [sympify(1)])
        else:
            self.A = Matrix(coefficients)
            self.b = Matrix([sympify(0) for _ in self.monomials])
            self.x = Matrix(initial_values)

        self.init_values_vector = Matrix(initial_values)
        self.recurrence_matrix = Matrix(coefficients)

    def _init_is_acyclic(self):
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
