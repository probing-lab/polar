from functools import lru_cache

from symengine.lib.symengine_wrapper import Expr, sympy2symengine, oo
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import gamma
from sympy import sympify, Rational, I
from sympy.stats import Gamma as GammaDist, E as EV


class Gamma(Distribution):
    k: Expr
    theta: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 2:
            raise RuntimeError("Gamma distribution requires 2 parameters")
        self.k = parameters[0]
        self.theta = parameters[1]

    @lru_cache()
    def get_moment(self, p: int):
        k = sympify(self.k)
        theta = sympify(self.theta)
        x = GammaDist("x", k, theta)
        return sympy2symengine(Rational(EV(x**p)))

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.k = self.k.subs(substitutions)
        self.theta = self.theta.subs(substitutions)

    def sample(self, state):
        k = self.k.subs(state)
        theta = self.theta.subs(state)
        if not k.is_Number or not theta.is_Number:
            raise EvaluationException(
                f"Parameters {self.k}, {self.theta} don't evaluate to numbers with state {state}"
            )
        return gamma.rvs(float(k), scale=float(theta))

    def cf(self, t: Expr):
        theta = sympify(self.theta)
        k = sympify(self.k)
        t = sympify(t)
        return (1 - theta * I * t) ** (-k)

    def mgf(self, t: Expr):
        theta = sympify(self.theta)
        k = sympify(self.k)
        t = sympify(t)
        return (1 - theta * t) ** (-k)

    def mgf_exists_at(self, t: Expr):
        theta = sympify(self.theta)
        t = sympify(t)
        does_exist = t < 1 / theta
        if not does_exist.is_Boolean or not bool(does_exist):
            return False
        return True

    def get_free_symbols(self):
        return self.k.free_symbols.union(self.theta.free_symbols)

    def get_support(self):
        return {(0, oo)}

    def __str__(self):
        return f"Gamma({self.k}, {self.theta})"
