from functools import lru_cache

from symengine.lib.symengine_wrapper import Expr, oo, sympy2symengine
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import norm
from sympy import sympify, Rational, E, I
from sympy.stats import Normal as NormalDist, E as EV
import math


class Normal(Distribution):
    mu: Expr
    sigma2: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 2:
            raise RuntimeError("Normal distribution requires 2 parameters")
        self.mu = parameters[0]
        self.sigma2 = parameters[1]

    @lru_cache()
    def get_moment(self, k: int):
        mu = sympify(self.mu)
        sigma = sympify(f"({self.sigma2}) ** (1/2)")
        x = NormalDist("x", mu, sigma)
        return sympy2symengine(Rational(EV(x ** k)))

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.mu = self.mu.subs(substitutions)
        self.sigma2 = self.sigma2.subs(substitutions)

    def sample(self, state):
        mu = sympify(self.mu.subs(state))
        sigma2 = sympify(self.sigma2.subs(state))
        if not mu.is_real or not sigma2.is_real:
            raise EvaluationException(
                f"Parameters {self.mu}, {self.sigma2} don't evaluate to numbers with state {state}")
        return norm.rvs(loc=float(mu), scale=math.sqrt(float(sigma2)))

    def cf(self, t: Expr):
        mu = sympify(self.mu)
        sigma2 = sympify(self.sigma2)
        t = sympify(t)
        return E**(I*mu*t - sigma2*(t**2)/2)

    def mgf(self, t: Expr):
        mu = sympify(self.mu)
        sigma2 = sympify(self.sigma2)
        t = sympify(t)
        return E**(mu*t + sigma2*(t**2)/2)

    def get_free_symbols(self):
        return self.mu.free_symbols.union(self.sigma2.free_symbols)

    def get_support(self):
        return {(-oo, oo)}

    def __str__(self):
        return f"Normal({self.mu}, {self.sigma2})"
