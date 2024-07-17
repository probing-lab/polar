from sympy import Matrix, Expr, sympify
from enum import Enum, auto


class ActuatorFaultStrategy(Enum):
    ZERO = auto()
    HOLD = auto()


class Actuator:
    effect: Matrix
    symbol: str
    variables: [str]
    fault_probability: Expr
    fault_strategy: ActuatorFaultStrategy

    def __init__(self, symbol: str = "u"):
        self.symbol = symbol

    def set_effect(self, e: Matrix):
        self.effect = e
        self.variables = [self.symbol + str(i) for i in range(e.cols)]

    def set_fault_probability(self, p: Expr | float):
        self.fault_probability = sympify(p)

    def set_fault_strategy(self, fs: ActuatorFaultStrategy):
        self.fault_strategy = fs
