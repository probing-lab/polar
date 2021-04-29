from symengine.lib.symengine_wrapper import sympify
from .condition import Condition


class TrueCond(Condition):
    def __str__(self):
        return "true"

    def simplify(self):
        return self

    def reduce(self):
        return []

    def get_normalized(self, program):
        return self

    def subs(self, substitutions):
        pass

    def get_free_symbols(self):
        return set()

    def to_arithm(self, p):
        return sympify(1)
