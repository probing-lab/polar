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

    def reduce(self):
        return self.cond1.reduce() + self.cond2.reduce()

    def get_normalized(self, program):
        self.cond1 = self.cond1.get_normalized(program)
        self.cond2 = self.cond2.get_normalized(program)
        return self

    def subs(self, substitutions):
        self.cond1.subs(substitutions)
        self.cond2.subs(substitutions)

    def to_arithm(self, p):
        return self.cond1.to_arithm(p) * self.cond2.to_arithm(p)

    def get_free_symbols(self):
        return self.cond1.get_free_symbols() | self.cond2.get_free_symbols()

    def __str__(self):
        return f"({self.cond1} ∧ {self.cond2})"
