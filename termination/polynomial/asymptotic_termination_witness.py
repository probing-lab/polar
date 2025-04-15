from sympy import Poly
from program.condition.condition import Condition
from termination.polynomial.termination_witness import TerminationWitness


class AsymptoticTerminationWitness(TerminationWitness):
    def __init__(self, polynomial: Poly) -> None:
        self.polynomial = polynomial

    def is_termination_witness(self):
        return True

    def __str__(self) -> str:
        return f"""The polynomial {self.polynomial} eventually (asymptotically) becomes negative, 
        as the coefficient of the n with the highest is negative in it's closed form"""
