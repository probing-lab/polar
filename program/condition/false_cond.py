from symengine.lib.symengine_wrapper import sympify, Expr
from .condition import Condition


class FalseCond(Condition):
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

    def is_implied_by_loop_guard(self):
        return self.is_loop_guard

    def get_loop_guard(self):
        if self.is_loop_guard:
            return self.copy()
        return None

    def __simple_copy__(self):
        return FalseCond()

    def __str__(self):
        return "false"

    def __eq__(self, obj):
        return isinstance(obj, FalseCond)

    def __hash__(self):
        return hash("FALSE")

    def get_normalized(self, program):
        return self, []
