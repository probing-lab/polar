from typing import Dict
from symengine.lib.symengine_wrapper import Expr, Symbol, sympify
from sympy.stats import Normal, density


class GramCharlierExpansion:

    cumulants: Dict[int, Expr]

    def __init__(self, cumulants: Dict[int, Expr]):
        self.cumulants = cumulants

    def __call__(self):
        x = Symbol("x")
        phi = sympify(density(Normal("_", 0, 1))(x))
        return phi
