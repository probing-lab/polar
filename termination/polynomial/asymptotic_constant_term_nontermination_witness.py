from sympy import Poly, Symbol
from program.condition.condition import Condition
from termination.polynomial.termination_witness import TerminationWitness


class AsymptoticConstantTermNonTerminationWitness(TerminationWitness):
    def __init__(self, polynomial: Poly, symbol: Symbol) -> None:
        self.polynomial = polynomial
        self.symbol = symbol

    def is_termination_witness(self):
        return False

    def __str__(self) -> str:
        return f"""The polynomial {self.polynomial} is eventually nonterminating,
        and the constant term can grow to infinity, because of the symbol {self.symbol},
        without affecting the other coefficients"""
