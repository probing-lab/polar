from sympy import expand, solve
from extension_ost.inner_loop_helper import get_martingale_for_inner_loop

LOOP_GUARD = 'y'
ITER_VAR = 'k'

VAR_OF_INTEREST = 'k**2'

monoms = ["k-1", "(k-1)**2", "y","y**2","y*(k-1)"]
monoms = ["k-(k1)", "k**2-(k1)**2", "y-y1", "y**2-y1**2", "y*k-(y1)*(k1)"]

def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1,1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]

def filter(x):
    if x.is_Atom:
        return True
    for arg in x.args:
        if arg.is_Pow or not filter(arg):
            return False
    return True

for s in powerset(monoms):
    expr = list(get_martingale_for_inner_loop(list(set(s))))
    print([e for e in expr if filter(e)])

print(expr)

# New attempt yields:
# E(k**2-(k1)**2) - E(y**2-y1**2) - 2*z + 2

# from that we derive the following martingale:
# (From the martingale-difference we just obtain the factors)
# E(k**2 - y**2 - (2z + 2)*k) = 0

# Hence:
# E(k**2) = E(y**2) + (2z+2)*k
# E(k**2) >= 0 + 2z**2 + 2z
# 
# Analogously:
# E(k**2) <= S**2 + (2z+2)*(z+1)
# E(k**2) <= S**2 + 2z**2 + 4z + 2 




# Get LB

# E(k**2) - E(kz) + yk = 0
# E(k**2) - E(kz) = - yk
# E(k**2) - E(kz) >= 0
# E(k**2) >= E(k*z)

# k**2 >= z**2 (since E(k) >= z, and z is a constant.)



# GET UB

# E((k-1)**2) - E((k-1)z) + E(y(k-1)) = 0
# From the second computed base: E((k-1)**2) = E(k**2) - E(2*k) +1
# This would also work without base, right?

# E(k**2) - E(2*k) + 1 - E((k-1)z) + E(y(k-1)) = 0

# E(k**2) - E(2*k) + 1 - E((k-1)z) = - E(y(k-1))
# E(k**2) - E(2*k) + 1 - E((k-1)z) <= 0 (since y is negative at k-1, and k > 1 (additional assumption! this is assumption is also connected to z>0))

# E(k**2) <= E(2*k) - 1 + E((k-1)z)
# E(k**2) <= 2*(z+1) - 1 + z**2







