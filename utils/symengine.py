from symengine.lib.symengine_wrapper import sympy2symengine, Expr, Symbol, One, Zero
from sympy import Rational


def fraction(expr: Expr):
    if not expr.is_Pow:
        raise RuntimeError()
    num, denom = expr.args[1] * (-1), expr.args[0]
    if not (bool(num.is_real) and bool(num.is_positive)):
        raise RuntimeError()
    return num, denom


def float_to_rational(expr: Expr):
    return sympy2symengine(Rational(str(expr)))


def get_terms_with_var(poly: Expr, var: Symbol):
    result = []
    rest = Zero()
    for term in poly.args:
        if var not in term.free_symbols:
            rest += term
            continue

        part_without_var = One()
        power = Zero()
        for part in term.args:
            if var not in part.free_symbols:
                part_without_var *= part
                continue
            power = part.args[1] if part.is_Pow else One()

        result.append((power, part_without_var))
    return result, rest
