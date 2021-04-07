from diofant import Symbol, Expr
from .assignment import Assignment
from ..distribution import sympify


class PolyAssignment(Assignment):
    variable: Symbol
    poly: Expr

    def __init__(self, var, poly):
        self.variable = sympify(var)
        self.poly = sympify(poly)
