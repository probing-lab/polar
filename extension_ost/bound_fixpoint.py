"""This algorithm continuously tries to obtain new bounds as long as possible.

Note that in the current implementation, there needs to be an iter-variable named "k" present in the loop to analyze.
"""
from typing import Dict, List

from sympy import Expr, Interval, Symbol, oo, sympify, solve

ITER_VAR = Symbol("k", integer=True, positive=True)

def _get_upper_bound(monom, bounds: List[Expr]):
    # This function constructs an upper bound for the expected value of a given monomial. 
    # Either by finding a bound directly, or through having a bound on the value (not the expected value!) for some factor.
    pass

def try_get_new_bound(map: Expr, goal_expr: Expr, bounds: List[Expr]):
    # This function tries to get an upper/lower bound for the goal_epression E([some monomial]) by inserting known bounds into the expression map.
    # Bounds need to be of form "monomial [<>] expr"
    interval_k = Interval(1, oo)
    interval_y = Interval(-oo, 0)
    subst = {sympify('k'): interval_k, sympify('y'): interval_y}
    rearranged = solve(map, goal_expr)
    sol = rearranged[0].subs(subst)
    sol1 = sol.simplify()
    pass


