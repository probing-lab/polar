from typing import Dict
from symengine.lib.symengine_wrapper import Expr, Symbol, sympify, sqrt, Zero, One, factorial
from sympy.stats import Normal, density
from utils import ce_bell_poly, prob_hermite_poly


class GramCharlierExpansion:

    cumulants: Dict[int, Expr]

    def __init__(self, cumulants: Dict[int, Expr]):
        self.cumulants = cumulants

    def __call__(self):
        x = Symbol("x")
        count_cumulants = len(self.cumulants.items())
        mu = self.cumulants[1] if count_cumulants > 0 else Zero()
        sigma2 = self.cumulants[2] if count_cumulants > 1 else One()
        sigma = sqrt(sigma2)
        phi = sympify(density(Normal("_", mu, sigma))(x))
        poly_term = One()
        for i in range(3, count_cumulants+1):
            bell_args = [Zero(), Zero()] + [self.cumulants[j] for j in range(3, i+1)]
            bell_part = ce_bell_poly(i, *bell_args) / (factorial(i) * (sigma ** i))
            hermit_part = prob_hermite_poly(i, (x - mu) / sigma)
            poly_term += bell_part * hermit_part
        return poly_term * phi
