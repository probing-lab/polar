from symengine.lib.symengine_wrapper import sympify, Expr
from .condition import Condition


class FalseCond(Condition):
    def __str__(self):
        return "false"

    def simplify(self):
        return self

    def reduce(self, store):
        return []

    def get_conjuncts(self):
        return [self]

    def subs(self, substitutions):
        pass

    def evaluate(self, state):
        return False

    def to_arithm(self, _) -> Expr:
        return sympify(0)

    def get_free_symbols(self):
        return set()

    def copy(self):
        return FalseCond()

    def __eq__(self, obj):
        return isinstance(obj, FalseCond)

    def get_normalized(self, program):
        return self, []
