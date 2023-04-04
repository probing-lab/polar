from typing import List, Set, Dict
from sympy import Symbol, Expr, sympify, groebner

from invariants.exceptions import LatticeIdealException
from utils import get_unique_var


class LatticeIdeal:

    lattice_basis: List[List[int]]
    inverse_symbols: Dict[Symbol, Symbol]

    def __init__(self, lattice_basis: List[List[int]], symbols: List[Symbol]):
        self.lattice_basis = lattice_basis
        self.symbols = symbols
        self.inverse_symbols = {}

    def compute_basis(self) -> Set[Expr]:
        if len(self.lattice_basis) == 0:
            return set()

        self.inverse_symbols = {}
        equations = set()
        for row in self.lattice_basis:
            expr = sympify(1)
            for i, power in enumerate(row):
                if power > 0:
                    expr *= self.symbols[i] ** power
                elif power < 0:
                    expr *= self.get_inverse_symbol(self.symbols[i]) ** (-power)
            equations.add(expr - 1)

        if len(self.inverse_symbols) == 0:
            return equations

        for symbol, inv_symbol in self.inverse_symbols.items():
            equations.add(symbol * inv_symbol - 1)

        inverse_symbols = set(self.inverse_symbols.values())
        all_symbols = list(inverse_symbols) + self.symbols
        all_symbols_basis = groebner(equations, *all_symbols)

        basis = set()
        for expr in all_symbols_basis:
            if not inverse_symbols & expr.free_symbols:
                basis.add(expr)
        return basis

    def get_inverse_symbol(self, symbol: Symbol):
        if symbol not in self.symbols:
            raise LatticeIdealException(f"Symbol {symbol} is not a symbol of the lattice ideal")
        if symbol not in self.inverse_symbols:
            self.inverse_symbols[symbol] = Symbol(get_unique_var("inv"))
        return self.inverse_symbols[symbol]
