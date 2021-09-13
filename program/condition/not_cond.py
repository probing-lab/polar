from .condition import Condition


class Not(Condition):
    cond: Condition

    def __init__(self, cond):
        self.cond = cond

    def simplify(self):
        self.cond = self.cond.simplify()
        return self

    def reduce(self, store):
        return self.cond.reduce(store)

    def get_normalized(self, program):
        self.cond, failed_atoms = self.cond.get_normalized(program)
        return self, failed_atoms

    def subs(self, substitutions):
        self.cond.subs(substitutions)

    def evaluate(self, state):
        return not self.cond.evaluate(state)

    def to_arithm(self, p):
        return 1 - self.cond.to_arithm(p)

    def get_free_symbols(self):
        return self.cond.get_free_symbols()

    def get_conjuncts(self):
        return [self]

    def is_implied_by_loop_guard(self):
        return self.is_loop_guard

    def __str__(self):
        return f"¬({self.cond})"

    def __eq__(self, obj):
        return isinstance(obj, Not) and self.cond == obj.cond

    def __hash__(self):
        return hash(("NOT", self.cond))

    def __simple_copy__(self):
        return Not(self.cond)
