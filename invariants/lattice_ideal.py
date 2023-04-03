from typing import List, Set
from sympy import Symbol, Expr


class LatticeIdeal:

    lattice_basis: List[List[int]]

    def __init__(self, lattice_basis: List[List[int]], symbols: List[Symbol]):
        self.lattice_basis = lattice_basis
        self.symbols = symbols

    def compute_basis(self) -> Set[Expr]:
        if len(self.lattice_basis) == 0:
            return set()
        # TODO
        raise NotImplementedError()
