from sympy import Expr, Set


class Bound:
    def __init__(self, value: Expr):
        self.value = value
        self.descendants:Set[Bound] = set()
        self.ancestors:Set[Bound] = set()

    def propagate_descendents(self, new_descendents):
        old_l = len(self.descendants)
        self.descendants.update(new_descendents)
        if old_l!=len(self.descendants):
            for anc in self.ancestors:
                anc.propagate_descendents(new_descendents)