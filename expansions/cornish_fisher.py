from functools import lru_cache
from typing import Dict
from symengine.lib.symengine_wrapper import Expr, Rational, Symbol, Zero, sqrt, sympy2symengine
from math import factorial
import sympy as sym
from utils import prob_hermite_poly, get_terms_with_var


class CornishFisherExpansion:

    cumulants: Dict[int, Expr]

    def __init__(self, cumulants: Dict[int, Expr]):
        self.cumulants = cumulants
        self.h = Symbol("h")
        self.z = Symbol("z")

    def __call__(self):
        result = self.z + sum([self.xi(k) for k in range(1, len(self.cumulants) - 1)])
        result = sqrt(self.cumulants[2]) * result + self.cumulants[1]
        result = sym.sympify(result)
        result = result.xreplace({sym.Symbol("z"): sym.sqrt(2) * sym.erfinv(2 * sym.Symbol("p") - 1)})
        return result

    @lru_cache(maxsize=None)
    def xi(self, k):
        xi_h = self.xi_h(k)
        terms_with_h, rest = get_terms_with_var(xi_h, self.h)
        result = rest
        for (power, coeff) in terms_with_h:
            result += coeff * prob_hermite_poly(power, self.z)
        return result.expand()

    @lru_cache(maxsize=None)
    def xi_h(self, k):
        result = self.a(k) * (self.h ** (k+1))

        s = Zero()
        for j in range(1, k):
            factor_2 = self.xi_h(k-j) - self.xi(k-j)
            factor_3 = self.xi(j) - self.a(j) * (self.h ** (j+1))
            s += Rational(j, k) * factor_2 * factor_3 * self.h

        result = result - s
        return result.expand()

    @lru_cache(maxsize=None)
    def a(self, k):
        return sympy2symengine(self.cumulants[k+2]) / (factorial(k+2) * sqrt(sympy2symengine(self.cumulants[2])) ** (k+2))
