from symengine.lib.symengine_wrapper import Expr, Zero, One
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import bernoulli
from sympy import I, E, sympify


class Bernoulli(Distribution):
    p: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 1:
            raise RuntimeError("Bernoulli distribution requires 1 parameter")
        self.p = parameters[0]

    def get_moment(self, _: int):
        return self.p

    def is_discrete(self):
        return True

    def subs(self, substitutions):
        self.p = self.p.subs(substitutions)

    def sample(self, state):
        p = self.p.subs(state)
        if not p.is_Number:
            raise EvaluationException(f"Parameter {self.p} doesn't evaluate to number with state {state}")
        return bernoulli.rvs(float(p))

    def cf(self, t: Expr):
        p = sympify(self.p)
        t = sympify(t)
        return (1 - p) + p*E**(I*t)

    def get_free_symbols(self):
        return self.p.free_symbols

    def get_support(self):
        return {Zero(), One()}

    def __str__(self):
        return f"Bernoulli({self.p})"
