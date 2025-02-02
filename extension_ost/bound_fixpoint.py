"""This algorithm continuously tries to obtain new bounds as long as possible.

Note that in the current implementation, there needs to be an iter-variable named "k" present in the loop to analyze.
"""
from typing import Dict, List

from sympy import Expr, Symbol, sympify

ITER_VAR = Symbol("k", integer=True, positive=True)


def try_get_new_bound(map: Expr, goal_expr: Expr, bounds: List[Expr]):
    # This function tries to get an upper/lower bound for the goal_epression E([some monomial]) by inserting known bounds into the expression map.
    # Bounds need to be of form "monomial [<>] expr"
    
    pass


