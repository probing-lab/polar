from functools import lru_cache
from symengine.lib.symengine_wrapper import sympy2symengine, Expr, oo, Zero
from sympy import sympify, Rational, I, exp
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import geom
from sympy.stats import Geometric as GeomDist, E as EV


class Geometric(Distribution):
    """Geometric distribution: number of failures before the first success with success probability p.
    In particular, the support is {0, 1, 2, ...}.
    (Note that there is another definition as the number trials instead of failures where the support is {1, 2, ...}.)"""

    p: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 1:
            raise RuntimeError("Geometric distribution requires 1 parameter")
        self.p = parameters[0]

    @lru_cache()
    def get_moment(self, k: int):
        p = sympify(self.p)
        x = GeomDist("x", p)
        # In sympy, the Geometric distribution starts at 1, not 0, so we have to subtract 1:
        return sympy2symengine(Rational(EV((x - 1) ** k)))

    def is_discrete(self):
        return True

    def subs(self, substitutions):
        self.p = self.p.subs(substitutions)

    def sample(self, state):
        p = self.p.subs(state)
        if not p.is_Number:
            raise EvaluationException(
                f"Parameter {self.p} doesn't evaluate to number with state {state}"
            )
        return geom.rvs(float(p))

    def get_free_symbols(self):
        return self.p.free_symbols

    def cf(self, t: Expr):
        t = sympify(t)
        p = sympify(self.p)
        return p / (1 - (1 - p) * exp(I * t))

    def mgf(self, t: Expr):
        t = sympify(t)
        p = sympify(self.p)
        return p / (1 - (1 - p) * exp(t))

    def mgf_exists_at(self, t: Expr):
        p = sympify(self.p)
        t = sympify(t)
        does_exist = (1 - p) * exp(t) < 1
        if not does_exist.is_Boolean or not bool(does_exist):
            return False
        return True

    def get_support(self):
        return {(Zero(), oo)}

    def __str__(self):
        return f"Geometric({self.p})"
