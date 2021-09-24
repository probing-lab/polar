from sympy import hermite_poly, Symbol, sqrt, bell
from symengine.lib.symengine_wrapper import Zero, sqrt, sympify


def prob_hermite_poly(n, x):
    """
    Returns the n-th probabilistic Hermite polynomial
    """
    tmp = Symbol("x")
    h = sympify(hermite_poly(n, tmp))
    h = h.xreplace({Symbol("x"): x / sqrt(2)})
    h = (sqrt(2) ** (-n)) * h
    return h.expand()


def ce_bell_poly(n, *variables):
    """
    Returns the n-th complete exponential bell polynomial
    """
    result = Zero()
    for k in range(1, n+1):
        b_n_k = bell(n, k, variables)
        result += sympify(b_n_k)
    return result.expand()
