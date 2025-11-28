from sympy import Expr, Set


class Bound:
    def __init__(self, value: Expr, ancestor_rules: Set):
        self.value = value
        self.used_rules:Set[Bound] = ancestor_rules
