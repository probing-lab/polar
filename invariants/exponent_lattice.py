from typing import List
from sympy import Expr, numer, denom, AlgebraicNumber
from utils import faccin_bound

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

    def is_trivially_empty(self):
        if len(self.bases) == 0:
            return True
        all_rational = all([b.is_Rational for b in self.bases])
        if all_rational:
            numerators = [numer(b) for b in self.bases if numer(b) != 1]
            denominators = [denom(b) for b in self.bases if denom(b) != 1]
            if all([abs(n) > 1 for n in numerators]) and are_coprime(numerators + denominators):
                return True
        return False

    def compute_basis_sage(self) -> List[List[int]]:
        if self.is_trivially_empty():
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

    def compute_basis(self) -> List[List[int]]:
        if self.is_trivially_empty():
            return []

        alg_bases = [AlgebraicNumber(b) for b in self.bases]
        print(faccin_bound(alg_bases))
