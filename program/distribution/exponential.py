from functools import lru_cache
from symengine.lib.symengine_wrapper import Expr, oo, Zero, factorial
from sympy import sympify, I
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import expon


class Exponential(Distribution):
    lamb: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 1:
            raise RuntimeError("Exponential distribution requires 1 parameter")
        self.lamb = parameters[0]

    @lru_cache()
    def get_moment(self, k: int):
        return factorial(k) / (self.lamb ** k)

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.lamb = self.lamb.subs(substitutions)

    def sample(self, state):
        lamb = self.lamb.subs(state)
        if not lamb.is_Number:
            raise EvaluationException(f"Parameter {self.lamb} doesn't evaluate to number with state {state}")
        return expon.rvs(scale=1/float(lamb))

    def get_free_symbols(self):
        return self.lamb.free_symbols

    def cf(self, t: Expr):
        lamb = sympify(self.lamb)
        t = sympify(t)
        return lamb/(lamb - I*t)

    def mgf(self, t: Expr):
        lamb = sympify(self.lamb)
        t = sympify(t)
        return lamb/(lamb - t)

    def mgf_exists_at(self, t: Expr):
        lamb = sympify(self.lamb)
        t = sympify(t)
        does_exist = t < lamb
        if not does_exist.is_Boolean or not bool(does_exist):
            return False
        return True

    def get_support(self):
        return {(Zero(), oo)}

    def __str__(self):
        return f"Exponential({self.lamb})"
