from typing import Dict
from sympy import Expr, sympify
from math import factorial


def raw_moments_to_cumulants(moments: Dict[int, Expr]):
    cumulants = {}
    for i in range(1, len(moments.items()) + 1):
        c_i = moments[i]
        for k in range(1, i):
            c_i -= comb(i - 1, k - 1) * cumulants[k] * moments[i - k]
        cumulants[i] = c_i.expand()
    return cumulants


def raw_moments_to_centrals(moments: Dict[int, Expr]):
    centrals = {1: moments[1]}
    for i in range(2, len(moments.items()) + 1):
        c_i = sympify(0)
        for j in range(i + 1):
            m_j = moments[j] if j > 0 else 1
            c_i += comb(i, j) * ((-1) ** (i - j)) * m_j * (moments[1] ** (i - j))
        centrals[i] = c_i.expand()
    return centrals


def comb(n, k):
    return 0 if k > n else int(factorial(n) / (factorial(k) * factorial(n - k)))
