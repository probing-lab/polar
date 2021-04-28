from symengine.lib.symengine_wrapper import Expr, oo, Zero
from .distribution import Distribution


class Exponential(Distribution):
    lamb: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 1:
            raise RuntimeError("Exponential distribution requires 1 parameter")
        self.lamb = parameters[0]

    def get_moment(self, k: int):
        #TODO
        pass

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.lamb = self.lamb.subs(substitutions)

    def get_free_symbols(self):
        return self.lamb.free_symbols

    def get_support(self):
        return Zero(), oo

    def __str__(self):
        return f"Exponential({self.lamb})"
