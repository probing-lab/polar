from functools import lru_cache
from typing import List
import random

from symengine.lib.symengine_wrapper import sympify, Expr, Rational
from sympy import I, E, sympify as ssympify

from .distribution import Distribution


class DiscreteUniform(Distribution):
    values: List[Expr]

    def set_parameters(self, parameters):
        if len(parameters) != 2:
            raise RuntimeError("Uniform distribution requires 2 parameters")
        if not parameters[0].is_Integer or not parameters[1].is_Integer:
            raise RuntimeError("For discrete uniform only integer parameters are supported")
        values = list(range(int(parameters[0]), int(parameters[1]) + 1))
        self.values = [sympify(v) for v in values]

    @lru_cache()
    def get_moment(self, k: int):
        m = 0
        p = Rational(1, len(self.values))
        for v in self.values:
            m += (v ** k) * p
        return m

    def subs(self, substitutions):
        return

    def get_free_symbols(self):
        return set()

    def is_discrete(self):
        return True

    def get_support(self):
        return set(self.values)

    def sample(self, state):
        return random.choice(self.values)

    def cf(self, t: Expr):
        a = ssympify(self.values[0])
        b = ssympify(self.values[-1])
        t = ssympify(t)
        return (E**(I*a*t) - E**(I*(b+1)*t))/((b - a + 1)*(1 - E**(I*t)))

    def mgf(self, t: Expr):
        a = ssympify(self.values[0])
        b = ssympify(self.values[-1])
        t = ssympify(t)
        return (E**(a*t) - E**((b+1)*t))/((b - a + 1)*(1 - (E**t)))

    def mgf_exists_at(self, t: Expr):
        return True

    def __str__(self):
        return f"DiscreteUniform({self.values[0]}, {self.values[-1]})"
