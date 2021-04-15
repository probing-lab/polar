from diofant import Expr, sympify
from .assignment import Assignment


class PolyAssignment(Assignment):
    poly: Expr

    def __init__(self, variable, poly):
        super().__init__(variable)
        self.poly = sympify(poly)

    def __str__(self):
        return str(self.variable) + " = " + str(self.poly) + "  |  " + str(self.condition) + "  :  " + str(self.default)

    def subs(self, substitutions):
        self.default = self.default.subs(substitutions)
        self.condition.subs(substitutions)
        self.poly = self.poly.subs(substitutions)
