from diofant import sympify
from .condition import Condition


class TrueCond(Condition):
    def __str__(self):
        return "true"

    def simplify(self):
        return self

    def subs(self, substitutions):
        pass

    def to_arithm(self, p):
        return sympify(1)
