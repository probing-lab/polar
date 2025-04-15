from typing import List
from sympy import Expr, Poly, Symbol, degree, solve


def has_real_zero(poly: Poly, symbol: Symbol):
    if degree(poly, gen=symbol) > 4:
        # Solve can only analyze quartics (higher degrees only for special cases)
        return None

    zeros = solve(poly, symbol)
    for zero in zeros:
        if zero.is_extended_real is True:
            return True
        if zero.is_extended_real is None:
            return None
    return False


def has_real_zero_for_any(poly: Poly):
    # exhaustively try for every symbol in poly.
    # This for sure is not optimal, but i am unaware if, there is an "optimal" way to determine
    # wheather a poly has zeros. e.g. by trying the highest/lowest degree poly.
    for sym in poly.free_symbols:
        res = has_real_zero(poly, sym)
        if res is True or res is False:
            return res
    return None


def get_sign(poly: Poly):
    # return True, when poly is always positive,
    # False, when poly is always negative and
    # None, if it can be both positive and negative, or it can not be determined
    if poly.is_extended_negative:
        return False
    if poly.is_extended_positive:
        return True
    if not has_real_zero_for_any(poly) is False:
        return None

    # leading_coeff has no zeros - now determine if it is positive
    symbols = poly.free_symbols
    substitutions = {sym: 0 for sym in symbols}
    zero_value = poly.subs(substitutions)

    assert zero_value != 0, "p(0) can not be 0, if p was found to have no zeros."

    if zero_value < 0:
        return False
    return True


def _get_possible_signs(expr: Expr):
    "returns a tuple (a,b), where a==True, (b==True) iff poly can be positive (negative)"
    return (expr.is_positive != False, expr.is_negative != False)


def get_possible_signs(*args: List[Expr]):
    maybe_pos = False
    maybe_neg = False
    for expr in args:
        p, n = _get_possible_signs(expr)
        maybe_pos = p or maybe_pos
        maybe_neg = n or maybe_neg
    return maybe_pos, maybe_neg
