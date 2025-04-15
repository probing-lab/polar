"""
This module contains functions deciding whether or not a given expression is an invariant of the program,
More precisely, it decides whether expression <= 0 is eventually invariant.
The methods are of course not complete in general.
"""

from typing import Dict, List
from sympy import Expr, Poly, Symbol, Tuple

from program.assignment.dist_assignment import DistAssignment
from termination.util.constants import ITER_VAR
from termination.util.poly_utils import get_sign
from . import bound_store


def is_invariant(
    expression: Expr,
    branches: Dict[Symbol, List[Tuple[Expr, Expr]]],
    dist_assignments: Dict[Symbol, DistAssignment],
    closed_forms: Dict[Symbol, Expr],
) -> bool:
    """
    Main function deciding whether expression <= 0 is eventually invariant
    """
    is_deterministic = len(expression.free_symbols.difference({n})) == 0
    if is_deterministic:
        return is_deterministic_invariant(expression, closed_forms)
    else:
        return is_probabilistic_invariant(expression, branches, dist_assignments)


def is_deterministic_invariant(
    expression: Expr, closed_forms: Dict[Symbol, Expr]
) -> bool:
    """
    Checks whether an expression only containing n eventually stays <= 0
    """
    expr = expression.subs(closed_forms)
    poly = Poly(expr, ITER_VAR)
    if poly.is_extended_positive == False:
        return True
    # TODO: Limitation: sign only knows to decide poly < 0 (excl. 0)
    sign = get_sign(poly)
    return sign


def is_probabilistic_invariant(
    expression: Expr,
    branches: Dict[Symbol, List[Tuple[Expr, Expr]]],
    dist_assignments: Dict[Symbol, DistAssignment],
) -> bool:
    """
    Tries several strategies to determine if a given expression eventually stays <= 0
    """
    answer = __is_probabilistic_invariant_via_bounds(expression)
    if answer.is_known():
        return answer.is_true()
    raise NotImplemented()


def __is_probabilistic_invariant_via_bounds(expression: Expr) -> Answer:
    """
    Tries to decide if expression <= 0 eventually becomes invariant via bounds.
    """
    n = symbols("n", integer=True, positive=True)
    bounds = bound_store.get_bounds_of_expr(expression)
    if is_dominating_or_same(bounds.upper, sympify(-1), n, direction=Direction.NegInf):
        return Answer.TRUE

    if is_dominating_or_same(bounds.lower, sympify(1), n, direction=Direction.PosInf):
        return Answer.FALSE

    return Answer.UNKNOWN
