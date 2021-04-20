from diofant import Expr
from .distribution import Distribution


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

    def get_type(self):
        return None

    def subs(self, substitutions):
        self.a = self.a.subs(substitutions)
        self.b = self.b.subs(substitutions)

    def get_free_symbols(self):
        return self.a.free_symbols.union(self.b.free_symbols)

    def is_discrete(self):
        return False

    def __str__(self):
        return f"Uniform({self.a}, {self.b})"
