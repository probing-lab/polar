from sympy import expand, solve, sympify
from extension_ost.inner_loop_helper import get_martingale_for_inner_loop
from invariants.invariant_ideal import InvariantIdeal

LOOP_GUARD = 'y'
ITER_VAR = 'k'

VAR_OF_INTEREST = 'k**2'




closed_forms={}
closed_forms[f"E(k1-k)"] = sympify("1")
closed_forms[f"E(k1**2-k**2)"] = sympify("2*n+1")

closed_forms[f"E(x1-x)"] = sympify("-2/5")
closed_forms[f"E(x1**2 - x**2)"] = sympify("-4/5*x+ 1/3") # E(((y+r1)(y+r1)) = E(y^2 + 2r1 y + E(r1^2))
closed_forms[f"E(x1*k1 - x*k)"] = sympify("x - 2/5*n - 2/5") #(x+z)*(k+1) = (xk + x + zk + z)-xk = x - 2/5n - 2/5
# Construct the invariant ideal
invariant_ideal = InvariantIdeal(closed_forms)
basis = invariant_ideal.compute_basis()
print(basis)

