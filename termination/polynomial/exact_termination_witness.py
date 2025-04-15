from typing import List, Optional
from sympy import Poly
from sympy.core.relational import Relational
from program.condition.condition import Condition
from termination.polynomial.termination_witness import TerminationWitness


class ExactWitness(TerminationWitness):
    def __init__(
        self,
        poly: Poly,
        zeros: List[float],
        first_false_integer: Optional[int],
        terminates_zero: bool,
        terminates_negative,
    ) -> None:
        self.zeros = zeros
        self.first_false_integer = first_false_integer
        self.terminates_zero = terminates_zero
        self.terminates_negative = terminates_negative
        self.poly = poly

    def is_termination_witness(self):
        return self.first_false_integer is not None

    def __str__(self) -> str:
        reason = (
            ("zero" if self.terminates_zero else "")
            + (" or " if self.terminates_zero and self.terminates_negative else "")
            + ("negative" if self.terminates_negative else "")
        )
        if self.is_termination_witness():
            return f"The polynomial was found to be {reason} at {self.first_false_integer}.\nIt's zeros are: {self.zeros}"
        else:
            return f"The polynomial {self.poly} never becomes {reason}."
