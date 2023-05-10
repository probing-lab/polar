from functools import lru_cache

from symengine.lib.symengine_wrapper import Expr, oo, sympy2symengine
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import laplace
from sympy import Rational, sympify, I, E, Abs
from sympy.stats import E as EV, Laplace as LaplaceRV


class Laplace(Distribution):
    mu: Expr
    b: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 2:
            raise RuntimeError("Laplace distribution requires 2 parameters")
        self.mu = parameters[0]
        self.b = parameters[1]

    @lru_cache()
    def get_moment(self, k: int):
        x = LaplaceRV("x", self.mu, self.b)
        return sympy2symengine(Rational(EV(x**k)))

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.mu = self.mu.subs(substitutions)
        self.b = self.b.subs(substitutions)

    def sample(self, state):
        mu = self.mu.subs(state)
        b = self.b.subs(state)
        if not mu.is_Number or not b.is_Number:
            raise EvaluationException(
                f"Parameters {self.mu}, {self.b} don't evaluate to numbers with state {state}"
            )
        return laplace.rvs(scale=float(b), loc=float(mu))

    def cf(self, t: Expr):
        mu = sympify(self.mu)
        b = sympify(self.b)
        t = sympify(t)
        return (E ** (mu * I * t)) / (1 + b**2 * t**2)

    def mgf(self, t: Expr):
        mu = sympify(self.mu)
        b = sympify(self.b)
        t = sympify(t)
        return (E ** (mu * t)) / (1 - b**2 * t**2)

    def mgf_exists_at(self, t: Expr):
        b = sympify(self.b)
        t = sympify(t)
        does_exist = Abs(t) < 1 / b
        if not does_exist.is_Boolean or not bool(does_exist):
            return False
        return True

    def get_free_symbols(self):
        return self.mu.free_symbols.union(self.b.free_symbols)

    def get_support(self):
        return {(-oo, oo)}

    def __str__(self):
        return f"Laplace({self.mu}, {self.b})"
