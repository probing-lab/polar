from diofant import sympify, Symbol, Expr
from .type import Type


class Finite(Type):
    variable: Symbol
    lower: Expr
    upper: Expr

    def __init__(self, variable, lower, upper):
        self.variable = sympify(variable)
        self.lower = sympify(lower)
        self.upper = sympify(upper)
