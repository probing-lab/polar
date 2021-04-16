from diofant import sympify, Expr
from .type import Type


class Finite(Type):
    values: [Expr]

    def __init__(self, parameters, expression=None):
        if len(parameters) == 0:
            raise RuntimeError("Finite type requires >=1 parameters")
        self.values = [sympify(p) for p in parameters]
        if expression:
            self.expression = sympify(expression)

    def __str__(self):
        return f"{self.expression} : Finite({', '.join([str(v) for v in self.values])})"
