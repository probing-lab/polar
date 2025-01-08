from sympy import solve
from extension_ost.inner_loop_helper import get_martingale_for_inner_loop

LOOP_GUARD = 'y'
ITER_VAR = 'k'

VAR_OF_INTEREST = 'k'

expr = get_martingale_for_inner_loop(list(set([LOOP_GUARD, "k-1", VAR_OF_INTEREST])))

print(expr)
# Get LB
rhs = solve(expr, LOOP_GUARD)[0]

lower_bound_expr = 0 >= rhs

print(solve(lower_bound_expr, 'k'))

# GET UB

rhs = solve(expr.subs('k', 'k-1'), LOOP_GUARD)[0]

upper_bound_expression = 0 <= rhs

print(solve(upper_bound_expression, 'k'))