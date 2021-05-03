from symengine.lib.symengine_wrapper import Expr
from .distribution import Distribution
from .exceptions import EvaluationException
from scipy.stats import uniform


class Uniform(Distribution):
    a: Expr
    b: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 2:
            raise RuntimeError("Uniform distribution requires 2 parameters")
        self.a = parameters[0]
        self.b = parameters[1]

    def get_moment(self, k: int):
        #TODO
        pass

    def subs(self, substitutions):
        self.a = self.a.subs(substitutions)
        self.b = self.b.subs(substitutions)

    def get_free_symbols(self):
        return self.a.free_symbols.union(self.b.free_symbols)

    def is_discrete(self):
        return False

    def get_support(self):
        return self.a, self.b

    def sample(self, state):
        a = self.a.subs(state)
        b = self.b.subs(state)
        if not a.is_Number or not b.is_Number:
            raise EvaluationException(f"Parameters {self.a}, {self.b} don't evaluate to numbers with state {state}")
        return uniform.rvs(loc=float(a), scale=float(b) - float(a))

    def __str__(self):
        return f"Uniform({self.a}, {self.b})"
