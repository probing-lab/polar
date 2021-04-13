from diofant import Symbol, Expr
from .assignment import Assignment
from ..distribution import sympify


class PolyAssignment(Assignment):
    variable: Symbol
    poly: Expr

    def __init__(self, var, poly):
        super().__init__()
        self.variable = sympify(var)
        self.poly = sympify(poly)

    def __str__(self):
        return str(self.variable) + " = " + str(self.poly) + "  |  " + str(self.condition)

    def subs(self, substitutions):
        self.condition.subs(substitutions)
        self.poly = self.poly.subs(substitutions)
