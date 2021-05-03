from symengine.lib.symengine_wrapper import sympify, Expr
from .condition import Condition


class FalseCond(Condition):
    def __str__(self):
        return "false"

    def simplify(self):
        return self

    def reduce(self):
        return []

    def get_conjuncts(self, program):
        return self, []

    def subs(self, substitutions):
        pass

    def evaluate(self, state):
        return False

    def to_arithm(self, _) -> Expr:
        return sympify(0)

    def get_conjunctions(self):
        return [self]

    def get_free_symbols(self):
        return set()
