from diofant import sympify, Expr
from .condition import Condition
from program import Program


class TrueCond(Condition):
    def __str__(self):
        return "true"

    def simplify(self):
        return self

    def subs(self, substitutions):
        pass

    def to_arithm(self, p: Program) -> Expr:
        return sympify(1)
