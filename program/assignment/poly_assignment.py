from diofant import Expr, sympify
from .assignment import Assignment
from program.condition import TrueCond


class PolyAssignment(Assignment):
    poly: Expr

    def __init__(self, variable, poly):
        super().__init__(variable)
        self.poly = sympify(poly)

    def __str__(self):
        result = str(self.variable) + " = " + str(self.poly)
        if not isinstance(self.condition, TrueCond):
            result += "  |  " + str(self.condition) + "  :  " + str(self.default)
        return result

    def subs(self, substitutions):
        self.default = self.default.subs(substitutions)
        self.condition.subs(substitutions)
        self.poly = self.poly.subs(substitutions)

    def get_assign_type(self):
        return None
