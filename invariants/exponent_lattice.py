import olll
from fractions import Fraction
from typing import List
from sympy import Expr, numer, denom, AlgebraicNumber, factorint, Rational, Matrix, pi, I, ZZ, ln, re, im, log, ceiling
from sympy.polys.matrices import DomainMatrix
from utils import faccin_bound
import numpy as np

from invariants.exceptions import ExponentLatticeException
from utils import are_coprime, algebraic_number_equals_const
import subprocess
import os
import json
import math

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

        return self.compute_basis_kauers()

    def compute_basis_kauers(self) -> List[List[int]]:
        bases = [AlgebraicNumber(b) for b in self.bases]
        M = faccin_bound(bases)
        es = [ln(b) for b in bases] + [2*pi*I]
        n = len(es)
        w = 1
        upper = M * (n + 2)**(1/2)
        B = np.zeros((n, n + 2), dtype=Fraction)
        B[0:n, 0:n] = np.identity(n, dtype=Fraction)

        while not self._all_in_lattice(B[:, :n-1]):
            w = 2*w
            precision = int(ceiling(log(n*w, 10)))
            real_approximations = [Fraction(str(re(e).round(precision))) for e in es]
            im_approximations = [Fraction(str(im(e).round(precision))) for e in es]
            for row in range(B.shape[0]):
                real_entry = w * sum([e*r for e, r in zip(B[row, :-2], real_approximations)])
                im_entry = w * sum([e*i for e, i in zip(B[row, :-2], im_approximations)])
                B[row, -2] = real_entry
                B[row, -1] = im_entry

            lll_vectors = olll.reduction(B.tolist(), 0.75)
            gs_vectors = olll.gramschmidt(list(map(olll.Vector, B.tolist())))
            r = len(gs_vectors) - 1
            while r > 0 and gs_vectors[r].dot(gs_vectors[r]) ** (1/2) > upper:
                r -= 1
            B = np.asarray(lll_vectors[:r+1], dtype=Fraction)

        return B[:, :len(self.bases)].astype(int).tolist()

    def _all_in_lattice(self, B):
        for row in range(B.shape[0]):
            expr = math.prod([e**c for c, e in zip(B[row, :], self.bases)])
            if re(expr).round(10) != 1 or im(expr).round(10) != 0:
                return False

        for row in range(B.shape[0]):
            expr = math.prod([e ** c for c, e in zip(B[row, :], self.bases)])
            if not algebraic_number_equals_const(expr, 1):
                return False
        return True

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
        return kernel_basis

    @classmethod
    def bases_are_equivalent(cls, basis1: List[List[int]], basis2: List[List[int]]) -> bool:
        """
        Returns true iff two given bases span the same integer lattice
        See: https://math.stackexchange.com/a/4467760
        """
        basis1 = Matrix(basis1).T
        basis2 = Matrix(basis2).T
        u = basis1.pinv() * basis2
        if basis1*u != basis2:
            return False
        u_det = u.det()
        if u_det != 1 and u_det != -1:
            return False
        u_is_integer = all([c.is_integer for row in u.tolist() for c in row])
        return u_is_integer
