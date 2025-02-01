"""This algorithm continuously tries to obtain new bounds as long as possible.

Note that in the current implementation, there needs to be an iter-variable named "k" present in the loop to analyze.
"""
from typing import Dict

from sympy import Expr, Symbol

ITER_VAR = Symbol("k", integer=True, positive=True)

def try_get_new_bound(k_subs, bounds: Dict[Expr, Expr]):
    pass


