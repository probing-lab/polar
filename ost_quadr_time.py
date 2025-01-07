from sympy import expand, solve
from extension_ost.inner_loop_helper import get_martingale_for_inner_loop

LOOP_GUARD = 'y'
ITER_VAR = 'k'

VAR_OF_INTEREST = 'k**2'

expr = list(get_martingale_for_inner_loop(list(set(["k**2", "y*k", "k"]))))
print(expr)


# Get LB

# E(k**2) - E(kz) + yk = 0
# E(k**2) - E(kz) = - yk
# E(k**2) - E(kz) >= 0
# E(k**2) >= E(k*z)

# k**2 >= z**2 (since E(k) >= z, and z is a constant.)


expr = list(get_martingale_for_inner_loop(list(set(["(k-1)**2","k**2","k"]))))
print(expr)

# GET UB

# E((k-1)**2) - E((k-1)z) + E(y(k-1)) = 0
# From the second computed base: E((k-1)**2) = E(k**2) - E(2*k) +1
# This would also work without base, right?

# E(k**2) - E(2*k) + 1 - E((k-1)z) + E(y(k-1)) = 0

# E(k**2) - E(2*k) + 1 - E((k-1)z) = - E(y(k-1))
# E(k**2) - E(2*k) + 1 - E((k-1)z) <= 0 (since y is negative at k-1, and k > 1 (additional assumption! this is assumption is also connected to z>0))

# E(k**2) <= E(2*k) - 1 + E((k-1)z)
# E(k**2) <= 2*(z+1) - 1 + z**2



rhs = solve(expr.subs('k', 'k-1'), LOOP_GUARD)[0]

upper_bound_expression = 0 <= rhs

print(solve(upper_bound_expression, 'k'))