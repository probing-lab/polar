from typing import List
from sympy import Expr, numer, denom, AlgebraicNumber, factorint, Rational, Matrix, ZZ
from sympy.polys.matrices import DomainMatrix
from utils import faccin_bound
import numpy as np

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

        if all([b.is_rational for b in self.bases]):
            return self.compute_basis_rational()

        alg_bases = [AlgebraicNumber(b) for b in self.bases]
        print(faccin_bound(alg_bases))

    def compute_basis_rational(self) -> List[List[int]]:
        factors_to_multiplicities = {}

        def add_factors_with_mults(fm, i):
            for f, m in fm.items():
                if f not in factors_to_multiplicities:
                    factors_to_multiplicities[f] = [0 for _ in self.bases]
                factors_to_multiplicities[f][i] = m

        for i, b in enumerate(self.bases):
            b = Rational(b)
            numer_factors = factorint(numer(b))
            denom_factors = {p: -m for p, m in factorint(denom(b)).items()}
            add_factors_with_mults(numer_factors, i)
            add_factors_with_mults(denom_factors, i)

        entries = [mults for k, mults in factors_to_multiplicities.items() if k != -1]
        matrix = Matrix(entries)
        if -1 in factors_to_multiplicities:
            matrix = matrix.row_insert(matrix.shape[0], Matrix([factors_to_multiplicities[-1]]))
            matrix = matrix.col_insert(matrix.shape[1], Matrix([0] * matrix.shape[0]))
            matrix[-1, -1] = 2

        matrix = DomainMatrix.from_Matrix(matrix)
        matrix.convert_to(ZZ)
        kernel_basis = matrix.nullspace().to_Matrix()
        if -1 in factors_to_multiplicities:
            kernel_basis.col_del(-1)

        kernel_basis = np.asarray(kernel_basis).astype(int).tolist()
        print(kernel_basis)
        return kernel_basis
