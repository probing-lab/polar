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

    def __str__(self):
        return f"({self.cond1} ∨ {self.cond2})"
