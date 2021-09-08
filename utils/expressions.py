from typing import List

from symengine.lib.symengine_wrapper import sympy2symengine, Expr, Symbol, One, Zero
from sympy import Rational, linsolve, Poly, sympify, re


def float_to_rational(expr: Expr):
    return sympy2symengine(Rational(str(expr)))


def get_all_roots(poly: Poly, numeric=False, numeric_croots=False, eps=1e-10):
    exact = True

    if numeric:
        roots = poly.intervals(eps=eps)
        result = []
        for (h, l), m in roots:
            result.append(((h + l) / 2, m))
            if h != l:
                exact = False
        return result, exact

    roots = poly.all_roots(multiple=False)
    result = []
    for r, m in roots:
        if numeric_croots:
            r, exact = numerify_croots(r)
        result.append((r, m))
    return result, exact


def solve_linear(equations, unknowns):
    sol = linsolve(equations, unknowns)
    return sol.args[0]


def without_piecewise(expr):
    """
    Removes the Piecewise from an expression by assuming that all restricting assumptions are false.
    """
    if not expr.args:
        return expr

    if expr.is_Piecewise:
        return without_piecewise(expr.args[-1].expr)

    return expr.func(*[without_piecewise(a) for a in expr.args])


def get_terms_with_var(poly: Expr, var: Symbol):
    """
    For a polynomial (flattened expression) and a given variable var returns a list of all
    monomials in the form (power of var, part of monomial without var) as well as the remaining polynomial
    not containing var.
    E.g: For poly=x**2*y*z - 2x + y + 2 returns
    [(2,y*z), (1,-2)], y+2

    This function is a specialization of get_terms_with_var and implemented as duplication for performance reasons.
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


def get_terms_with_vars(poly: Expr, variables: List[Symbol]):
    """
    For a polynomial (flattened expression) and a given list of variable vars returns a list of all
    monomials in the form (power of vars, part of monomial without vars) as well as the remaining polynomial
    not containing var.
    E.g: For poly=x**2*y*z*a - 2x*a + y + 2  and variables [x,a] returns
    [([2,1],y*z), ([1,1],-2)], y + 2
    """
    result = []
    rest = Zero()
    terms = poly.args if poly.is_Add else [poly]
    vars_set = set(variables)
    vars_to_index = {var: i for i, var in enumerate(variables)}
    for term in terms:
        if not vars_set.intersection(term.free_symbols):
            rest += term
            continue

        part_without_vars = One()
        powers = [Zero()] * len(variables)
        parts = term.args if term.is_Mul else [term]
        for part in parts:
            if len(part.free_symbols) == 0:
                part_without_vars *= part
                continue
            part_var = next(iter(part.free_symbols))
            if part_var not in vars_set:
                part_without_vars *= part
                continue
            powers[vars_to_index[part_var]] = part.args[1] if part.is_Pow else One()

        result.append((powers, part_without_vars))
    return result, rest


def get_monoms(poly: Expr, constant_symbols=None, with_constant=False, zero=Zero(), one=One()):
    """
    For a given polynomial returns a list of its monomials with separated coefficients - (coeff, monom).
    The polynomial is assumed to be in all symbols it contains minus constant_symbols.
    The monomial 1 is only included if with_constant is true.
    """
    if constant_symbols is None:
        constant_symbols = set()

    monoms = []
    constant = zero
    terms = poly.args if poly.is_Add else [poly]
    for term in terms:
        if not term.free_symbols.difference(constant_symbols):
            constant += term
            continue

        coeff = one
        monom = one
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


def eval_re(subs, expression):
    result = expression.xreplace({sympify(k): v for k, v in subs.items()})
    return float(re(result.expand()))


def numerify_croots(expression):
    """
    Replaces every croot in an expression by a floating-point representation
    Returns the new expression and a boolean which is true iff no croots where found
    """
    return expression, False
