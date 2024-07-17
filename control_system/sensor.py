from sympy import Matrix, Expr, sympify


class Sensor:
    measurement: Matrix
    symbol: str
    variables: [str]
    fault_probability: Expr

    def __init__(self, symbol: str = "y"):
        self.symbol = symbol

    def set_measurement(self, m: Matrix):
        self.measurement = m
        self.variables = [self.symbol + str(i) for i in range(m.rows)]

    def set_fault_probability(self, p: Expr | float):
        self.fault_probability = sympify(p)
