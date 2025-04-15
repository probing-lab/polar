from functools import cache, lru_cache
from typing import List, Tuple
from sympy import Expr, Monomial, Symbol, limit, oo, simplify
from termination.util.constants import ITER_VAR


def amber_limit(expr):
    if expr.free_symbols and ITER_VAR in expr.free_symbols:
        return limit(expr.as_expr(), ITER_VAR, oo)
    return expr


count = 0


def unique_positive_symbol():
    global count
    count += 1
    return Symbol(f"__a__{count}", positive=True, real=True, is_finite=True)


def inhom(branches: List[Tuple[Expr, Expr]], monomial: Monomial):
    inhom_parts = []
    for prob, expr in branches:
        inhom_parts.append(_get_inhom_part(expr, monomial))
    return inhom_parts


def recurrence_constant(branches: List[Tuple[Expr, Expr]], monomial: Monomial):
    coeffs = []
    for prob, expr in branches:
        coeffs.append(_get_integer_coefficient(expr, monomial))
    return coeffs


@cache
def _get_inhom_part(expr: Expr, monomial: Monomial):
    return simplify(expr - monomial * _get_integer_coefficient(expr, monomial))


@cache
def _get_integer_coefficient(expr: Expr, monomial: Monomial):
    return expr.coeff(monomial)
