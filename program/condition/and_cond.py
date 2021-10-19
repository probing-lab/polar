from .condition import Condition
from .true_cond import TrueCond


class And(Condition):
    cond1: Condition
    cond2: Condition

    def __init__(self, cond1, cond2):
        self.cond1 = cond1
        self.cond2 = cond2

    def simplify(self):
        self.cond1 = self.cond1.simplify()
        self.cond2 = self.cond2.simplify()
        if isinstance(self.cond1, TrueCond):
            return self.cond2
        if isinstance(self.cond2, TrueCond):
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
        return self.cond1.evaluate(state) and self.cond2.evaluate(state)

    def get_conjuncts(self):
        return self.cond1.get_conjuncts() + self.cond2.get_conjuncts()

    def to_arithm(self, p):
        return self.cond1.to_arithm(p) * self.cond2.to_arithm(p)

    def get_free_symbols(self):
        return self.cond1.get_free_symbols() | self.cond2.get_free_symbols()

    def is_implied_by_loop_guard(self):
        if self.is_loop_guard:
            return True
        return self.cond1.is_implied_by_loop_guard() and self.cond1.is_implied_by_loop_guard()

    def get_loop_guard(self):
        if self.is_loop_guard:
            return self.copy()
        cond1_guard = self.cond1.get_loop_guard()
        return cond1_guard if cond1_guard is not None else self.cond2.get_loop_guard()

    def __str__(self):
        return f"({self.cond1} ∧ {self.cond2})"

    def __eq__(self, obj):
        return isinstance(obj, And) and (self.cond1, self.cond2) == (obj.cond1, obj.cond2)

    def __hash__(self):
        return hash(("AND", self.cond1, self.cond2))

    def __simple_copy__(self):
        return And(self.cond1.copy(), self.cond2.copy())
