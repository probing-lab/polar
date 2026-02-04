from sympy import Expr, Set


class Bound:
    def __init__(self, value: Expr, ancestor_rules: Set):
        self.value = value
        self.used_rules:Set[Bound] = ancestor_rules

    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return hash(self.__str__())