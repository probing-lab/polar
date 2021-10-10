from typing import List, Tuple
from sympy import Expr, Symbol, groebner, PolynomialError

ClosedForm = Expr


class InvariantIdeal:

    invariant_data: List[Tuple[Symbol, ClosedForm]]

    def __init__(self, invariant_data: List[Tuple[Symbol, ClosedForm]]):
        self.invariant_data = invariant_data

    def compute_basis(self) -> List[Expr]:
        try:
            polys = [s - cf for s, cf in self.invariant_data]
            n = Symbol("n", integer=True)
            symbols = [n] + [s for s, _ in self.invariant_data]
            cf_basis = groebner(polys, *symbols)
            basis = []
            for expr in cf_basis:
                if n not in expr.free_symbols:
                    basis.append(expr)
            return basis
        except PolynomialError:
            print("Invariants for exponential closed-forms are not yet supported.")
            exit()
