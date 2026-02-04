from sympy import Expr, Set


class Bound:
    def __init__(self, value: Expr, ancestor_rules: Set, hash_salt = None):
        self.value = value
        self.used_rules:Set[Bound] = ancestor_rules
        self.hash_salt = hash_salt

    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return hash((self.hash_salt, self.__str__()))