from functools import lru_cache

from symengine.lib.symengine_wrapper import Expr, sympy2symengine
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import beta
from sympy import sympify, Rational
from sympy.stats import Beta as BetaDist, E


class Beta(Distribution):
    a: Expr
    b: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 2:
            raise RuntimeError("Beta distribution requires 2 parameters")
        self.a = parameters[0]
        self.b = parameters[1]

    @lru_cache()
    def get_moment(self, k: int):
        a = sympify(self.a)
        b = sympify(self.b)
        x = BetaDist("x", a, b)
        return sympy2symengine(Rational(E(x ** k)))

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.a = self.a.subs(substitutions)
        self.b = self.b.subs(substitutions)

    def sample(self, state):
        a = self.a.subs(state)
        b = self.b.subs(state)
        if not a.is_Number or not b.is_Number:
            raise EvaluationException(
                f"Parameters {self.a}, {self.b} don't evaluate to numbers with state {state}")
        return beta.rvs(float(a), float(b))

    def get_free_symbols(self):
        return self.a.free_symbols.union(self.b.free_symbols)

    def get_support(self):
        return {(0, 1)}

    def __str__(self):
        return f"Beta({self.a}, {self.b})"
