from functools import lru_cache

from symengine.lib.symengine_wrapper import Expr, sympy2symengine, One, Zero
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import beta
from sympy import sympify, Rational, E, I
from sympy.stats import Beta as BetaDist, E as EV


class Beta(Distribution):
    a: Expr
    b: Expr
    scale: Expr

    def set_parameters(self, parameters):
        if len(parameters) == 2:
            self.a = parameters[0]
            self.b = parameters[1]
            self.scale = One()
        elif len(parameters) == 3:
            self.a = parameters[0]
            self.b = parameters[1]
            self.scale = parameters[2]
        else:
            raise RuntimeError("Beta distribution requires 2 or 3 parameters")

    @lru_cache()
    def get_moment(self, k: int):
        a = sympify(self.a)
        b = sympify(self.b)
        scale = sympify(self.scale)
        x = BetaDist("x", a, b)
        return sympy2symengine(Rational((scale ** k) * EV(x ** k)))

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.a = self.a.subs(substitutions)
        self.b = self.b.subs(substitutions)
        self.scale = self.scale.subs(substitutions)

    def sample(self, state):
        a = self.a.subs(state)
        b = self.b.subs(state)
        scale = self.scale.subs(state)
        if not a.is_Number or not b.is_Number:
            raise EvaluationException(
                f"Parameters {self.a}, {self.b} don't evaluate to numbers with state {state}")
        if not scale.is_Number:
            raise EvaluationException(
                f"Parameter {self.scale}, does not evaluate to a number with state {state}")
        return scale * beta.rvs(float(a), float(b))

    def cf(self, t: Expr):
        a = sympify(self.a)
        b = sympify(self.b)
        scale = sympify(self.scale)
        t = sympify(t)
        x = BetaDist("x", a, b)
        return EV(E**(I*t*scale*x))

    def mgf(self, t: Expr):
        a = sympify(self.a)
        b = sympify(self.b)
        scale = sympify(self.scale)
        t = sympify(t)
        x = BetaDist("x", a, b)
        return EV(E**(t*scale*x))

    def get_free_symbols(self):
        return self.a.free_symbols.union(self.b.free_symbols).union(self.scale.free_symbols)

    def get_support(self):
        return {(Zero(), self.scale)}

    def __str__(self):
        if self.scale == One():
            return f"Beta({self.a}, {self.b})"
        else:
            return f"Beta({self.a}, {self.b}, {self.scale})"
