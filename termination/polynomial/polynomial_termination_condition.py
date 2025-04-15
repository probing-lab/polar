from typing import List, Tuple, cast
import numpy as np
from sympy import Poly, PolynomialError, Symbol, limit, real_roots, simplify, solve
from program.condition.and_cond import And
from program.condition.atom_cond import Atom
from program.condition.condition import Condition
from program.condition.false_cond import FalseCond
from program.condition.true_cond import TrueCond
from termination.polynomial.asymptotic_constant_term_nontermination_witness import (
    AsymptoticConstantTermNonTerminationWitness,
)
from termination.polynomial.asymptotic_termination_witness import (
    AsymptoticTerminationWitness,
)
from termination.polynomial.exact_termination_witness import ExactWitness
from termination.polynomial.termination_witness import TerminationWitness
from termination.util.poly_utils import get_sign, has_real_zero, has_real_zero_for_any
from utils.expressions import unpack_piecewise
import numpy.polynomial.polynomial as np_poly


class PolynomialTerminationCondition:
    def __init__(
        self, poly: Poly, terminates_zero: bool, terminates_negative: bool
    ) -> None:
        self.poly = poly
        self.terminates_zero = terminates_zero
        self.terminates_negative = terminates_negative

    def get_witness(self) -> TerminationWitness:
        n = Symbol("n")
        # n = next((sym for sym in self.poly.free_symbols if str(sym) == 'n'), n)
        # print(self.poly.free_symbols)
        # print(n)
        # print(self.poly)
        poly = Poly(self.poly, n)

        if len(poly.free_symbols) == 1:
            return self._get_exact_witness(
                poly, self.terminates_zero, self.terminates_negative
            )

        return self._get_asymptotic_witness(
            poly, self.terminates_zero, self.terminates_negative
        )

    def _get_asymptotic_witness(
        self, poly: Poly, terminates_on_zero: bool, terminates_negative: bool
    ):
        # We basically analyze the sign of the leading coefficient
        leading_coeff = poly.coeffs()[0]
        print(f"Polynomial: {poly}")
        print(f"Leading coefficient: {leading_coeff}")

        if not terminates_negative:
            # exact termination conditions can not be checked asymptotically
            return None

        if get_sign(leading_coeff) is None:
            return None

        if get_sign(leading_coeff) is False:
            return AsymptoticTerminationWitness(poly)

        # The polynomial is eventually nonterminating.
        # Eventual nontermination implies actual nontermination, when the constant term of the polynomial
        # can grow without affecting the other coefficients
        # (TODO: This can maybe be strengthened, as eventual termination implies actual termination, when there is no
        # loop prolog, i.e. no symbol is "restricted" to a certain value: https://epubs.siam.org/doi/epdf/10.1137/1.9781611973730.65)
        # I think coming up with a method for "nonterminatin2.prob" should be possible

        poly_coeffs = poly.all_coeffs()
        constant_term = poly_coeffs[-1]
        print(f"Constant term: {constant_term}")
        for symbol in constant_term.free_symbols:
            try:
                p = constant_term.as_poly(symbol)
                # check if symbol is a part of the other coefficients
                for coefficient in poly_coeffs[0:-1]:
                    if symbol not in coefficient.free_symbols:
                        return AsymptoticConstantTermNonTerminationWitness(poly, symbol)

            except PolynomialError:
                # For example a/(b+1) can not be converted to a poly in b, but to a poly in a.
                # Such terms are not supported
                pass
        return None

    def _get_exact_witness(
        self, poly: Poly, terminates_on_zero: bool, terminates_negative: bool
    ):
        # extract coefficients
        coeffs = [float(coeff) for coeff in poly.all_coeffs()]
        zeros = cast(np.ndarray, np_poly.polyroots(list(reversed(coeffs))))
        print(f"Found zeros: {zeros}")

        ns_to_check = (
            [0] + [int(zero) for zero in zeros] + [int(zero) + 1 for zero in zeros]
        )
        ns_to_check.sort()

        first_n = None
        for n in ns_to_check:
            if n < 0:
                continue
            value = poly.eval(n)
            if value < 0 and terminates_negative:
                first_n = n
                break
            if value == 0 and terminates_on_zero:
                first_n = n
                break
        return ExactWitness(
            poly, zeros, first_n, terminates_on_zero, terminates_negative
        )
