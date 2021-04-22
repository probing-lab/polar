from symengine.lib.symengine_wrapper import sympy2symengine, Expr, Symbol, One, Zero
from sympy import Rational


def float_to_rational(expr: Expr):
    return sympy2symengine(Rational(str(expr)))


def get_terms_with_var(poly: Expr, var: Symbol):
    """
    For a polynomial (flattened expression) and a given variable var returns a list of all
    monomials in the form (power of var, part of monomial without var) as well as the remaining polynomial
    not containing var.
    E.g: For poly=x**2*y*z - 2x + y + 2 returns
    [(2,y*z), (1,-2)], y+2
    """
    result = []
    rest = Zero()
    terms = poly.args if poly.is_Add else [poly]
    for term in terms:
        if var not in term.free_symbols:
            rest += term
            continue

        part_without_var = One()
        power = Zero()
        parts = term.args if term.is_Mul else [term]
        for part in parts:
            if var not in part.free_symbols:
                part_without_var *= part
                continue
            power = part.args[1] if part.is_Pow else One()

        result.append((power, part_without_var))
    return result, rest


def get_monoms(poly: Expr, constant_symbols=None, with_constant=False):
    """
    For a given polynomial returns a list of its monomials with separated coefficients - (coeff, monom).
    The polynomial is assumed to be in all symbols it contains minus constant_symbols.
    The monomial 1 is only included if with_constant is true.
    """
    if constant_symbols is None:
        constant_symbols = set()

    monoms = []
    constant = Zero()
    terms = poly.args if poly.is_Add else [poly]
    for term in terms:
        if not term.free_symbols.difference(constant_symbols):
            constant += term
            continue

        coeff = One()
        monom = One()
        parts = term.args if term.is_Mul else [term]
        for part in parts:
            if part.free_symbols.difference(constant_symbols):
                monom *= part
            else:
                coeff *= part
        monoms.append((coeff, monom))

    if with_constant and constant != 0:
        monoms.append((constant, One()))
    return monoms
