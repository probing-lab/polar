from .condition import Condition


class Not(Condition):
    cond: Condition

    def __init__(self, cond):
        self.cond = cond

    def simplify(self):
        self.cond = self.cond.simplify()
        return self

    def subs(self, substitutions):
        self.cond.subs(substitutions)

    def __str__(self):
        return f"¬({self.cond})"
