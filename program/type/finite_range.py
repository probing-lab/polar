from diofant import sympify, Expr
from .type import Type


class FiniteRange(Type):
    expression: Expr
    lower: Expr
    upper: Expr

    def __init__(self, expression, parameters):
        if len(parameters) != 2:
            raise RuntimeError("FiniteRange type requires 2 parameters")
        self.expression = sympify(expression)
        self.lower = sympify(parameters[0])
        self.upper = sympify(parameters[1])
