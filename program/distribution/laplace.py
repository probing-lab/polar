from symengine.lib.symengine_wrapper import Expr, oo
from .distribution import Distribution


class Laplace(Distribution):
    mu: Expr
    b: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 2:
            raise RuntimeError("Laplace distribution requires 2 parameters")
        self.mu = parameters[0]
        self.b = parameters[1]

    def get_moment(self, k: int):
        #TODO
        pass

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.mu = self.mu.subs(substitutions)
        self.b = self.b.subs(substitutions)

    def get_free_symbols(self):
        return self.mu.free_symbols.union(self.b.free_symbols)

    def get_support(self):
        return -oo, oo

    def __str__(self):
        return f"Laplace({self.mu}, {self.b})"

