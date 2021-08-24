from typing import Dict
from symengine.lib.symengine_wrapper import Expr
from math import comb


def raw_moments_to_cumulants(moments: Dict[int, Expr]):
    cumulants = {}
    for i in range(1, len(moments.items())+1):
        c_i = moments[i]
        for k in range(1, i):
            c_i -= comb(i-1, k-1) * cumulants[k] * moments[i-k]
        cumulants[i] = c_i.expand()
    return cumulants
