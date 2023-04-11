import olll
from fractions import Fraction
from typing import List
from sympy import Expr, numer, denom, AlgebraicNumber, factorint, Rational, Matrix, pi, I, ZZ, ln, re, im, log, ceiling
from sympy.polys.matrices import DomainMatrix
from utils import faccin_bound
import numpy as np

from utils import are_coprime, algebraic_number_equals_const
import math

ExponentBase = Expr


class ExponentLattice:
    """
    For some given bases of algebraic numbers b1,...,bn this class represent the lattice given by the solutions
    b1^x1 * ... * bn^xn = 1 where all xi are integers. The set of these solutions has a lattice structure.
    Moreover, this lattice has a (non-unique) basis.
    This class provides the functionality to compute a basis for this lattice.
    """

    bases: List[ExponentBase]

    def __init__(self, bases: List[ExponentBase]):
        self.bases = bases

    def is_trivially_empty(self):
        """
        Returns true iff all exponent-bases are rational and all numerators and denominators are coprime.
        If this holds, the lattice is trivial (only consists of the 0 solution)
        """
        if len(self.bases) == 0:
            return True
        all_rational = all([b.is_Rational for b in self.bases])
        if all_rational:
            numerators = [numer(b) for b in self.bases if numer(b) != 1]
            denominators = [denom(b) for b in self.bases if denom(b) != 1]
            if all([abs(n) > 1 for n in numerators]) and are_coprime(numerators + denominators):
                return True
        return False

    def compute_basis(self) -> List[List[int]]:
        """
        Returns a basis for the exponent lattice
        """
        if self.is_trivially_empty():
            return []

        if all([b.is_rational for b in self.bases]):
            return self.compute_basis_rational()

        return self.compute_basis_kauers()

    def compute_basis_kauers(self) -> List[List[int]]:
        """
        This function implements the algorithm for compute a basis for an exponent-lattice as described in
        https://arxiv.org/abs/2302.04070
        The algorithm treats the equation b1^x1 * ... * bn^xn = 1 as the equivalent equation
        ln(b1)*x1 + ... + ln(bn)xn + x*2*pi*I = 0 and uses the LLL algorithm and a known upper bound for |xi|.
        """
        bases = [AlgebraicNumber(b) for b in self.bases]
        M = faccin_bound(bases)
        es = [ln(b) for b in bases] + [2*pi*I]
        n = len(es)
        w = 1
        upper = M * (n + 2)**(1/2)
        B = np.zeros((n, n + 2), dtype=Fraction)
        B[0:n, 0:n] = np.identity(n, dtype=Fraction)

        while not self._all_in_lattice(B[:, :n-1]):
            # Computer ever more precise approximations of the es.
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
            while r >= 0 and gs_vectors[r].dot(gs_vectors[r]) ** (1/2) > upper:
                r -= 1
            if r < 0:
                return []
            B = np.asarray(lll_vectors[:r+1], dtype=Fraction)

        return B[:, :len(self.bases)].astype(int).tolist()

    def _all_in_lattice(self, B):
        """
        Returns true iff the rows of B are a subset of the lattice.
        """
        # First do a fast numeric check. We cannot conclusively say whether B is a subset of the lattice,
        # but we can very quickly get an answer if B is clearly not a subset of the lattice.
        for row in range(B.shape[0]):
            expr = math.prod([e**c for c, e in zip(B[row, :], self.bases)])
            if re(expr).round(10) != 1 or im(expr).round(10) != 0:
                return False

        # If the numeric check could not rule out that B is not a subset of the lattice, we perform an exact check.
        for row in range(B.shape[0]):
            expr = math.prod([e ** c for c, e in zip(B[row, :], self.bases)])
            if not algebraic_number_equals_const(expr, 1):
                return False
        return True

    def compute_basis_rational(self) -> List[List[int]]:
        """
        Computes a basis of the exponent lattice given that all exponent-bases are rational.
        The method works by factoring all numerators and denominators into their prime factors.
        For every prime factor p, all multiplicities of the numerator minus all multiplicities of the denominators
        need to some up to 0. Moreover, the multiplicities of the factor (-1) needs to sum up to an even integer.
        This leads to a system of linear diophantine equations.
        """
        # maps factors (primes and -1) to multiplicities
        # The multiplicities are represented by a list with one entry for every base.
        # If the factor occurs in the denominator the multiplicity is negative
        factors_to_multiplicities = {}

        def add_factors_with_mults(fm, i):
            # Adds the factors of the exponent-base bi to the map
            for f, m in fm.items():
                if f not in factors_to_multiplicities:
                    factors_to_multiplicities[f] = [0 for _ in self.bases]
                factors_to_multiplicities[f][i] = m

        # First, for every exponent-base add all factors with multiplicites to the map
        for i, b in enumerate(self.bases):
            b = Rational(b)
            numer_factors = factorint(numer(b))
            denom_factors = {p: -m for p, m in factorint(denom(b)).items()}
            add_factors_with_mults(numer_factors, i)
            add_factors_with_mults(denom_factors, i)

        # Next, we set up the system of linear diophantine equations, modelling that the multiplicites of all
        # prime factors must sum up to 0.
        entries = [mults for k, mults in factors_to_multiplicities.items() if k != -1]
        matrix = Matrix(entries)
        # If one or more bases have -1 as a factor, we need to add the extra constraint, that the number of -1 factors
        # must add up to an even integer.
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
