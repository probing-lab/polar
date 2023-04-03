from typing import List
from sympy import Expr, numer, denom
from utils import are_coprime

ExponentBase = Expr


class ExponentLattice:

    bases: List[ExponentBase]

    def __init__(self, bases: List[ExponentBase]):
        self.bases = bases

    def compute_basis(self) -> List[List[int]]:
        if len(self.bases) <= 1:
            return []
        all_rational = all([b.is_Rational for b in self.bases])
        if all_rational:
            integers = [numer(b) for b in self.bases if numer(b) != 1]
            integers += [denom(b) for b in self.bases if denom(b) != 1]
            if are_coprime(integers):
                return []

        # Implement algebraic relations for algebraic numbers
        raise NotImplementedError()
