from diofant import sympify, Expr
from .type import Type


class Finite(Type):
    expression: Expr
    values: [Expr]

    def __init__(self, expression, parameters):
        if len(parameters) == 0:
            raise RuntimeError("Finite type requires >=1 parameters")
        self.expression = sympify(expression)
        self.values = [sympify(p) for p in parameters]
