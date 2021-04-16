from diofant import sympify, Expr
from .condition import Condition
from program import Program


class FalseCond(Condition):
    def __str__(self):
        return "false"

    def simplify(self):
        return self

    def subs(self, substitutions):
        pass

    def to_arithm(self, p: Program) -> Expr:
        return sympify(0)
