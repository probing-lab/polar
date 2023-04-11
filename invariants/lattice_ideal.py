from typing import List, Set, Dict
from sympy import Symbol, Expr, sympify, groebner

from invariants.exceptions import LatticeIdealException
from utils import get_unique_var


class LatticeIdeal:
    """
    Given a basis for an exponent-lattice, this class represents the ideal of all polynomial relations among the
    lattice elements. All these polynomial relations form an ideal. This class provides the functionality of
    computing a finite basis for this ideal.
    """

    lattice_basis: List[List[int]]
    # Every symbol lattice component with symbol b, its inverse symbol c is such that b*c = 1
    # e.g. if b represents 2 then c represents 1/2.
    inverse_symbols: Dict[Symbol, Symbol]

    def __init__(self, lattice_basis: List[List[int]], symbols: List[Symbol]):
        """
        :param lattice_basis: A basis for the exponent-lattice
        :param symbols: A list of symbols that represent the components of the exponent-lattice (that is one symbol
        for every exponent-base)
        """
        self.lattice_basis = lattice_basis
        self.symbols = symbols
        self.inverse_symbols = {}

    def compute_basis(self) -> Set[Expr]:
        """
        Computes a finite basis for the ideal of all polynomial relations among the components of the exponent-lattice.
        """
        if len(self.lattice_basis) == 0:
            return set()

        self.inverse_symbols = {}
        equations = set()
        # Add all the polynomial relationships given by the basis of the exponent-lattice
        for row in self.lattice_basis:
            expr = sympify(1)
            for i, power in enumerate(row):
                if power > 0:
                    expr *= self.symbols[i] ** power
                elif power < 0:
                    # for negative powers we use the symbol for the inverse of bi.
                    expr *= self.get_inverse_symbol(self.symbols[i]) ** (-power)
            equations.add(expr - 1)

        # if we didn't have any negative powers (no inverse symbols were used) than we already have a basis.
        if len(self.inverse_symbols) == 0:
            return equations

        # If not we further add the polynomial relationship b*c = 1 for every symbol b and its inverse symbol c.
        for symbol, inv_symbol in self.inverse_symbols.items():
            equations.add(symbol * inv_symbol - 1)

        # No, we need to eliminate all inverse symbols (compute the elimination ideal)
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
