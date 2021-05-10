from .condition import Condition
from .false_cond import FalseCond


class Or(Condition):
    cond1: Condition
    cond2: Condition

    def __init__(self, cond1, cond2):
        self.cond1 = cond1
        self.cond2 = cond2

    def simplify(self):
        self.cond1 = self.cond1.simplify()
        self.cond2 = self.cond2.simplify()
        if isinstance(self.cond1, FalseCond):
            return self.cond2
        if isinstance(self.cond2, FalseCond):
            return self.cond1
        return self

    def reduce(self, store):
        return self.cond1.reduce(store) + self.cond2.reduce(store)

    def get_normalized(self, program):
        self.cond1, failed_atoms1 = self.cond1.get_normalized(program)
        self.cond2, failed_atoms2 = self.cond2.get_normalized(program)
        return self, failed_atoms1 + failed_atoms2

    def subs(self, substitutions):
        self.cond1.subs(substitutions)
        self.cond2.subs(substitutions)

    def evaluate(self, state):
        return self.cond1.evaluate(state) or self.cond1.evaluate(state)

    def to_arithm(self, p):
        not_cond1 = 1 - self.cond1.to_arithm(p)
        not_cond2 = 1 - self.cond2.to_arithm(p)
        return 1 - (not_cond1 * not_cond2)

    def get_free_symbols(self):
        return self.cond1.get_free_symbols() | self.cond2.get_free_symbols()

    def get_conjuncts(self):
        return [self]

    def __str__(self):
        return f"({self.cond1} ∨ {self.cond2})"

    def __eq__(self, obj):
        return isinstance(obj, And) and (self.cond1, self.cond2) == (obj.cond1, obj.cond2)

    def copy(self):
        return Or(self.cond1.copy(), self.cond2.copy())
