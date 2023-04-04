from typing import List
from sympy import Expr, numer, denom

from invariants.exceptions import ExponentLatticeException
from utils import are_coprime
import subprocess
import os
import json

ExponentBase = Expr


class ExponentLattice:

    bases: List[ExponentBase]

    def __init__(self, bases: List[ExponentBase]):
        self.bases = bases

    def compute_basis(self) -> List[List[int]]:
        if len(self.bases) <= 1:
            return []
        all_rational = all([b.is_Rational for b in self.bases])
        if all_rational:
            integers = [numer(b) for b in self.bases if numer(b) != 1]
            integers += [denom(b) for b in self.bases if denom(b) != 1]
            if are_coprime(integers):
                return []

        dir_path = os.path.dirname(os.path.realpath(__file__))
        command = ["sage", dir_path + "/integer-relations.py"] + [str(b) for b in self.bases]
        try:
            result = subprocess.run(command, capture_output=True)
            if result.returncode != 0:
                raise ExponentLatticeException("Something went wrong while computing the basis of the exponent lattice")
            return json.loads(result.stdout)
        except FileNotFoundError:
            raise ExponentLatticeException("To compute the exponent lattice for invariants please install sagemath and make the 'sage' command visible on your system.")
