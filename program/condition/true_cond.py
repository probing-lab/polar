from symengine.lib.symengine_wrapper import sympify
from .condition import Condition


class TrueCond(Condition):

    def is_implied_by_loop_guard(self):
        return True

    def get_loop_guard(self):
        if self.is_loop_guard:
            return self.copy()
        return None

    def simplify(self):
        return self

    def reduce(self, store):
        return []

    def get_normalized(self, program):
        return self, []

    def subs(self, substitutions):
        pass

    def evaluate(self, state):
        return True

    def get_free_symbols(self):
        return set()

    def get_conjuncts(self):
        return [self]

    def to_arithm(self, p):
        return sympify(1)

    def __str__(self):
        return "true"

    def __eq__(self, obj):
        return isinstance(obj, TrueCond)

    def __hash__(self):
        return hash("TRUE")

    def __simple_copy__(self):
        return TrueCond()
