from diofant import sympify

from program.condition import Condition


class Atom(Condition):

    def __init__(self, poly1, cop, poly2):
        self.poly1 = sympify(poly1)
        self.cop = cop
        self.poly2 = sympify(poly2)

    def simplify(self):
        return self

    def subs(self, substitutions):
        self.poly1 = self.poly1.subs(substitutions)
        self.poly2 = self.poly2.subs(substitutions)

    def __str__(self):
        return f"{self.poly1} {self.cop} {self.poly2}"
