from symengine.lib.symengine_wrapper import sympify, Expr
from .condition import Condition


class FalseCond(Condition):
    def __str__(self):
        return "false"

    def simplify(self):
        return self

    def subs(self, substitutions):
        pass

    def to_arithm(self, _) -> Expr:
        return sympify(0)
